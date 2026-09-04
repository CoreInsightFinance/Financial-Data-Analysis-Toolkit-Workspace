"""
Column name cleaning and standardisation utilities.

This module contains functions used to clean and standardise
DataFrame column headers for reliable downstream analysis.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

import pandas as pd

from fda_toolkit.registry import register_function
from fda_toolkit.utils.logging import audit_log


@register_function(
    name="clean_column_headers",
    category="Column Management",
    module="core.columns",
)
def clean_column_headers(
    df: pd.DataFrame,
    lowercase: bool = True,
    replace_spaces_with: str = "_",
    remove_non_alnum: bool = True,
    copy: bool = True,
) -> pd.DataFrame:
    """
    Standardize column headers with flexible options.

    Performs the following steps in order:
    - Strip leading/trailing whitespace
    - Normalize consecutive spaces
    - Optional: convert to lowercase
    - Optional: replace spaces with specified character
    - Optional: remove non-alphanumeric characters
    - Handle duplicate column names by appending suffixes

    Args:
        df (pd.DataFrame): Input DataFrame
        lowercase (bool): Convert headers to lowercase. Default: True
        replace_spaces_with (str): Character replacing spaces.
            Default: "_"
        remove_non_alnum (bool): Remove non-alphanumeric chars.
            Default: True
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with standardized column headers

    Raises:
        TypeError: If input is not a pandas DataFrame

    Example:
        >>> df = pd.DataFrame({'Name ': [1], 'Age (years)': [2]})
        >>> clean_column_headers(df).columns.tolist()
        ['name', 'age_years']
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    cols = df.columns.astype(str).str.strip()

    if lowercase:
        cols = cols.str.lower()

    cols = cols.str.replace(r"\s+", replace_spaces_with, regex=True)

    if remove_non_alnum:
        pattern = rf"[^a-z0-9_{replace_spaces_with}]"
        cols = cols.str.replace(pattern, "", regex=True)

    pattern_dup = rf"{replace_spaces_with}+"
    cols = cols.str.replace(pattern_dup, replace_spaces_with, regex=True)
    cols = cols.str.strip(replace_spaces_with)

    # Handle duplicates
    seen: dict[Any, int] = {}
    new_cols: list[Any] = []
    for col in cols:
        count: int = seen.get(col, 0)
        new_cols.append(col if count == 0 else f"{col}_{count}")
        seen[col] = count + 1

    df.columns = new_cols
    audit_log("clean_column_headers", before=None, after=df)

    return df


@register_function(
    name="make_unique_columns",
    category="Column Management",
    module="core.columns",
)
def make_unique_columns(df: pd.DataFrame, copy: bool = True) -> pd.DataFrame:
    """
    Ensure column names are unique by appending numeric suffixes.

    For duplicate column names, appends _1, _2, etc. to create uniqueness.
    The first occurrence keeps its original name.

    Args:
        df (pd.DataFrame): Input DataFrame
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with unique column names

    Raises:
        TypeError: If input is not a pandas DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1], 'B': [2], 'A': [3]})  # Dup 'A'
        >>> make_unique_columns(df).columns.tolist()
        ['A', 'B', 'A_1']
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if copy:
        df = df.copy()

    seen: dict[Any, int] = {}
    new_cols: list[Any] = []
    for col in df.columns:
        count: int = seen.get(col, 0)
        new_cols.append(col if count == 0 else f"{col}_{count}")
        seen[col] = count + 1

    df.columns = new_cols
    audit_log("make_unique_columns", before=None, after=df)

    return df


def _require_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    selected = list(columns)
    missing = [column for column in selected if column not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")
    return selected


@register_function(name="rename_columns", category="Column Management", module="core.columns")
def rename_columns(df: pd.DataFrame, mapping: dict[str, str], copy: bool = True) -> pd.DataFrame:
    """Rename columns with validation for missing names and duplicate results."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if not isinstance(mapping, dict):
        raise TypeError("mapping must be a dictionary")
    _require_columns(df, mapping)
    result = df.copy() if copy else df
    renamed = [mapping.get(str(column), column) for column in result.columns]
    if len(renamed) != len(set(renamed)):
        raise ValueError("Renaming would create duplicate column names")
    result.columns = renamed
    audit_log("rename_columns", before=df.shape, after=result.shape)
    return result


@register_function(name="drop_empty_columns", category="Column Management", module="core.columns")
def drop_empty_columns(df: pd.DataFrame, copy: bool = True) -> pd.DataFrame:
    """Remove columns containing only missing or blank values."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    result = df.copy() if copy else df
    empty = result.apply(lambda column: column.isna() | column.astype("string").str.strip().eq(""))
    result.drop(columns=empty.all()[lambda values: values].index, inplace=True)
    audit_log("drop_empty_columns", before=df.shape, after=result.shape)
    return result


@register_function(
    name="drop_constant_columns", category="Column Management", module="core.columns"
)
def drop_constant_columns(
    df: pd.DataFrame, include_missing: bool = True, copy: bool = True
) -> pd.DataFrame:
    """Remove columns containing no more than one distinct value."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    result = df.copy() if copy else df
    constant = [
        column
        for column in result.columns
        if result[column].nunique(dropna=not include_missing) <= 1
    ]
    result.drop(columns=constant, inplace=True)
    audit_log("drop_constant_columns", before=df.shape, after=result.shape)
    return result


