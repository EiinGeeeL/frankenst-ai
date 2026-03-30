"""Optional deployment entrypoint.

Use this module only when exposing a compiled graph through FastAPI, Streamlit
or another frontend/service layer.

The reusable graph assembly logic belongs in `main.py` and `src/core`, builder with `src/frank` utilities. This file is intended for local assembly and experimentation. 
Service-specific entrypoints under `src/services` for cloud deployment.
"""
