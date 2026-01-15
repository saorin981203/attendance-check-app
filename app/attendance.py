from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(slots=True)
class AttendanceEntry:
    department: str
    name: str
    date: str
    start_time: str | None
    end_time: str | None
    file_path: str
    sheet_name: str


def load_attendance_entries(attendance_root: str, target_year_month: str) -> list[AttendanceEntry]:
    root = Path(attendance_root)
    entries: list[AttendanceEntry] = []
    if not root.exists():
        logging.warning("Attendance root not found: %s", attendance_root)
        return entries
    for file_path in root.rglob("*.xlsx"):
        department = file_path.parent.name
        try:
            sheet_names = pd.ExcelFile(file_path).sheet_names
        except Exception as exc:
            logging.warning("Failed to read sheets: %s (%s)", file_path, exc)
            continue
        for sheet_name in sheet_names:
            try:
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_name,
                    usecols="A,C,D",
                    header=None,
                )
            except Exception as exc:
                logging.warning(
                    "Failed to read sheet: %s - %s (%s)", file_path, sheet_name, exc
                )
                continue
            for _, row in df.iterrows():
                day = row.iloc[0]
                if pd.isna(day):
                    continue
                day_value = str(day).split(".")[0]
                date = f"{target_year_month}-{int(day_value):02d}"
                start_time = None if pd.isna(row.iloc[1]) else str(row.iloc[1])
                end_time = None if pd.isna(row.iloc[2]) else str(row.iloc[2])
                entries.append(
                    AttendanceEntry(
                        department=department,
                        name=sheet_name,
                        date=date,
                        start_time=start_time,
                        end_time=end_time,
                        file_path=str(file_path),
                        sheet_name=sheet_name,
                    )
                )
    return entries
