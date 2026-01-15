from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class PaidLeaveColumns:
    name: str
    date: str
    type: str


@dataclass(slots=True)
class AppConfig:
    attendance_root: str
    target_year_month: str
    paidleave_excel_path: str
    paidleave_sheet_name: str
    paidleave_col_name: PaidLeaveColumns
    paidleave_type_mapping: dict[str, str]
    employee_master_path: str
    name_normalize_replacements: str
    output_dir: str


DEFAULT_CONFIG_PATH = Path("config.yaml")


def load_config(config_path: str | None = None) -> AppConfig:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    paidleave_col = raw.get("paidleave_col_name", {})
    return AppConfig(
        attendance_root=str(raw.get("attendance_root", "")),
        target_year_month=str(raw.get("target_year_month", "")),
        paidleave_excel_path=str(raw.get("paidleave_excel_path", "")),
        paidleave_sheet_name=str(raw.get("paidleave_sheet_name", "")),
        paidleave_col_name=PaidLeaveColumns(
            name=str(paidleave_col.get("name", "氏名")),
            date=str(paidleave_col.get("date", "日付")),
            type=str(paidleave_col.get("type", "区分")),
        ),
        paidleave_type_mapping={
            str(key): str(value)
            for key, value in (raw.get("paidleave_type_mapping") or {}).items()
        },
        employee_master_path=str(raw.get("employee_master_path", "")),
        name_normalize_replacements=str(raw.get("name_normalize_replacements", "")),
        output_dir=str(raw.get("output_dir", "results")),
    )


def override_config(base: AppConfig, updates: dict[str, Any]) -> AppConfig:
    return AppConfig(
        attendance_root=str(updates.get("attendance_root", base.attendance_root)),
        target_year_month=str(
            updates.get("target_year_month", base.target_year_month)
        ),
        paidleave_excel_path=str(
            updates.get("paidleave_excel_path", base.paidleave_excel_path)
        ),
        paidleave_sheet_name=str(
            updates.get("paidleave_sheet_name", base.paidleave_sheet_name)
        ),
        paidleave_col_name=PaidLeaveColumns(
            name=str(
                updates.get("paidleave_col_name_name", base.paidleave_col_name.name)
            ),
            date=str(
                updates.get("paidleave_col_name_date", base.paidleave_col_name.date)
            ),
            type=str(
                updates.get("paidleave_col_name_type", base.paidleave_col_name.type)
            ),
        ),
        paidleave_type_mapping=base.paidleave_type_mapping,
        employee_master_path=str(
            updates.get("employee_master_path", base.employee_master_path)
        ),
        name_normalize_replacements=str(
            updates.get("name_normalize_replacements", base.name_normalize_replacements)
        ),
        output_dir=str(updates.get("output_dir", base.output_dir)),
    )
