# Frankenst-AI
TODO: ad description

The Graph has the following architecture captured by each run:

![alt text](/artifacts/cheese_graph.png)

## Prerequisites

- Python 3.12.5
- Ollama 4.0 or higher (free); or an Azure OpenAI Deployment (payment)
- pip (Python package manager)

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

    ```python3 -m pip install -e .```


## Running the Project

To run the project:

1. Set LLM Services

   Choose one of the following options:

   #### 1.1 Using a local model with Ollama
   Start the Ollama service by running 
   
   ```ollama run llama3.1```
  
   #### 1.2 Using AzureChatOpenAI Deployment
    Config all your model variables in your ```.env```

    ```cp .env.example .env```

2. Run the LangGraph Platforms app 

    ```make run-app``` 

3. Compile the graph mannually

    You can check ```./runnable.ipynb``` for more information.

## Repository Structure

```bash
cheese-chatter/
├── main.py                # Main file to run the project
├── app.py                 # Main file to assemble the app
├── runnable.ipynb         # Notebook for debugging and interacting with the project
├── requirements.txt       # Project dependency list
├── .env                   # Environment variables for configuration
├── README.md              # Project documentation
├── src/
│   └── cheese/
│       ├── components/
│       │   ├── nodes/
│       │   ├── edges/
│       │   │   ├── evaluators/      # Contains StateEvaluator for conditional edges
│       │   │   └── conditionals/    # Contains ConditionalEdge
│       │   ├── tools/               # Contains BaseTool
│       │   └── runnables/           # Contains executable invoke files
│       ├── utils/
│       │   ├── common.py
│       │   ├── logger.py
│       │   └── type_vars.py
│       ├── config/                 
│       │   ├── config_graph.py      # Contains the definition of graph nodes and edges
│       │   ├── subgraphs/           # Contain subgraphs to be implemented as nodes
│       │   └── runnables/           # Contains prompts and LLM configuration
│       ├── managers/      # Contains manager classes
│       ├── services/      # Contains services
│       ├── entity/
│       │   ├── models/              # Contains structural models
│       │   ├── graph_layout.py      # Initialize the Graph Layout with a Config Graph dataclass
│       │   ├── runnable_builder.py  # Builder for LangChain Runnable
│       │   ├── statehandler.py      # Contains main entities for GraphState handlers
│       │   ├── node.py              # Contains main entities related to nodes
│       │   └── edge.py              # Contains main entities related to edges
│       └── constants/
│           └── __init__.py          # Contains project constants
├── config/
│   └── config.yaml        # Main configuration files
├── research/              # Directory for experimentation scripts and notebooks
├── tests/                 # Directory for testing modules
│   ├── integration_test/
│   └── unit_test/
├── artifacts/             # Directory for artifacts
│   ├── cheese_graph.png   # Image of the application's main architecture
│   └── models/            # Directory for models generated in research
└── logs/                  # Directory for project logs
```