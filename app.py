"""Optional deployment entrypoint.

Use this module only when exposing a compiled graph through FastAPI, Streamlit
or another frontend/service layer.

The reusable graph assembly logic belongs in `main.py` and `src/core_examples`,
assembled with `src/frankstate` utilities. This file is intended for local assembly
and experimentation.

Service-specific entrypoints for cloud deployment live under `src/services`.
"""
