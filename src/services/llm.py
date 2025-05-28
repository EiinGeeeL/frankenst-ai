import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_core.runnables import Runnable
from frank.utils.common import read_yaml
from frank.constants import *

class LLMServices:
    config = read_yaml(CONFIG_FILE_PATH)

    model: Runnable = None
    embeddings: Runnable = None
    turbo_model: Runnable = None

    @classmethod
    def _load_ollama(cls):
        return ChatOllama(
            model=cls.config['ollama']['model'],
            temperature=cls.config['ollama']['temperature'],
        )

    @classmethod
    def _load_azureopenai(cls):
        return AzureChatOpenAI(
            temperature=cls.config['azureopenai']['temperature'],
        )

    @classmethod
    def _load_azureai(cls):
        try:
            return AzureAIChatCompletionsModel(
                endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
                credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
                model_name=os.environ["AZURE_INFERENCE_MODEL_NAME"],
                api_version=os.environ["AZURE_INFERENCE_API_VERSION"],
            )
        except KeyError as e:
            raise RuntimeError(f"Missing required environment variable for AzureAI: {e}")

    @classmethod
    def _load_model(cls, model_name: str):
        loaders = {
            'ollama': cls._load_ollama,
            'azureopenai': cls._load_azureopenai,
            'azureai': cls._load_azureai,
        }
        if model_name not in loaders:
            raise ValueError(f"Unsupported model: {model_name}")
        return loaders[model_name]()

    @classmethod
    def _load_embeddings(cls, embedding_name: str):
        if embedding_name == 'ollama':
            return OllamaEmbeddings(model=cls.config['ollama']['embeddings'])
        return None

    @classmethod
    def launch(cls):
        cls.config = read_yaml(CONFIG_FILE_PATH)

        # Initialize only the model specified in config
        model_name = cls.config['launch']['model']
        embedding_name = cls.config['launch'].get('embeddings')
        turbo_model_name = cls.config['launch'].get('turbo_model')

        cls.model = cls._load_model(model_name)
        cls.embeddings = cls._load_embeddings(embedding_name)
        cls.turbo_model = None
