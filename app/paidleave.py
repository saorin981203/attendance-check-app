from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class PaidLeaveEntry:
    name: str
    date: str
    leave_type: str
    raw_type: str


def load_paidleave_entries(
    excel_path: str,
    sheet_name: str,
    name_col: str,
    date_col: str,
    type_col: str,
    type_mapping: dict[str, str],
) -> list[PaidLeaveEntry]:
    if not excel_path:
        return []
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
    except Exception as exc:
        logging.warning("Failed to read paid leave file: %s (%s)", excel_path, exc)
        return []
    entries: list[PaidLeaveEntry] = []
    for _, row in df.iterrows():
        raw_name = row.get(name_col)
        raw_date = row.get(date_col)
        raw_type = row.get(type_col)
        if pd.isna(raw_name) or pd.isna(raw_date) or pd.isna(raw_type):
            continue
        date_value = pd.to_datetime(raw_date).strftime("%Y-%m-%d")
        raw_type_str = str(raw_type)
        leave_type = type_mapping.get(raw_type_str, "work")
        entries.append(
            PaidLeaveEntry(
                name=str(raw_name),
                date=date_value,
                leave_type=leave_type,
                raw_type=raw_type_str,
            )
        )
    return entries
