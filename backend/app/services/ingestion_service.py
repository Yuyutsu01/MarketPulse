import io
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Tuple
import pandas as pd
from sqlalchemy.orm import Session
from app.models.models import Campaign, DataQualityReport, JobStatus

class BaseConnector(ABC):
    """
    Abstract Connector Interface for data ingestion sources.
    """
    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        pass

class FileUploadConnector(BaseConnector):
    """
    Connector for CSV/Excel file uploads.
    """
    def __init__(self, file_contents: bytes, filename: str):
        self.file_contents = file_contents
        self.filename = filename

    def fetch_data(self) -> pd.DataFrame:
        if self.filename.endswith(".csv"):
            return pd.read_csv(io.BytesIO(self.file_contents))
        elif self.filename.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(self.file_contents))
        else:
            raise ValueError(f"Unsupported file format: {self.filename}")

class DataQualityEngine:
    """
    Multi-stage Data Quality Audit & Validation Pipeline.
    """
    REQUIRED_COLUMNS = [
        "campaign_name", "platform", "spend", "clicks",
        "impressions", "conversions", "device",
        "audience_age", "geography", "hour", "date"
    ]

    @classmethod
    def validate_and_normalize(cls, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Executes schema validation, range checks, sanity verification, and quality reporting.
        """
        total_rows = len(df)
        issues: List[str] = []
        valid_rows_mask = [True] * total_rows
        warning_count = 0
        rejected_count = 0

        # 1. Schema Validation
        missing_cols = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Schema Error: Missing required columns: {', '.join(missing_cols)}")

        # 2. Row-level Data Quality Checks
        for idx, row in df.iterrows():
            row_num = idx + 2
            row_has_error = False

            try:
                spend = float(row["spend"])
                clicks = int(row["clicks"])
                impressions = int(row["impressions"])
                conversions = int(row["conversions"])
                hour = int(row["hour"])

                # Impossible metric bounds check
                if spend < 0 or clicks < 0 or impressions < 0 or conversions < 0:
                    issues.append(f"Row {row_num}: Metrics (spend, clicks, impressions, conversions) cannot be negative.")
                    row_has_error = True

                if hour < 0 or hour > 23:
                    issues.append(f"Row {row_num}: Hour must be between 0 and 23.")
                    row_has_error = True

                # Funnel sanity check
                if clicks > impressions and impressions > 0:
                    issues.append(f"Row {row_num}: Warning - Clicks ({clicks}) exceed impressions ({impressions}).")
                    warning_count += 1

                if conversions > clicks and clicks > 0:
                    issues.append(f"Row {row_num}: Warning - Conversions ({conversions}) exceed clicks ({clicks}).")
                    warning_count += 1

            except Exception as e:
                issues.append(f"Row {row_num}: Type conversion error - {str(e)}")
                row_has_error = True

            if row_has_error:
                valid_rows_mask[idx] = False
                rejected_count += 1

        clean_df = df[valid_rows_mask].copy()
        valid_rows = len(clean_df)

        report_data = {
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "warning_rows": warning_count,
            "rejected_rows": rejected_count,
            "quality_score_percent": round((valid_rows / total_rows * 100) if total_rows > 0 else 0.0, 2),
            "issues": issues[:50]  # Cap top 50 issues
        }

        return clean_df, report_data

def ingest_campaign_data(
    db: Session,
    workspace_id: int,
    user_id: int,
    organization_id: int,
    connector: BaseConnector,
    dataset_name: str
) -> Dict[str, Any]:
    """
    Orchestrates Data Ingestion, Data Quality Validation, Database Ingestion, and Lineage Logging.
    """
    raw_df = connector.fetch_data()
    clean_df, quality_report = DataQualityEngine.validate_and_normalize(raw_df)

    if clean_df.empty:
        raise ValueError("Data Ingestion Failed: No valid rows passed data quality checks.")

    # Record Data Quality Audit Report
    report_record = DataQualityReport(
        workspace_id=workspace_id,
        dataset_name=dataset_name,
        total_rows=quality_report["total_rows"],
        valid_rows=quality_report["valid_rows"],
        warning_rows=quality_report["warning_rows"],
        rejected_rows=quality_report["rejected_rows"],
        issues_json=json.dumps(quality_report["issues"])
    )
    db.add(report_record)

    # Convert clean rows to Campaign ORM objects with Data Lineage Metadata
    campaigns_to_add = []
    sync_job_id = str(uuid.uuid4())

    for _, row in clean_df.iterrows():
        # Date parsing
        date_val = row["date"]
        if isinstance(date_val, str):
            date_parsed = datetime.strptime(date_val.strip(), "%Y-%m-%d").date()
        elif isinstance(date_val, (datetime, pd.Timestamp)):
            date_parsed = date_val.date()
        else:
            date_parsed = date_val

        revenue = float(row["revenue"]) if "revenue" in clean_df.columns and not pd.isna(row["revenue"]) else None

        campaign = Campaign(
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            campaign_name=str(row["campaign_name"]).strip(),
            platform=str(row["platform"]).strip(),
            spend=float(row["spend"]),
            clicks=int(row["clicks"]),
            impressions=int(row["impressions"]),
            conversions=int(row["conversions"]),
            revenue=revenue,
            device=str(row["device"]).strip(),
            audience_age=str(row["audience_age"]).strip(),
            geography=str(row["geography"]).strip(),
            hour=int(row["hour"]),
            date=date_parsed
        )
        campaigns_to_add.append(campaign)

    db.add_all(campaigns_to_add)
    db.commit()

    return {
        "sync_job_id": sync_job_id,
        "inserted_records": len(campaigns_to_add),
        "quality_report": quality_report
    }
