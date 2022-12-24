"""Main package for ``czech-plus`` addon."""

from czech_plus._vendor.loguru import logger

from czech_plus import config, utils

__all__ = ["main"]


def main() -> None:
    """Main function to initialize and run entire addon."""
    utils.setup_logging()
    utils.compile_all_notes()
