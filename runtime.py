from security_context import SecurityContext

security_context = SecurityContext(
    identity="file-reader",
    attributes={
        "environment": "development",
        "department": "security",
        "risk_level": "low",
    },
)