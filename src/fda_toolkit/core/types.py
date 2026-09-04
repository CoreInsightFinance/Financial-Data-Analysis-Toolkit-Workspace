"""
Data type conversion and cleaning utilities.

This module provides functions to convert and standardize data types
for numeric, boolean, and date columns.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from fda_toolkit.registry import register_function
from fda_toolkit.utils.logging import audit_log


@register_function(
    name="convert_data_types",
    category="Type Conversion",
    module="core.types",
)
def convert_data_types(
    df: pd.DataFrame,
    dtype_map: dict[str, Any],
    errors: str = "raise",
    copy: bool = True,
) -> pd.DataFrame:
    """
    Convert columns to specified dtypes.

    Applies dtype conversions from a mapping dictionary. Can coerce invalid
    values to NaN or raise errors based on the 'errors' parameter.

    Args:
        df (pd.DataFrame): Input DataFrame
        dtype_map (dict): Mapping of column names to target dtypes
        errors (str): How to handle errors - 'raise' or 'coerce'. Default: 'raise'
        copy (bool): Return a copy or modify in-place. Default: True

    Returns:
        pd.DataFrame: DataFrame with converted dtypes

    Raises:
        TypeError: If input is not a DataFrame or mapping is not a dict
        ValueError: If column doesn't exist (when errors='raise')

    Example:
        >>> df = pd.DataFrame({'A': ['1', '2'], 'B': ['x', 'y']})
        >>> convert_data_types(df, {'A': 'int64'}).dtypes['A']
        dtype('int64')
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if not isinstance(dtype_map, dict):
        raise TypeError("dtype_map must be a dictionary")

    if copy:
        df = df.copy()

    for col, dtype in dtype_map.items():
        if col not in df.columns:
            if errors == "raise":
                raise ValueError(f"Column '{col}' not found in DataFrame")
            continue

        try:
            df[col] = df[col].astype(dtype)
        except (ValueError, TypeError):
            if errors == "raise":
                raise
            elif errors == "coerce":
                df[col] = pd.to_numeric(df[col], errors="coerce")

    audit_log("convert_data_types", before=None, after=df)
    return df


@register_function(
    name="clean_numeric_column",
    category="Type Conversion",
    module="core.types",
)
def clean_numeric_column(
    s: pd.Series,
    thousands: str = ",",
    decimal: str = ".",
    allow_parentheses_negative: bool = True,
) -> pd.Series:
    """
    Clean numeric strings into numeric dtype.

    Removes thousands separators, handles different decimal notations,
    and optionally interprets parentheses as negative indicators.

    Args:
        s (pd.Series): Input Series with numeric strings
        thousands (str): Thousands separator character. Default: ","
        decimal (str): Decimal separator character. Default: "."
        allow_parentheses_negative (bool): Treat (n) as negative. Default: True

    Returns:
        pd.Series: Series with numeric dtype

    Raises:
        TypeError: If input is not a pandas Series

    Example:
        >>> s = pd.Series(['1,234.56', '(789.01)', '10.00'])
        >>> clean_numeric_column(s).tolist()
        [1234.56, -789.01, 10.0]
    """
    if not isinstance(s, pd.Series):
        raise TypeError("Input must be a pandas Series")

    s = s.copy()

    if allow_parentheses_negative:
        s = s.astype(str).str.replace(r"^\((.+)\)$", "-\\1", regex=True)

    s = s.astype(str).str.replace(thousands, "", regex=False)
    s = s.str.replace(decimal, ".", regex=False)

    s = pd.to_numeric(s, errors="coerce")

    audit_log("clean_numeric_column", before=None, after=s)
    return s


@register_function(
    name="clean_boolean_column",
    category="Type Conversion",
    module="core.types",
)
def clean_boolean_column(
    s: pd.Series,
    true_values: Iterable[str] = ("y", "yes", "true", "1"),
    false_values: Iterable[str] = ("n", "no", "false", "0"),
) -> pd.Series:
    """
    Standardize boolean-like values into True or False.

    Converts a wide variety of text representations into Boolean dtype,
    treating unlisted values as NaN.

    Args:
        s (pd.Series): Input Series with boolean-like strings
        true_values (Iterable[str]): Values to interpret as True. Default: standard true values
        false_values (Iterable[str]): Values to interpret as False. Default: standard false values

    Returns:
        pd.Series: Series with boolean dtype

    Raises:
        TypeError: If input is not a pandas Series

    Example:
        >>> s = pd.Series(['yes', 'no', 'y', 'n'])
        >>> clean_boolean_column(s).tolist()
        [True, False, True, False]
    """
    if not isinstance(s, pd.Series):
        raise TypeError("Input must be a pandas Series")

    s = s.copy()
    s_lower = s.astype(str).str.lower().str.strip()

    true_set = set(str(v).lower() for v in true_values)
    false_set = set(str(v).lower() for v in false_values)

    s = s_lower.map(lambda x: True if x in true_set else (False if x in false_set else None))

    audit_log("clean_boolean_column", before=None, after=s)
    return s


@register_function(
    name="clean_date_column",
    category="Type Conversion",
    module="core.types",
)
def clean_date_column(
    s: pd.Series,
    dayfirst: bool = True,
    errors: str = "coerce",
) -> pd.Series:
    """
    Parse dates safely into datetime dtype.

    Attempts to infer date formats and convert strings to pandas datetime.
    Invalid dates are coerced to NaT based on the 'errors' parameter.

    Args:
        s (pd.Series): Input Series with date strings
        dayfirst (bool): Interpret ambiguous dates as day/month/year. Default: True
        errors (str): How to handle errors - 'raise' or 'coerce'. Default: 'coerce'

    Returns:
        pd.Series: Series with datetime64 dtype

    Raises:
        TypeError: If input is not a pandas Series
        ValueError: If parsing fails and errors='raise'

    Example:
        >>> s = pd.Series(['01/12/2020', '15/12/2020', 'invalid'])
        >>> clean_date_column(s, dayfirst=True)
        0   2020-12-01
        1   2020-12-15
        2         NaT
    """
    if not isinstance(s, pd.Series):
        raise TypeError("Input must be a pandas Series")

    s = pd.to_datetime(s, dayfirst=dayfirst, errors=errors)

    audit_log("clean_date_column", before=None, after=s)
    return s


@register_function(
    name="convert_date_columns",
    category="Type Conversion",
    module="core.types",
)
def convert_date_columns(
    df: pd.DataFrame,
    columns: Iterable[str],
    dayfirst: bool = True,
    errors: str = "coerce",
    utc: bool = False,
    formats: dict[str, str] | None = None,
    normalize: bool = False,
    copy: bool = True,
) -> pd.DataFrame:
    """Convert multiple DataFrame columns to datetime values."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    selected = list(columns)
    missing = [column for column in selected if column not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")
    if errors not in {"raise", "coerce"}:
        raise ValueError("errors must be 'raise' or 'coerce'")
    unknown_formats = set(formats or {}) - set(selected)
    if unknown_formats:
        raise ValueError(f"Formats provided for unselected columns: {sorted(unknown_formats)}")

    result = df.copy() if copy else df
    for column in selected:
        result[column] = pd.to_datetime(
            result[column],
            format=(formats or {}).get(column),
            dayfirst=dayfirst,
            errors=errors,
            utc=utc,
        )
        if normalize:
            result[column] = result[column].dt.normalize()

    audit_log("convert_date_columns", before=df.shape, after=result.shape)
    return result
