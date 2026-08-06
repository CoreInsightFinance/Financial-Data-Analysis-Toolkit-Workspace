import fda_toolkit as ftk


def test_info_core_returns_all_core_groups():
    result = ftk.info(category="Core").data

    assert not result.empty
    assert result["module"].str.startswith("core.").all()
    assert set(result["category"]) == {
        "Column Management",
        "Data Quality",
        "Outlier Detection",
        "Text Processing",
        "Type Conversion",
    }


def test_info_core_filter_is_case_insensitive():
    result = ftk.info(category="core").data

    assert not result.empty
    assert result["module"].str.startswith("core.").all()
