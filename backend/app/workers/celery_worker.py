import json
import logging
from celery import Celery
from app.core.config import settings
from app.database.database import SessionLocal
from app.models.models import JobStatus
from app.services.ingestion_service import FileUploadConnector, ingest_campaign_data
from app.ml.ml_service import train_user_model

logger = logging.getLogger(__name__)

# Initialize Celery app backed by Redis
celery_app = Celery(
    "marketpulse_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(bind=True)
def process_csv_upload_task(self, workspace_id: int, user_id: int, organization_id: int, file_bytes_hex: str, filename: str):
    """
    Celery background task for parsing CSV uploads, validating data quality, and inserting campaigns.
    """
    task_id = self.request.id
    db = SessionLocal()
    
    try:
        # Create JobStatus record
        job = JobStatus(
            id=task_id,
            workspace_id=workspace_id,
            task_type="CSV_UPLOAD",
            status="RUNNING",
            progress_percent=10
        )
        db.merge(job)
        db.commit()

        file_bytes = bytes.fromhex(file_bytes_hex)
        connector = FileUploadConnector(file_bytes, filename)
        
        result = ingest_campaign_data(
            db=db,
            workspace_id=workspace_id,
            user_id=user_id,
            organization_id=organization_id,
            connector=connector,
            dataset_name=filename
        )

        job.status = "SUCCESS"
        job.progress_percent = 100
        job.result_json = json.dumps(result)
        db.commit()

        # Trigger model retraining task asynchronously
        train_user_model_task.delay(user_id)
        return result

    except Exception as e:
        logger.exception(f"Error executing CSV upload task {task_id}")
        job = db.query(JobStatus).filter(JobStatus.id == task_id).first()
        if job:
            job.status = "FAILED"
            job.error_message = str(e)
            db.commit()
        raise e
    finally:
        db.close()

@celery_app.task(bind=True)
def train_user_model_task(self, user_id: int):
    """
    Celery background task for training Scikit-Learn Random Forest Regressor models per user.
    """
    task_id = self.request.id
    db = SessionLocal()
    
    try:
        job = JobStatus(
            id=task_id,
            task_type="MODEL_TRAIN",
            status="RUNNING",
            progress_percent=20
        )
        db.merge(job)
        db.commit()

        success = train_user_model(db, user_id)

        job.status = "SUCCESS" if success else "FAILED"
        job.progress_percent = 100
        job.result_json = json.dumps({"trained": success})
        db.commit()
        return {"trained": success}

    except Exception as e:
        logger.exception(f"Error training model task {task_id}")
        job = db.query(JobStatus).filter(JobStatus.id == task_id).first()
        if job:
            job.status = "FAILED"
            job.error_message = str(e)
            db.commit()
        raise e
    finally:
        db.close()
