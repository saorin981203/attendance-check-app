from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path


PUNCTUATION_PATTERN = re.compile(r"[\s・･•．.\-ー—―()（）\[\]【】]+")


def normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = PUNCTUATION_PATTERN.sub("", normalized)
    return normalized


def load_replacements(path: str) -> dict[str, str]:
    if not path:
        return {}
    file_path = Path(path)
    if not file_path.exists():
        return {}
    if file_path.suffix.lower() == ".json":
        return {str(k): str(v) for k, v in json.loads(file_path.read_text()).items()}
    if file_path.suffix.lower() == ".csv":
        replacements: dict[str, str] = {}
        with file_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            for row in reader:
                if len(row) >= 2:
                    replacements[str(row[0])] = str(row[1])
        return replacements
    return {}


def apply_replacements(value: str, replacements: dict[str, str]) -> str:
    return replacements.get(value, value)
