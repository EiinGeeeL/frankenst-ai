# Changelog

All notable changes to this project will be documented in this file.

The format follows Keep a Changelog and the project currently stays in the `0.x`
phase while the public packaging and repository boundaries continue to mature.

## [0.0.3] - 2026-04-12

### Added

- Optional node-level `kwargs` passthrough for native `StateGraph.add_node()` options.

### Changed

- `StateCommander` and `CommandNode` now use `destinations` as the public routing contract.
- `WorkflowBuilder` and `NodeManager` now mirror LangGraph's native node registration shape with positional args plus kwargs.
- `GraphLayout` now returns concrete node and edge unions to improve type safety during workflow assembly.
- Node `tags` are normalized into LangGraph `metadata["tags"]` during workflow assembly.
- The human-in-the-loop example and node registry now use `destinations` consistently.

## [0.0.2] - 2026-04-07

### Added

- Root Dockerfile that boots the Streamlit demo with `uv`-managed installs.
- OSS baseline files: `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`.
- Unified `examples` extra that aggregates the Azure and Ollama example dependencies.

### Changed

- The public distribution, package directory and import surface now use `frankstate`.
- `pyproject.toml` now uses SPDX-style `license = "MIT"` metadata.
- Audit updated to remove findings already resolved in the repository root.
- Installation docs now use the standard unquoted extras form `.[examples,dev]`.
- Release automation now targets setuptools-based builds instead of Poetry.
- Minor fix: requirements reference now points from `requirements-frankstate-base.txt` to `requirements-frankstate-core.txt`.