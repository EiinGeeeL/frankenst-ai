# Contributing

## Scope

This repository contains three different layers:

- `src/frankstate`: reusable public package surface.
- `src/core_examples`: reference package showing how to consume `frankstate`.
- `src/services`: runtime integrations and deployment-facing adapters.
- `research`: exploratory material that can inform future work but is not part of the repository's contractual surface.

Keep those boundaries explicit in pull requests.

## Local setup

Create and activate a virtual environment, then install the repository in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m uv pip install -e .[examples,dev]
```

## Tests

Run the test suite from the repository root:

```bash
pytest -q
```

If you touch packaging, also validate the distributions:

```bash
python -m build --wheel --sdist --no-isolation
```

## Pull requests

- Keep changes focused and avoid unrelated refactors.
- Add or update tests when modifying reusable contracts in `src/frankstate`.
- Update documentation when changing public behavior, install steps or repository structure.
- Preserve the distinction between public API, examples and service integrations.

## Documentation

- Prefer adding documentation close to the contract it explains: docstrings in `src/frankstate`, comments in YAML and examples in layout classes.
- When a component reads or writes new state keys, document that change in the state schema and in the component docstring.
- Keep project abstractions aligned with official LangGraph terminology to avoid confusion in new layouts.

## Issue reports

When opening a bug report, include:

- Python version
- installation method used
- minimal reproduction
- expected behavior
- actual behavior

For changes that affect providers such as Ollama, Azure AI or Foundry, include the relevant runtime configuration shape without exposing secrets.