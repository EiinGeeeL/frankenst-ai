# 🧟 Frankenst-AI | LangGraph Patterns
**Frankenst-AI** is a project that introduces a **modular and scalable structure** based on design patterns and coding best practices, applied to **LangGraph**.

It is not a framework that replaces LangGraph. It is a reusable project layer that helps you organize components, layouts and runtime assembly so you can build LangGraph workflows with less duplication and stronger boundaries.

This project aims to improve **scalability**, **reusability**, **testability**, and **maintainability** through reusable, configurable, and highly decoupled components designed to assemble complex LLM workflows.

By leveraging a well-organized structure, the project enables the creation of composable and extensible AI systems (agent patterns, RAG patterns, MCPs, etc.) while still returning official LangGraph graphs at the end of the build process.

The project has been designed with the following goals:

- **Isolated logic and separation of concerns** between conditional edges, nodes, tools, and runnables, encapsulated as reusable and independent components.

- Key components like **StateEnhancer**, **StateCommander**, and **StateEvaluator** are designed to be reused across multiple workflows.

- Use of YAML, **centralized configurations**, and explicit layout classes managed with builders and managers to define, **modify**, and **scale** different graph architectures **without duplicating logic**.

## How Frankenst-AI Maps to LangGraph

Frankenst-AI keeps the official LangGraph runtime model and adds a small layer
of project-specific naming around it:

- **StateEnhancer** wraps the async node callable that reads the current state and returns a partial update.
- **StateEvaluator** wraps the callable passed to conditional edges and returns the routing key used in the path map.
- **StateCommander** wraps nodes that return an official LangGraph `Command` when routing and state updates must happen in the same step.

These names are project abstractions, but the compiled graph still relies on
`StateGraph`, `add_node()`, `add_edge()`, `add_conditional_edges()` and
`Command` from LangGraph.

In other words, Frankenst-AI helps you structure and assemble LangGraph workflows; it does not introduce a separate graph runtime.

## Frank Public API

The root package `frank` intentionally exposes only one shortcut:

```python
from frank import WorkflowBuilder
```

That root import is reserved for the main assembly entrypoint.

All other reusable contracts should be imported from their concrete modules,
not from `frank.__init__`. For example:

```python
from frank.entity.graph_layout import GraphLayout
from frank.entity.node import SimpleNode, CommandNode
from frank.entity.edge import SimpleEdge, ConditionalEdge
from frank.entity.statehandler import StateEnhancer, StateEvaluator, StateCommander
from frank.entity.runnable_builder import RunnableBuilder
from frank.managers.node_manager import NodeManager
from frank.managers.edge_manager import EdgeManager
```

This keeps `frank` root stable and prevents it from turning into an absolute import bucket for every internal type.

## Repository Shape

This mono-repo has four layers with different responsibilities:

- `src/frank` is the reusable pattern layer. It contains the assembly utilities and contracts used to structure LangGraph projects with consistent design rules.
- `src/core_examples` is the repository's importable reference package. It demonstrates one concrete way to organize layouts, state models, components, YAML configuration and prompt assets on top of `frank`.
- `src/services` is the service and integration layer. It contains runtime-specific entrypoints such as MCP servers, Azure Functions handlers and shared provider adapters used by the repository.
- `research` is exploratory material. The notebooks are useful to understand how layouts are compiled and exercised, but they are not part of the project's contractual surface.

`src/core_examples` is supported as the repository reference package, but it is not the stable public API of the published base `frank` wheel. `src/services` is repository integration code, not an extension of the `frank` public API.

The published base wheel intentionally contains only `frank`. `core_examples` and `services` remain repository-level layers with different responsibilities.

If you are evaluating or reusing Frankenst-AI, start with `src/frank`, then move to `src/core_examples` for the concrete reference package, and only read `src/services` when you need repository runtime entrypoints or shared provider adapters.

## Prerequisites

- Python 3.12.10 or higher
- Ollama 0.20.2 or higher (free); or an Azure Foundry Deployment (payment)
- pip (Python package manager)
- uv (install with pip)

## Installation

1. Clone the repository

2. Create a virtual environment:

    ```python3 -m venv .venv```

3. Activate the virtual environment:
- On Windows:
  ```.venv\Scripts\activate```
- On macOS and Linux:
  ```source .venv/bin/activate```

4. Install the project:

    Minimal `frank` install:

    ```python3 -m uv pip install -e .```

    Reference implementation on Azure:

    ```python3 -m uv pip install -e .[examples-azure]```

    Reference implementation with Ollama:

    ```python3 -m uv pip install -e .[examples-ollama]```

    Development environment:

    ```python3 -m uv pip install -e .[examples-ollama,dev]```

    These extras install the dependency profiles used by the `core_examples` reference package and related repo entrypoints. The stable reusable API remains `frank`.

5. (Optional) Install system packages for the example extras:
    ```bash
    sudo apt update
    sudo apt-get install poppler-utils
    sudo apt install tesseract-ocr
    ```

## Running the Project Locally

To run the project locally:

1. Choose an LLM Services backend

   Choose one of the following options:

   #### 1.1 Using a local model with Ollama
   Start the Ollama service by running:
   
   ```ollama run ministral-3:8b```
  
   #### 1.2 Using Azure AI Foundry Deployment
    Configure your model variables in `.env`:

    ```cp .env.example .env```
