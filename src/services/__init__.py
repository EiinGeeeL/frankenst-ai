"""Repository service and integration layer.

`services` contains runtime-specific entrypoints such as MCP servers, Azure
Functions integrations and shared provider adapters used by this repository.

It is not part of the stable public API of `frankstate`, but parts of it may be
consumed by the repository reference package when a concrete provider adapter
is intentionally centralized here.
"""
