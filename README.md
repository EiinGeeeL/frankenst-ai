# 🧟 Frankenst-AI | LangGraph Patterns
**Frankenst-AI** is a project that introduces a **modular and scalable architecture** based on design patterns and coding best practices, applied to **LangGraph**.

This project aims to improve **scalability**, **reusability**, **testability**, and **maintainability** through an architectural approach built on reusable, configurable, and highly decoupled components, designed to build complex workflows for LLMs.

By leveraging a well-organized and highly scalable structure, the project enables the creation of composable, configurable, and extensible AI systems (Agent patterns, RAG patterns, MCPs, etc.).

The project has been designed with the following goals:

- **Isolated logic and separation of concerns** between conditional edges, nodes, tools, and runnables, encapsulated as reusable and independent components.

- Key components like **StateEnhancer**, **StateCommander**, and **StateEvaluator** are designed for be used across multiple workflows.

- Use of YAML, **centralized configurations** based on dataclasses, and managed with builders and managers to define, **modify**, and **scale** different graph architectures **without duplicating logic**.

## Prerequisites

- Python 3.12.5
- Ollama 4.0 or higher (free); or an Azure AI Foundry Deployment (payment)
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
   
   ```ollama run llama3.1```
  
   #### 1.2 Using Azure AI Foundry Deployment
    Config all your model variables in your ```.env```

    ```cp .env.example .env```
2. Compile Graph Layouts with Workflow Builder
    
    For additional information, please refer to ```research/demo...ipynb``` notebooks.

## Repository Structure

```bash
frankenst-ai/
├── main.py                  # Entry point to run the project
├── app.py                   # Main application assembly script
├── requirements.txt         # Python dependencies for the project
├── .env                     # Environment variables for local configuration; .env.example for reference
├── README.md                # Main project documentation
├── src/
│   ├── services/            # Service modules
│   ├── core/                # Custom LangGraph implementation for illustration purposes
│   │   ├── components/
│   │   │   ├── nodes/
│   │   │   │   ├── enhancers/        # StateEnhancers for simple node logic modifying StateGraph via runnables
│   │   │   │   └── commands/         # StateCommander for routing and modifying state through LangGraph commands
│   │   │   ├── edges/
│   │   │   │   └── evaluators/       # StateEvaluator for conditional edge logic
│   │   │   ├── tools/                # Tool definitions and integrations
│   │   │   └── runnables/            # Executable LangChain RunnableBuilder modules
│   │   ├── config/
│   │   │   ├── config.yaml           # Main configuration file for the project
│   │   │   ├── config_nodes.py       # Contains all the graph nodes definition of your project
│   │   │   └── layouts/              # Contains ConfigGraph dataclass examples
│   │   ├── constants/           
│   │   ├── models/                   # Structural models: StateGraph, tool properties, structured outputs, etc.
│   │   └── utils/                  
│   └── frank/               # Frank utilities for assembling, refactoring, and compiling LangGraph
│       ├── entity/
│       │   ├── graph_layout.py       # Initializes the GraphLayout using a ConfigGraph dataclass
│       │   ├── runnable_builder.py   # Builder class for LangChain Runnable objects
│       │   ├── statehandler.py       # Core entities for handling StateGraph
│       │   ├── node.py               # Core node-related entities 
│       │   └── edge.py               # Core edge-related entities
│       ├── managers/               
│       └── workflow_builder.py       # Workflow Builder to compile the LangGraph using a ConfigGraph dataclass
├── research/                # Research, demos and experimental resources
├── tests/
│   ├── integration_test/      
│   └── unit_test/              
├── artifacts/               # Generated artifacts, static files and outputs
└── logs/                    # Log files and runtime logs
