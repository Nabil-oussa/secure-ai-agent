from policy_engine import PolicyEngine

policy_engine = PolicyEngine("policy.yaml")

RESOURCE = "/tmp/agent-data/test.txt"


def test_reader_can_read_in_development():
    assert policy_engine.is_allowed(
        "file-reader",
        "read_file",
        RESOURCE,
        {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
        },
    )


def test_reader_can_read_in_production():
    assert policy_engine.is_allowed(
        "file-reader",
        "read_file",
        RESOURCE,
        {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
},
    )


def test_reader_cannot_delete():
    assert not policy_engine.is_allowed(
        "file-reader",
        "delete_file",
        RESOURCE,
        {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
},
    )


def test_admin_can_delete_in_development():
    assert policy_engine.is_allowed(
        "file-admin",
        "delete_file",
        RESOURCE,
        {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
},
    )


def test_admin_cannot_delete_in_production():
    assert not policy_engine.is_allowed(
        "file-admin",
        "delete_file",
        RESOURCE,
        {"environment": "production"},
    )


def test_reader_cannot_access_outside_allowed_directory():
    assert not policy_engine.is_allowed(
        "file-reader",
        "read_file",
        "/etc/passwd",
        {"environment": "development"},
    )


def test_unknown_identity_is_denied():
    assert not policy_engine.is_allowed(
        "unknown-agent",
        "read_file",
        RESOURCE,
        {"environment": "development"},
    )


def test_unknown_action_is_denied():
    assert not policy_engine.is_allowed(
        "file-admin",
        "unknown_action",
        RESOURCE,
      {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
    },
      )

def test_reader_cannot_access_similar_path():
    assert not policy_engine.is_allowed(
        "file-reader",
        "read_file",
        "/tmp/agent-data-secret/test.txt",
        {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
    },
    )


def test_reader_cannot_use_path_traversal():
    assert not policy_engine.is_allowed(
        "file-reader",
        "read_file",
        "/tmp/agent-data/../etc/passwd",
        {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
    },
    )


def test_admin_cannot_delete_public_file():
    assert not policy_engine.is_allowed(
        "file-admin",
        "delete_file",
        "/tmp/public/test.txt",
        {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
    },
    )


def test_empty_identity_is_denied():
    assert not policy_engine.is_allowed(
        "",
        "read_file",
        "/tmp/agent-data/test.txt",
        {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
    },
    )


def test_empty_action_is_denied():
    assert not policy_engine.is_allowed(
        "file-admin",
        "",
        "/tmp/agent-data/test.txt",
        {
    "environment": "development",
    "department": "security",
    "risk_level": "low",
    },
    )


def test_missing_environment_is_denied_for_delete():
    assert not policy_engine.is_allowed(
        "file-admin",
        "delete_file",
        "/tmp/agent-data/test.txt",
        {},
    )

def test_admin_cannot_delete_with_wrong_department():
    assert not policy_engine.is_allowed(
        "file-admin",
        "delete_file",
        "/tmp/agent-data/test.txt",
        {
            "environment": "development",
            "department": "marketing",
            "risk_level": "low",
        },
    )