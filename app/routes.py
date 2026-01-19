from __future__ import annotations

import urllib.parse
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for

from app.config import AppConfig, override_config
from app.runner import ErrorEntry, run_check


def build_mailto(
    name: str, department: str, date: str, error_type: str, email: str | None
) -> str:
    subject = f"【出勤簿】入力確認のお願い（{datetime.now():%Y年%m月}）"
    body = (
        "お疲れさまです。\n"
        "出勤簿の入力確認をお願いいたします。\n\n"
        f"部署: {department}\n"
        f"氏名: {name}\n"
        f"対象日: {date}\n"
        f"エラー内容: {error_type}\n\n"
        "ご対応後にご一報ください。"
    )
    params = urllib.parse.urlencode({"subject": subject, "body": body})
    recipient = email or ""
    return f"mailto:{recipient}?{params}"


def to_view_model(item: ErrorEntry) -> dict[str, str]:
    return {
        "department": item.department,
        "name": item.name,
        "date": item.date,
        "error_type": item.error_type,
        "attendance_detail": item.attendance_detail,
        "paidleave_detail": item.paidleave_detail,
        "file_path": item.file_path,
        "sheet_name": item.sheet_name,
        "email": item.email or "",
        "mailto": build_mailto(
            item.name,
            item.department,
            item.date,
            item.error_type,
            item.email,
        ),
    }


def register_routes(app: Flask) -> None:
    @app.get("/")
    def index() -> str:
        config: AppConfig = app.config["APP_CONFIG"]
        return render_template("index.html", config=config, results=None)

    @app.post("/run")
    def run() -> str:
        config: AppConfig = app.config["APP_CONFIG"]
        overrides = request.form.to_dict()
        config = override_config(config, overrides)
        results, output_dir = run_check(config)
        view_results = [to_view_model(item) for item in results]
        return render_template(
            "index.html",
            config=config,
            results=view_results,
            output_dir=str(output_dir),
        )

    @app.get("/refresh")
    def refresh() -> str:
        return redirect(url_for("index"))
