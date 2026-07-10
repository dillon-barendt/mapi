from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path

import logfire

DEFAULT_SERVICE_NAME = "tvx-agents-runner"
DEFAULT_MODEL = "gpt-5.4"
DEFAULT_RESUME_PROMPT = (
    "Inspect the current repository state and TASKS.md first, "
    "do not redo completed work, finish only incomplete tasks, rerun validations "
    "that are directly affected, update TASKS.md accurately, and summarize "
    "results with remaining blockers."
)


def _get_git_value(args: Sequence[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    value = result.stdout.strip()
    return value or None


def _detect_auth_mode() -> str:
    if os.getenv("CODEX_API_KEY") or os.getenv("OPENAI_API_KEY"):
        return "api-key"
    return "chatgpt"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resume the latest or a specific Codex run with Logfire instrumentation."
        ),
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=DEFAULT_RESUME_PROMPT,
        help="Continuation prompt sent to Codex after resume.",
    )
    parser.add_argument(
        "--session-id",
        help="Specific Codex session id to resume. Defaults to --last.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("CODEX_MODEL", DEFAULT_MODEL),
        help="Codex model to use when resuming.",
    )
    parser.add_argument(
        "--service-name",
        default=os.getenv("LOGFIRE_SERVICE_NAME", DEFAULT_SERVICE_NAME),
        help="Logfire service name.",
    )
    parser.add_argument(
        "--task-file",
        default="TASKS.md",
        help="Task file associated with the resumed run.",
    )
    parser.add_argument(
        "--sandbox",
        default=os.getenv("CODEX_SANDBOX", "workspace-write"),
        help="Codex sandbox mode.",
    )
    parser.add_argument(
        "--cd",
        dest="working_dir",
        type=Path,
        default=Path.cwd(),
        help="Working directory to execute Codex in.",
    )
    parser.add_argument(
        "--config",
        action="append",
        default=[],
        help="Optional repeated Codex --config key=value entries.",
    )
    parser.add_argument(
        "--skip-git-check",
        action="store_true",
        help="Do not fail when git metadata is unavailable.",
    )
    return parser


def _build_command(args: argparse.Namespace) -> list[str]:
    command = [
        "agents",
        "exec",
        "resume",
        "--cd",
        str(args.working_dir),
        "--sandbox",
        args.sandbox,
    ]
    if args.session_id:
        command.append(args.session_id)
    else:
        command.append("--last")
    command.extend(
        [
            "--model",
            args.model,
        ]
    )
    for entry in args.config:
        command.extend(["--config", entry])
    command.append(args.prompt)
    return command


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    logfire.configure(service_name=args.service_name)

    working_dir = args.working_dir.resolve()
    branch = _get_git_value(["branch", "--show-current"])
    commit = _get_git_value(["rev-parse", "HEAD"])
    auth_mode = _detect_auth_mode()

    if not args.skip_git_check and (branch is None or commit is None):
        raise SystemExit(
            "Git metadata is unavailable. Re-run with --skip-git-check to bypass."
        )

    command = _build_command(args)
    command_str = shlex.join(command)
    start = time.perf_counter()

    with logfire.span(
        "agents.exec.resume",
        model=args.model,
        auth_mode=auth_mode,
        cwd=str(working_dir),
        git_branch=branch,
        git_commit=commit,
        task_file=args.task_file,
        session_id=args.session_id or "last",
        prompt_preview=args.prompt[:200],
        command=command_str,
        sandbox=args.sandbox,
        config=args.config,
    ):
        result = subprocess.run(command, cwd=working_dir)
        duration_s = round(time.perf_counter() - start, 3)
        logfire.info(
            "agents.exec.resume.finished",
            returncode=result.returncode,
            duration_s=duration_s,
            model=args.model,
            auth_mode=auth_mode,
            cwd=str(working_dir),
            git_branch=branch,
            git_commit=commit,
            task_file=args.task_file,
            session_id=args.session_id or "last",
            command=command_str,
            sandbox=args.sandbox,
            config=args.config,
        )
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
