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
DEFAULT_SANDBOX = "workspace-write"


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
    return (
        "api-key"
        if os.getenv("CODEX_API_KEY") or os.getenv("OPENAI_API_KEY")
        else "chatgpt"
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Codex with Logfire instrumentation."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to send to Codex. Omit when using --prompt-file.",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Read the prompt from a file.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("CODEX_MODEL", DEFAULT_MODEL),
        help="Codex model to use.",
    )
    parser.add_argument(
        "--service-name",
        default=os.getenv("LOGFIRE_SERVICE_NAME", DEFAULT_SERVICE_NAME),
        help="Logfire service name.",
    )
    parser.add_argument(
        "--task-file",
        default="TASKS.md",
        help="Task file associated with the run.",
    )
    parser.add_argument(
        "--sandbox",
        default=os.getenv("CODEX_SANDBOX", DEFAULT_SANDBOX),
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
        metavar="KEY=VALUE",
        help="Optional repeated Codex --config key=value entries.",
    )
    parser.add_argument(
        "--skip-git-check",
        action="store_true",
        help="Do not fail when git metadata is unavailable.",
    )
    parser.add_argument(
        "--skill",
        help="Preferred Codex skill name to invoke through the prompt.",
    )
    parser.add_argument(
        "--automation",
        help="Preferred Codex automation name to mirror through the prompt.",
    )
    return parser


def _augment_prompt(
    prompt: str,
    *,
    skill: str | None,
    automation: str | None,
) -> str:
    instructions: list[str] = []

    if skill:
        instructions.append(
            f"Use the Codex skill named '{skill}' if it is available in this project. "
            "Load and follow that skill's workflow before inventing a new one."
        )

    if automation:
        instructions.append(
            f"Mirror the behavior of the Codex automation named '{automation}' "
            "if it exists. Treat its expected workflow as the operating pattern "
            "for this run."
        )

    if not instructions:
        return prompt

    return f"{'\n'.join(instructions)}\n\n{prompt}".strip()


def _read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file is not None:
        return str(args.prompt_file.read_text(encoding="utf-8").strip())
    if isinstance(args.prompt, str) and args.prompt:
        return args.prompt.strip()
    raise SystemExit("Provide a prompt argument or --prompt-file.")


def _build_command(args: argparse.Namespace, prompt: str) -> list[str]:
    command = [
        "agents",
        "exec",
        "--cd",
        str(args.working_dir),
        "--sandbox",
        args.sandbox,
        "--model",
        args.model,
    ]
    for entry in args.config:
        command.extend(["--config", entry])
    command.append(prompt)
    return command


def main() -> int:
    args = _build_parser().parse_args()
    prompt = _augment_prompt(
        _read_prompt(args),
        skill=args.skill,
        automation=args.automation,
    )

    logfire.configure(service_name=args.service_name)

    working_dir = args.working_dir.resolve()
    branch = _get_git_value(["branch", "--show-current"])
    commit = _get_git_value(["rev-parse", "HEAD"])
    auth_mode = _detect_auth_mode()

    if not args.skip_git_check and (branch is None or commit is None):
        raise SystemExit(
            "Git metadata is unavailable. Re-run with --skip-git-check to bypass."
        )

    command = _build_command(args, prompt)
    command_str = shlex.join(command)
    start = time.perf_counter()

    with logfire.span(
        "agents.exec",
        model=args.model,
        auth_mode=auth_mode,
        cwd=str(working_dir),
        git_branch=branch,
        git_commit=commit,
        task_file=args.task_file,
        skill=args.skill,
        automation=args.automation,
        prompt_preview=prompt[:200],
        command=command_str,
    ):
        result = subprocess.run(command, cwd=working_dir)
        duration_s = round(time.perf_counter() - start, 3)
        logfire.info(
            "agents.exec.finished",
            returncode=result.returncode,
            duration_s=duration_s,
            model=args.model,
            auth_mode=auth_mode,
            cwd=str(working_dir),
            git_branch=branch,
            git_commit=commit,
            task_file=args.task_file,
            skill=args.skill,
            automation=args.automation,
            command=command_str,
        )
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
