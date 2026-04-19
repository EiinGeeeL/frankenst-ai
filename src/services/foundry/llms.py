from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from azure.identity import DefaultAzureCredential
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_azure_ai.chat_models import AzureAIOpenAIApiChatModel
from langchain_azure_ai.embeddings import AzureAIOpenAIApiEmbeddingsModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from core_examples.constants import CONFIG_FILE_PATH
from core_examples.utils.config_loader import read_yaml
from core_examples.utils.key_vault import get_secret
from core_examples.utils.ollama.ollama_wsl_proxy import resolve_ollama_base_url


@dataclass(frozen=True)
class LLMRuntime:
	"""Resolved runtime objects exposed to the rest of the application."""

	model: BaseChatModel
	embeddings: Embeddings
	turbo_model: BaseChatModel | None = None


class LLMServices:
	"""Centralized runtime builder for chat models and embeddings providers.

	The class keeps a small provider registry with direct callables while
	preserving provider-specific preparation logic in dedicated helpers.
	Consumers should continue to call `launch()` and then read
	`LLMServices.model` and `LLMServices.embeddings`.
	"""

	model: BaseChatModel | None = None
	embeddings: Embeddings | None = None
	turbo_model: BaseChatModel | None = None

	@classmethod
	def _model_providers(cls) -> dict[str, Callable[[dict[str, Any]], BaseChatModel]]:
		"""Return the provider registry used by the model dispatcher."""

		return {
			"ollama": cls._load_ollama_model,
			"azureai": cls._load_azureai_model,
		}

	@classmethod
	def _embeddings_providers(cls) -> dict[str, Callable[[dict[str, Any]], Embeddings]]:
		"""Return the provider registry used by the embeddings dispatcher."""

		return {
			"ollama": cls._load_ollama_embeddings,
			"azureai": cls._load_azureai_embeddings,
		}

	@classmethod
	def _load_config(cls, config: dict[str, Any] | None = None) -> dict[str, Any]:
		"""Load the central config and validate the launch selector section."""

		resolved_config = config if config is not None else read_yaml(CONFIG_FILE_PATH)
		launch_config = resolved_config.get("launch")
		if not isinstance(launch_config, dict):
			raise RuntimeError("Missing config section for: launch")

		for key in ("model", "embeddings"):
			if key not in launch_config:
				raise RuntimeError(f"Missing config entry for: launch.{key}")

		return resolved_config

	@classmethod
	def _require(cls, config: dict[str, Any], path: str, *, as_section: bool = False) -> Any:
		"""Read a dotted config path and optionally require that it resolves to a section.

		When `as_section` is true, missing keys and non-mapping results are both
		reported as missing config sections for the requested path.
		"""

		value: Any = config
		for key in path.split("."):
			if not isinstance(value, dict) or key not in value:
				message_kind = "section" if as_section else "entry"
				raise RuntimeError(f"Missing config {message_kind} for: {path}")
			value = value[key]

		if as_section and not isinstance(value, dict):
			raise RuntimeError(f"Missing config section for: {path}")

		return value

	@classmethod
	def _resolve_config_value(cls, value: Any) -> Any:
		"""Resolve config literals and `{secret: ...}` references recursively."""

		if isinstance(value, dict):
			if set(value) == {"secret"}:
				secret_name = value["secret"]
				if not isinstance(secret_name, str) or not secret_name:
					raise RuntimeError("Config secret references must be non-empty strings.")
				return get_secret(secret_name)

			return {key: cls._resolve_config_value(item) for key, item in value.items()}

		if isinstance(value, list):
			return [cls._resolve_config_value(item) for item in value]

		return value

	@classmethod
	def _resolve_runtime_kwargs(cls, runtime_config: dict[str, Any]) -> dict[str, Any]:
		"""Resolve a runtime subsection into constructor kwargs."""

		resolved = cls._resolve_config_value(runtime_config)
		if not isinstance(resolved, dict):
			raise RuntimeError("Runtime configuration must resolve to a mapping.")
		return {key: value for key, value in resolved.items() if value is not None}

	@classmethod
	def _prepare_ollama_kwargs(cls, runtime_config: dict[str, Any], config_path: str) -> dict[str, Any]:
		"""Prepare Ollama kwargs and inject the resolved base URL when missing."""

		kwargs = cls._resolve_runtime_kwargs(runtime_config)
		host = kwargs.pop("host", None)
		if "base_url" not in kwargs:
			kwargs["base_url"] = resolve_ollama_base_url(config_host=host)

		if not kwargs.get("model"):
			raise RuntimeError(f"Missing config entry for: {config_path}.model")

		return kwargs

	@classmethod
	def _prepare_azureai_kwargs(cls, runtime_config: dict[str, Any], config_path: str) -> dict[str, Any]:
		"""Resolve and apply the AzureAI config validation owned by this project.

		This method intentionally validates only the local config contract and
		leaves deeper client validation to `langchain_azure_ai`.
		"""

		kwargs = cls._resolve_runtime_kwargs(runtime_config)
		if kwargs.get("endpoint") and kwargs.get("project_endpoint"):
			raise RuntimeError(f"Config section {config_path} cannot define both endpoint and project_endpoint.")

		if not kwargs.get("endpoint") and not kwargs.get("project_endpoint"):
			raise RuntimeError(f"Missing config entry for: {config_path}.endpoint or {config_path}.project_endpoint")

		if not kwargs.get("model"):
			raise RuntimeError(f"Missing config entry for: {config_path}.model")

		if kwargs.get("project_endpoint") is None and not kwargs.get("api_version"):
			raise RuntimeError(f"Missing config entry for: {config_path}.api_version")

		if not kwargs.get("credential"):
			kwargs["credential"] = DefaultAzureCredential()

		return kwargs

	@classmethod
	def _load_ollama_model(cls, config: dict[str, Any]) -> BaseChatModel:
		runtime_config = cls._require(config, "ollama.model", as_section=True)
		kwargs = cls._prepare_ollama_kwargs(runtime_config, "ollama.model")
		return ChatOllama(**kwargs)

	@classmethod
	def _load_ollama_embeddings(cls, config: dict[str, Any]) -> Embeddings:
		runtime_config = cls._require(config, "ollama.embeddings", as_section=True)
		kwargs = cls._prepare_ollama_kwargs(runtime_config, "ollama.embeddings")
		return OllamaEmbeddings(**kwargs)

	@classmethod
	def _load_azureai_model(cls, config: dict[str, Any]) -> BaseChatModel:
		runtime_config = cls._require(config, "azureai.model", as_section=True)
		kwargs = cls._prepare_azureai_kwargs(runtime_config, "azureai.model")
		return AzureAIOpenAIApiChatModel(**kwargs)

	@classmethod
	def _load_azureai_embeddings(cls, config: dict[str, Any]) -> Embeddings:
		runtime_config = cls._require(config, "azureai.embeddings", as_section=True)
		kwargs = cls._prepare_azureai_kwargs(runtime_config, "azureai.embeddings")
		return AzureAIOpenAIApiEmbeddingsModel(**kwargs)

	@classmethod
	def _load_model(cls, config: dict[str, Any], provider_name: str) -> BaseChatModel:
		loader = cls._model_providers().get(provider_name)
		if loader is None:
			raise ValueError(f"Unsupported provider type: {provider_name}")
		return loader(config)

	@classmethod
	def _load_embeddings(cls, config: dict[str, Any], provider_name: str) -> Embeddings:
		loader = cls._embeddings_providers().get(provider_name)
		if loader is None:
			raise ValueError(f"Unsupported provider type: {provider_name}")
		return loader(config)

	@classmethod
	def build_runtime(cls, config: dict[str, Any] | None = None) -> LLMRuntime:
		"""Build a fresh runtime from config without mutating class attributes."""

		resolved_config = cls._load_config(config)
		model_provider = cls._require(resolved_config, "launch.model")
		embeddings_provider = cls._require(resolved_config, "launch.embeddings")
		model = cls._load_model(resolved_config, model_provider)
		embeddings = cls._load_embeddings(resolved_config, embeddings_provider)
		return LLMRuntime(model=model, embeddings=embeddings, turbo_model=None)

	@classmethod
	def launch(cls, config: dict[str, Any] | None = None) -> LLMRuntime:
		"""Build the runtime and publish it through the class-level shared state."""

		runtime = cls.build_runtime(config)
		cls.model = runtime.model
		cls.embeddings = runtime.embeddings
		cls.turbo_model = runtime.turbo_model
		return runtime
