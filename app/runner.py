from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from app.attendance import AttendanceEntry, load_attendance_entries
from app.config import AppConfig
from app.employee_master import load_employee_emails
from app.normalize import apply_replacements, load_replacements, normalize_name
from app.paidleave import PaidLeaveEntry, load_paidleave_entries


@dataclass(slots=True)
class ErrorEntry:
    department: str
    name: str
    date: str
    error_type: str
    attendance_detail: str
    paidleave_detail: str
    file_path: str
    sheet_name: str
    email: str | None


def run_check(config: AppConfig) -> tuple[list[ErrorEntry], Path]:
    output_dir = Path(config.output_dir) / config.target_year_month.replace("-", "")
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "run.log"
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    replacements = load_replacements(config.name_normalize_replacements)
    attendance_entries = load_attendance_entries(
        config.attendance_root, config.target_year_month
    )
    paidleave_entries = load_paidleave_entries(
        config.paidleave_excel_path,
        config.paidleave_sheet_name,
        config.paidleave_col_name.name,
        config.paidleave_col_name.date,
        config.paidleave_col_name.type,
        config.paidleave_type_mapping,
    )
    employee_emails = load_employee_emails(config.employee_master_path)

    paidleave_index: dict[tuple[str, str], PaidLeaveEntry] = {}
    for entry in paidleave_entries:
        normalized_name = apply_replacements(normalize_name(entry.name), replacements)
        paidleave_index[(normalized_name, entry.date)] = entry

    errors: list[ErrorEntry] = []
    for entry in attendance_entries:
        normalized_name = apply_replacements(normalize_name(entry.name), replacements)
        start_missing = not entry.start_time or entry.start_time == "nan"
        end_missing = not entry.end_time or entry.end_time == "nan"
        if start_missing or end_missing:
            errors.append(
                ErrorEntry(
                    department=entry.department,
                    name=entry.name,
                    date=entry.date,
                    error_type="MISSING_TIME",
                    attendance_detail=f"始業: {entry.start_time or '-'}, 終業: {entry.end_time or '-'}",
                    paidleave_detail="-",
                    file_path=entry.file_path,
                    sheet_name=entry.sheet_name,
                    email=employee_emails.get(entry.name),
                )
            )
        attendance_status = "leave" if start_missing and end_missing else "work"
        paidleave = paidleave_index.get((normalized_name, entry.date))
        if paidleave and paidleave.leave_type != attendance_status:
            errors.append(
                ErrorEntry(
                    department=entry.department,
                    name=entry.name,
                    date=entry.date,
                    error_type="PAIDLEAVE_MISMATCH",
                    attendance_detail=f"始業: {entry.start_time or '-'}, 終業: {entry.end_time or '-'}",
                    paidleave_detail=paidleave.raw_type,
                    file_path=entry.file_path,
                    sheet_name=entry.sheet_name,
                    email=employee_emails.get(entry.name),
                )
            )
    save_results(errors, output_dir)
    return errors, output_dir


def save_results(errors: list[ErrorEntry], output_dir: Path) -> None:
    json_path = output_dir / "results.json"
    json_path.write_text(
        json.dumps([asdict(error) for error in errors], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    df = pd.DataFrame([asdict(error) for error in errors])
    if df.empty:
        df = pd.DataFrame(
            columns=[
                "department",
                "name",
                "date",
                "error_type",
                "attendance_detail",
                "paidleave_detail",
                "file_path",
                "sheet_name",
                "email",
            ]
        )
    df.to_excel(output_dir / "summary.xlsx", index=False)
