from smolagents import CodeAgent, InferenceClientModel, tool
from pathlib import Path


# 1. Identités et permissions
AGENTS = {
    "file-reader": {
        "read_file",
    },
    "file-admin": {
        "read_file",
        "delete_file",
    },
}

AGENT_IDENTITY = "file-admin"



# 2. Policy Engine
def is_allowed(identity: str, action: str) -> bool:
    permissions = AGENTS.get(identity, set())
    return action in permissions




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
    identity = AGENT_IDENTITY

    if not is_allowed(identity, "read_file"):
        raise PermissionError(
            f"DENY: {identity} cannot read files"
        )

    requested_path = Path(path).expanduser().resolve()

    try:
        requested_path.relative_to(BASE_DIR)
    except ValueError:
        raise PermissionError(
            f"DENY: {requested_path} is outside {BASE_DIR}"
        )

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
    identity = AGENT_IDENTITY

    if not is_allowed(identity, "delete_file"):
        raise PermissionError(
            f"DENY: {identity} cannot delete files"
        )

    requested_path = Path(path).expanduser().resolve()

    try:
        requested_path.relative_to(BASE_DIR)
    except ValueError:
        raise PermissionError(
            f"DENY: {requested_path} is outside {BASE_DIR}"
        )

    requested_path.unlink()

    return f"File deleted: {requested_path}"


model = InferenceClientModel(
    model_id="Qwen/Qwen3-32B",
    max_tokens=4096
)

agent = CodeAgent(
    tools=[read_file, delete_file],
    model=model
)

result = agent.run(
    "Lis le fichier /tmp/agent-data/test.txt"
)

print(result)