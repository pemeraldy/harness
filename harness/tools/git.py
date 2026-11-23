from harness.tools.registry import tool
from harness.tools.filesystem import WORKSPACE
import subprocess


GIT_TIMEOUT = 10

def _run_git(*args: str) -> str:
    """
    Run a git command in the workspace and return a combined output string.

    The first argument's working directory is hard-coded to WORKSPACE — the
    model cannot influence it. Non-zero exit codes are not raised; the
    output is returned with an exit-code note so the model can read it
    and decide what to do.
    """

    result  = subprocess.run(
        ["git", *args],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=GIT_TIMEOUT,
        check=False # Don't raise on non-zero exit; leave model to handle that.
    )

    output =  result.stdout.strip() or result.stderr.strip()

    if result.returncode != 0:
        return f"[git exit {result.returncode}] {output}"

    return output or "No output"


if not (WORKSPACE / ".git").exists():
    _run_git("init")
    _run_git("config", "user.name", "agent")
    _run_git("config", "user.email", "agent@harness.local")
    _run_git("symbolic-ref", "HEAD", "refs/heads/main")


@tool
def _check_args(value:str, what:str) -> str:
    """Rejects empty values and values git would read as options"""
    value = value.strip()

    if not value:
        raise ValueError(f"{what} must not be empty")
    if value.startswith("-"):
        raise ValueError(f"{what} must not start with '-': {value!r}")
    return value


@tool
def git_status() -> str:
    """Show the current working directory, list modified, staged, and untracked files"""
    return _run_git("status")

@tool
def git_commit(commit_message: str) -> str:
    """Stage all current changes and commit them with the given message.
        Returns the commit hash on success, or an error on failure (e.g., nothing to commit).
    """
    _run_git("add", "-A")
    return _run_git("commit", "-m", commit_message)

@tool
def git_diff(path: str = "") -> str:
    """Show unstaged changes in the workspace. Optionally restrict to a single path."""
    args = ["diff"]
    if path:
        args.append(path)

    return _run_git(*args)

@tool
def git_log(limit: int = 10, ref: str = "") -> str:
    """Show recent commit history. Defaults to the last 10 commits."""   
    args = ["log", f"--max-count={limit}", "--oneline"]
    if ref:
        args.append(_check_args(ref, "ref"))
    return _run_git()


@tool
def git_checkout(ref: str) -> str:
    """Switch to a commit or branch. Used for both rollback (to an earlier commit)
    and branch switching (to a sibling branch)."""    
    ref = _check_args(ref, "ref")
    return _run_git("checkout", ref)

@tool
def git_branch(name: str = "") -> str:
    """List branches if called with no argument. Create a new branch if a name is given.
    Does NOT switch to the new branch — call git_checkout afterward to switch."""

    if not name:
        return _run_git("branch")
    
    name = _check_args(name, "name")
    return _run_git("branch", name)