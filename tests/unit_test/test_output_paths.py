import logging
from pathlib import Path

import core_examples.utils.common as common_module
import core_examples.utils.logger as logger_module
import core_examples.utils.rag.local_chroma as local_chroma_module


def test_resolve_configured_path_uses_base_dir_for_relative_paths(tmp_path: Path) -> None:
    base_dir = tmp_path / "workspace"
    base_dir.mkdir()

    assert common_module.resolve_configured_path("logs", base_dir) == base_dir / "logs"


def test_resolve_configured_path_preserves_absolute_paths(tmp_path: Path) -> None:
    base_dir = tmp_path / "workspace"
    base_dir.mkdir()
    absolute_path = tmp_path / "shared" / "logs"

    assert common_module.resolve_configured_path(absolute_path, base_dir) == absolute_path


def test_save_text_to_artifact_uses_default_directory_without_constants_or_cwd(tmp_path: Path, monkeypatch) -> None:
    project_root = tmp_path / "template-root"
    other_dir = tmp_path / "elsewhere"
    project_root.mkdir()
    other_dir.mkdir()
    monkeypatch.chdir(other_dir)
    monkeypatch.setattr(common_module, "get_project_root_path", lambda: project_root)
    monkeypatch.setattr(common_module, "get_default_artifacts_directory", lambda: project_root / "artifacts")

    artifact_path = common_module.save_text_to_artifact("hello")

    assert artifact_path == project_root / "artifacts" / "artifact_template-root.txt"
    assert artifact_path.read_text(encoding="utf-8") == "hello"


def test_setup_logging_uses_default_directory_without_constants_or_cwd(tmp_path: Path, monkeypatch) -> None:
    project_root = tmp_path / "template-root"
    other_dir = tmp_path / "elsewhere"
    project_root.mkdir()
    other_dir.mkdir()
    monkeypatch.chdir(other_dir)
    monkeypatch.setattr(logger_module, "get_project_root_path", lambda: project_root)
    monkeypatch.setattr(logger_module, "get_default_logs_directory", lambda: project_root / "logs")

    config = {
        "logging": {
            "format": "%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_file": "graph.log",
        },
    }

    log_path = logger_module.setup_logging(config)
    logging.getLogger("frank-tests").info("configured log path")
    logging.shutdown()

    assert log_path == project_root / "logs" / "graph.log"
    assert log_path.exists()
    assert "configured log path" in log_path.read_text(encoding="utf-8")


def test_default_output_directories_fall_back_when_constants_are_missing(monkeypatch) -> None:
    monkeypatch.setattr(common_module, "_get_core_constants_module", lambda: None)

    project_root = common_module.get_project_root_path()

    assert common_module.get_default_logs_directory() == project_root / "logs"
    assert common_module.get_default_artifacts_directory() == project_root / "artifacts"


def test_local_chroma_uses_default_directories_without_constants_or_cwd(tmp_path: Path, monkeypatch) -> None:
    project_root = tmp_path / "template-root"
    other_dir = tmp_path / "elsewhere"
    project_root.mkdir()
    other_dir.mkdir()
    monkeypatch.chdir(other_dir)
    monkeypatch.setattr(local_chroma_module, "get_project_root_path", lambda: project_root)
    monkeypatch.setattr(
        local_chroma_module,
        "get_default_artifacts_directory",
        lambda: project_root / "artifacts",
    )

    assert local_chroma_module.get_default_local_chroma_directory() == project_root / "artifacts" / ".chromadb"
    assert local_chroma_module.get_default_local_docstore_directory() == project_root / "artifacts" / ".docstore"
    assert local_chroma_module.get_default_local_rag_docs_directory() == project_root / "artifacts" / "rag_docs"
    assert local_chroma_module._resolve_local_storage_path(None, local_chroma_module.get_default_local_chroma_directory) == (
        project_root / "artifacts" / ".chromadb"
    )


def test_local_chroma_resolves_relative_paths_against_project_root(tmp_path: Path, monkeypatch) -> None:
    project_root = tmp_path / "template-root"
    project_root.mkdir()
    monkeypatch.setattr(local_chroma_module, "get_project_root_path", lambda: project_root)

    resolved = local_chroma_module._resolve_local_storage_path(
        Path("custom/chroma"),
        local_chroma_module.get_default_local_chroma_directory,
    )

    assert resolved == project_root / "custom" / "chroma"