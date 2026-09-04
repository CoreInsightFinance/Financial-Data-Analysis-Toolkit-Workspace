"""
Data profiling and reporting utilities.

This module provides functions to generate comprehensive reports on
data structure, quality, and characteristics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from fda_toolkit.registry import FUNCTION_REGISTRY, register_function
from fda_toolkit.utils.logging import audit_log

if TYPE_CHECKING:
    from pandas.io.formats.style import Styler


INFO_LEVELS = (
    "core",
    "features",
    "finance",
    "validation",
    "reporting",
    "input_output",
    "pipelines",
    "utils",
)


@register_function(
    name="infer_and_report_types",
    category="Reporting",
    module="reporting.profiling",
)
def infer_and_report_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a report of inferred types and current dtypes.

    Compares inferred types (based on content) with actual pandas dtypes
    to identify potential type conversion issues.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: Type report with columns: column, current_dtype, inferred_type

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': ['1', '2'], 'B': [1.5, 2.5]})
        >>> infer_and_report_types(df)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    report = []
    for col in df.columns:
        report.append(
            {
                "column": col,
                "current_dtype": str(df[col].dtype),
                "non_null_count": df[col].notna().sum(),
                "null_count": df[col].isna().sum(),
            }
        )

    result = pd.DataFrame(report)
    audit_log("infer_and_report_types", before=None, after=result)
    return result


@register_function(
    name="missingness_profile",
    category="Reporting",
    module="reporting.profiling",
)
def missingness_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return missing counts and percentages per column.

    Provides a comprehensive view of data completeness across all columns.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: Missingness report with counts and percentages

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1, None], 'B': [None, None]})
        >>> missingness_profile(df)
          column  missing_count  missing_percent
        0      A              1               50
        1      B              2              100
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    report = []
    for col in df.columns:
        missing = df[col].isna().sum()
        missing_pct = (missing / len(df)) * 100
        report.append(
            {
                "column": col,
                "missing_count": missing,
                "missing_percent": round(missing_pct, 2),
                "non_null_count": len(df) - missing,
            }
        )

    result = pd.DataFrame(report).sort_values("missing_percent", ascending=False)
    audit_log("missingness_profile", before=None, after=result)
    return result


@register_function(
    name="get_data_summary",
    category="Reporting",
    module="reporting.profiling",
)
def get_data_summary(df: pd.DataFrame) -> dict[str, Any]:
    """
    Return a compact summary of the dataset.

    Provides high-level statistics about shape, dtypes, and quality.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        dict: Summary dictionary with key statistics

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
        >>> summary = get_data_summary(df)
        >>> summary['shape']
        (3, 2)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    summary = {
        "shape": df.shape,
        "total_cells": df.shape[0] * df.shape[1],
        "dtypes_count": dict(df.dtypes.astype(str).value_counts()),
        "total_null_cells": df.isna().sum().sum(),
        "total_null_percent": round((df.isna().sum().sum() / (df.shape[0] * df.shape[1])) * 100, 2),
        "duplicated_rows": df.duplicated().sum(),
        "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 ** 2,
    }

    audit_log("get_data_summary", before=None, after=summary)
    return summary


@register_function(
    name="memory_profile",
    category="Reporting",
    module="reporting.profiling",
)
def memory_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return memory usage by column.

    Identifies columns consuming the most memory, useful for optimization.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: Memory usage report per column

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1]*1000, 'B': ['text']*1000})
        >>> memory_profile(df)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    memory = df.memory_usage(deep=True)
    report = pd.DataFrame(
        {
            "column": memory.index[1:],  # Skip index
            "memory_bytes": memory.values[1:],
        }
    )
    report["memory_mb"] = (report["memory_bytes"] / 1024 ** 2).round(3)
    report = report.sort_values("memory_bytes", ascending=False).reset_index(drop=True)

    audit_log("memory_profile", before=None, after=report)
    return report


