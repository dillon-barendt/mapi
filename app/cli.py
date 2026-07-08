from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from app.services import compress_section_rows, load_csv_records


def import_csv(path: str) -> dict[str, dict[str, str]]:
    records = load_csv_records(path)
    return {"sections": compress_section_rows(records)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.cli",
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