2. Compile Graph Layouts with WorkflowBuilder
    
    The minimal example below uses the reference package under `src/core_examples` to show how `src/frank` is consumed in a real project.

    Reference layouts now follow a two-step contract:

    - `build_runtime()` resolves runtime dependencies such as LLM services, runnable builders, embeddings or retrievers.
    - The keys returned by `build_runtime()` are projected onto the layout instance and must be declared as annotated attributes in the layout class.
    - `layout()` declares nodes and edges using those already-resolved attributes on the layout instance.

    This keeps imports side-effect free while preserving a declarative layout file.

    In that example:

    - `WorkflowBuilder` is part of the reusable pattern in `src/frank`.
    - `SimpleOakConfigGraph` and `SharedState` are concrete reference classes from `src/core_examples`.
    - In your own project, those `src/core_examples` imports would be replaced by your own layouts and state schemas.

    For exploratory examples and experimentation, refer to the `research/demo...ipynb` notebooks.

#### Minimal WorkflowBuilder Example

```python
from frank import WorkflowBuilder
from core_examples.config.layouts.simple_oak_config_graph import SimpleOakConfigGraph
from core_examples.models.stategraph.stategraph import SharedState

workflow_builder = WorkflowBuilder(
    config=SimpleOakConfigGraph,
    state_schema=SharedState,
)

graph = workflow_builder.compile()
```

`graph` is still a LangGraph graph object produced through LangGraph's own runtime.

## Running Tests

Use the root pytest entrypoint:

```bash
pytest -q
```

`python -m pytest -q` should behave the same way, but `pytest -q` is the canonical local and CI command.

## Local Functions Apps Container 
- Start your Function App Container recipes: 
```bash 
docker build <build args -> build-and-push-acr.yml> mylocalfunction:0.1 . 
docker run -d -p 8080:80 mylocalfunction:0.1
docker logs <container_id>  
```

- Docker deep debug recipes: 
```bash 
docker exec -it <container_id> /bin/bash 
apt-get update 
apt-get install azure-functions-core-tools-4 
apt-get install azure-cli 
cd /home/site/wwwroot 
az login 
func start --verbose
```

## Repository Structure

```bash
frankenst-ai/
├── main.py                  # Local entry point to assemble and compile graph layouts
├── app.py                   # Optional deployment-facing wrapper entry point
├── requirements.txt         # Aggregate dependency set for the full repository environment
├── requirements-*.txt       # Dependency profiles split into base frank, example backends and dev
├── .env                     # Environment variables for local configuration; .env.example for reference
├── README.md                # Main project documentation
├── src/
│   ├── services/            # Service entrypoints plus shared provider adapters used by the repository
│   ├── core_examples/       # Importable reference package showing how to structure a real LangGraph project using `frank` utilities
│   │   ├── components/
│   │   │   ├── nodes/
│   │   │   │   ├── enhancers/        # StateEnhancers for simple node logic modifying StateGraph via runnables or custom modules
│   │   │   │   └── commands/         # StateCommander for routing and modifying state through LangGraph commands
│   │   │   ├── edges/
│   │   │   │   └── evaluators/       # StateEvaluator for conditional edge logic
│   │   │   ├── tools/                # Tool definitions and integrations
│   │   │   ├── retrievers/           # Retrievers definitions, builders and integrations
│   │   │   └── runnables/            # Executable LangChain RunnableBuilder modules for invoke or ainvoke logic
│   │   ├── config/
│   │   │   ├── config.yml            # Main runtime configuration file for the project
│   │   │   ├── config_nodes.yml      # Node registry used by the example graph layouts
│   │   │   └── layouts/              # Reference GraphLayout subclasses using build_runtime() + layout()
│   │   ├── constants/           
│   │   ├── models/                   # Structural models: StateGraph, tool properties, structured outputs, etc.
│   │   └── utils/                  
│   └── frank/               # Frank utilities for assembling and compiling LangGraph
│       ├── entity/
│       │   ├── graph_layout.py       # Base GraphLayout contract: build runtime first, then declare nodes and edges
│       │   ├── runnable_builder.py   # Builder class for LangChain Runnable objects
│       │   ├── statehandler.py       # Core entities for handling StateGraph
│       │   ├── node.py               # Core node-related entities 
│       │   └── edge.py               # Core edge-related entities
│       ├── managers/               
│       └── workflow_builder.py       # Workflow Builder to compile LangGraph from GraphLayout subclasses
├── research/                # Exploratory notebooks and experiments; useful as reference
├── tests/
│   ├── integration_test/      
│   └── unit_test/              
├── artifacts/               # Generated artifacts, static files and outputs
└── logs/                    # Log files and runtime logs
```

## Notes For Contributors

- Prefer adding documentation close to the contract it explains: docstrings in `src/frank`, comments in YAML and examples in layout classes.
- When a component reads or writes new state keys, document that change in the state schema and in the component docstring.
- Keep project abstractions aligned with official LangGraph terminology to avoid confusion in new layouts.
- Treat `src/core_examples` as the repository's reference package for the project's pattern and `research` as exploratory support material.
- Treat `src/services` as repository integration code, not as an extension of the public `frank` API.
