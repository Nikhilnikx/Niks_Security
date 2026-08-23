"""Risk scoring and severity classification."""


EVENT_TYPE_SCORES = {
    "failed_login": 20,
    "brute_force": 85,
    "port_scan": 45,
    "sql_injection": 90,
    "xss_attack": 70,
    "command_injection": 95,
    "malware": 95,
    "privilege_escalation": 80,
    "successful_login": 5,
    "unknown_event": 10,
}

SEVERITY_SCORES = {
    "low": 10,
    "medium": 35,
    "high": 65,
    "critical": 90,
}


def classify_risk(score):
    if score >= 75:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def calculate_risk_score(event_type, severity="low"):
    event_score = EVENT_TYPE_SCORES.get(event_type, 0)
    severity_score = SEVERITY_SCORES.get(severity, 0)
    score = max(event_score, severity_score)
    return score, classify_risk(score)
