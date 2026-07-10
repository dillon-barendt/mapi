#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
cd "$REPO_ROOT"

TASKS_FILE="${1:-TASKS.md}"
MODEL="${MODEL:-gpt-5-agents}"
SANDBOX="${SANDBOX:-workspace-write}"
APPROVAL="${APPROVAL:-on-request}"
BASE_BRANCH="${BASE_BRANCH:-$(git branch --show-current 2>/dev/null || echo main)}"
SKILL_NAME="${SKILL_NAME:-thread-conventional-pr-push}"
DRY_RUN="${DRY_RUN:-0}"

if [[ ! -f "$TASKS_FILE" ]]; then
  echo "ERROR: TASKS file not found: $TASKS_FILE" >&2
  exit 1
fi

if ! command -v agents >/dev/null 2>&1; then
  echo "ERROR: codex CLI not found in PATH." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git not found in PATH." >&2
  exit 1
fi

slugify() {
  local s="$1"
  s="$(printf '%s' "$s" | tr '[:upper:]' '[:lower:]')"
  s="$(printf '%s' "$s" | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-{2,}/-/g')"
  printf '%s' "${s:0:48}"
}

extract_tasks() {
  python3 - "$TASKS_FILE" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

patterns = [
    re.compile(r'^\s*(\d+)\.\s+(.+?)\s*$', re.MULTILINE),
    re.compile(r'^\s*#+\s*(\d+)\.\s+(.+?)\s*$', re.MULTILINE),
    re.compile(r'^\s*#+\s*Task\s+(\d+)\s*[:\-]\s+(.+?)\s*$', re.MULTILINE | re.IGNORECASE),
]

seen = set()
for pat in patterns:
    for m in pat.finditer(text):
        num = m.group(1).strip()
        title = m.group(2).strip()
        key = (num, title)
        if key in seen:
            continue
        seen.add(key)
        print(f"{num}\t{title}")

if not seen:
    sys.exit(2)
PY
}

ensure_clean_tree() {
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERROR: Working tree is not clean. Commit/stash changes first." >&2
    exit 1
  fi
}

run_task() {
  local task_num="$1"
  local task_title="$2"

  local padded
  padded="$(printf '%02d' "$task_num")"

  local slug
  slug="$(slugify "$task_title")"
  local branch_name="task/${padded}-${slug}"

  echo
  echo "============================================================"
  echo "Task ${task_num}: ${task_title}"
  echo "Branch: ${branch_name}"
  echo "============================================================"

  git checkout "$BASE_BRANCH"
  git pull --ff-only || true
  git checkout -B "$branch_name"

  local prompt
  prompt=$(cat <<EOF
Read ${TASKS_FILE} and execute exactly one numbered task per run: task ${task_num}.

Task title:
${task_title}

${TASKS_FILE} is the source of truth for:
- scope
- dependencies
- implementation steps
- validation steps
- definition of done

Rules:
- work only on task ${task_num}
- do not batch multiple numbered tasks
- keep the diff strictly scoped to task ${task_num}
- run the task's validation steps before any commit
- only if validation passes, update ${TASKS_FILE} for task ${task_num}
- then invoke the skill '${SKILL_NAME}'
- create exactly one conventional commit
- push the branch
- open exactly one PR for task ${task_num}
- abort instead of guessing if boundaries are unclear or the diff becomes mixed
- do not create more than one commit
- do not open more than one PR
- do not modify unrelated tasks except for minimal explicitly required dependencies

Expected outputs:
- summary of changes
- validations run and results
- commit message
- commit hash
- PR URL
EOF
)

  if [[ "$DRY_RUN" == "1" ]]; then
    echo
    echo "[DRY RUN] agents exec --model \"$MODEL\" --sandbox \"$SANDBOX\" --ask-for-approval \"$APPROVAL\""
    echo "---------- PROMPT BEGIN ----------"
    printf '%s\n' "$prompt"
    echo "----------- PROMPT END -----------"
    return 0
  fi

  agents exec \
    --model "$MODEL" \
    --sandbox "$SANDBOX" \
    --ask-for-approval "$APPROVAL" \
    "$prompt"
}

main() {
  ensure_clean_tree

  local tasks
  if ! tasks="$(extract_tasks)"; then
    echo "ERROR: Could not detect numbered tasks in ${TASKS_FILE}" >&2
    exit 1
  fi

  echo "Base branch: ${BASE_BRANCH}"
  echo "Model: ${MODEL}"
  echo "Tasks file: ${TASKS_FILE}"
  echo

  while IFS=$'\t' read -r task_num task_title; do
    [[ -z "${task_num:-}" ]] && continue
    run_task "$task_num" "$task_title" || {
      echo
      echo "Stopped on task ${task_num}: ${task_title}" >&2
      exit 1
    }
  done <<< "$tasks"

  echo
  echo "All detected tasks processed."
}

main "$@"
