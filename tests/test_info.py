import fda_toolkit as ftk


def test_info_displays_requested_columns() -> None:
    result = ftk.info().data

    assert not result.empty
    assert list(result.columns) == ["level", "module", "function", "detail"]
    assert result["detail"].str.len().gt(0).all()


def test_info_level_filter_is_case_insensitive() -> None:
    result = ftk.info("Core").data

    assert not result.empty
    assert result["module"].str.startswith("core.").all()
    assert set(result["level"]) == {"core"}


def test_info_level_keyword_filter_remains_supported() -> None:
    result = ftk.info(level="finance").data

    assert not result.empty
    assert set(result["level"]) == {"finance"}


def test_info_level_sort_uses_package_workflow_order() -> None:
    result = ftk.info("level").data

    observed = list(dict.fromkeys(result["level"]))
    expected = [
        "core",
        "features",
        "finance",
        "validation",
        "reporting",
        "input_output",
        "pipelines",
        "utils",
    ]
    assert observed == expected


def test_info_defaults_to_level_sort() -> None:
    default_result = ftk.info().data
    level_result = ftk.info("level").data

    assert default_result.equals(level_result)


def test_info_maps_io_module_to_input_output_level() -> None:
    result = ftk.info(level="input_output").data

    assert not result.empty
    assert result["module"].str.startswith("io.").all()
