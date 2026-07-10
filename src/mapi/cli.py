from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from mapi.services import compress_section_rows, load_csv_records


def import_csv(path: str) -> dict[str, dict[str, str]]:
    """
    Imports data from a CSV file and returns a structured dictionary.

    This function takes the path to a CSV file as input, reads the contents,
    and transforms them into a dictionary with sections and their corresponding
    records compressed into row format.

    :param path: The file path to the CSV file that needs to be imported.
    :type path: str

    :return: A dictionary where keys are section names and values are dictionaries
             mapping field names to their respective string values.
    :rtype: dict[str, dict[str, str]]
    """
    records = load_csv_records(path)
    return {"sections": compress_section_rows(records)}


def build_parser() -> argparse.ArgumentParser:
    """
    Builds an argument parser for the command-line interface of the Mapi tool.

    This function configures an argument parser with specific commands and their
    associated options for the Mapi local utilities. It's designed to facilitate
    the creation of synthetic venue row-map demonstrations with an available
    command for importing CSV data.

    :return: An instance of `argparse.ArgumentParser` configured with subcommands
             for the Mapi tool.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="python -m mapi.cli",
        description="Mapi local utilities for synthetic venue row-map demos.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    import_parser = subparsers.add_parser(
        "import-csv",
        help="Convert spreadsheet-shaped CSV rows into compact DSL values.",
    )
    import_parser.add_argument("path", help="Path to a CSV with section,row,position.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    The main function serves as the entry point for a command-line tool that processes
    commands and arguments. It supports the "import-csv" command for importing CSV
    data from a specified file path. It handles errors and prints error messages to
    standard error output. The function returns an exit status code.

    :param argv: A sequence of command-line arguments, typically parsed from sys.argv.
    :type argv: Sequence[str] | None
    :return: An integer indicating the exit status.
        Returns 0 on success and 1 on failure.
    :rtype: int
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "import-csv":
            payload = import_csv(args.path)
        else:
            parser.error(f"Unknown command: {args.command}")
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
