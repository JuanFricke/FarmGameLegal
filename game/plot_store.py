"""
Persists each plot's Python source code on disk.

Directory layout:
    plots/
        plot_2_1.py   ← tile at col=2, row=1
        plot_4_3.py
        ...

Starter code is written on first interaction; subsequent opens read the saved version.
"""
from __future__ import annotations
from pathlib import Path

_PLOTS_DIR = Path("plots")


def _path(col: int, row: int) -> Path:
    return _PLOTS_DIR / f"plot_{col}_{row}.py"


def init(col: int, row: int, starter_code: str) -> Path:
    """
    Ensure the code file for (col, row) exists.
    Writes *starter_code* only if the file does not exist yet.
    Returns the file path.
    """
    _PLOTS_DIR.mkdir(exist_ok=True)
    p = _path(col, row)
    if not p.exists():
        p.write_text(starter_code, encoding="utf-8")
    return p


def load(col: int, row: int, fallback: str = "") -> str:
    """Read the saved code for (col, row), or return *fallback* if none."""
    p = _path(col, row)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return fallback


def save(col: int, row: int, code: str) -> None:
    """Overwrite the code file for (col, row)."""
    _PLOTS_DIR.mkdir(exist_ok=True)
    _path(col, row).write_text(code, encoding="utf-8")


def filepath(col: int, row: int) -> str:
    """Return the string path (creates the plots/ dir if needed)."""
    _PLOTS_DIR.mkdir(exist_ok=True)
    return str(_path(col, row))
