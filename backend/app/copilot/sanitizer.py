"""Sanitize security data before sending to AI. Remove secrets, PII, and sensitive data."""
import re
from typing import Any


# Patterns to sanitize
SECRET_PATTERNS = [
    (re.compile(r'(password|passwd|pwd)\s*[=:]\s*\S+', re.I), r'\1=[REDACTED]'),
    (re.compile(r'(api[_-]?key|apikey|api[_-]?secret)\s*[=:]\s*\S+', re.I), r'\1=[REDACTED]'),
    (re.compile(r'(token|jwt|bearer)\s*[=:]\s*\S+', re.I), r'\1=[REDACTED]'),
    (re.compile(r'(secret[_-]?key|access[_-]?key)\s*[=:]\s*\S+', re.I), r'\1=[REDACTED]'),
    (re.compile(r'(authorization)\s*[=:]\s*\S+', re.I), r'\1=[REDACTED]'),
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL_REDACTED]'),
]

# Fields to strip from data before AI context
SENSITIVE_FIELDS = {
    'password', 'password_hash', 'password_hash', 'secret_key', 'api_key',
    'access_token', 'refresh_token', 'smtp_password', 'raw_log',
    'parsed_data', 'api_keys', 'key_hash',
}


def sanitize_text(text: str) -> str:
    """Remove secrets and PII from text."""
    if not text:
        return text
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def sanitize_dict(data: dict) -> dict:
    """Remove sensitive fields from a dictionary."""
    if not data:
        return data
    sanitized = {}
    for key, value in data.items():
        if key.lower() in SENSITIVE_FIELDS:
            continue
        if isinstance(value, str):
            sanitized[key] = sanitize_text(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_dict(item) if isinstance(item, dict) else sanitize_text(str(item)) if isinstance(item, str) else item for item in value]
        else:
            sanitized[key] = value
    return sanitized


def sanitize_context(context: dict) -> dict:
    """Full context sanitization pipeline."""
    sanitized = sanitize_dict(context)
    # Add metadata
    sanitized['_sanitized'] = True
    return sanitized
