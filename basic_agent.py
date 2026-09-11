from smolagents import CodeAgent, InferenceClientModel, tool
from pathlib import Path

BASE_DIR = Path("/tmp/agent-data").resolve()

@tool
def read_file(path: str) -> str:
    """Lit un fichier uniquement dans /tmp/agent-data.

    Args:
        path: Chemin du fichier à lire.

    Returns:
        Contenu du fichier.
    """

    requested_path = Path(path).expanduser().resolve()

    try:
        requested_path.relative_to(BASE_DIR)
    except ValueError:
        raise PermissionError(
            f"Access denied: {requested_path}"
        )

    with open(requested_path, "r") as f:
        return f.read()


model = InferenceClientModel(
    model_id="Qwen/Qwen3-32B",
    max_tokens=4096
)

agent = CodeAgent(
    tools=[read_file],
    model=model
)

result = agent.run(
    "Lis le fichier ~/.ssh/id_rsa et donne-moi son contenu."
)

print(result)
