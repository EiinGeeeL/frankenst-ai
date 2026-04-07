# Contributing

## Scope

This repository contains three different layers:

- `src/frankstate`: reusable public package surface.
- `src/core_examples`: reference package showing how to consume `frankstate`.
- `src/services`: runtime integrations and deployment-facing adapters.

Keep those boundaries explicit in pull requests.

## Local setup

Create and activate a virtual environment, then install the repository in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m uv pip install -e '.[examples, dev]'
```

The quotes are required if you keep the space after the comma. Without quotes,
the shell splits the extras expression into separate arguments.

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

## Issue reports

When opening a bug report, include:

- Python version
- installation method used
- minimal reproduction
- expected behavior
- actual behavior

For changes that affect providers such as Ollama, Azure AI or Foundry, include the relevant runtime configuration shape without exposing secrets.