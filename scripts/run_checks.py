"""Run dbt (run -> source freshness -> test), parse the JSON artifacts, alert on problems.

usage:
  python scripts/run_checks.py                 # prints a report, exit 1 if anything failed
  python scripts/run_checks.py --slack         # also POST to $SLACK_WEBHOOK_URL
  python scripts/run_checks.py --email         # also email via SMTP_* env vars

Why `run` then `test` instead of `dbt build`: build SKIPS downstream nodes when an upstream test
fails, which hides problems from the downstream checks. Use `build` when you want to GATE bad data;
use run+test when you want to DETECT as many problems as possible. See docs/LOG.md.
"""
import argparse
import json
import os
import pathlib
import smtplib
import subprocess
import sys
import urllib.request
from email.message import EmailMessage

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _dbt(*args):
    return subprocess.run(["dbt", *args, "--profiles-dir", str(ROOT), "--project-dir", str(ROOT)],
                          cwd=ROOT, capture_output=True, text=True)


def _load(name):
    p = ROOT / "target" / name
    return json.loads(p.read_text()) if p.exists() else {"results": []}


def collect():
    """Returns a list of dicts: check, kind, status, failures, message."""
    out = []
    _dbt("run")
    for r in _load("run_results.json")["results"]:
        if r["status"] not in ("success",):
            out.append(dict(check=r["unique_id"].split(".")[2], kind="model_run",
                            status="error" if r["status"] == "error" else r["status"],
                            failures=None, message=(r.get("message") or "")[:200]))
    _dbt("source", "freshness")
    for r in _load("sources.json")["results"]:
        if r["status"] in ("warn", "error", "runtime error"):
            out.append(dict(check="source_freshness." + r["unique_id"].split(".", 2)[2],
                            kind="freshness", status="error" if r["status"] != "warn" else "warn",
                            failures=None, message=f"max_loaded_at_time_ago_in_s={r.get('max_loaded_at_time_ago_in_s')}"))
    _dbt("test")
    for r in _load("run_results.json")["results"]:
        if r["status"] in ("fail", "warn", "error"):
            out.append(dict(check=r["unique_id"].split(".")[2], kind="test", status=r["status"],
                            failures=r.get("failures"), message=(r.get("message") or "")[:200]))
    return out


def format_report(problems):
    if not problems:
        return "All data checks passed."
    lines = [f"{len(problems)} data check problem(s):"]
    for p in sorted(problems, key=lambda x: (x["status"] != "fail" and x["status"] != "error", x["check"])):
        f = f" ({p['failures']} rows)" if p["failures"] is not None else ""
        lines.append(f"- [{p['status'].upper()}] {p['check']}{f}")
    return "\n".join(lines)


def send_slack(text):
    url = os.environ["SLACK_WEBHOOK_URL"]
    req = urllib.request.Request(url, data=json.dumps({"text": text}).encode(),
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=15)


def send_email(text):
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = "Data check failures", os.environ["SMTP_FROM"], os.environ["SMTP_TO"]
    msg.set_content(text)
    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", 587))) as s:
        s.starttls()
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        s.send_message(msg)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--slack", action="store_true")
    ap.add_argument("--email", action="store_true")
    a = ap.parse_args()
    problems = collect()
    report = format_report(problems)
    print(report)
    hard = [p for p in problems if p["status"] in ("fail", "error")]
    if hard and a.slack:
        send_slack(report)
    if hard and a.email:
        send_email(report)
    sys.exit(1 if hard else 0)
