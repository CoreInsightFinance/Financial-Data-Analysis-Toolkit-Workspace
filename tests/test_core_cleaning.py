import pandas as pd

import fda_toolkit as fda
from fda_toolkit import core


def test_column_structure_cleaners() -> None:
    df = pd.DataFrame(
        {
            "old": [1, 2],
            "empty": [None, " "],
            "constant": ["x", "x"],
            "sparse": [None, 1],
            "keep": [3, 4],
        }
    )

    result = fda.rename_columns(df, {"old": "identifier"})
    result = fda.drop_empty_columns(result)
    result = fda.drop_constant_columns(result)
    result = fda.drop_sparse_columns(result, threshold=0.5)

    assert result.columns.tolist() == ["identifier", "keep"]


def test_select_reorder_combine_and_split_columns() -> None:
    df = pd.DataFrame({"first": ["Ada"], "last": ["Lovelace"], "id": [1]})

    combined = fda.combine_columns(df, ["first", "last"], "name")
    split = fda.split_column(combined, "name", " ", ["given_name", "family_name"])
    reordered = fda.reorder_columns(split, ["id", "given_name", "family_name"])
    selected = fda.select_columns(reordered, ["id", "name"])

    assert combined.loc[0, "name"] == "Ada Lovelace"
    assert split.loc[0, "family_name"] == "Lovelace"
    assert reordered.columns[:3].tolist() == ["id", "given_name", "family_name"]
    assert selected.columns.tolist() == ["id", "name"]


def test_classify_and_select_columns_by_type() -> None:
    df = pd.DataFrame(
        {
            "amount": [1.5],
            "label": pd.Series(["sale"], dtype="string"),
            "date": pd.to_datetime(["2026-01-01"]),
            "approved": [True],
        }
    )

    groups = fda.classify_columns(df)

    assert groups == {
        "numerical": ["amount"],
        "categorical": ["label"],
        "datetime": ["date"],
        "boolean": ["approved"],
    }
    assert fda.select_columns_by_type(df, "numerical") == ["amount"]
    assert fda.select_columns_by_type(df, "categorical", "dataframe").columns.tolist() == ["label"]


def test_missing_and_structural_row_cleaners() -> None:
    df = pd.DataFrame(
        {
            "id": [None, "id", 1, 2, None, "Total", None],
            "amount": [None, "amount", 10, None, None, 10, None],
            "note": [None, "note", "ok", None, "present", None, None],
        }
    )

    result = fda.trim_leading_trailing_rows(df)
    result = fda.remove_repeated_headers(result)
    result = fda.remove_summary_rows(result, columns=["id"])
    result = fda.drop_empty_rows(result)
    result = fda.drop_sparse_rows(result, threshold=2 / 3)
    result = fda.drop_missing_required(result, ["id"])

    assert result["id"].tolist() == [1]


def test_explicit_and_range_row_filters() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-02-01", "invalid"],
            "amount": [10, 20, 30],
        }
    )

    explicit = fda.filter_rows(df, lambda frame: frame["amount"] >= 20)
    dated = fda.filter_by_date_range(df, "date", start="2026-01-15", end="2026-12-31")
    valued = fda.filter_by_value_range(df, "amount", minimum=15, maximum=25)

    assert explicit["amount"].tolist() == [20, 30]
    assert dated["amount"].tolist() == [20]
    assert valued["amount"].tolist() == [20]


def test_convert_multiple_date_columns() -> None:
    df = pd.DataFrame(
        {
            "invoice_date": ["01/02/2026", "invalid"],
            "payment_date": ["2026-02-10", "2026-02-11"],
        }
    )

    result = fda.convert_date_columns(
        df,
        ["invoice_date", "payment_date"],
        formats={"invoice_date": "%d/%m/%Y", "payment_date": "%Y-%m-%d"},
    )

    assert result.loc[0, "invoice_date"] == pd.Timestamp("2026-02-01")
    assert pd.isna(result.loc[1, "invoice_date"])
    assert pd.api.types.is_datetime64_any_dtype(result["payment_date"])


def test_new_functions_appear_in_core_info() -> None:
    functions = set(fda.info("core").data["function"])

    assert "classify_columns()" in functions
    assert "drop_empty_rows()" in functions
    assert "convert_date_columns()" in functions


def test_functions_can_be_imported_by_core_level() -> None:
    df = pd.DataFrame({"empty": [None], "amount": [1]})

    assert core.drop_empty_columns(df).columns.tolist() == ["amount"]
    assert core.classify_columns(df)["numerical"] == ["amount"]
