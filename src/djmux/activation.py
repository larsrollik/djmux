"""Schema activation helpers — deferred (Elements-style) and eager (modular) variants.

Both name schemas ``'<prefix>__<name>'`` with the prefix resolved from the config
map by ``key``. Generalises lbr_phd_db's ``get_datajoint_schema(...)`` factory to a
per-package prefix map.
"""
from __future__ import annotations

from pathlib import Path

import datajoint as dj

from .prefixes import schema_name


def deferred() -> dj.Schema:
    """A DEFERRED (unnamed) schema — decorate tables with it, activate later via :func:`activate`."""
    return dj.Schema()


def get_datajoint_schema(
    file: str,
    linking_module,
    key: str,
    override: "str | None" = None,
    *,
    create_schema: bool = True,
    create_tables: bool = True,
) -> dj.Schema:
    """orm-patterns style, per-file modular schema: name = ``<prefix>__<filestem>``,
    prefix resolved from the config map by ``key`` (or ``override``). EAGER — requires
    :func:`config.load` (or dj creds) beforehand. Use per table module::

        schema = djmux.get_datajoint_schema(__file__, __name__, key="mypipeline")   # -> <prefix>__ephys

    (Prefer :func:`activate` for deferred/import-anytime, Elements style.)
    """
    return dj.Schema(
        schema_name(key, Path(file).stem, override),
        create_schema=create_schema,
        create_tables=create_tables,
        add_objects=getattr(linking_module, "__dict__", None)
        if not isinstance(linking_module, str)
        else __import__("sys").modules.get(linking_module).__dict__,
    )


def activate(
    schema: dj.Schema,
    key: str,
    name: str,
    linking_module=None,
    override: "str | None" = None,
    *,
    create_schema: bool = True,
    create_tables: bool = True,
) -> dj.Schema:
    """Activate a deferred ``dj.Schema()`` under ``'<prefix>__<name>'``; ``key`` selects the
    per-package prefix from the config map (or ``override``). Call from a package's ``activate()``.
    """
    schema.activate(
        schema_name(key, name, override),
        create_schema=create_schema,
        create_tables=create_tables,
        add_objects=getattr(linking_module, "__dict__", None),
    )
    return schema
