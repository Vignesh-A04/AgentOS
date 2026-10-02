from pathlib import Path


WORKSPACE_ROOT = (
    Path(__file__).resolve().parents[3] / "workspace"
)


def _safe_path(relative_path: str) -> Path:
    """
    Resolve a path while keeping access inside
    the AgentOS workspace.
    """

    target = (WORKSPACE_ROOT / relative_path).resolve()

    if not target.is_relative_to(WORKSPACE_ROOT.resolve()):
        raise ValueError(
            "Access denied: path is outside AgentOS workspace."
        )

    return target


def create_file(path: str, content: str) -> str:
    """
    Create a text file inside the AgentOS workspace.
    """

    target = _safe_path(path)

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        content,
        encoding="utf-8",
    )

    return f"File created successfully: {path}"


def read_file(path: str) -> str:
    """
    Read a text file from the AgentOS workspace.
    """

    target = _safe_path(path)

    if not target.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not target.is_file():
        raise ValueError(
            f"Not a file: {path}"
        )

    return target.read_text(
        encoding="utf-8"
    )


def list_files(path: str = ".") -> list[str]:
    """
    List files and directories inside the AgentOS workspace.
    """

    target = _safe_path(path)

    if not target.exists():
        raise FileNotFoundError(
            f"Path not found: {path}"
        )

    return [
        item.relative_to(WORKSPACE_ROOT).as_posix()
        for item in target.iterdir()
    ]