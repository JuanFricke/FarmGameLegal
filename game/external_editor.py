"""
Opens a code file in the chosen editor inside the CURRENT terminal.

Press SPACE in the game to cycle through installed editors.
"""
from __future__ import annotations
import os
import shutil
import subprocess

# Editors shown in the cycle (Space key rotates through installed ones)
_CANDIDATES = ["nvim", "vim", "micro", "nano", "vi"]


def available_editors() -> list[str]:
    """Return base-names of editors that are actually installed."""
    found = []
    # Honour $VISUAL / $EDITOR first
    for env in (os.environ.get("VISUAL", ""), os.environ.get("EDITOR", "")):
        name = os.path.basename(env) if env else ""
        if name and shutil.which(env) and name not in found:
            found.append(name)
    for name in _CANDIDATES:
        if shutil.which(name) and name not in found:
            found.append(name)
    return found


class EditorManager:
    """Tracks which editor is currently selected and lets the player cycle."""

    def __init__(self) -> None:
        self._editors = available_editors()
        if not self._editors:
            raise RuntimeError(
                "Nenhum editor encontrado. Instale nvim, vim, micro ou nano,\n"
                "ou defina a variavel $EDITOR."
            )
        self._idx = 0

    @property
    def current(self) -> str:
        return self._editors[self._idx]

    @property
    def all(self) -> list[str]:
        return list(self._editors)

    def cycle(self) -> str:
        """Advance to the next editor and return its name."""
        self._idx = (self._idx + 1) % len(self._editors)
        return self.current

    def open(self, filepath: str) -> subprocess.Popen:
        """Spawn the current editor on *filepath* in the current terminal."""
        return subprocess.Popen([shutil.which(self.current) or self.current, filepath])
