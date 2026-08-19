"""Shared config load — patch the standard ``dj.config`` from one YAML file.

``load()`` reads a single YAML file and sets the *standard* DataJoint connection
keys plus a **map of schema prefixes keyed by package** (``custom.prefixes``), so
several table-set packages can activate side-by-side on the SAME server, each under
its own prefix, with no package hardcoding one. Everything else about DataJoint
works unchanged — this only patches ``dj.config``.

Config path resolution: explicit arg > ``$DJMUX_CONFIG`` > ``~/.djmux.yaml``.
"""

from __future__ import annotations

import os
from pathlib import Path

import datajoint as dj


#: The parsed config. Mutated in place by :func:`load` so re-exports stay live.
class _RedactedConfig(dict):
    """The config mapping, with secrets hidden from its display form.

    `load()` returns the config, and a REPL echoes whatever the last expression evaluates to -- so
    calling it at an IPython prompt or in a notebook cell printed the database password to the
    screen, and into any saved notebook output. Behaviour is unchanged (this is a plain dict for
    every purpose except display); only `repr` redacts, so the value is still readable by code that
    asks for it explicitly.
    """

    _SECRET_KEYS = ("password", "pass", "secret", "token", "key")

    @classmethod
    def _redact(cls, value):
        if isinstance(value, dict):
            return {
                k: (
                    "***" if any(s in k.lower() for s in cls._SECRET_KEYS) and v else cls._redact(v)
                )
                for k, v in value.items()
            }
        return value

    def __repr__(self) -> str:
        return repr(self._redact(dict(self)))

    __str__ = __repr__


CONFIG: dict = _RedactedConfig()


def load(path: str | os.PathLike | None = None) -> dict:
    """Load the shared config; set the MySQL connection + prefix map + filepath@ stores.

    Connection keys already present in ``~/.datajoint_config.json`` / ``DJ_*`` env are
    left to DataJoint if omitted here — this only sets what the config provides.
    """
    import yaml

    # the mypipeline schema (and others) use filepath@ stores; DataJoint gates this
    # experimental type behind an env var. Enable by default for every client (opt-out via env).
    os.environ.setdefault("DJ_SUPPORT_FILEPATH_MANAGEMENT", "TRUE")

    p = Path(path or os.environ.get("DJMUX_CONFIG", "~/.djmux.yaml")).expanduser()
    CONFIG.clear()
    CONFIG.update(yaml.safe_load(p.read_text()) or {})

    d = CONFIG.get("datajoint", {}) or {}
    if d.get("host"):
        dj.config["database.host"] = d["host"]
    if d.get("port"):
        dj.config["database.port"] = int(d["port"])
    if d.get("user"):
        dj.config["database.user"] = d["user"]
    if d.get("password") is not None:
        dj.config["database.password"] = d["password"]
    dj.config["database.use_tls"] = d.get("use_tls", True)
    dj.config["safemode"] = d.get("safemode", False)
    dj.config.setdefault("custom", {})["prefixes"] = CONFIG.get("prefixes", {}) or {}

    stores = CONFIG.get("stores") or {}
    if stores:
        dj.config["stores"] = {
            **(dj.config.get("stores") or {}),
            **{
                name: {
                    "protocol": s.get("protocol", "file"),
                    "location": s["location"],
                    "stage": s.get("stage", s["location"]),
                }
                for name, s in stores.items()
            },
        }
    return CONFIG
