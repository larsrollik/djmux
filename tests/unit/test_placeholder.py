from __future__ import annotations

import djmux


def test_version() -> None:
    assert djmux.__version__ is not None
    assert isinstance(djmux.__version__, str)
