from __future__ import annotations

import logging

import pandas as pd


def load_employee_emails(path: str) -> dict[str, str]:
    if not path:
        return {}
    try:
        df = pd.read_excel(path)
    except Exception:
        try:
            df = pd.read_csv(path)
        except Exception as exc:
            logging.warning("Failed to read employee master: %s (%s)", path, exc)
            return {}
    name_col = None
    email_col = None
    for column in df.columns:
        if "氏名" in str(column):
            name_col = column
        if "メール" in str(column) or "email" in str(column).lower():
            email_col = column
    if not name_col or not email_col:
        logging.warning("Employee master missing required columns: %s", path)
        return {}
    mapping: dict[str, str] = {}
    for _, row in df.iterrows():
        name = row.get(name_col)
        email = row.get(email_col)
        if pd.isna(name) or pd.isna(email):
            continue
        mapping[str(name)] = str(email)
    return mapping
