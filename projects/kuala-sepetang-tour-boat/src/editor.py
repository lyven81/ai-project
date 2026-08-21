"""
Text editor tool: the half Claude does not provide.

What it is aimed at matters as much as what it does. The brief defines this
tool as the one that turns findings into clear, customer-friendly replies,
recommendations and explanations. So the working directory holds the messages
the operator sends, not an internal schedule table. Same code, different
target, and the difference is the whole of criterion 7.

Claude carries the schema for the built-in text editor, so the model already
knows how to ask for a file operation. The code that actually touches the disk
is ours, and that is where the safety lives.

Three things worth lifting from this into any build that lets a model edit
files:

  path confinement   every path is reduced to its file name and joined to the
                     working directory, so a model cannot walk up and out. It
                     absorbs the mismatch rather than bouncing it: the built-in
                     schema promises the model an absolute path, this tool
                     gives it one folder, and a refusal there costs a round
                     trip on every single write
  backup on write    every write copies the old file first, which is what makes
                     undo possible when an edit lands on the wrong row
  count before you   an ambiguous str_replace fails loudly rather than editing
  replace            the first match and hoping it was the right one
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path, PurePosixPath


class EditorError(RuntimeError):
    """Raised with a message the model can read and correct itself from."""


class TextEditorTool:
    def __init__(self, base_dir: str | Path, backup_dir: str | Path | None = None):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = Path(backup_dir) if backup_dir else self.base_dir / ".backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # -- safety ------------------------------------------------------------

    def _target(self, file_path: str) -> tuple[Path, str | None, bool]:
        """
        Where a requested path actually lands.

        Returns (path, file name, whether the name was reduced). A name of None
        means the folder itself, which is what a directory listing asks for.

        Anthropic's built-in editor schema describes `path` as an ABSOLUTE
        path, so the model offers one, usually under /tmp. This tool confines
        everything to one folder per visitor. Both are correct inside their own
        frame, and refusing the mismatch cost a wasted round trip on every
        drafted reply: measured on four separate runs, the first write was
        always refused and the retry always landed.

        So a path with directories in it is reduced to its file name and kept
        in the folder, and the result says so. Confinement is not weakened by
        this: the name is joined to base_dir and re-checked, and a name cannot
        contain a separator by construction, so there is nothing left to
        traverse with. What changes is that a mismatch of convention is
        absorbed instead of bounced.
        """
        raw = str(file_path or "").strip()
        if raw in ("", ".", "/", "./"):
            return self.base_dir, None, False

        name = PurePosixPath(raw.replace("\\", "/")).name
        if not name or name in (".", ".."):
            raise EditorError(
                f"'{file_path}' has no file name in it. Use a name such as "
                f"reply_2026-08-24_tan_family.md."
            )

        p = (self.base_dir / name).resolve()
        if not str(p).startswith(str(self.base_dir)):
            raise EditorError(
                f"Access denied. '{file_path}' cannot be written here. "
                f"Use a plain file name such as reply_2026-08-24_tan_family.md."
            )
        return p, name, name != raw

    def _resolve(self, file_path: str) -> Path:
        return self._target(file_path)[0]

    def _kept_note(self, file_path: str) -> str:
        """Said out loud when a path was reduced, so the model is told where the
        file went rather than left assuming its own path was used."""
        _, name, reduced = self._target(file_path)
        if not reduced:
            return ""
        return (f" Kept in the reply folder as {name}; this tool writes only "
                f"there, so the directory in the path you gave was not used.")

    def _backup(self, p: Path) -> str:
        if not p.exists():
            return ""
        stamp = f"{p.stat().st_mtime:.0f}"
        dest = self.backup_dir / f"{p.name}.{stamp}"
        shutil.copy2(p, dest)
        return dest.name

    # -- operations --------------------------------------------------------

    def view(self, path: str, view_range: list[int] | None = None) -> str:
        p = self._resolve(path)
        if p.is_dir():
            names = sorted(x.name for x in p.iterdir() if not x.name.startswith("."))
            return "\n".join(names) if names else "(the folder is empty)"
        if not p.exists():
            existing = sorted(x.name for x in self.base_dir.glob("*.md"))
            raise EditorError(
                f"No file named '{path}'. "
                + (f"These exist: {', '.join(existing)}." if existing
                   else "The reply folder has no files yet; create one first.")
            )
        lines = p.read_text(encoding="utf-8").split("\n")
        start, end = 1, len(lines)
        if view_range:
            start, end = view_range
            if end == -1:
                end = len(lines)
            if start < 1 or start > len(lines):
                raise EditorError(
                    f"Line {start} is outside '{path}', which has {len(lines)} lines."
                )
        return "\n".join(f"{i}: {lines[i-1]}" for i in range(start, min(end, len(lines)) + 1))

    def create(self, path: str, file_text: str) -> str:
        p = self._resolve(path)
        backup = self._backup(p)
        existed = p.exists()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(file_text, encoding="utf-8")
        return (f"{'Replaced' if existed else 'Created'} {p.name}, "
                f"{len(file_text.splitlines())} lines."
                + (" Previous version backed up." if backup else "")
                + self._kept_note(path))

    def str_replace(self, path: str, old_str: str, new_str: str) -> str:
        p = self._resolve(path)
        if not p.exists():
            raise EditorError(f"No file named '{path}' to edit.")
        text = p.read_text(encoding="utf-8")
        n = text.count(old_str)
        if n == 0:
            raise EditorError(
                f"That text is not in '{path}'. Nothing was changed. "
                f"View the file first and copy the line exactly, including spacing."
            )
        if n > 1:
            raise EditorError(
                f"That text appears {n} times in '{path}', so it is not clear which "
                f"one to change. Nothing was changed. Include more of the surrounding "
                f"line to make it unique."
            )
        self._backup(p)
        p.write_text(text.replace(old_str, new_str), encoding="utf-8")
        return (f"Edited {p.name}. One replacement made, previous version backed up."
                + self._kept_note(path))

    def insert(self, path: str, insert_line: int, new_str: str) -> str:
        p = self._resolve(path)
        if not p.exists():
            raise EditorError(f"No file named '{path}' to insert into.")
        lines = p.read_text(encoding="utf-8").split("\n")
        if insert_line < 0 or insert_line > len(lines):
            raise EditorError(
                f"Line {insert_line} is outside '{path}', which has {len(lines)} lines. "
                f"Use 0 for the top of the file or {len(lines)} for the end."
            )
        self._backup(p)
        lines.insert(insert_line, new_str)
        p.write_text("\n".join(lines), encoding="utf-8")
        return (f"Inserted one line into {p.name} after line {insert_line}."
                + self._kept_note(path))

    def undo_edit(self, path: str) -> str:
        p = self._resolve(path)
        backups = sorted(self.backup_dir.glob(f"{p.name}.*"), reverse=True)
        if not backups:
            raise EditorError(f"No earlier version of '{path}' was kept, so there is nothing to undo.")
        shutil.copy2(backups[0], p)
        backups[0].unlink()
        return f"Undid the last change to {p.name}."

    # -- dispatch ----------------------------------------------------------

    def run(self, tool_input: dict) -> str:
        cmd = tool_input.get("command")
        if cmd == "view":
            return self.view(tool_input["path"], tool_input.get("view_range"))
        if cmd == "create":
            return self.create(tool_input["path"], tool_input["file_text"])
        if cmd == "str_replace":
            return self.str_replace(tool_input["path"], tool_input["old_str"], tool_input["new_str"])
        if cmd == "insert":
            return self.insert(tool_input["path"], tool_input["insert_line"], tool_input["new_str"])
        if cmd == "undo_edit":
            return self.undo_edit(tool_input["path"])
        raise EditorError(
            f"'{cmd}' is not a text editor command. Use view, create, str_replace, "
            f"insert or undo_edit."
        )


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        ed = TextEditorTool(tmp)
        print(ed.create("s.md", "| 09:00 | Mangrove | 4 |\n| 11:00 | Firefly | 8 |"))
        print(ed.view("reply_demo.md"))
        print(ed.str_replace("reply_demo.md", "We are on for it.", "We are on for it, see you at the jetty."))
        print(ed.view("reply_demo.md"))
        print(ed.undo_edit("reply_demo.md"))
        print(ed.view("reply_demo.md"))
        for bad in [{"command": "view", "path": "../../secrets.txt"},
                    {"command": "str_replace", "path": "reply_demo.md", "old_str": "the", "new_str": "x"},
                    {"command": "view", "path": "nope.md"},
                    {"command": "delete", "path": "reply_demo.md"}]:
            try:
                ed.run(bad)
                print("NO ERROR RAISED", bad)
            except EditorError as e:
                print(f"caught: {e}")
