#!/usr/bin/env python3
"""Link workspace markdown into a MkDocs-visible tree under docs/linked."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_LINK_ROOT = REPO_ROOT / "docs" / "linked"
GENERATED_ROOT = DOCS_LINK_ROOT / "generated"

ROOT_MARKDOWN = (
    Path("README.md"),
    Path("CHANGELOG.md"),
    Path("SPEC-TICKETS.md"),
    Path("CONTRIBUTING.md"),
    Path("SECURITY.md"),
    Path("LICENSE.md"),
)
SCAN_ROOTS = (Path("apps"), Path("libs"))
IGNORED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "site",
    ".git",
}

APP_GAPS = {
    "tvx-watchlist": [
        "Connect the GameTime publish loop to the curated speculative inventory "
        "handoff instead "
        "of the current in-memory source hook.",
        "Drive sale-triggered hold and zero-out behavior directly from "
        "reconciliation events so "
        "speculative listings react before stale inventory sells again.",
        "Tighten GameTime reconciliation so listing-state decisions are explicit "
        "and observable.",
    ],
    "tvx-checkout": [
        "Add an idempotent acquisition lock keyed to the sale or inventory "
        "reservation so "
        "duplicate buys cannot race.",
        "Emit explicit result and audit topics instead of relying on local logs "
        "and session "
        "persistence alone.",
        "Capture purchase evidence and hand notifier-ready lifecycle events to "
        "downstream "
        "operators.",
        "Clarify the session-runtime contract between the shared Redis "
        "`cims_session`, the "
        "Playwright browser lifecycle, and the upstream dispatcher.",
    ],
    "tvx-gateway": [
        "Define a typed sale-ingress contract that maps cleanly from HTTP or RPC "
        "ingress to the "
        "checkout worker dispatch topic.",
        "Align the current dispatch topic with checkout's "
        "`purchase-to-inventory` subscriber or "
        "document a translator service explicitly.",
        "Add concrete operator-facing examples for the sale-detection to "
        "checkout-dispatch path.",
    ],
    "tvx-notifier": [
        "Cover the full lifecycle for sale detected, acquisition connect, "
        "acquisition success, "
        "acquisition failure, and listing hold flows with stable routing.",
        "Ensure checkout and watchlist producers emit notifier-v2 envelopes "
        "consistently across "
        "those lifecycle stages.",
        "Keep audit output tied to the same lifecycle so operator forensics do "
        "not depend on "
        "service-local logs.",
    ],
    "tvx-cli": [
        "Add operator workflows that exercise the full sale-to-acquisition path "
        "end to end, not "
        "just isolated service startup and Telegram probing.",
        "Provide repeatable commands or fixtures for validating gateway ingress, "
        "checkout pickup, "
        "watchlist reconciliation, and notifier fanout together.",
        "Keep the CLI as the documented source of truth for local runtime "
        "validation paths.",
    ],
}

FLOW_STAGES = (
    (
        "Signal & selection",
        ("tvx-watchlist", "tvx-cli"),
        "Watchlist still needs the curated speculative inventory handoff, and "
        "CLI still needs a "
        "repeatable operator probe for validating candidate selection.",
    ),
    (
        "Publish speculative offers",
        ("tvx-watchlist",),
        "The GameTime publisher is running safely, but it still depends on a "
        "local hook rather "
        "than the final curated inventory feed and listing-state controls.",
    ),
    (
        "Sale detection",
        ("tvx-gateway", "tvx-notifier"),
        "Gateway needs a typed sale-ingress contract, and notifier needs stable "
        "sale-detected "
        "coverage as the first operator-visible lifecycle event.",
    ),
    (
        "Acquisition / checkout",
        ("tvx-checkout", "tvx-gateway"),
        "Checkout still needs an idempotent critical section and a dispatcher "
        "contract that lines "
        "up with the real subscribed topic.",
    ),
    (
        "Post-purchase actions",
        ("tvx-checkout", "tvx-notifier"),
        "Checkout should emit structured result and audit events with evidence "
        "capture, and "
        "notifier should fan those lifecycle updates out to operators.",
    ),
    (
        "Inventory reconciliation",
        ("tvx-watchlist", "tvx-gateway"),
        "Watchlist should convert reconciliation changes into hold or zero-out "
        "actions, while "
        "gateway needs examples that show how operators trigger and inspect that flow.",
    ),
    (
        "Notifications & audit",
        ("tvx-notifier", "tvx-cli"),
        "Notifier and CLI together still need an operator-grade end-to-end path "
        "that validates "
        "audits, lifecycle fanout, and recovery expectations.",
    ),
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Mirror workspace markdown into docs/linked using symlinks and "
            "generated catalog pages."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify docs/linked already matches the expected linked tree.",
    )
    return parser.parse_args()


def is_ignored(path: Path) -> bool:
    """Check if a path should be ignored."""
    return any(part in IGNORED_PARTS for part in path.parts)


def iter_workspace_markdown() -> list[Path]:
    """Iterate over workspace markdown files."""
    markdown_paths: list[Path] = []

    for rel_path in ROOT_MARKDOWN:
        path = REPO_ROOT / rel_path
        if path.is_file():
            markdown_paths.append(rel_path)

    for scan_root in SCAN_ROOTS:
        root_path = REPO_ROOT / scan_root
        if not root_path.exists():
            continue
        for path in root_path.rglob("*.md"):
            if not path.is_file():
                continue
            rel_path = path.relative_to(REPO_ROOT)
            if is_ignored(rel_path):
                continue
            markdown_paths.append(rel_path)

    return sorted(set(markdown_paths), key=lambda path: path.as_posix())


def rel_link(from_path: Path, to_path: Path) -> str:
    """Get a relative link from one path to another."""
    return os.path.relpath(to_path, start=from_path.parent).replace(os.sep, "/")


def render_workspace_catalog(markdown_paths: list[Path]) -> str:
    """Render the workspace markdown catalog."""
    current_page = GENERATED_ROOT / "workspace-markdown.md"
    root_docs: list[Path] = []
    app_docs: dict[str, list[Path]] = defaultdict(list)
    lib_docs: dict[str, list[Path]] = defaultdict(list)

    for rel_path in markdown_paths:
        if len(rel_path.parts) == 1:
            root_docs.append(rel_path)
            continue
        if rel_path.parts[0] == "apps":
            app_docs[rel_path.parts[1]].append(rel_path)
            continue
        if rel_path.parts[0] == "libs":
            lib_docs[rel_path.parts[1]].append(rel_path)

    lines = [
        "# Workspace Markdown Catalog",
        "",
        "This page is generated by `tools/docs/link_workspace_markdown.py` and "
        "mirrors the "
        "workspace markdown linked under `docs/linked`.",
        "",
        f"- Total markdown files: `{len(markdown_paths)}`",
        f"- Root docs: `{len(root_docs)}`",
        f"- App docs: `{sum(len(paths) for paths in app_docs.values())}`",
        f"- Library docs: `{sum(len(paths) for paths in lib_docs.values())}`",
        "",
        "## Root Documents",
        "",
    ]

    for rel_path in root_docs:
        link_target = rel_link(current_page, DOCS_LINK_ROOT / rel_path)
        lines.append(f"- [{rel_path.as_posix()}]({link_target})")

    lines.extend(["", "## Apps", ""])
    for app_name in sorted(app_docs):
        lines.extend([f"### `{app_name}`", ""])
        for rel_path in sorted(app_docs[app_name], key=lambda path: path.as_posix()):
            link_target = rel_link(current_page, DOCS_LINK_ROOT / rel_path)
            lines.append(f"- [{rel_path.as_posix()}]({link_target})")
        lines.append("")

    lines.extend(["## Libraries", ""])
    for lib_name in sorted(lib_docs):
        lines.extend([f"### `{lib_name}`", ""])
        for rel_path in sorted(lib_docs[lib_name], key=lambda path: path.as_posix()):
            link_target = rel_link(current_page, DOCS_LINK_ROOT / rel_path)
            lines.append(f"- [{rel_path.as_posix()}]({link_target})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_dropshipping_gap_analysis() -> str:
    """Render the dropshipping gap analysis page."""
    current_page = GENERATED_ROOT / "dropshipping-gap-analysis.md"
    lines = [
        "# Dropshipping Gap Analysis",
        "",
        "This page is generated by `tools/docs/link_workspace_markdown.py` and "
        "summarizes the next requirements that remain between the current "
        "service docs and the target workflow in "
        "[SPEC-TICKETS.md]"
        f"({rel_link(current_page, DOCS_LINK_ROOT / 'SPEC-TICKETS.md')}).",
        "",
        "## Stage Coverage",
        "",
        "| Flow Stage | Current Owners | Next Requirement |",
        "| --- | --- | --- |",
    ]

    for stage, owners, summary in FLOW_STAGES:
        owner_labels = ", ".join(f"`{owner}`" for owner in owners)
        lines.append(f"| {stage} | {owner_labels} | {summary} |")

    lines.extend(["", "## App Requirements", ""])
    for app_name, requirements in APP_GAPS.items():
        root_state = DOCS_LINK_ROOT / "apps" / app_name / "CURRENT_STATE.md"
        docs_state = DOCS_LINK_ROOT / "apps" / app_name / "docs" / "CURRENT_STATE.md"
        root_link = rel_link(current_page, root_state)
        docs_link = rel_link(current_page, docs_state)
        lines.extend(
            [
                f"### `{app_name}`",
                "",
                f"- Root snapshot: [{app_name}/CURRENT_STATE.md]({root_link})",
                "- Rendered docs snapshot: "
                f"[{app_name}/docs/CURRENT_STATE.md]({docs_link})",
            ]
        )
        for requirement in requirements:
            lines.append(f"- {requirement}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def expected_link_targets(markdown_paths: list[Path]) -> dict[Path, Path]:
    """Generate expected link targets for given markdown paths."""
    return {rel_path: rel_path for rel_path in markdown_paths}


def expected_generated_files(markdown_paths: list[Path]) -> dict[Path, str]:
    """Generate expected generated files for given markdown paths."""
    return {
        Path("generated/workspace-markdown.md"): render_workspace_catalog(
            markdown_paths
        ),
        Path(
            "generated/dropshipping-gap-analysis.md"
        ): render_dropshipping_gap_analysis(),
    }


def expected_directories(
    symlinks: dict[Path, Path], generated_files: dict[Path, str]
) -> set[Path]:
    """Generate expected directories for given symlinks and generated files."""
    directories: set[Path] = set()
    for rel_path in (*symlinks.keys(), *generated_files.keys()):
        parent = rel_path.parent
        while parent != Path():
            directories.add(parent)
            parent = parent.parent
    return directories


def ensure_link_tree(markdown_paths: list[Path]) -> None:
    """Ensure the link tree exists and is up to date."""
    symlinks = expected_link_targets(markdown_paths)
    generated_files = expected_generated_files(markdown_paths)
    directories = expected_directories(symlinks, generated_files)

    if DOCS_LINK_ROOT.exists():
        shutil.rmtree(DOCS_LINK_ROOT)
    DOCS_LINK_ROOT.mkdir(parents=True, exist_ok=True)

    for rel_dir in sorted(directories, key=lambda path: path.as_posix()):
        (DOCS_LINK_ROOT / rel_dir).mkdir(parents=True, exist_ok=True)

    for dest_rel, source_rel in sorted(
        symlinks.items(), key=lambda item: item[0].as_posix()
    ):
        dest = DOCS_LINK_ROOT / dest_rel
        source = REPO_ROOT / source_rel
        target = os.path.relpath(source, start=dest.parent)
        dest.symlink_to(target)

    for dest_rel, content in generated_files.items():
        dest = DOCS_LINK_ROOT / dest_rel
        dest.write_text(content, encoding="utf-8")


def check_link_tree(markdown_paths: list[Path]) -> list[str]:
    """Check the link tree for consistency and completeness."""
    symlinks = expected_link_targets(markdown_paths)
    generated_files = expected_generated_files(markdown_paths)
    directories = expected_directories(symlinks, generated_files)
    errors: list[str] = []

    if not DOCS_LINK_ROOT.exists():
        return ["docs/linked does not exist"]

    expected_entries = directories | set(symlinks) | set(generated_files)
    actual_entries = {
        path.relative_to(DOCS_LINK_ROOT)
        for path in DOCS_LINK_ROOT.rglob("*")
        if path.name != ".DS_Store"
    }

    for extra in sorted(
        actual_entries - expected_entries, key=lambda path: path.as_posix()
    ):
        errors.append(f"unexpected path under docs/linked: {extra.as_posix()}")

    for missing in sorted(
        expected_entries - actual_entries, key=lambda path: path.as_posix()
    ):
        errors.append(f"missing path under docs/linked: {missing.as_posix()}")

    for rel_dir in sorted(directories, key=lambda path: path.as_posix()):
        path = DOCS_LINK_ROOT / rel_dir
        if not path.exists() or not path.is_dir():
            errors.append(
                f"expected directory missing or invalid: {rel_dir.as_posix()}"
            )

    for dest_rel, source_rel in sorted(
        symlinks.items(), key=lambda item: item[0].as_posix()
    ):
        dest = DOCS_LINK_ROOT / dest_rel
        if not dest.is_symlink():
            errors.append(f"expected symlink missing or invalid: {dest_rel.as_posix()}")
            continue
        expected_target = os.path.relpath(REPO_ROOT / source_rel, start=dest.parent)
        actual_target = os.readlink(dest)
        if actual_target != expected_target:
            errors.append(
                "symlink target mismatch for "
                f"{dest_rel.as_posix()}: expected {expected_target}, got "
                f"{actual_target}"
            )

    for dest_rel, expected_content in generated_files.items():
        dest = DOCS_LINK_ROOT / dest_rel
        if dest.is_symlink() or not dest.exists():
            errors.append(
                f"expected generated file missing or invalid: {dest_rel.as_posix()}"
            )
            continue
        actual_content = dest.read_text(encoding="utf-8")
        if actual_content != expected_content:
            errors.append(f"generated file content mismatch: {dest_rel.as_posix()}")

    return errors


def main() -> int:
    """Main entry point."""
    args = parse_args()
    markdown_paths = iter_workspace_markdown()

    if args.check:
        errors = check_link_tree(markdown_paths)
        if errors:
            for _error in errors:
                pass
            return 1
        return 0

    ensure_link_tree(markdown_paths)
    return 0


if __name__ == "__main__":
    sys.exit(main())