@register_function(
    name="profile_report",
    category="Reporting",
    module="reporting.profiling",
)
def profile_report(df: pd.DataFrame) -> dict[str, Any]:
    """
    Return a combined profile report.

    Aggregates multiple profiling functions into one comprehensive report.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        dict: Complete profiling report

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
        >>> report = profile_report(df)
        >>> report['shape']
        (3, 2)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    report = {
        "summary": get_data_summary(df),
        "types": infer_and_report_types(df).to_dict(orient="records"),
        "missingness": missingness_profile(df).to_dict(orient="records"),
        "memory": memory_profile(df).to_dict(orient="records"),
    }

    audit_log("profile_report", before=None, after=report)
    return report


@register_function(
    name="quick_check",
    category="Reporting",
    module="reporting.profiling",
)
def quick_check(df: pd.DataFrame) -> None:
    """
    Print key checks for fast diagnosis.

    Displays a quick summary of the dataset for immediate insights.

    Args:
        df (pd.DataFrame): Input DataFrame

    Raises:
        TypeError: If input is not a DataFrame

    Example:
        >>> df = pd.DataFrame({'A': [1, 2, None], 'B': ['x', 'y', 'z']})
        >>> quick_check(df)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    summary = get_data_summary(df)

    print(f"\n{'='*60}")
    print("FDA Toolkit Quick Check")
    print(f"{'='*60}")
    print(f"\nShape:                  {summary['shape']}")
    print(f"Total cells:            {summary['total_cells']:,}")
    print(f"Null cells:             {summary['total_null_cells']:,} ({summary['total_null_percent']}%)")
    print(f"Duplicated rows:        {summary['duplicated_rows']}")
    print(f"Memory usage:           {summary['memory_usage_mb']:.2f} MB")

    missing = missingness_profile(df)
    high_missing = missing[missing["missing_percent"] > 50]
    if len(high_missing) > 0:
        print("\n⚠️  High missing values (>50%):")
        for _, row in high_missing.iterrows():
            print(f"   {row['column']}: {row['missing_percent']}%")

    print(f"\n{'='*60}\n")

    audit_log("quick_check", before=None, after=None)


@register_function(
    name="info",
    category="Reporting",
    module="reporting.profiling",
)
def info(
    sort_by: str | None = None,
    *,
    level: str | None = None,
    module: str | None = None,
) -> Styler:
    """
    Return a sortable function reference table.

    Lists all available FDA Toolkit functions, automatically updated
    from the dynamic registry. Each row includes the package level, module,
    function name, and a short note describing the function's use.

    Args:
        sort_by (str): Column to sort by (``"level"``, ``"module"``,
            ``"function"``, or ``"detail"``), or a package level to filter
            directly (for example, ``info("core")``). Default: None (level order)
        level (str): Filter by package level. Valid levels are ``core``,
            ``features``, ``finance``, ``validation``, ``reporting``,
            ``input_output``, ``pipelines``, and ``utils``.
        module (str): Filter by module. Default: None (all modules)

    Returns:
        pd.io.formats.style.Styler: Styled function reference table

    Example:
        >>> functions = info()
        >>> functions_by_level = info('level')
        >>> core_funcs = info('core')
        >>> parsing_funcs = info(module='finance.parsing')
        >>> both = info(level='finance', module='finance.parsing')
    """
    valid_sort_columns = {"level", "module", "function", "detail"}
    normalized_argument = "level" if sort_by is None else sort_by.casefold()
    if normalized_argument == "io":
        normalized_argument = "input_output"

    if normalized_argument in INFO_LEVELS:
        if level is not None and level.casefold() not in {normalized_argument, "io"}:
            raise ValueError("Specify a level either positionally or with level=, not both")
        level = normalized_argument
        normalized_sort = "level"
    elif normalized_argument in valid_sort_columns:
        normalized_sort = normalized_argument
    else:
        valid = ", ".join((*INFO_LEVELS, *sorted(valid_sort_columns)))
        raise ValueError(f"argument must be a level or sort column: {valid}")

    rows = []

    for name, meta in FUNCTION_REGISTRY.items():
        doc = meta.get("doc", "")
        # Extract first non-empty line from docstring
        first_line = ""
        if doc:
            for line in doc.split("\n"):
                stripped = line.strip()
                if stripped:
                    first_line = stripped
                    break

        module_name = meta.get("module", "unknown")
        package_name = module_name.split(".", maxsplit=1)[0].casefold()
        level_name = "input_output" if package_name == "io" else package_name

        rows.append(
            {
                "level": level_name,
                "module": module_name,
                "function": f"{name}()",
                "detail": first_line,
            }
        )

    df = pd.DataFrame(rows, columns=["level", "module", "function", "detail"])

    if level:
        normalized_level = level.casefold()
        if normalized_level == "io":
            normalized_level = "input_output"
        if normalized_level not in INFO_LEVELS:
            valid = ", ".join(INFO_LEVELS)
            raise ValueError(f"level must be one of: {valid}")
        df = df[df["level"].str.casefold() == normalized_level]

    if module:
        df = df[df["module"].str.casefold() == module.casefold()]

    if normalized_sort == "level":
        level_order = {name: position for position, name in enumerate(INFO_LEVELS)}
        df = (
            df.assign(_level_order=df["level"].map(level_order).fillna(len(INFO_LEVELS)))
            .sort_values(["_level_order", "module", "function"])
            .drop(columns="_level_order")
        )
    else:
        secondary_columns = [column for column in ("level", "module", "function") if column != normalized_sort]
        df = df.sort_values([normalized_sort, *secondary_columns])

    df = df.reset_index(drop=True)

    audit_log("info", before=None, after=df)

    styled = df.style.set_properties(**{"text-align": "left"})
    styled = styled.set_uuid("fda-toolkit-info")

    return styled
