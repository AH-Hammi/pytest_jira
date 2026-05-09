import six

from pytest_jira import _get_value
from pytest_jira import _load_default_config


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


def test_load_default_config_from_malformed_toml(tmp_path, capsys):
    config_path = tmp_path / "pytest_jira_default.toml"
    config_path.write_text("[default\nmarker_strategy = 'strict'")

    defaults = _load_default_config(tmp_path)
    stderr = capsys.readouterr().err
    assert "unable to parse" in stderr
    assert defaults["marker_strategy"] == "open"
    assert defaults["run_test_case"] == "true"
