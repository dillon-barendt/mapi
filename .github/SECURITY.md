# Security Policy

## Supported Versions

This repository is currently prepared as a public engineering artifact. Until a formal release process exists, security fixes should target the default development branch.

## Reporting A Vulnerability

Do not open a public issue that contains secrets, credentials, private URLs, session cookies, webhook tokens, or exploitable operational details.

For now, report sensitive findings directly to the repository owner through a private channel. A public GitHub Security Advisory workflow should be enabled before accepting external vulnerability reports at scale.

## Secret Handling Rules

- Do not commit `.env`, `.env.*`, generated `.logfire/` state, browser storage files, local databases, private keys, tokens, or provider credentials.
- Use `.env.example` for variable names only.
- Use environment variables, local secret stores, or deployment secret managers for real values.
- Keep provider credentials out of defaults, docs, tests, notebooks, and generated examples.
- Treat Playwright storage state as sensitive because it can contain authenticated cookies or session material.
- Treat webhook URLs and bearer tokens as credentials.

## Public Exposure Audit

The public-readiness pass identified these repository risks:

- Environment files were previously tracked: `.env.dev`, `.env.stage`, and `.env.prod`.
- Browser session state was previously tracked at `data/storage_state.json`.
- Generated package metadata was tracked under `src/brokervision.egg-info/`.
- Provider credential defaults existed in source code.
- The README contained a Logfire token-bearing setup command.
- `opencode.jsonc` contained a Logfire read token.
- Local runtime state exists outside tracked files, including `.logfire/`, `identifier.sqlite`, and sync ledger databases.

The working tree now ignores those classes of local state and replaces source defaults with blank or example-only values. Because some sensitive values were already present in tracked content, deleting them from the current tree is not enough before a public push.

## Required History Cleanup Before Publication

Before publishing or mirroring this repository publicly, rewrite history to remove any committed secrets and local state. Two common options are:

```bash
git filter-repo --path .env.dev --path .env.stage --path .env.prod --path data/storage_state.json --invert-paths
```

or, for broad secret scrubbing:

```bash
bfg --delete-files '.env*' --delete-files 'storage_state.json' --delete-files '*.sqlite' --delete-files '*.db'
```

After rewriting history:

```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

Rotate every credential that may have appeared in committed history, including provider credentials, Logfire tokens, webhook secrets, browser sessions, and API keys. History cleanup reduces exposure in Git, but rotation is the actual recovery step.

## Pre-Publish Checklist

- Run a secret scanner such as `gitleaks detect --source .`.
- Confirm `git ls-files` does not include `.env*`, `.logfire/`, browser storage, local databases, private keys, or generated package metadata.
- Confirm examples use placeholder values only.
- Confirm docs do not link to private dashboards, private portals, or internal infrastructure.
- Add an explicit license before inviting outside contributions.
- Enable GitHub secret scanning and private vulnerability reporting on the public repository.
