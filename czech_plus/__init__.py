"""Main package for ``czech-plus`` addon."""

from czech_plus._vendor.loguru import logger

from czech_plus import config, utils
from czech_plus.logic.hooks import append_hooks

__all__ = ["main"]


def main() -> None:
    """Main function to run entire app."""
    utils.setup_logging()
    append_hooks()


main()
