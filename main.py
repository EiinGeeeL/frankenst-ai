"""Entry point for assembling and compiling Frankenst-AI graph layouts.

Typical usage:
1. Choose or define a layout dataclass under `src/core_examples/config/layouts`.
2. Instantiate `WorkflowBuilder` with the layout and the matching state schema.
3. Compile the graph.
4. Invoke the compiled graph from a notebook, script or service entrypoint.

This file is intended for local assembly and experimentation. Service-specific
deployment entrypoints live under `src/services`.
"""