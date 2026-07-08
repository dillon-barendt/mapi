# Mapi Documentation

This directory supports Mapi as a public engineering portfolio repository. The
examples are synthetic and should stay free of customer data, proprietary
credentials, or claims of production deployment.

## Suggested Repository Metadata

Repository description:

```text
Ticketing venue row-map parser, validator, diff engine, and review workflow API.
```

Suggested topics:

```text
python fastapi pydantic-v2 ticketing domain-modeling dsl parser redis portfolio-project
```

Suggested social preview:

```text
docs/assets/mapi-social-preview.svg
```

## Documentation Map

- [DOMAIN.md](DOMAIN.md): row progression DSL rules and examples.
- [ARCHITECTURE.md](ARCHITECTURE.md): parser, API, Redis, and agent flow.
- [REDIS_MODEL.md](REDIS_MODEL.md): Redis string, hash, JSON, and indexing model.
- [EXAMPLES.md](EXAMPLES.md): API and DSL examples.
- [PORTFOLIO_CASE_STUDY.md](PORTFOLIO_CASE_STUDY.md): recruiter-facing case study.
- [BROKER_WORKFLOW.md](BROKER_WORKFLOW.md): spreadsheet-to-review workflow.
- [DEMO.md](DEMO.md): local demo script.
- [PRODUCTION_EXTENSIONS.md](PRODUCTION_EXTENSIONS.md): realistic next steps.

## Public Repository Guardrails

- Keep all examples synthetic.
- Do not add private TicketVision credentials, broker data, customer venue maps,
  marketplace data, API keys, or personal tokens.
- Do not overclaim production usage. Describe Mapi as a portfolio case study
  unless the repository is later backed by a real deployment.
- Keep generated files, IDE settings, and local caches out of git.
