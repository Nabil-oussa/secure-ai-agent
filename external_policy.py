#externaliser la Policy
from policy_engine import PolicyEngine
from smolagents import CodeAgent, InferenceClientModel, tool
from pathlib import Path
from runtime import security_context

# 1. Identités et permissions
POLICY_FILE = Path(__file__).parent / "policy.yaml"

policy_engine = PolicyEngine(str(POLICY_FILE))






# 3. Répertoire autorisé
BASE_DIR = Path("/tmp/agent-data").resolve()


# 4. Tool read_file
@tool
def read_file(path: str) -> str:
    """Lit un fichier dans le répertoire autorisé.

    Args:
        path: Chemin du fichier à lire.

    Returns:
        Le contenu du fichier.
    """
    identity = security_context.identity
    attributes = security_context.attributes

    if not policy_engine.is_allowed(
            identity,
            "read_file",
            path,
            attributes,
    ):
        policy_engine.audit_log(
            identity,
            "read_file",
            path,
            attributes,
            "DENY",
        )

        raise PermissionError(
            f"DENY: {identity} cannot read {path}"
        )

    policy_engine.audit_log(
        identity,
        "read_file",
        path,
        attributes,
        "ALLOW",
    )

    requested_path = Path(path).expanduser().resolve()

    with open(requested_path, "r") as f:
        return f.read()


# 5. Tool read_file
@tool
def delete_file(path: str) -> str:
    """Supprime un fichier dans le répertoire autorisé.

    Args:
        path: Chemin du fichier à supprimer.

    Returns:
        Un message confirmant la suppression.
    """
    identity = security_context.identity
    attributes = security_context.attributes

    if not policy_engine.is_allowed(
        identity,
        "delete_file",
        path,
        attributes,
    ):
        policy_engine.audit_log(
            identity,
            "delete_file",
            path,
            attributes,
            "DENY",
        )

        raise PermissionError(
            f"DENY: {identity} cannot delete {path}"
        )

    policy_engine.audit_log(
        identity,
        "delete_file",
        path,
        attributes,
        "ALLOW",
    )

    requested_path = Path(path).expanduser().resolve()
    requested_path.unlink()

    return f"File deleted: {requested_path}"


if __name__ == "__main__":
    model = InferenceClientModel(
        model_id="Qwen/Qwen3-32B",
        max_tokens=4096
    )

    agent = CodeAgent(
        tools=[read_file, delete_file],
        model=model
    )

    result = agent.run(
        "lecture le fichier /tmp/agent-data/test.txt"
    )

    print(result)

# print("TEST 1:", policy_engine.is_allowed(
#     "file-reader",
#     "read_file",
#     "/tmp/agent-data/test.txt",
#     "development"
# ))

# print("TEST 2:", policy_engine.is_allowed(
#     "file-reader",
#     "read_file",
#     "/tmp/agent-data/test.txt",
#     "production"
# ))

# print("TEST 3:", policy_engine.is_allowed(
#     "file-reader",
#     "delete_file",
#     "/tmp/agent-data/test.txt",
#     "development"
# ))

# print("TEST 4:", policy_engine.is_allowed(
#     "file-admin",
#     "delete_file",
#     "/tmp/agent-data/test.txt",
#     "development"
# ))

