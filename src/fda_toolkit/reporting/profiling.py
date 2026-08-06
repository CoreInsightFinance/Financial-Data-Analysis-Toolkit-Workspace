"""
Data profiling and reporting utilities.

This module provides functions to generate comprehensive reports on
data structure, quality, and characteristics.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from fda_toolkit.utils.logging import audit_log
from fda_toolkit.registry import FUNCTION_REGISTRY
from fda_toolkit.registry import register_function


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
def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
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
def profile_report(df: pd.DataFrame) -> Dict[str, Any]:
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
    print(f"FDA Toolkit Quick Check")
    print(f"{'='*60}")
    print(f"\nShape:                  {summary['shape']}")
    print(f"Total cells:            {summary['total_cells']:,}")
    print(f"Null cells:             {summary['total_null_cells']:,} ({summary['total_null_percent']}%)")
    print(f"Duplicated rows:        {summary['duplicated_rows']}")
    print(f"Memory usage:           {summary['memory_usage_mb']:.2f} MB")

    missing = missingness_profile(df)
    high_missing = missing[missing["missing_percent"] > 50]
    if len(high_missing) > 0:
        print(f"\n⚠️  High missing values (>50%):")
        for _, row in high_missing.iterrows():
            print(f"   {row['column']}: {row['missing_percent']}%")

    print(f"\n{'='*60}\n")

    audit_log("quick_check", before=None, after=None)


@register_function(
    name="info",
    category="Reporting",
    module="reporting.profiling",
)
def info(category: Optional[str] = None, module: Optional[str] = None):
    """
    Return a function reference table with tooltips.

    Lists all available FDA Toolkit functions, automatically updated
    from the dynamic registry. Hover over function names to see descriptions.

    Args:
        category (str): Filter by category. ``"Core"`` returns all functions
            from the core package. Default: None (all functions)
        module (str): Filter by module. Default: None (all modules)

    Returns:
        pd.io.formats.style.Styler: Styled DataFrame with tooltip docstrings

    Example:
        >>> functions = info()
        >>> core_funcs = info(category='Core')
        >>> finance_funcs = info(category='Finance')
        >>> parsing_funcs = info(module='finance.parsing')
        >>> both = info(category='Finance', module='finance.parsing')
    """
    rows = []
    docstrings = {}
    
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
        
        func_name = f"{name}()"
        rows.append(
            {
                "function": func_name,
                "category": meta.get("category", "Uncategorized"),
                "module": meta.get("module", "unknown"),
            }
        )
        docstrings[func_name] = first_line

    df = (
        pd.DataFrame(rows)
        .sort_values(["category", "module", "function"])
        .reset_index(drop=True)
    )

    if category:
        if category.casefold() == "core":
            # Core functions are organized into descriptive categories such as
            # Data Quality and Type Conversion. Treat "Core" as their umbrella
            # category without replacing those useful labels in the output.
            df = df[df["module"].str.casefold().str.startswith("core.")].reset_index(drop=True)
        else:
            df = df[df["category"].str.casefold() == category.casefold()].reset_index(drop=True)
    
    if module:
        df = df[df["module"].str.lower() == module.lower()].reset_index(drop=True)

    audit_log("info", before=None, after=df)
    
    # Apply tooltips using pandas Styler
    def make_tooltip(val):
        tooltip = docstrings.get(val, "")
        return f'data-toggle="tooltip" title="{tooltip}"' if tooltip else ""
    
    styled = df.style.set_properties(**{'text-align': 'left'})
    
    # Add HTML attributes for tooltips (Jupyter/notebook compatible)
    styled = styled.set_uuid("fda-toolkit-info")
    
    return styled
