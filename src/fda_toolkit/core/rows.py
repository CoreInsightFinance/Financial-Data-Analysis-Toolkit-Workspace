"""Row selection and cleaning utilities."""

from __future__ import annotations

from collections.abc import Callable, Iterable

import pandas as pd

from fda_toolkit.registry import register_function
from fda_toolkit.utils.logging import audit_log


def _require_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    selected = list(columns)
    missing = [column for column in selected if column not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")
    return selected


def _missing_mask(df: pd.DataFrame) -> pd.DataFrame:
    return df.isna() | df.astype("string").apply(lambda column: column.str.strip().eq(""))


def _finish(name: str, before: tuple[int, int], result: pd.DataFrame) -> pd.DataFrame:
    audit_log(name, before=before, after=result.shape)
    return result


@register_function(name="drop_empty_rows", category="Data Quality", module="core.rows")
def drop_empty_rows(df: pd.DataFrame, copy: bool = True) -> pd.DataFrame:
    """Remove rows containing no nonblank values."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    result = df.copy() if copy else df
    result.drop(index=result.index[_missing_mask(result).all(axis=1)], inplace=True)
    return _finish("drop_empty_rows", df.shape, result)


@register_function(name="drop_sparse_rows", category="Data Quality", module="core.rows")
def drop_sparse_rows(df: pd.DataFrame, threshold: float = 0.9, copy: bool = True) -> pd.DataFrame:
    """Remove rows whose missing-value proportion meets or exceeds a threshold."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    result = df.copy() if copy else df
    result.drop(index=result.index[_missing_mask(result).mean(axis=1) >= threshold], inplace=True)
    return _finish("drop_sparse_rows", df.shape, result)


@register_function(name="drop_missing_required", category="Data Quality", module="core.rows")
def drop_missing_required(
    df: pd.DataFrame,
    columns: Iterable[str],
    how: str = "any",
    copy: bool = True,
) -> pd.DataFrame:
    """Remove rows with blank values in required columns."""
    selected = _require_columns(df, columns)
    if how not in {"any", "all"}:
        raise ValueError("how must be 'any' or 'all'")
    result = df.copy() if copy else df
    missing = _missing_mask(result[selected])
    mask = missing.any(axis=1) if how == "any" else missing.all(axis=1)
    result.drop(index=result.index[mask], inplace=True)
    return _finish("drop_missing_required", df.shape, result)


@register_function(name="filter_rows", category="Data Quality", module="core.rows")
def filter_rows(
    df: pd.DataFrame,
    condition: pd.Series | Callable[[pd.DataFrame], pd.Series],
    keep: bool = True,
    copy: bool = True,
) -> pd.DataFrame:
    """Keep or remove rows selected by a boolean mask or callable condition."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    mask = condition(df) if callable(condition) else condition
    if not isinstance(mask, pd.Series) or not pd.api.types.is_bool_dtype(mask.dtype):
        raise TypeError("condition must produce a boolean pandas Series")
    mask = mask.reindex(df.index)
    if mask.isna().any():
        raise ValueError("condition must align with the DataFrame index")
    result = df.loc[mask if keep else ~mask]
    if copy:
        result = result.copy()
    return _finish("filter_rows", df.shape, result)


@register_function(name="remove_repeated_headers", category="Data Quality", module="core.rows")
def remove_repeated_headers(df: pd.DataFrame, copy: bool = True) -> pd.DataFrame:
    """Remove rows whose values repeat their corresponding column names."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    result = df.copy() if copy else df
    values = result.astype("string").apply(lambda column: column.str.strip().str.casefold())
    headers = pd.Series(
        [str(column).strip().casefold() for column in result.columns], index=result.columns
    )
    repeated = values.eq(headers, axis="columns").all(axis=1)
    result.drop(index=result.index[repeated], inplace=True)
    return _finish("remove_repeated_headers", df.shape, result)


@register_function(name="remove_summary_rows", category="Data Quality", module="core.rows")
def remove_summary_rows(
    df: pd.DataFrame,
    labels: Iterable[str] = ("total", "subtotal", "grand total"),
    columns: Iterable[str] | None = None,
    copy: bool = True,
) -> pd.DataFrame:
    """Remove spreadsheet summary rows identified by exact text labels."""
    selected = list(df.columns) if columns is None else _require_columns(df, columns)
    normalized_labels = {str(label).strip().casefold() for label in labels}
    result = df.copy() if copy else df
    matches = (
        result[selected]
        .astype("string")
        .apply(lambda column: column.str.strip().str.casefold().isin(normalized_labels))
    )
    result.drop(index=result.index[matches.any(axis=1)], inplace=True)
    return _finish("remove_summary_rows", df.shape, result)


@register_function(name="trim_leading_trailing_rows", category="Data Quality", module="core.rows")
def trim_leading_trailing_rows(df: pd.DataFrame, copy: bool = True) -> pd.DataFrame:
    """Remove blank rows before the first and after the last populated row."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    populated = ~_missing_mask(df).all(axis=1)
    if not populated.any():
        result = df.iloc[0:0]
    else:
        positions = populated.to_numpy().nonzero()[0]
        result = df.iloc[positions[0] : positions[-1] + 1]
    if copy:
        result = result.copy()
    return _finish("trim_leading_trailing_rows", df.shape, result)


@register_function(name="filter_by_date_range", category="Data Quality", module="core.rows")
def filter_by_date_range(
    df: pd.DataFrame,
    column: str,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
    inclusive: str = "both",
    copy: bool = True,
) -> pd.DataFrame:
    """Keep rows whose date value falls within an inclusive reporting period."""
    _require_columns(df, [column])
    if start is None and end is None:
        raise ValueError("start or end must be provided")
    dates = pd.to_datetime(df[column], errors="coerce")
    mask = dates.notna()
    if start is not None:
        start_date = pd.Timestamp(start)
        mask &= dates.ge(start_date) if inclusive in {"both", "left"} else dates.gt(start_date)
    if end is not None:
        end_date = pd.Timestamp(end)
        mask &= dates.le(end_date) if inclusive in {"both", "right"} else dates.lt(end_date)
    if inclusive not in {"both", "left", "right", "neither"}:
        raise ValueError("inclusive must be 'both', 'left', 'right', or 'neither'")
    result = df.loc[mask]
    if copy:
        result = result.copy()
    return _finish("filter_by_date_range", df.shape, result)


@register_function(name="filter_by_value_range", category="Data Quality", module="core.rows")
def filter_by_value_range(
    df: pd.DataFrame,
    column: str,
    minimum: float | None = None,
    maximum: float | None = None,
    inclusive: str = "both",
    copy: bool = True,
) -> pd.DataFrame:
    """Keep rows whose numeric value falls within a specified range."""
    _require_columns(df, [column])
    if minimum is None and maximum is None:
        raise ValueError("minimum or maximum must be provided")
    if inclusive not in {"both", "left", "right", "neither"}:
        raise ValueError("inclusive must be 'both', 'left', 'right', or 'neither'")
    values = pd.to_numeric(df[column], errors="coerce")
    mask = values.notna()
    if minimum is not None:
        mask &= values.ge(minimum) if inclusive in {"both", "left"} else values.gt(minimum)
    if maximum is not None:
        mask &= values.le(maximum) if inclusive in {"both", "right"} else values.lt(maximum)
    result = df.loc[mask]
    if copy:
        result = result.copy()
    return _finish("filter_by_value_range", df.shape, result)
