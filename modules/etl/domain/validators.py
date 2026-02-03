import os


class FileValidator:
    @staticmethod
    def validate_file_exists(file_path: str) -> None:
        if not file_path:
            raise ValueError("Caminho do arquivo não fornecido")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    @staticmethod
    def validate_file_size(file_path: str, min_size_bytes: int = 1) -> None:
        FileValidator.validate_file_exists(file_path)
        
        size = os.path.getsize(file_path)
        if size < min_size_bytes:
            raise ValueError(
                f"Arquivo muito pequeno: {size} bytes (mínimo: {min_size_bytes} bytes)"
            )

    @staticmethod
    def validate_downloaded_file(file_path: str, expected_min_size: int = 100) -> None:
        FileValidator.validate_file_exists(file_path)
        FileValidator.validate_file_size(file_path, min_size_bytes=expected_min_size)
