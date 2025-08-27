from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.vectorstores import VectorStore
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_azure_ai.embeddings import AzureAIEmbeddingsModel
from langchain_core.language_models import BaseLanguageModel
from langchain_core.embeddings import Embeddings
from core.utils.common import read_yaml
from core.utils.key_vault import get_secret
from core.constants import *

class LLMServices:
    config = read_yaml(CONFIG_FILE_PATH)
    model: BaseLanguageModel = None
    embeddings: Embeddings = None
    turbo_model: BaseLanguageModel = None
    vectorstore: VectorStore = None 

    @classmethod
    def _get_config(cls, provider: str, key: str = None):
        try:
            if key:
                return cls.config[provider][key]
            return cls.config[provider]
        except KeyError:
            raise RuntimeError(f"Missing config entry for: {provider}.{key if key else ''}")

    @classmethod
    def _get_secrets(cls, **kwargs):
        missing = []
        values = {}
        for alias, secret_name in kwargs.items():
            try:
                value = get_secret(secret_name)
                values[alias] = value
            except Exception:
                missing.append(secret_name)
        if missing:
            raise RuntimeError(f"Missing required secrets: {', '.join(missing)}")
        return values

    @classmethod
    def _load_ollama_model(cls):
        vars = {
            "model": cls._get_config('ollama', 'model'),
            "temperature": cls._get_config('ollama', 'temperature'),
        }
        return ChatOllama(**vars)

    @classmethod
    def _load_azureai_model(cls):
        vars = cls._get_secrets(
            endpoint="AZURE_INFERENCE_ENDPOINT",
            credential="AZURE_INFERENCE_CREDENTIAL",
            model_name="AZURE_INFERENCE_MODEL_NAME",
            api_version="AZURE_INFERENCE_API_VERSION",
        )
        vars["temperature"] = 0
        return AzureAIChatCompletionsModel(**vars)

    @classmethod
    def _load_model(cls, model_name: str):
        model_loaders = {
            'ollama': cls._load_ollama_model,
            'azureai': cls._load_azureai_model,
        }
        try:
            return model_loaders[model_name]()
        except KeyError:
            raise ValueError(f"Unsupported model type: {model_name}")

    @classmethod
    def _load_ollama_embeddings(cls):
        vars = {
            "model": cls._get_config('ollama', 'embeddings'),
            "temperature": 0,
        }
        return OllamaEmbeddings(**vars)

    @classmethod
    def _load_azureai_embeddings(cls):
        vars = cls._get_secrets(
            endpoint="AZURE_EMBEDDINGS_ENDPOINT",
            credential="AZURE_EMBEDDINGS_CREDENTIAL",
            model_name="AZURE_EMBEDDINGS_MODEL_NAME",
            api_version="AZURE_EMBEDDINGS_API_VERSION",
        )
        vars["temperature"] = 0
        return AzureAIEmbeddingsModel(**vars)

    @classmethod
    def _load_embeddings(cls, embedding_name: str):
        embedding_loaders = {
            'ollama': cls._load_ollama_embeddings,
            'azureai': cls._load_azureai_embeddings,
        }
        try:
            return embedding_loaders[embedding_name]()
        except KeyError:
            raise ValueError(f"Unsupported embedding type: {embedding_name}")

    @classmethod
    def launch(cls):
        cls.model = cls._load_model(cls._get_config('launch', 'model'))
        cls.embeddings = cls._load_embeddings(cls._get_config('launch', 'embeddings'))
        cls.turbo_model = None
        cls.vectorstore = None
