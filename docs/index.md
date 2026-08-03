# djmux

**One config, many DataJoint packages on one server.** `djmux` runs several DataJoint table-set
packages side-by-side on the same MySQL server, each under its own schema **prefix**, from a single
shared config file — patching nothing else about DataJoint.

## The problem it solves

DataJoint natively supports a *single* schema prefix. With more than one table-set package on a
server (a shared pipeline + per-user downstream packages + a versioned schema), they collide or must
hardcode prefixes. `djmux` reads **one YAML** → sets the standard `dj.config` connection **plus a map
of prefixes keyed by package**, names each package's schemas `<prefix>__<name>`, and makes `v1 → v2`
a one-line config edit.

## Install

```sh
pip install djmux
```

## Config (`~/.djmux.yaml`)

```yaml
datajoint: { host: db.lab, port: 3306, user: alice, password: ..., use_tls: true }
prefixes:
  mypipeline: mypipeline_v1   # shared pipeline  -> mypipeline_v1__<name>
  mine:      alice_replay   # your package     -> alice_replay__<name>
stores:
  tree: { location: /data/store }
```

## Usage

```python
import djmux, mypipeline, my_replay
djmux.load("~/.djmux.yaml")   # shared connection + prefix map (once)
mypipeline.activate()        # -> mypipeline_v1__*
my_replay.activate()           # -> alice_replay__*
```

A package becomes djmux-aware by decorating tables with a deferred `dj.Schema()` and delegating
activation to `djmux.activate(schema, key=..., name=..., linking_module=__name__)`.

**API**: `load`, `activate`, `get_datajoint_schema`, `schema_name`, `resolve_prefix`.
Prefix resolution: `override=` arg → `$DJMUX_PREFIX_<KEY>` env → config `prefixes[key]`.

See the [README](https://github.com/larsrollik/djmux#readme) for the full walkthrough.

## Development

```sh
git clone https://github.com/larsrollik/djmux.git
cd djmux
uv sync --extra dev
uv run pytest
```