@register_function(name="drop_sparse_columns", category="Column Management", module="core.columns")
def drop_sparse_columns(
    df: pd.DataFrame, threshold: float = 0.9, copy: bool = True
) -> pd.DataFrame:
    """Remove columns whose missing-value proportion meets or exceeds a threshold."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    result = df.copy() if copy else df
    sparse = result.columns[result.isna().mean() >= threshold]
    result.drop(columns=sparse, inplace=True)
    audit_log("drop_sparse_columns", before=df.shape, after=result.shape)
    return result


@register_function(name="select_columns", category="Column Management", module="core.columns")
def select_columns(df: pd.DataFrame, columns: Iterable[str], copy: bool = True) -> pd.DataFrame:
    """Keep selected columns in the requested order."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    selected = _require_columns(df, columns)
    result = df.loc[:, selected]
    if copy:
        result = result.copy()
    audit_log("select_columns", before=df.shape, after=result.shape)
    return result


@register_function(name="reorder_columns", category="Column Management", module="core.columns")
def reorder_columns(
    df: pd.DataFrame, columns: Iterable[str], append_remaining: bool = True, copy: bool = True
) -> pd.DataFrame:
    """Move selected columns to the front in a specified order."""
    selected = _require_columns(df, columns)
    remaining = [column for column in df.columns if column not in selected]
    if not append_remaining and remaining:
        raise ValueError(f"Columns omitted from order: {remaining}")
    return select_columns(df, [*selected, *remaining] if append_remaining else selected, copy=copy)


@register_function(name="combine_columns", category="Column Management", module="core.columns")
def combine_columns(
    df: pd.DataFrame,
    columns: Iterable[str],
    output_column: str,
    separator: str = " ",
    drop_original: bool = False,
    copy: bool = True,
) -> pd.DataFrame:
    """Combine selected columns into one text column."""
    selected = _require_columns(df, columns)
    if not selected:
        raise ValueError("columns must contain at least one column")
    result = df.copy() if copy else df
    result[output_column] = (
        result[selected].fillna("").astype(str).agg(separator.join, axis=1).str.strip()
    )
    if drop_original:
        result.drop(
            columns=[column for column in selected if column != output_column], inplace=True
        )
    audit_log("combine_columns", before=df.shape, after=result.shape)
    return result


@register_function(name="split_column", category="Column Management", module="core.columns")
def split_column(
    df: pd.DataFrame,
    column: str,
    separator: str,
    output_columns: Iterable[str],
    max_splits: int = -1,
    drop_original: bool = False,
    copy: bool = True,
) -> pd.DataFrame:
    """Split one text column into named output columns."""
    _require_columns(df, [column])
    names = list(output_columns)
    if not names:
        raise ValueError("output_columns must contain at least one name")
    result = df.copy() if copy else df
    parts = result[column].astype("string").str.split(separator, n=max_splits, expand=True)
    if parts.shape[1] > len(names):
        raise ValueError("output_columns does not provide enough names for the split values")
    parts = parts.reindex(columns=range(len(names)))
    parts.columns = names
    for name in names:
        result[name] = parts[name]
    if drop_original and column not in names:
        result.drop(columns=column, inplace=True)
    audit_log("split_column", before=df.shape, after=result.shape)
    return result


@register_function(name="classify_columns", category="Column Management", module="core.columns")
def classify_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    """Group column names into numerical, categorical, datetime, and boolean types."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    groups = {
        "numerical": df.select_dtypes(include="number", exclude="bool").columns.tolist(),
        "categorical": df.select_dtypes(include=["object", "string", "category"]).columns.tolist(),
        "datetime": df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist(),
        "boolean": df.select_dtypes(include="bool").columns.tolist(),
    }
    audit_log("classify_columns", before=df.shape, after=groups)
    return groups


@register_function(
    name="select_columns_by_type", category="Column Management", module="core.columns"
)
def select_columns_by_type(
    df: pd.DataFrame,
    column_type: Literal["numerical", "categorical", "datetime", "boolean"],
    return_type: Literal["columns", "dataframe"] = "columns",
    copy: bool = True,
) -> list[str] | pd.DataFrame:
    """Return column names or data for one classified data type."""
    groups = classify_columns(df)
    if column_type not in groups:
        raise ValueError(f"Unknown column_type: {column_type}")
    if return_type == "columns":
        return groups[column_type]
    if return_type == "dataframe":
        return select_columns(df, groups[column_type], copy=copy)
    raise ValueError("return_type must be 'columns' or 'dataframe'")
