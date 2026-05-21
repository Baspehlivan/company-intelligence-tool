"""
Invoke OpenClaude headless (-p) for CIT analysis tasks.

Requires OpenClaude installed and provider configured (see .openclaude-profile.json).
API key must be in environment (set via OpenClaude /provider — not committed to git).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INBOX = ROOT / ".openclaude" / "inbox"
TASK_FILE = INBOX / "TASK.md"
DONE_FILE = INBOX / "DONE.md"


class OpenClaudeRunner:
    """Run OpenClaude in print mode from the CIT repo."""

    def __init__(self, cwd: Path | None = None, timeout: int = 300):
        self.cwd = cwd or ROOT
        self.timeout = timeout
        self.binary = shutil.which("openclaude") or "openclaude"

    @property
    def available(self) -> bool:
        return bool(shutil.which("openclaude"))

    def run_prompt(
        self,
        prompt: str,
        *,
        allowed_tools: str = "Read,Bash,Grep,Glob",
        bare: bool = True,
    ) -> str | None:
        """Execute openclaude -p and return stdout text, or None on failure."""
        if not self.available:
            return None

        cmd = [self.binary]
        if bare:
            cmd.append("--bare")
        cmd.extend(["-p", prompt])
        if allowed_tools:
            cmd.extend(["--allowedTools", allowed_tools])

        env = os.environ.copy()
        # Let .openclaude-profile.json in cwd configure provider
        env.pop("CLAUDE_CODE_USE_OPENAI", None)  # profile file takes precedence on launch

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.cwd),
                env=env,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except (subprocess.TimeoutExpired, OSError):
            return None

        out = (proc.stdout or "").strip()
        if proc.returncode != 0 and not out:
            err = (proc.stderr or "").strip()
            if err:
                return None
        return out or None

    def complete(self, system: str, user: str) -> str | None:
        prompt = f"{system}\n\n---\n\n{user}"
        return self.run_prompt(prompt, allowed_tools="", bare=True)

    def complete_json(self, system: str, user: str) -> dict | None:
        from src.analysis.llm import parse_json

        text = self.complete(
            system + "\n\nRespond with valid JSON only — no markdown fences.",
            user,
        )
        if not text:
            return None
        return parse_json(text)


def delegate_task(
    task: str,
    *,
    context: str = "",
    from_cursor: bool = True,
) -> Path:
    """Write a task to OpenClaude inbox for interactive or later pickup."""
    INBOX.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat(timespec="seconds")
    source = "Cursor" if from_cursor else "CLI"

    body = f"""# Task ({ts})

**From:** {source}

## Request

{task.strip()}

"""
    if context:
        body += f"""## Context

{context.strip()}

"""

    body += """## When done

1. Implement the change in `src/analysis/` or `src/data_collector/`
2. Run: `python -m src.analysis "Rhenus" --from-file data/rhenus.json --no-llm --pretty`
3. Append summary to `.openclaude/inbox/DONE.md`
4. Clear the Request section above or mark done

"""

    TASK_FILE.write_text(body, encoding="utf-8")
    return TASK_FILE


def try_headless(task: str) -> tuple[bool, str]:
    """Attempt immediate headless run; return (success, message)."""
    runner = OpenClaudeRunner()
    if not runner.available:
        return False, "openclaude not found in PATH (npm install -g @gitlawb/openclaude)"

    out = runner.run_prompt(
        f"You are working on the CIT repo at {ROOT}. {task}\n"
        "Reply with a concise summary of what you would change (no tools if --bare blocks them).",
        allowed_tools="Read,Bash",
        bare=False,
    )
    if out:
        return True, out
    return False, (
        "Headless call failed. Open OpenClaude in this repo and read "
        f"{TASK_FILE.relative_to(ROOT)}"
    )
