from application.download import DownloadMeteogram
from application.transform import MeteogramTransformer
from application.analyzer.main import MainAnalyzer
from domain.exceptions import (
    RetryableException,
    NonRetryableException,
)
from infra.file_system import FileSystem
from infra.celery.config import app
from infra.logger import get_logger
from infra.timer import Timer
from settings import settings

logger = get_logger("etl.main")

_pipeline_timer: Timer | None = None


def on_retry_handler(sender, task_id, args, kwargs, einfo, **kw):
    retry_count = kw.get("retry_count", 0)
    max_retries = kw.get("max_retries", settings.CELERY_MAX_RETRIES)

    logger.warning(
        "Task retry triggered",
        task_id=task_id,
        task_name=sender.name,
        retry_count=retry_count,
        max_retries=max_retries,
        error=str(einfo) if einfo else None,
        args=str(args) if args else None,
        kwargs=str(kwargs) if kwargs else None,
    )


@app.task(
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def analyze(input_file: str):
    global _pipeline_timer

    with Timer() as timer:
        logger.info("Starting analyze task", task="analyze")

        try:
            analyzer = MainAnalyzer(input_file, logger)
            results = analyzer.analyze_all()
            output_path = "tmp/meteograms/alerts_results.json"
            FileSystem.save_json(results, output_path)

            logger.info(
                "Analyze task completed",
                task="analyze",
                input_file=input_file,
                output_file=output_path,
                polygons_with_alerts=len(results),
                duration_seconds=timer.elapsed_seconds,
            )

            logger.info(
                "Full pipeline duration",
                duration_seconds=_pipeline_timer.elapsed_seconds,
            )

            return {"results": results, "saved_to": output_path}
        except NonRetryableException as e:
            logger.exception(
                "Non-retryable error analyzing file",
                task="analyze",
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except RetryableException as e:
            logger.exception(
                "Retryable error analyzing file",
                task="analyze",
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except Exception as e:
            logger.critical(
                "Unexpected error in analyze task - should be handled by application layer",
                task="analyze",
                error=str(e),
                error_type=type(e).__name__,
                duration_seconds=timer.elapsed_seconds,
            )
            raise NonRetryableException(f"Unexpected error: {e}") from e


@app.task(
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def transform(input: str, output: str):
    global _pipeline_timer

    with Timer() as timer:
        logger.info("Starting transform task", task="transform", input=input)

        try:
            transformer = MeteogramTransformer(input, logger)
            output_path = transformer.perform(output_json_path=output)

            logger.info(
                "Transform task completed",
                task="transform",
                input=input,
                output=output_path,
                duration_seconds=timer.elapsed_seconds,
            )

            analyze.delay(output)

            return {"path": str(output_path)}
        except NonRetryableException as e:
            logger.exception(
                "Non-retryable error transforming file",
                task="transform",
                input=input,
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except RetryableException as e:
            logger.exception(
                "Retryable error transforming file",
                task="transform",
                input=input,
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except Exception as e:
            logger.critical(
                "Unexpected error in transform task - should be handled by application layer",
                task="transform",
                input=input,
                error=str(e),
                error_type=type(e).__name__,
                duration_seconds=timer.elapsed_seconds,
            )
            raise NonRetryableException(f"Unexpected error: {e}") from e


@app.task(
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def download_file():
    global _pipeline_timer

    _pipeline_timer = Timer()
    _pipeline_timer.__enter__()

    with Timer() as timer:
        logger.info("Starting download file task", task="download")

        try:
            download_service = DownloadMeteogram(logger)
            output_path = download_service.process()

            logger.info(
                "Download file task completed",
                task="download",
                output_path=output_path,
                duration_seconds=timer.elapsed_seconds,
            )

            json_path = FileSystem.create_json_path_from_file(output_path)

            transform.delay(str(output_path), json_path)

            return {"path": str(output_path)}
        except NonRetryableException as e:
            logger.exception(
                "Non-retryable error downloading file",
                task="download",
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except RetryableException as e:
            logger.exception(
                "Retryable error downloading file",
                task="download",
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except Exception as e:
            logger.critical(
                "Unexpected error in download_file task - should be handled by application layer",
                task="download",
                error=str(e),
                error_type=type(e).__name__,
                duration_seconds=timer.elapsed_seconds,
            )
            raise NonRetryableException(f"Unexpected error: {e}") from e


if __name__ == "__main__":
    app.start()
