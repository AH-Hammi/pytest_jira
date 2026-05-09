import six
import pytest

from pytest_jira import Configuration
from pytest_jira import _get_value
from pytest_jira import _load_default_config
from pytest_jira import _load_pyproject_config


def init_config_parser():
    c = six.moves.configparser.ConfigParser()
    c.set("DEFAULT", "key", "value")
    return c


def test_get_value1():
    c = init_config_parser()
    assert _get_value(c, "DEFAULT", "key") == "value"


def test_get_value2():
    c = init_config_parser()
    assert _get_value(c, "DEFAULT", "nokey") is None


def test_get_value3():
    c = init_config_parser()
    assert _get_value(c, "DEFAULT", "nokey", "one") == "one"


def test_load_default_config_without_toml(tmp_path):
    defaults = _load_default_config(tmp_path)
    assert defaults["marker_strategy"] == "open"
    assert defaults["resolved_statuses"] == "closed,resolved"
    assert defaults["connection_retry_total"] == "5"


def test_load_default_config_from_toml(tmp_path):
    config_path = tmp_path / "pytest_jira_default.toml"
    config_path.write_text(
        """
[default]
marker_strategy = "strict"
run_test_case = false
docs_search = true
connection_retry_total = 9
""".strip()
    )

    defaults = _load_default_config(tmp_path)
    assert defaults["marker_strategy"] == "strict"
    assert defaults["run_test_case"] == "false"
    assert defaults["docs_search"] == "true"
    assert defaults["connection_retry_total"] == "9"
    assert defaults["ssl_verification"] == "true"
    assert defaults["error_strategy"] == "strict"
    assert defaults["resolved_statuses"] == "closed,resolved"
    assert defaults["connection_retry_backoff_factor"] == "0.2"


def test_load_default_config_from_malformed_toml(tmp_path, capsys):
    config_path = tmp_path / "pytest_jira_default.toml"
    config_path.write_text("[default\nmarker_strategy = 'strict'")

    defaults = _load_default_config(tmp_path)
    stderr = capsys.readouterr().err
    assert "unable to parse" in stderr
    assert defaults["marker_strategy"] == "open"
    assert defaults["run_test_case"] == "true"
    assert defaults["ssl_verification"] == "true"
    assert defaults["error_strategy"] == "strict"
    assert defaults["connection_retry_backoff_factor"] == "0.2"


def test_load_pyproject_config(tmp_path):
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(
        """
[tool.pytest-jira]
marker_strategy = "warn"
run_test_case = false
resolved_statuses = ["resolved", "closed"]
connection_retry_total = 9
""".strip()
    )

    config = _load_pyproject_config(tmp_path)
    assert config["marker_strategy"] == "warn"
    assert config["run_test_case"] is False
    assert config["resolved_statuses"] == ["resolved", "closed"]
    assert config["connection_retry_total"] == 9


def test_load_default_config_from_pyproject(tmp_path):
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(
        """
[tool.pytest-jira]
marker_strategy = "warn"
run_test_case = false
resolved_statuses = ["resolved", "closed"]
""".strip()
    )

    defaults = _load_default_config(tmp_path)
    assert defaults["marker_strategy"] == "warn"
    assert defaults["run_test_case"] == "false"
    assert defaults["resolved_statuses"] == "resolved,closed"
    assert defaults["error_strategy"] == "strict"


def test_load_default_config_with_invalid_pyproject_setting(tmp_path):
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(
        """
[tool.pytest-jira]
marker_strategy = "invalid"
""".strip()
    )

    with pytest.raises(ValueError, match="Invalid pytest-jira configuration"):
        _load_default_config(tmp_path)


def test_configuration_normalizes_hyphenated_keys_and_lists():
    config = Configuration.validate(
        {
            "run-test-case": False,
            "resolved-statuses": ["closed", "resolved"],
            "marker-strategy": "WARN",
        }
    )
    assert config["run_test_case"] is False
    assert config["resolved_statuses"] == "closed,resolved"
    assert config["marker_strategy"] == "warn"
