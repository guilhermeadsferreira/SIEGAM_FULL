from infra.httpx import download_file
from domain.value_objects import Date
from domain.exceptions import (
    InfrastructureException,
    RetryableException,
    NonRetryableException,
    NetworkException,
    FileValidationException,
)
from domain.validators import FileValidator
from infra.file_system import FileSystem
from infra.logger import JsonLogger
from settings import settings


class DownloadMeteogram:
    def __init__(self, logger: JsonLogger):
        self.__logger = logger
        self.__base_url = settings.METEOGRAM_BASE_URL
        self.__base_path = settings.METEOGRAM_BASE_PATH

    def __create_file_name(self) -> str:
        current_date = Date.get_current_date().replace("-", "")
        return f"HST{current_date}00-MeteogramASC.out"

    def __create_url(self, filename: str) -> str:
        return self.__base_url + filename

    def process(self) -> str:
        self.__logger.info("Starting download process", operation="download")

        try:
            filename = self.__create_file_name()
            self.__logger.debug("Filename created", filename=filename)
            url = self.__create_url(filename)
            self.__logger.debug("URL created", url=url)
            self.__logger.debug("Deleting folder if exists", path=self.__base_path)
            FileSystem.delete_folder_if_exists(self.__base_path)
            output_path = FileSystem.create_path(self.__base_path, filename)
            self.__logger.debug("Output path created", path=output_path)
            self.__logger.info("Downloading file", url=url, output=output_path)

            result_path = download_file(url, output_path)

            try:
                FileValidator.validate_downloaded_file(
                    str(result_path),
                    settings.MIN_FILE_SIZE_BYTES,
                )
            except (ValueError, FileNotFoundError) as e:
                raise FileValidationException(f"Arquivo baixado inválido: {e}") from e

            self.__logger.info(
                "Download completed",
                operation="download",
                file=filename,
                output_path=result_path,
            )
            return str(result_path)

        except NetworkException as e:
            self.__logger.exception(
                "Network error downloading file",
                operation="download",
                error=str(e),
            )
            raise RetryableException(f"Network error downloading file: {e}") from e
        except FileValidationException as e:
            self.__logger.exception(
                "File validation error",
                operation="download",
                error=str(e),
            )
            raise NonRetryableException(f"File validation error: {e}") from e
        except InfrastructureException as e:
            self.__logger.exception(
                "Infrastructure error downloading file",
                operation="download",
                error=str(e),
            )
            raise RetryableException(
                f"Infrastructure error downloading file: {e}"
            ) from e
        except (ValueError, FileNotFoundError) as e:
            self.__logger.exception(
                "Validation error",
                operation="download",
                error=str(e),
            )
            raise NonRetryableException(f"Validation error: {e}") from e
