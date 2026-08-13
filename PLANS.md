# Codex Execution Plans

An execution plan, or **ExecPlan**, is a self-contained living design document
that a coding agent or a developer unfamiliar with Mapi can follow to deliver a
working, observable result. Use ExecPlans for complex features, significant
refactors, migrations, cross-domain changes, and work with multiple verifiable
milestones.

Store each ExecPlan at `docs/plans/YYYY-MM-DD-<short-slug>.md`. The plan file is
the source of truth for the work it describes and must remain sufficient to
resume the task without relying on chat history or unstated prior knowledge.

## Authoring and Using ExecPlans

Read this entire file before writing or implementing an ExecPlan. Start from the
skeleton below, investigate the current tree, and replace every instructional
placeholder with project-specific content before implementation begins.

An ExecPlan must be:

- **Self-contained:** define non-obvious terms, describe the relevant current
  state, name exact repository-relative paths, and restate every assumption the
  executor needs.
- **Outcome-focused:** explain what a user or maintainer gains and how a human
  can observe that result, not merely which symbols will change.
- **Decision-complete:** settle interfaces, data flow, edge cases, compatibility,
  and validation choices so implementation does not require invention.
- **Living:** update progress, discoveries, decisions, commands, and outcomes at
  every stopping point. A resumed executor must be able to trust the file.
- **Safe and idempotent:** preserve unrelated worktree changes, prefer repeatable
  steps, and document recovery for risky or partially completed operations.

Keep narrative sections prose-first. Checklists belong in `Progress`. Use short
lists where they make contracts or commands clearer, but do not turn the plan
into an issue tracker detached from user-visible outcomes.

When implementing an approved ExecPlan, continue through its milestones without
asking the user to choose routine next steps. Stop and request direction when
work requires destructive action, new authority, ambiguous publication scope, a
material scope expansion, or a product decision the plan did not resolve.

## Mapi Planning Requirements

Before writing a plan, inspect the current branch, worktree, affected modules,
tests, configuration, and documentation. Historical plans and docs are evidence,
not guaranteed current truth.

Every Mapi ExecPlan must account for the applicable repository boundaries:

- Venue DSL behavior is pure and deterministic in
  `src/mapi/schemas/validators.py` and its Pydantic contracts.
- Schema.org event normalization and SQLite persistence live in
  `src/mapi/events/`.
- Provider-specific transport and payloads remain in
  `src/mapi/providers/<provider>/`.
- Cross-provider orchestration belongs in `src/mapi/services/`.
- Public HTTP contracts and error mapping belong in `src/mapi/api/v1/`.
- Configuration uses `APP_`-prefixed settings from
  `src/mapi/core/config.py`.

State which public routes, JSON aliases, environment variables, Python types,
database shapes, or compatibility aliases change. If none change, say so.
Distinguish existing behavior, behavior introduced by the plan, and ideas that
remain out of scope.

Plans involving external providers must include keyless tests, failure mapping,
timeouts, injectable fakes, and secret-handling constraints. Plans involving
SQLite must describe transaction/upsert behavior, stable ordering, recovery,
and how tests isolate database files. Plans involving the Venue DSL must name
the relevant gap, alias, range, duplicate, and round-trip invariants.

## Observable Milestones

Each milestone must produce an independently verifiable increment. Introduce it
with a short narrative that states:

1. what capability will exist at the end;
2. which repository areas will change;
3. how to exercise the capability; and
4. what exact result proves the milestone succeeded.

Use prototypes only when they reduce a specific uncertainty. Label them as
prototypes, give them promotion or deletion criteria, and keep them additive and
testable. Do not allow exploratory code to become an undocumented production
path.

Run focused tests after each meaningful change. Before completion, run the full
non-mutating repository gate from the repository root:

    UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv lock --check
    UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run ruff check . --no-cache
    UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run ruff format . --check --no-cache
    UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run mypy src --show-error-codes
    UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run pytest -q --no-cov
    git diff --check

Do not use `make quality` as an ExecPlan validation command: it applies unsafe
automatic fixes and supplies mypy with the nonexistent `tools` path. If the
default uv cache is inaccessible, use the explicit temporary cache shown above
and record the environment issue separately from code failures.

Validation must also demonstrate useful behavior. Depending on the change, this
may be a focused pytest scenario, a CLI transcript, a FastAPI `TestClient`
contract, a local HTTP request/response, a SQLite persistence/query example, or
an OpenAPI assertion. Include expected status codes, response fields, database
results, or other observable output.

