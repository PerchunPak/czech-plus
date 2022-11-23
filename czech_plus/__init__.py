"""Main package for ``czech-plus`` addon."""

from czech_plus._vendor.loguru import logger

from czech_plus import config, utils

__all__ = ["main"]


def main() -> None:
    """Main function to run entire app."""
    utils.setup_logging()


main()
