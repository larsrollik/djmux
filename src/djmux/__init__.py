"""djmux — shared DataJoint connection + multi-prefix schema activation.

ONE config file feeds (a) the shared MySQL connection and (b) a MAP of schema
**prefixes keyed by package**, so several table-set packages activate side-by-side
on the SAME server, each under its own prefix, with no package hardcoding a prefix.
Versioning (v1 -> v2) is a config edit.

Typical use (several packages, same MySQL, own prefixes, all live)::

    import djmux, mypipeline, other_pkg

    djmux.load("~/.djmux.yaml")
    mypipeline.activate()  # -> mypipeline_v1__*
    other_pkg.activate()  # -> other_pkg_v1__*
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .activation import activate, deferred, get_datajoint_schema
from .config import CONFIG, load
from .prefixes import resolve_prefix, schema_name

try:
    __version__ = version("djmux")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

__all__ = [
    "load",
    "CONFIG",
    "resolve_prefix",
    "schema_name",
    "deferred",
    "get_datajoint_schema",
    "activate",
    "__version__",
]
