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

## Running the Project

To run the project:

1. Set LLM Services

   Choose one of the following options:

   #### 1.1 Using a local model with Ollama
   Start the Ollama service by running 
   
   ```ollama run llama3.1```
  
   #### 1.2 Using Azure AI Foundry Deployment
    Config all your model variables in your ```.env```

    ```cp .env.example .env```
2. Compile Graphs Layouts with Workflow Builder

    You can check ```research/demo...ipynb``` for more information.

## Repository Structure

```bash
frank/
├── main.py                # Main file to run the project
├── app.py                 # Main file to assemble the app
├── requirements.txt       # Project dependency list
├── .env                   # Environment variables for configuration
├── README.md              # Project documentation
├── src/
│   ├── services/          # Contains services
│   └── frank/
│       ├── components/
│       │   ├── nodes/
│       │   │   ├── enhancers/       # Contains StateEnhancers for simple nodes to modifications with runnables
│       │   │   └── commands/        # Contains StateCommander for simple nodes. Commands for LangGraph method can route and modificate the state.
│       │   ├── edges/
│       │   │   └── evaluators/      # Contains StateEvaluator for conditional edges
│       │   ├── tools/               
│       │   └── runnables/           # Contains executable invoke files of RunnableBuilders
│       ├── config/    
│       │   ├── config.yaml          # Main configuration files for project
│       │   ├── config_nodes.py      # Contains the definition of graph nodes of your project
│       │   └── layouts/             # Contains all Config Graph dataclass of your project
│       ├── models/                  # Contains structural models like, stategraphs, base tools properties, structured output...
│       ├── entity/
│       │   ├── graph_layout.py      # Initialize the Graph Layout with a Config Graph dataclass
│       │   ├── runnable_builder.py  # Builder for LangChain Runnable
│       │   ├── statehandler.py      # Contains main entities for GraphState handlers
│       │   ├── node.py              # Contains main entities related to nodes
│       │   └── edge.py              # Contains main entities related to edges
│       ├── managers/                
│       ├── utils/
│       └── constants/
│           └── __init__.py          # Contains project constants
├── research/              
├── tests/                 
│   ├── integration_test/
│   └── unit_test/
├── artifacts/             
└── logs/                  
```