## Living-Document Rules

The following sections are mandatory and must be kept current:

- `Progress`: timestamped UTC checkboxes for completed, pending, and partially
  completed work. Split partial work into explicit completed and remaining
  portions.
- `Surprises & Discoveries`: unexpected behavior, constraints, failures, or
  performance findings with concise evidence.
- `Decision Log`: each material decision, its rationale, and date/author.
- `Outcomes & Retrospective`: results, gaps, and lessons at major milestones and
  at completion, compared with the original purpose.

When implementation changes course, update every affected section rather than
adding a contradictory note at the end. Append a short revision note describing
what changed and why. Never leave `TBD`, `TODO`, vague error handling, unresolved
alternatives, or references to decisions that exist only in a conversation.

Commits are not implicit authorization. If the user explicitly requests commits
or publication, use small milestone-sized Conventional Commits with a required
scope and record the commit SHA in `Progress`. Otherwise, leave changes
unstaged. Never stage unrelated files or use `git add -A` in a mixed worktree.

## ExecPlan Skeleton

Copy the structure below into the new plan and replace all angle-bracketed
instructions with concrete content. Remove instructional text that is not part
of the finished plan.

    # <Short, action-oriented outcome>

    This ExecPlan is a living document governed by `PLANS.md`. Keep `Progress`,
    `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective`
    current as implementation proceeds.

    ## Purpose / Big Picture

    Explain what someone can do after the change that they cannot do now and
    how they can observe it working. Describe the current limitation in plain
    language.

    ## Progress

    - [x] (YYYY-MM-DD HH:MMZ) Completed step and evidence.
    - [ ] Pending step.
    - [ ] Partially completed step (completed: ...; remaining: ...).

    ## Surprises & Discoveries

    - Observation: Describe an unexpected fact or behavior.
      Evidence: Include a concise command result, test result, or source path.

    Use `None yet.` until implementation produces a discovery.

    ## Decision Log

    - Decision: State the resolved choice.
      Rationale: Explain why it fits the goal and repository constraints.
      Date/Author: YYYY-MM-DD / <name or agent>.

    ## Outcomes & Retrospective

    Summarize what is working, what remains, and lessons learned. Before work
    begins, state that this section will be completed at each major milestone.

    ## Context and Orientation

    Describe the current implementation for a reader new to Mapi. Define every
    domain term and name the exact files, functions, routes, settings, and tests
    that matter. Describe relevant worktree state and unrelated changes that
    must be preserved.

    ## Scope and Public Contracts

    State what is in scope and out of scope. Specify changes to HTTP routes,
    request/response fields, Schema.org aliases, Python types, database schema,
    environment settings, CLI behavior, and compatibility aliases. Explicitly
    say when a category is unchanged.

    ## Plan of Work

    Describe the ordered milestones in prose. For every milestone, name the
    affected repository areas, the behavior added, and how the result becomes
    independently verifiable. Resolve interfaces and failure behavior here.

    ## Concrete Steps

    Give exact commands and the repository root from which to run them. Name
    focused tests before the full gate and include short expected results. Keep
    commands non-mutating unless mutation is necessary and authorized.

    ## Validation and Acceptance

    Define acceptance as observable behavior with concrete inputs and outputs.
    Include regression, error, compatibility, and end-to-end scenarios relevant
    to the change. State the full Mapi gate and the expected successful result.

    ## Idempotence and Recovery

    Explain which steps can be repeated safely. For migrations or external
    effects, describe retry, backup, rollback, and partial-failure recovery.
    Explain how unrelated worktree changes remain protected.

    ## Artifacts and Evidence

    Preserve only concise transcripts, diffs, HTTP examples, query results, or
    logs that prove the outcome. Do not paste secrets or noisy command output.

    ## Interfaces and Dependencies

    Specify final module paths, public types, function signatures, protocols,
    schema aliases, settings, and dependency changes. Explain why each new
    dependency is necessary; write `No new dependencies.` when applicable.

    ## Revision Note

    Record the date, the sections changed, and why the ExecPlan was revised.

The finished ExecPlan must contain concrete project content rather than the
instructional examples above. A novice should be able to implement, verify, and
recover the work using only the current checkout, the plan, and standard
repository tooling.
