from application.download import DownloadMeteogram
from application.load import LoadService
from application.transform import MeteogramTransformer
from application.analyzer.main import MainAnalyzer
from domain.exceptions import (
    RetryableException,
    NonRetryableException,
)
from infra.file_system import FileSystem
from infra.celery.config import app
from domain.constants import (
    REDIS_NOTIFICATIONS_QUEUE,
    STATUS_ERROR,
    STATUS_IN_PROGRESS,
    STATUS_STARTED,
    STATUS_SUCCESS,
    TASK_NAME_DISPATCH,
    TASK_NAME_ETL,
    TASK_NAME_LOAD,
)
from infra.database import insert_application_log
from infra.logger import get_logger
from infra.timer import Timer
from settings import settings

logger = get_logger("etl.main")


def _log_safe(
    execution_id,
    message: str,
    status: str | None = None,
    extra: dict | None = None,
    *,
    task: str = TASK_NAME_ETL,
) -> None:
    """Insere log no banco sem falhar a task em caso de erro (ex: Postgres indisponível)."""
    try:
        insert_application_log(
            task=task,
            execution_id=execution_id,
            message=message,
            status=status,
            extra=extra,
        )
    except Exception as e:
        logger.exception(
            "Falha ao inserir application_log - verifique Postgres e tabela application_logs",
            error=str(e),
            message=message,
        )

_pipeline_timer: Timer | None = None


