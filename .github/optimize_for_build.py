"""This script removes all unecessery files for building ``czech_plus`` into ``.ankiaddon``.

.. warn::
    It will remove ``.git`` too! Do not run anywhere, except CI!
"""
import os
import typing as t
from pathlib import Path

TO_KEEP: list[t.Callable[[str], bool]] = [
    lambda p: p.startswith("czech_plus"),
    lambda p: p in ("CONFIG.md", "config.json", "LICENSE"),
]

TO_REMOVE = [
    lambda p: "__pycache__" in p,
    lambda p: p
    in (
        "czech_plus/_vendor/win32_setctime.LICENSE",
        "czech_plus/_vendor/loguru/LICENSE",
        "czech_plus/_vendor/requirements.txt",
        "czech_plus/_vendor/README.md",
    ),
    lambda p: p.endswith("py.typed"),
    lambda p: p.endswith(".pyi"),
]


def for_removing(file: str) -> bool:
    """Checks, if file is needed to be removed."""
    return any(to_remove(file) for to_remove in TO_REMOVE) or not any(to_keep(file) for to_keep in TO_KEEP)


def main() -> None:
    """The entrypoint."""
    possible_dirs_to_remove: list[str] = []
    for file in get_list_of_files():
        if for_removing(file.replace("\\", "/")):
            try:
                os.remove(file)
            except (PermissionError, IsADirectoryError):  # `os.remove` can't remove folders. PermissionError on Windows
                possible_dirs_to_remove.append(file)

    possible_dirs_to_remove.reverse()
    for directory in possible_dirs_to_remove:
        os.rmdir(directory)


def get_list_of_files(path: Path = Path()) -> t.Iterator[str]:
    """Recursively walks through all the files."""
    for sub in path.iterdir():
        yield str(sub)
        if sub.is_dir():
            yield from get_list_of_files(sub)


if __name__ == "__main__":
    main()
