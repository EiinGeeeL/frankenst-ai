from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import AzureChatOpenAI
import os
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel

model = AzureAIChatCompletionsModel(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
    model_name=os.environ["AZURE_INFERENCE_MODEL_NAME"],
    api_version=os.environ["AZURE_INFERENCE_API_VERSION"]
)
from langchain_core.runnables import Runnable
from frank.utils.common import read_yaml
from frank.constants import *

class LLMServices:
    config = read_yaml(CONFIG_FILE_PATH)
    
    ## Models available
    models_dict = {
        'ollama': ChatOllama(
            model=config['ollama']['model'],
            temperature=config['ollama']['temperature'],
            # Add other parameters from config as needed
        ),
        'azureopenai': AzureChatOpenAI( # Configured from .env
            temperature=config['azureopenai']['temperature'],
        ),
        'azureai': AzureAIChatCompletionsModel(
            endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
            credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
            model_name=os.environ["AZURE_INFERENCE_MODEL_NAME"],
            api_version=os.environ["AZURE_INFERENCE_API_VERSION"],
        ),
    }

    ## Embeddings available
    embeddings_dict = None

    ## Turbo model available
    turbo_models_dict = None

    ## Attributes
    model: Runnable = models_dict[config['launch']['model']]
    embeddings: Runnable = None # embeddings_dict[config['launch']['embeddings']]
    turbo_model: Runnable = None # embeddings_dict[config['launch']['turbo_model']]

    @classmethod
    def reinitialize(cls):
        cls.config = read_yaml(CONFIG_FILE_PATH)
        
        # Reinitialize models_dict
        cls.models_dict = {
            'ollama': ChatOllama(
                model=cls.config['ollama']['model'],
                temperature=cls.config['ollama']['temperature'],
                # Add other parameters from config as needed
            ),
            'azureopenai': AzureChatOpenAI( # Configured from .env
                temperature=cls.config['azureopenai']['temperature'],
            ),
        }
        
        # Reinitialize embeddings_dict
        cls.embeddings_dict = {
            'ollama': OllamaEmbeddings(
                model=cls.config['ollama']['embeddings'],
            ),
        }
        
        # Reinitialize turbo_models_dict
        
        # Update model, embeddings, and turbo_model
        cls.model = cls.models_dict[cls.config['launch']['model']]
        cls.embeddings = cls.embeddings_dict[cls.config['launch']['embeddings']]
        cls.turbo_model = cls.turbo_models_dict.get(cls.config['launch']['turbo_model'])
