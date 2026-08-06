"""Top level imports for common FDA workflows."""

__version__ = "0.2.9"

# Core functions
from fda_toolkit.core.columns import clean_column_headers, make_unique_columns
from fda_toolkit.core.types import (
    convert_data_types,
    clean_numeric_column,
    clean_boolean_column,
    clean_date_column,
)
from fda_toolkit.core.duplicates import (
    find_duplicates,
    deduplicate_by_priority,
    remove_duplicates,
)
from fda_toolkit.core.missing import coerce_empty_to_nan, fill_missing
from fda_toolkit.core.outliers import (
    detect_outliers_iqr,
    remove_outliers_iqr,
    remove_outliers_zscore,
    flag_outliers,
    cap_outliers,
    winsorize_outliers,
)
from fda_toolkit.core.text import (
    clean_text_column,
    standardize_text_values,
    clean_categorical_column,
)

# Features
from fda_toolkit.features.categorical import (
    limit_cardinality,
    rare_category_handler,
    encode_categorical_variables,
)
from fda_toolkit.features.datetime import (
    extract_date_features,
    create_period_keys,
    create_fiscal_calendar_features,
    lag_features,
)

# Finance
from fda_toolkit.finance.parsing import (
    parse_currency,
    parse_percentage,
    clean_accounting_negative,
)
from fda_toolkit.finance.entities import (
    standardize_entity_names,
    strip_legal_suffixes,
    normalize_reference_codes,
)
from fda_toolkit.finance.rules import (
    impute_by_rule,
    detect_outliers_groupwise,
    seasonality_aware_outliers,
    validate_sign_conventions,
    check_balanced_entries,
)

# Input/Output
from fda_toolkit.io.readers import (
    read_csv_safely,
    read_excel_safely,
    chunked_processing,
)
from fda_toolkit.io.writers import export_parquet, export_validation_report

# Validation
from fda_toolkit.validation.schema import (
    standardize_schema,
    validate_required_fields,
    validate_category_set,
)
from fda_toolkit.validation.ranges import validate_data_ranges
from fda_toolkit.validation.integrity import (
    assert_primary_key,
    check_referential_integrity,
    check_time_continuity,
    check_data_consistency,
    reconciliation_check,
)

# Pipelines
from fda_toolkit.pipelines.quick_clean import quick_clean, quick_clean_finance

# Reporting
from fda_toolkit.reporting.profiling import (
    quick_check,
    profile_report,
    get_data_summary,
    missingness_profile,
    infer_and_report_types,
    memory_profile,
    info,
)
from fda_toolkit.reporting.delta import (
    snapshot_dataset,
    compare_snapshots,
    delta_report,
)

# Utilities
from fda_toolkit.utils.security import (
    mask_sensitive_fields,
    anonymize_identifiers,
)
from fda_toolkit.utils.types import optimize_dtypes

__all__ = [
    # Core
    "clean_column_headers",
    "make_unique_columns",
    "convert_data_types",
    "clean_numeric_column",
    "clean_boolean_column",
    "clean_date_column",
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
