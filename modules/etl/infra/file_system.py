from pathlib import Path
import shutil
import json

from domain.exceptions import InfrastructureException


class FileSystem:
    @staticmethod
    def create_path(base_path: str, filename: str) -> str:
        try:
            output_path = Path(base_path) / filename
            return str(output_path)
        except Exception as e:
            raise InfrastructureException(
                f"Erro ao criar caminho: {e}"
            ) from e

    @staticmethod
    def delete_folder_if_exists(folder_path: str) -> None:
        try:
            path = Path(folder_path)
            if path.exists() and path.is_dir():
                shutil.rmtree(path)
        except (OSError, PermissionError) as e:
            raise InfrastructureException(
                f"Erro ao deletar pasta: {e}"
            ) from e

    @staticmethod
    def save_json(data: dict, path: str) -> None:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except (OSError, IOError, PermissionError) as e:
            raise InfrastructureException(
                f"Erro ao salvar arquivo JSON: {e}"
            ) from e
        except (TypeError, ValueError) as e:
            raise InfrastructureException(
                f"Erro ao serializar dados JSON: {e}"
            ) from e

    @staticmethod
    def get_parent_directory(path: str) -> str:
        return str(Path(path).parent)

    @staticmethod
    def get_stem(path: str) -> str:
        return Path(path).stem

    @staticmethod
    def create_json_path_from_file(input_file: str) -> str:
        base_path = FileSystem.get_parent_directory(input_file)
        json_filename = FileSystem.get_stem(input_file) + ".json"
        return FileSystem.create_path(base_path, json_filename)
