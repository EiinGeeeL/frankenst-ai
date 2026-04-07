# Changelog

All notable changes to this project will be documented in this file.

The format follows Keep a Changelog and the project currently stays in the `0.x`
phase while the public packaging and repository boundaries continue to mature.

## [0.0.2] - 2026-04-07

### Added

- Root Dockerfile that boots the Streamlit demo with `uv`-managed installs.
- OSS baseline files: `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`.
- Unified `examples` extra that aggregates the Azure and Ollama example dependencies.

### Changed

- The public distribution, package directory and import surface now use `frankstate`.
- `pyproject.toml` now uses SPDX-style `license = "MIT"` metadata.
- Audit updated to remove findings already resolved in the repository root.
- Installation docs now use the quoted extras form `'.[examples, dev]'` when keeping spaces after the comma.
- Release automation now targets setuptools-based builds instead of Poetry.
- Minor fix base to core