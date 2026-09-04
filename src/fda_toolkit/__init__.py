"""Top level imports for common FDA workflows."""

__version__ = "0.4.0"

# Core functions
from fda_toolkit.core.columns import (
    classify_columns,
    clean_column_headers,
    combine_columns,
    drop_constant_columns,
    drop_empty_columns,
    drop_sparse_columns,
    make_unique_columns,
    rename_columns,
    reorder_columns,
    select_columns,
    select_columns_by_type,
    split_column,
)
from fda_toolkit.core.duplicates import (
    deduplicate_by_priority,
    find_duplicates,
    remove_duplicates,
)
from fda_toolkit.core.missing import coerce_empty_to_nan, fill_missing
from fda_toolkit.core.outliers import (
    cap_outliers,
    detect_outliers_iqr,
    flag_outliers,
    remove_outliers_iqr,
    remove_outliers_zscore,
    winsorize_outliers,
)
from fda_toolkit.core.rows import (
    drop_empty_rows,
    drop_missing_required,
    drop_sparse_rows,
    filter_by_date_range,
    filter_by_value_range,
    filter_rows,
    remove_repeated_headers,
    remove_summary_rows,
    trim_leading_trailing_rows,
)
from fda_toolkit.core.text import (
    clean_categorical_column,
    clean_text_column,
    standardize_text_values,
)
from fda_toolkit.core.types import (
    clean_boolean_column,
    clean_date_column,
    clean_numeric_column,
    convert_data_types,
    convert_date_columns,
)

# Features
from fda_toolkit.features.categorical import (
    encode_categorical_variables,
    limit_cardinality,
    rare_category_handler,
)
from fda_toolkit.features.datetime import (
    create_fiscal_calendar_features,
    create_period_keys,
    extract_date_features,
    lag_features,
)
from fda_toolkit.finance.entities import (
    normalize_reference_codes,
    standardize_entity_names,
    strip_legal_suffixes,
)

# Finance
from fda_toolkit.finance.parsing import (
    clean_accounting_negative,
    parse_currency,
    parse_percentage,
)
from fda_toolkit.finance.rules import (
    check_balanced_entries,
    detect_outliers_groupwise,
    impute_by_rule,
    seasonality_aware_outliers,
    validate_sign_conventions,
)

# Input/Output
from fda_toolkit.io.readers import (
    chunked_processing,
    read_csv_safely,
    read_excel_safely,
)
from fda_toolkit.io.writers import export_parquet, export_validation_report

# Pipelines
from fda_toolkit.pipelines.quick_clean import quick_clean, quick_clean_finance
from fda_toolkit.reporting.delta import (
    compare_snapshots,
    delta_report,
    snapshot_dataset,
)

# Reporting
from fda_toolkit.reporting.profiling import (
    get_data_summary,
    infer_and_report_types,
    info,
    memory_profile,
    missingness_profile,
    profile_report,
    quick_check,
)

# Utilities
from fda_toolkit.utils.security import (
    anonymize_identifiers,
    mask_sensitive_fields,
)
from fda_toolkit.utils.types import optimize_dtypes
from fda_toolkit.validation.integrity import (
    assert_primary_key,
    check_data_consistency,
    check_referential_integrity,
    check_time_continuity,
    reconciliation_check,
)
from fda_toolkit.validation.ranges import validate_data_ranges

# Validation
from fda_toolkit.validation.schema import (
    standardize_schema,
    validate_category_set,
    validate_required_fields,
)

__all__ = [
    # Core
    "clean_column_headers",
    "make_unique_columns",
    "rename_columns",
    "drop_empty_columns",
    "drop_constant_columns",
    "drop_sparse_columns",
    "select_columns",
    "reorder_columns",
    "combine_columns",
    "split_column",
    "classify_columns",
    "select_columns_by_type",
    "convert_data_types",
    "clean_numeric_column",
    "clean_boolean_column",
    "clean_date_column",
    "convert_date_columns",
    "find_duplicates",
    "deduplicate_by_priority",
    "remove_duplicates",
    "coerce_empty_to_nan",
    "fill_missing",
    "detect_outliers_iqr",
    "remove_outliers_iqr",
    "remove_outliers_zscore",
    "flag_outliers",
    "cap_outliers",
    "winsorize_outliers",
    "clean_text_column",
    "standardize_text_values",
    "clean_categorical_column",
    "drop_empty_rows",
    "drop_sparse_rows",
    "drop_missing_required",
    "filter_rows",
    "remove_repeated_headers",
    "remove_summary_rows",
    "trim_leading_trailing_rows",
    "filter_by_date_range",
    "filter_by_value_range",
    # Features
    "limit_cardinality",
    "rare_category_handler",
    "encode_categorical_variables",
    "extract_date_features",
    "create_period_keys",
    "create_fiscal_calendar_features",
    "lag_features",
    # Finance
    "parse_currency",
    "parse_percentage",
    "clean_accounting_negative",
    "standardize_entity_names",
    "strip_legal_suffixes",
    "normalize_reference_codes",
    "impute_by_rule",
    "detect_outliers_groupwise",
    "seasonality_aware_outliers",
    "validate_sign_conventions",
    "check_balanced_entries",
    # I/O
    "read_csv_safely",
    "read_excel_safely",
    "chunked_processing",
    "export_parquet",
    "export_validation_report",
    # Validation
    "standardize_schema",
    "validate_required_fields",
    "validate_category_set",
    "validate_data_ranges",
    "assert_primary_key",
    "check_referential_integrity",
    "check_time_continuity",
    "check_data_consistency",
    "reconciliation_check",
    # Pipelines
    "quick_clean",
    "quick_clean_finance",
    # Reporting
    "quick_check",
    "profile_report",
    "get_data_summary",
    "missingness_profile",
    "infer_and_report_types",
    "memory_profile",
    "info",
    "snapshot_dataset",
    "compare_snapshots",
    "delta_report",
    # Utilities
    "mask_sensitive_fields",
    "anonymize_identifiers",
    "optimize_dtypes",
]
