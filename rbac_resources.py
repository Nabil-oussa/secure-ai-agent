#RBAC
from smolagents import CodeAgent, InferenceClientModel, tool
from pathlib import Path


# 1. Identités et permissions
ROLES = {
    "file-reader": {
        "read_file": {
            "/tmp/agent-data",
            "/tmp/public",
        },
    },

    "file-admin": {
        "read_file": {
            "/tmp/agent-data",
            "/tmp/public",
        },
        "delete_file": {
            "/tmp/agent-data",
        },
    },
}


AGENT_IDENTITY = "file-reader"


# 2. Policy Engine
def is_allowed(identity: str, action: str, resource: str) -> bool:
    permissions = ROLES.get(identity, {})

    # Récupère les ressources autorisées pour cette action
    allowed_resources = permissions.get(action, set())

    # L'action n'est pas autorisée
    if not allowed_resources:
        return False

    requested_path = Path(resource).expanduser().resolve()

    # Vérifie si la ressource demandée est sous
    # l'un des répertoires autorisés
    for allowed_resource in allowed_resources:
        allowed_path = Path(allowed_resource).resolve()

        try:
            requested_path.relative_to(allowed_path)
            return True
        except ValueError:
            continue

    return False

def audit_log(identity: str, action: str, resource: str, decision: str):
    print(
        f"[AUDIT] "
        f"identity={identity} "
        f"action={action} "
        f"resource={resource} "
        f"decision={decision}"
    )
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

    if not is_allowed(identity, "read_file", path):
        audit_log(
            identity,
            "read_file",
            path,
            "DENY"
        )

        raise PermissionError(
            f"DENY: {identity} cannot read {path}"
        )

    audit_log(
        identity,
        "read_file",
        path,
        "ALLOW"
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

    if not is_allowed(identity, "delete_file", path):
        audit_log(
            identity,
            "delete_file",
            path,
            "DENY"
        )

        raise PermissionError(
            f"DENY: {identity} cannot delete {path}"
        )

    audit_log(
        identity,
        "delete_file",
        path,
        "ALLOW"
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
    "supprime le fichier /tmp/agent-data/test.txt"
)


print("TEST 1:", is_allowed(
    "file-reader",
    "read_file",
    "/tmp/agent-data/test.txt"
))

print("TEST 2:", is_allowed(
    "file-reader",
    "read_file",
    "/tmp/public/test.txt"
))

print("TEST 3:", is_allowed(
    "file-reader",
    "delete_file",
    "/tmp/agent-data/test.txt"
))

print("TEST 4:", is_allowed(
    "file-admin",
    "delete_file",
    "/tmp/agent-data/test.txt"
))

print("TEST 5:", is_allowed(
    "file-reader",
    "read_file",
    "/etc/passwd"
))