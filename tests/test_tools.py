from pathlib import Path

import pytest

from runtime import security_context
from external_policy import read_file, delete_file


TEST_DIR = Path("/tmp/agent-data")
TEST_FILE = TEST_DIR / "test.txt"


@pytest.fixture
def test_file():
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    TEST_FILE.write_text("Bonjour depuis le fichier de test de agent-data")

    yield TEST_FILE

    if TEST_FILE.exists():
        TEST_FILE.unlink()


def test_read_authorized_file(test_file):
    content = read_file(str(test_file))

    assert content == "Bonjour depuis le fichier de test de agent-data"


def test_read_forbidden_file():
    with pytest.raises(PermissionError):
        read_file("/etc/passwd")


def test_delete_forbidden_for_file_reader(test_file):
    with pytest.raises(PermissionError):
        delete_file(str(test_file))

    assert test_file.exists()


def test_security_context():
    assert security_context.identity == "file-reader"
    assert security_context.attributes["environment"] == "development"
    assert security_context.attributes["department"] == "security"
    assert security_context.attributes["risk_level"] == "low"