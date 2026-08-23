"""
Log parser supporting CSV, key=value, Apache, syslog, and generic formats.
"""
import csv
import io
import re
import json
from datetime import datetime

_TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
    "%d/%b/%Y:%H:%M:%S %z",
    "%b %d %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
]

_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_KEY_VALUE_RE = re.compile(r"(\w+)=([^,]+)")
_APACHE_RE = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+(?P<user>\S+)\s+\[(?P<ts>[^\]]+)\]\s+'
    r'"(?P<action>[^"]*)"\s+(?P<status>\d{3})'
)
_GENERIC_RE = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})\s+'
    r'(?P<ip>\S+)\s+(?P<user>\S+)\s+(?P<action>\S+)\s+(?P<status>\S+)'
)


def try_parse_timestamp(value):
    if not value:
        return None
    value = value.strip()
    for fmt in _TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def classify_event_type(entry):
    """Classify a parsed entry into an event category."""
    action = (entry.get("action") or "").lower()
    desc = (entry.get("raw_line") or "").lower()

    if any(w in action or w in desc for w in ["failed", "failure", "invalid", "denied", "rejected"]):
        if any(w in action or w in desc for w in ["login", "auth", "password", "ssh"]):
            return "authentication", "failed_login"
    if any(w in action or w in desc for w in ["port scan", "nmap", "portscan", "scanning"]):
        return "network", "port_scan"
    if any(w in action or w in desc for w in ["select", "union", "insert", "drop", "sql", "injection"]):
        return "web", "sql_injection"
    if any(w in action or w in desc for w in ["<script", "xss", "cross-site", "alert("]):
        return "web", "xss_attack"
    if any(w in action or w in desc for w in ["cmd", "command", "exec", "shell", "eval"]):
        return "application", "command_injection"
    if any(w in action or w in desc for w in ["malware", "virus", "trojan", "ransomware"]):
        return "endpoint", "malware"
    if any(w in action or w in desc for w in ["privilege", "escalat", "sudo", "root"]):
        return "endpoint", "privilege_escalation"
    if any(w in action or w in desc for w in ["success", "accepted", "ok", "200"]):
        return "authentication", "successful_login"
    return "unknown", "unknown_event"


def parse_csv(file_bytes):
    text = file_bytes.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    entries = []
    for row in reader:
        normalized = {k.lower().strip(): v for k, v in row.items() if k}
        category, event_type = classify_event_type(normalized)
        entries.append({
            "timestamp": try_parse_timestamp(normalized.get("timestamp", "")),
            "source_ip": normalized.get("source_ip") or normalized.get("ip"),
            "destination_ip": normalized.get("destination_ip") or normalized.get("dest_ip"),
            "username": normalized.get("username") or normalized.get("user"),
            "action": normalized.get("action") or normalized.get("event"),
            "status": normalized.get("status"),
            "category": category,
            "event_type": event_type,
            "raw_line": ",".join(f"{k}={v}" for k, v in row.items()),
            "parsed": True,
        })
    return entries


def parse_key_value_line(line):
    fields = dict(_KEY_VALUE_RE.findall(line))
    if not fields:
        return None
    category, event_type = classify_event_type(fields)
    return {
        "timestamp": try_parse_timestamp(fields.get("timestamp")),
        "source_ip": fields.get("source_ip") or fields.get("ip"),
        "destination_ip": fields.get("destination_ip"),
        "username": fields.get("username") or fields.get("user"),
        "action": fields.get("action") or fields.get("event"),
        "status": fields.get("status"),
        "category": category,
        "event_type": event_type,
        "raw_line": line,
        "parsed": True,
    }


def parse_text_line(line):
    line = line.strip()
    if not line:
        return None
    result = parse_key_value_line(line)
    if result:
        return result
    for pattern in (_APACHE_RE, _GENERIC_RE):
        match = pattern.match(line)
        if match:
            data = match.groupdict()
            category, event_type = classify_event_type(data)
            return {
                "timestamp": try_parse_timestamp(data.get("ts")),
                "source_ip": data.get("ip"),
                "username": data.get("user"),
                "action": data.get("action"),
                "status": data.get("status"),
                "category": category,
                "event_type": event_type,
                "raw_line": line,
                "parsed": True,
            }
    ip = _IP_RE.search(line)
    return {
        "timestamp": None,
        "source_ip": ip.group(0) if ip else None,
        "username": None,
        "action": None,
        "status": None,
        "category": "unknown",
        "event_type": "unknown_event",
        "raw_line": line,
        "parsed": False,
    }


def parse_text(file_bytes):
    text = file_bytes.decode("utf-8", errors="ignore")
    return [item for line in text.splitlines() if (item := parse_text_line(line))]


def parse_json_logs(file_bytes):
    """Parse JSON-formatted log entries."""
    text = file_bytes.decode("utf-8", errors="ignore")
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            category, event_type = classify_event_type(data)
            entries.append({
                "timestamp": try_parse_timestamp(data.get("timestamp") or data.get("time") or data.get("@timestamp")),
                "source_ip": data.get("source_ip") or data.get("src_ip") or data.get("source", {}).get("ip") if isinstance(data.get("source"), dict) else data.get("source_ip"),
                "destination_ip": data.get("destination_ip") or data.get("dest_ip"),
                "username": data.get("username") or data.get("user"),
                "action": data.get("action") or data.get("event_type") or data.get("event"),
                "status": str(data.get("status", "")),
                "category": data.get("category") or category,
                "event_type": data.get("event_type") or event_type,
                "severity": data.get("severity"),
                "raw_line": line,
                "parsed": True,
            })
        except json.JSONDecodeError:
            continue
    return entries


def parse_file(filename, file_bytes):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "csv":
        return parse_csv(file_bytes)
    elif ext == "json":
        return parse_json_logs(file_bytes)
    return parse_text(file_bytes)
