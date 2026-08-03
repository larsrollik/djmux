# djmux

[![PyPI](https://img.shields.io/pypi/v/djmux.svg)](https://pypi.org/project/djmux/)
[![Python versions](https://img.shields.io/pypi/pyversions/djmux.svg)](https://pypi.org/project/djmux/)
[![License: BSD-3-Clause](https://img.shields.io/pypi/l/djmux.svg)](https://github.com/larsrollik/djmux/blob/main/LICENSE)
[![CI](https://github.com/larsrollik/djmux/actions/workflows/ci.yml/badge.svg)](https://github.com/larsrollik/djmux/actions/workflows/ci.yml)

**One config, many DataJoint packages on one server.** `djmux` lets several DataJoint
table-set packages run side-by-side on the same MySQL server — each under its own schema
**prefix** — from a single shared config file. It patches nothing else about DataJoint.

## Why

DataJoint natively supports a *single* schema prefix. As soon as you have more than one table-set
package on a server — a shared lab pipeline, a couple of per-user downstream packages, a `v1` and a
`v2` of the same schema — they either collide or need each package to hardcode a prefix. `djmux`
solves this with **one YAML file** that provides:

- the shared MySQL connection (standard `dj.config` keys), and
- a **map of schema prefixes keyed by package**.

Each package's schemas are then named `<prefix>__<name>`, so many packages activate together with
**no package hardcoding a prefix**, and versioning (`v1 → v2`) is a one-line config edit. Everything
else works exactly like stock DataJoint — `djmux` only patches `dj.config`.

## Install

```sh
pip install djmux
```

## Use

A single config file (`~/.djmux.yaml`, or point `$DJMUX_CONFIG` at it):

```yaml
datajoint:                     # standard DataJoint connection
  host: db.lab
  port: 3306
  user: alice
  password: ...
  use_tls: true
prefixes:                      # one prefix per table-set package (v1 -> v2 = edit here)
  mypipeline: mypipeline_v1      #   shared pipeline package -> schemas mypipeline_v1__<name>
  mine:      alice_replay      #   your downstream package  -> schemas alice_replay__<name>
stores:                        # optional filepath@ external store(s)
  tree: { location: /data/store }
```

Then several packages activate together, each under its own prefix:

```python
import djmux, mypipeline, my_replay
djmux.load("~/.djmux.yaml")    # sets the shared connection + prefix map (once)
mypipeline.activate()         # -> mypipeline_v1__*
my_replay.activate()            # -> alice_replay__*
```

A package makes itself djmux-aware by decorating tables with a **deferred** schema and delegating
activation:

```python
import datajoint as dj, djmux
schema = dj.Schema()            # deferred (unnamed)

@schema
class Session(dj.Manual): ...

def activate(**kw):
    djmux.activate(schema, key="mypipeline", name="core", linking_module=__name__, **kw)
```

## API

| function | purpose |
|---|---|
| `djmux.load(path=None)` | read the YAML, patch `dj.config` (connection + `custom.prefixes` + `stores`); enables `filepath@` |
| `djmux.activate(schema, key, name, ...)` | activate a deferred `dj.Schema()` as `<prefix>__<name>` (prefix from config `key`) |
| `djmux.get_datajoint_schema(file, module, key)` | eager per-file modular schema, `<prefix>__<filestem>` (orm-patterns style) |
| `djmux.schema_name(key, name)` / `resolve_prefix(key)` | naming helpers |

Prefix resolution order: explicit `override=` arg → `$DJMUX_PREFIX_<KEY>` env → config `prefixes[key]`.
Credentials may live in `~/.datajoint_config.json` instead and be omitted from the djmux config.

## Development

```sh
git clone https://github.com/larsrollik/djmux.git
cd djmux
uv sync --extra dev
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
uv run pytest
```

## Release

Bump `VERSION`, merge to `main`; the tag triggers a GitHub release + **OIDC trusted-publish** to PyPI
(no tokens). See `.github/workflows/release.yml`.

## License

BSD-3-Clause — see [LICENSE](LICENSE).
