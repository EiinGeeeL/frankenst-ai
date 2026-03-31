# 🧟 Frankenst-AI | LangGraph Patterns
**Frankenst-AI** is a project that introduces a **modular and scalable architecture** based on design patterns and coding best practices, applied to **LangGraph**.

This project aims to improve **scalability**, **reusability**, **testability**, and **maintainability** through an architectural approach built on reusable, configurable, and highly decoupled components, designed to build complex workflows for LLMs.

By leveraging a well-organized and highly scalable structure, the project enables the creation of composable, configurable, and extensible AI systems (Agent patterns, RAG patterns, MCPs, etc.).

The project has been designed with the following goals:

- **Isolated logic and separation of concerns** between conditional edges, nodes, tools, and runnables, encapsulated as reusable and independent components.

- Key components like **StateEnhancer**, **StateCommander**, and **StateEvaluator** are designed for be used across multiple workflows.

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

## Repository Intent

This repository has three different roles, and it helps to read it that way:

- `src/frank` is the reusable pattern layer. It contains the core abstractions and assembly utilities used to structure LangGraph projects with consistent design rules.
- `src/core` is a reference template built on top of `src/frank`. It shows one concrete way to organize layouts, state models, components, YAML configuration and service integration in a real project.
- `research` is exploratory material. The notebooks are useful to understand how layouts are compiled and exercised, but they are not the contractual surface of the framework.

In other words, `src/frank` is the stable architectural idea, while `src/core` demonstrates how that idea can be applied in practice.

## How To Read This Repository

If you are evaluating or reusing Frankenst-AI:

- Read `src/frank` when you want to understand the reusable pattern, the abstractions and the workflow assembly model.
- Read `src/core` when you want a concrete scaffold showing how to build a real LangGraph project on top of that pattern.
- Read `research` only as exploratory support material.

The utilities contract and abstraction live in `src/frank`. The rest of the repository exists to demonstrate, apply or experiment with that contract.

## Prerequisites

- Python 3.12.5
- Ollama 4.0 or higher (free); or an Azure Foundry Deployment (payment)
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

    ```python3 -m uv pip install -e .```

5. (Optional) Install extra dependencies for unstructured:
    ```bash
    sudo apt update
    sudo apt-get install poppler-utils
    sudo apt install tesseract-ocr
    ```

## Running the Project Locally

To run the project:

1. Set LLM Services

   Choose one of the following options:

   #### 1.1 Using a local model with Ollama
   Start the Ollama service by running 
   
   ```ollama run ministral-3:8b```
  
   #### 1.2 Using Azure AI Foundry Deployment
    Config all your model variables in your ```.env```

    ```cp .env.example .env```
2. Compile Graph Layouts with Workflow Builder
    
    The minimal example below uses the reference template under `src/core` to show how `src/frank` is consumed in a real project.

    Reference layouts now follow a two-step contract:

    - `build_runtime()` resolves runtime dependencies such as LLM services, runnable builders, embeddings or retrievers.
    - The keys returned by `build_runtime()` are projected onto the layout instance and must be declared as annotated attributes in the layout class.
    - `layout()` declares nodes and edges using those already-resolved attributes on the layout instance.

    This keeps imports side-effect free while preserving the declarative layout style in the layout file itself.

    In that example:

    - `WorkflowBuilder` is part of the reusable pattern in `src/frank`.
    - `SimpleOakConfigGraph` and `SharedState` are concrete reference classes from `src/core`.
    - In your own project, those `src/core` imports would be replaced by your own layouts and state schemas.

    For exploratory examples and experimentation, please refer to the `research/demo...ipynb` notebooks.

#### Minimal WorkflowBuilder Example

```python
from frank.workflow_builder import WorkflowBuilder
from core.config.layouts.simple_oak_config_graph import SimpleOakConfigGraph
from core.models.stategraph.stategraph import SharedState

workflow_builder = WorkflowBuilder(
    config=SimpleOakConfigGraph,
    state_schema=SharedState,
)

graph = workflow_builder.compile()
```

## Local Functions Apps Container 
- Start your Function App Container recipes: 
```bash 
docker build <build args -> build-and-push-acr.yml> mylocalfunction:0.1 . 
docker run -d -p 8080:80 
mylocalfunction:0.1 docker logs <container_id>  
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
├── requirements.txt         # Python dependencies for the project
├── .env                     # Environment variables for local configuration; .env.example for reference
├── README.md                # Main project documentation
├── src/
│   ├── services/            # Service modules
│   ├── core/                # Reference template showing how to structure a real LangGraph project using `frank` utilities
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
- Treat `src/core` as a reference implementation of the project's pattern and `research` as exploratory support material.
