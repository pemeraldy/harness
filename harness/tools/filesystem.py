from pathlib import Path
from harness.tools.registry import tool

WORKSPACE = Path("./workspace").resolve()

WORKSPACE.mkdir(exist_ok=True)

def _resolve_path(path: str) -> Path:
    """Resolve `path` against the workspace and confirm it stays inside."""
    target = (WORKSPACE / path).resolve()

    if not target.is_relative_to(WORKSPACE):
        raise ValueError(f"path escapes workspace: {path}")
    
    return target


@tool
def read(path: str) -> str:
    """Read the contents of a file from the workspace, by path."""
    return _resolve_path(path).read_text()

@tool
def write(path:str, content:str) -> str:
    """Write content to a file in the workspace, creating it if needed.
    Overwrites the file if it already exists. Returns confirmation with byte count."""
    target = _resolve_path(path)
    target.write_text(content)

    return f" Wrote {len(content)} bytes into {path}"

@tool
def list_dir(path: str = ".") -> str:
    """List the files and directories at the given path inside the workspace.
    Defaults to the workspace root. Returns one entry per line."""
    target = _resolve_path(path)

    if not target.is_dir():
        return f"error: not a directory: {path}"
   
    entries = sorted(target.iterdir())
    return "\n".join(e.name + ("/" if e.is_dir() else "") for e in entries)

@tool
def mkdir(path: str) -> str:
    """Create a directory in the workspace, including any parent directories.
    No error if the directory already exists."""
    target = _resolve_path(path)

    target.mkdir(parents=True,exist_ok=True)

    return f"created directory {path}"

@tool
def delete(path:str) -> str:
    """Delete a file from the workspace. Will not delete directories."""
    target = _resolve_path(path)

    if target.is_dir():
        return f" refusing to delete directory: {path}"

    target.unlink()

    return f"deleted {path}"