def on_retry_handler(sender, task_id, args, kwargs, einfo, **kw):
    retry_count = kw.get("retry_count", 0)
    max_retries = kw.get("max_retries", settings.CELERY_MAX_RETRIES)
    execution_id = kwargs.get("execution_id") or task_id

    _log_safe(
        execution_id,
        f"Task retry {retry_count}/{max_retries}",
        STATUS_IN_PROGRESS,
        extra={
            "task": sender.name,
            "error": str(einfo) if einfo else None,
            "retry_count": retry_count,
            "max_retries": max_retries,
        },
    )

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
    bind=True,
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def analyze(self, input_file: str, execution_id=None):
    global _pipeline_timer

    execution_id = execution_id or self.request.id
    _log_safe(execution_id, "Análise Iniciada", STATUS_IN_PROGRESS)

    with Timer() as timer:
        logger.info("Starting analyze task", task="analyze")

        try:
            analyzer = MainAnalyzer(input_file, logger)
            results = analyzer.analyze_all()
            output_path = "tmp/meteograms/alerts_results.json"
            FileSystem.save_json(results, output_path)

            _log_safe(execution_id, "Análise Finalizada", STATUS_SUCCESS)

            logger.info(
                "Analyze task completed",
                task="analyze",
                input_file=input_file,
                output_file=output_path,
                polygons_with_alerts=len(results),
                duration_seconds=timer.elapsed_seconds,
            )

            load.delay({"results": results}, execution_id=execution_id)

            return {"results": results, "saved_to": output_path}
        except NonRetryableException as e:
            _log_safe(execution_id, "Erro na Análise", STATUS_ERROR, extra={"error": str(e)})
            logger.exception(
                "Non-retryable error analyzing file",
                task="analyze",
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except RetryableException as e:
            _log_safe(execution_id, "Erro na Análise", STATUS_ERROR, extra={"error": str(e)})
            logger.exception(
                "Retryable error analyzing file",
                task="analyze",
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except Exception as e:
            _log_safe(execution_id, "Erro na Análise", STATUS_ERROR, extra={"error": str(e)})
            logger.critical(
                "Unexpected error in analyze task - should be handled by application layer",
                task="analyze",
                error=str(e),
                error_type=type(e).__name__,
                duration_seconds=timer.elapsed_seconds,
            )
            raise NonRetryableException(f"Unexpected error: {e}") from e


@app.task(
    bind=True,
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def load(self, analyze_output: dict, execution_id=None):
    """
    Task 4: resolve polygon→cidade e alert_type→evento no banco ETL,
    monta os avisos e persiste.
    """
    execution_id = execution_id or self.request.id
    _log_safe(execution_id, "Load Iniciado", STATUS_IN_PROGRESS, task=TASK_NAME_LOAD)

    with Timer() as timer:
        logger.info("Starting load task", task="load")

        try:
            results = analyze_output.get("results", {})
            service = LoadService(logger)
            load_result = service.process(results)

            _log_safe(
                execution_id,
                "Load Finalizado",
                STATUS_SUCCESS,
                extra={
                    "avisos_inserted": load_result.avisos_inserted,
                    "unmatched_polygons": load_result.unmatched_polygons,
                    "unmatched_events": load_result.unmatched_events,
                },
                task=TASK_NAME_LOAD,
            )

            logger.info(
                "Load task completed",
                task="load",
                avisos_inserted=load_result.avisos_inserted,
                unmatched_polygons=load_result.unmatched_polygons,
                duration_seconds=timer.elapsed_seconds,
            )

            dispatch.delay(
                alerts=load_result.dispatch_alerts,
                avisos_count=load_result.avisos_inserted,
                execution_id=execution_id,
            )

            return {
                "avisos_inserted": load_result.avisos_inserted,
                "unmatched_polygons": load_result.unmatched_polygons,
            }

        except NonRetryableException as e:
            _log_safe(
                execution_id, "Erro no Load", STATUS_ERROR, extra={"error": str(e)}, task=TASK_NAME_LOAD
            )
            logger.exception("Non-retryable error in load task", error=str(e))
            raise
        except RetryableException as e:
            _log_safe(
                execution_id, "Erro no Load", STATUS_ERROR, extra={"error": str(e)}, task=TASK_NAME_LOAD
            )
            logger.exception("Retryable error in load task", error=str(e))
            raise
        except Exception as e:
            _log_safe(
                execution_id, "Erro no Load", STATUS_ERROR, extra={"error": str(e)}, task=TASK_NAME_LOAD
            )
            raise NonRetryableException(f"Unexpected error in load: {e}") from e


@app.task(
    bind=True,
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def dispatch(self, alerts: dict, avisos_count: int, execution_id=None):
    """
    Task 5: publica evento no Redis para o módulo de notificações.
    O payload contém apenas dados meteorológicos (sem UUIDs do modulo_usuarios).
    """
    import json

    from redis import Redis

    from domain.value_objects import Date

    execution_id = execution_id or self.request.id
    _log_safe(execution_id, "Dispatch Iniciado", STATUS_IN_PROGRESS, task=TASK_NAME_DISPATCH)

    with Timer() as timer:
        logger.info("Starting dispatch task", task="dispatch")

        try:
            payload = {
                "execution_id": str(execution_id),
                "date": Date.get_current_date(),
                "avisos_count": avisos_count,
                "alerts": alerts,
            }

            redis_client = Redis.from_url(settings.REDIS_URL)
            redis_client.rpush(REDIS_NOTIFICATIONS_QUEUE, json.dumps(payload))

            _log_safe(execution_id, "Task Finalizada", STATUS_SUCCESS, task=TASK_NAME_DISPATCH)

            logger.info(
                "Dispatch task completed",
                task="dispatch",
                queue=REDIS_NOTIFICATIONS_QUEUE,
                avisos_count=avisos_count,
                duration_seconds=timer.elapsed_seconds,
            )
            if _pipeline_timer is not None:
                logger.info(
                    "Full pipeline duration",
                    duration_seconds=_pipeline_timer.elapsed_seconds,
                )

            return {"queue": REDIS_NOTIFICATIONS_QUEUE, "avisos_count": avisos_count}

        except Exception as e:
            _log_safe(
                execution_id, "Erro no Dispatch", STATUS_ERROR, extra={"error": str(e)}, task=TASK_NAME_DISPATCH
            )
            raise NonRetryableException(f"Unexpected error in dispatch: {e}") from e


@app.task(
    bind=True,
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def transform(self, input: str, output: str, execution_id=None):
    global _pipeline_timer

    execution_id = execution_id or self.request.id
    _log_safe(execution_id, "Transform Iniciado", STATUS_IN_PROGRESS)

    with Timer() as timer:
        logger.info("Starting transform task", task="transform", input=input)

        try:
            transformer = MeteogramTransformer(input, logger)
            output_path = transformer.perform(output_json_path=output)

            _log_safe(execution_id, "Transform Finalizado", STATUS_SUCCESS)

            logger.info(
                "Transform task completed",
                task="transform",
                input=input,
                output=output_path,
                duration_seconds=timer.elapsed_seconds,
            )

            analyze.delay(output, execution_id=execution_id)

            return {"path": str(output_path)}
        except NonRetryableException as e:
            _log_safe(execution_id, "Erro no Transform", STATUS_ERROR, extra={"error": str(e)})
            logger.exception(
                "Non-retryable error transforming file",
                task="transform",
                input=input,
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except RetryableException as e:
            _log_safe(execution_id, "Erro no Transform", STATUS_ERROR, extra={"error": str(e)})
            logger.exception(
                "Retryable error transforming file",
                task="transform",
                input=input,
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except Exception as e:
            _log_safe(execution_id, "Erro no Transform", STATUS_ERROR, extra={"error": str(e)})
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
    bind=True,
    autoretry_for=(RetryableException,),
    retry_backoff=True,
    retry_backoff_max=settings.CELERY_RETRY_BACKOFF_MAX,
    max_retries=settings.CELERY_MAX_RETRIES,
    throws=(NonRetryableException,),
    on_retry=on_retry_handler,
)
def download_file(self):
    global _pipeline_timer

    execution_id = self.request.id
    _log_safe(execution_id, "Task Iniciada", STATUS_STARTED)
    _log_safe(execution_id, "Download Iniciado", STATUS_IN_PROGRESS)

    _pipeline_timer = Timer()
    _pipeline_timer.__enter__()

    with Timer() as timer:
        logger.info("Starting download file task", task="download")

        try:
            download_service = DownloadMeteogram(logger)
            output_path = download_service.process()

            _log_safe(execution_id, "Download Finalizado", STATUS_SUCCESS)

            logger.info(
                "Download file task completed",
                task="download",
                output_path=output_path,
                duration_seconds=timer.elapsed_seconds,
            )

            json_path = FileSystem.create_json_path_from_file(output_path)

            transform.delay(str(output_path), json_path, execution_id=execution_id)

            return {"path": str(output_path)}
        except NonRetryableException as e:
            _log_safe(execution_id, "Falha no Download", STATUS_ERROR, extra={"error": str(e)})
            logger.exception(
                "Non-retryable error downloading file",
                task="download",
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except RetryableException as e:
            _log_safe(execution_id, "Falha no Download", STATUS_ERROR, extra={"error": str(e)})
            logger.exception(
                "Retryable error downloading file",
                task="download",
                error=str(e),
                duration_seconds=timer.elapsed_seconds,
            )
            raise
        except Exception as e:
            _log_safe(execution_id, "Falha no Download", STATUS_ERROR, extra={"error": str(e)})
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
