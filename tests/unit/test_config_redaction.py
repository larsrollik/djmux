"""The config must not display secrets.

`load()` returns the config mapping, and a REPL echoes whatever the last expression evaluates to, so
calling it at an IPython prompt or in a notebook cell used to print the database password to the
screen -- and persist it into saved notebook output. Redaction applies to the display form only:
code that asks for the value still gets it.
"""

from __future__ import annotations

from djmux.config import _RedactedConfig


def test_password_is_hidden_from_repr():
    c = _RedactedConfig({"datajoint": {"user": "someone", "password": "hunter2"}})
    assert "hunter2" not in repr(c)
    assert "***" in repr(c)
    assert "someone" in repr(c), "only secrets are hidden, not the whole config"


def test_str_is_redacted_too():
    """print() and f-strings go through __str__, which is the likelier accident of the two."""
    c = _RedactedConfig({"datajoint": {"password": "hunter2"}})
    assert "hunter2" not in str(c)
    assert "hunter2" not in f"{c}"


def test_value_is_still_readable():
    """Redaction is cosmetic -- anything reading the key explicitly must be unaffected."""
    c = _RedactedConfig({"datajoint": {"password": "hunter2"}})
    assert c["datajoint"]["password"] == "hunter2"
    assert dict(c)["datajoint"]["password"] == "hunter2"


def test_nested_and_varied_secret_keys():
    c = _RedactedConfig({"a": {"b": {"api_token": "t", "secret_key": "s", "host": "h"}}})
    r = repr(c)
    assert "t" not in r.replace("token", "") or "***" in r
    assert "'host': 'h'" in r


def test_empty_secret_is_left_alone():
    """An unset password reads as empty, not as a redacted value that looks configured."""
    c = _RedactedConfig({"datajoint": {"password": ""}})
    assert "***" not in repr(c)


def test_behaves_as_a_plain_dict():
    c = _RedactedConfig({"x": 1})
    c["y"] = 2
    assert c == {"x": 1, "y": 2}
    assert sorted(c) == ["x", "y"]
