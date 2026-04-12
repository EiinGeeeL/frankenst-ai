from dataclasses import dataclass

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_azure_ai.embeddings import AzureAIOpenAIApiEmbeddingsModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from core_examples.constants import CONFIG_FILE_PATH
from core_examples.utils.common import read_yaml
from core_examples.utils.key_vault import get_secret
from core_examples.utils.ollama.ollama_wsl_proxy import resolve_ollama_base_url


@dataclass(frozen=True)
class LLMRuntime:
	model: BaseChatModel
	embeddings: Embeddings
	turbo_model: BaseChatModel | None = None


class LLMServices:
	model: BaseChatModel | None = None
	embeddings: Embeddings | None = None
	turbo_model: BaseChatModel | None = None

	@classmethod
	def _load_config(cls, config: dict | None = None) -> dict:
		return config if config is not None else read_yaml(CONFIG_FILE_PATH)

	@classmethod
	def _get_config(cls, config: dict, provider: str, key: str | None = None):
		try:
			if key:
				return config[provider][key]
			return config[provider]
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
	def _load_ollama_model(cls, config: dict):
		ollama_config = cls._get_config(config, "ollama")
		vars = {
			"model": ollama_config["model"],
			"temperature": ollama_config["temperature"],
			"base_url": resolve_ollama_base_url(config_host=ollama_config.get("host")),
		}
		return ChatOllama(**vars)

	@classmethod
	def _load_azureai_model(cls, config: dict):
		vars = cls._get_secrets(
			endpoint="AZURE_INFERENCE_ENDPOINT",
			credential="AZURE_INFERENCE_CREDENTIAL",
			model_name="AZURE_INFERENCE_MODEL_NAME",
			api_version="AZURE_INFERENCE_API_VERSION",
		)
		vars["temperature"] = 0
		return AzureAIChatCompletionsModel(**vars)

	@classmethod
	def _load_model(cls, config: dict, model_name: str):
		model_loaders = {
			"ollama": cls._load_ollama_model,
			"azureai": cls._load_azureai_model,
		}
		try:
			return model_loaders[model_name](config)
		except KeyError:
			raise ValueError(f"Unsupported model type: {model_name}")

	@classmethod
	def _load_ollama_embeddings(cls, config: dict):
		ollama_config = cls._get_config(config, "ollama")
		model_name = ollama_config.get("embeddings_model") or ollama_config.get("embeddings")
		if not model_name:
			raise RuntimeError("Missing config entry for: ollama.embeddings_model")

		vars = {
			"model": model_name,
			"base_url": resolve_ollama_base_url(config_host=ollama_config.get("host")),
		}
		return OllamaEmbeddings(**vars)

	@classmethod
	def _load_azureai_embeddings(cls, config: dict):
		vars = cls._get_secrets(
			endpoint="AZURE_EMBEDDINGS_ENDPOINT",
			credential="AZURE_EMBEDDINGS_CREDENTIAL",
			model_name="AZURE_EMBEDDINGS_MODEL_NAME",
			api_version="AZURE_EMBEDDINGS_API_VERSION",
		)
		vars["temperature"] = 0
		return AzureAIOpenAIApiEmbeddingsModel(**vars)

	@classmethod
	def _load_embeddings(cls, config: dict, embedding_name: str):
		embedding_loaders = {
			"ollama": cls._load_ollama_embeddings,
			"azureai": cls._load_azureai_embeddings,
		}
		try:
			return embedding_loaders[embedding_name](config)
		except KeyError:
			raise ValueError(f"Unsupported embedding type: {embedding_name}")

	@classmethod
	def build_runtime(cls, config: dict | None = None) -> LLMRuntime:
		resolved_config = cls._load_config(config)
		model = cls._load_model(resolved_config, cls._get_config(resolved_config, "launch", "model"))
		embeddings = cls._load_embeddings(
			resolved_config,
			cls._get_config(resolved_config, "launch", "embeddings"),
		)
		return LLMRuntime(model=model, embeddings=embeddings, turbo_model=None)

	@classmethod
	def launch(cls, config: dict | None = None) -> LLMRuntime:
		runtime = cls.build_runtime(config)
		cls.model = runtime.model
		cls.embeddings = runtime.embeddings
		cls.turbo_model = runtime.turbo_model
		return runtime
