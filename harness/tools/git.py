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
def git_status() -> str:
    """SHow the current working directory, list modified, staged, and untracked files"""
    return _run_git("status")