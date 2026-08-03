"""Per-package prefix resolution and ``'<prefix>__<name>'`` schema naming.

The prefix for a package is resolved: explicit ``override`` > ``$DJMUX_PREFIX_<KEY>``
> the config ``prefixes[key]`` map. This is the one thing DataJoint does not do
natively (it has a single ``database.prefix``); everything else is stock DataJoint.
"""
from __future__ import annotations

import os

import datajoint as dj

from . import config


def resolve_prefix(key: str, override: "str | None" = None) -> str:
    """Prefix for a package: explicit ``override`` > ``$DJMUX_PREFIX_<KEY>`` > config ``prefixes[key]``."""
    if override:
        return override
    env = os.environ.get(f"DJMUX_PREFIX_{key.upper()}")
    if env:
        return env
    prefixes = (dj.config.get("custom") or {}).get("prefixes") or config.CONFIG.get("prefixes") or {}
    if key in prefixes:
        return str(prefixes[key])
    raise KeyError(
        f"no prefix for package '{key}': set prefixes.{key} in the djmux config, pass override=, "
        f"or export DJMUX_PREFIX_{key.upper()}"
    )


def schema_name(key: str, name: str, override: "str | None" = None) -> str:
    """``'<prefix>__<name>'`` (double-underscore join; lbr_phd_db convention)."""
    return "__".join([resolve_prefix(key, override), name])
