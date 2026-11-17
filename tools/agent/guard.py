"""A Claude Code PreToolUse hook that keeps sessions and agents within a usage budget (CLAUDE.md §8).

It refuses two kinds of tool call, and tells the agent what to do instead:

- **A whole Read of a big text file** (over `max_whole_read_bytes` with no offset or limit). A large log,
  plan or README costs tens of thousands of tokens, and every later call re-sends it. Read the lines you
  need (find them with `grep -n`), or read `docs/learnings/DIGEST.md` instead of the learnings log.
  Files with an `exempt_suffixes` suffix (images, PDFs) are allowed.
- **A long-running command in the foreground** (any `background_only` regex matching a command segment
  that is not backgrounded with a lone `&`). Slow or hang-prone test suites belong in the background,
  with the log polled.

Configuration is `guard.json` beside this file (SETUP.md fills `background_only` per project). Wiring:
`.claude/settings.json` runs `python3 -I "$CLAUDE_PROJECT_DIR/tools/agent/guard.py"` for Read and Bash.
The hook reads the tool call as JSON on stdin; exit code 2 blocks the call and shows stderr to the agent,
0 allows it. This is a usage guard, not a security control, so unreadable input or a broken config
**fails open**: a bug here must never block every tool call. Python 3.9+, standard library only.
"""
import json
import re
import sys
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path(__file__).resolve().parent / "guard.json"

DEFAULTS = {
    "max_whole_read_bytes": 48000,
    "exempt_suffixes": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"],
    "background_only": [],
    "background_hint": "",
}

SEGMENT = re.compile(r"((?:[<>]&|&>|[^;&|\n])+)(&&|\|\||&|;|\||\n|$)")
"""One command segment (redirections such as `2>&1` included) and the operator that ends it; a lone `&`
backgrounds the segment."""

READ_MESSAGE = (
    "{name} is {kb} KB, too big to read whole (usage budget, CLAUDE.md §8). Find the lines you need with "
    "`grep -n`, then Read with offset/limit. For the learnings log, read docs/learnings/DIGEST.md instead."
)

BASH_MESSAGE = (
    "This command is long-running: run it in the background, never in the foreground (usage budget, "
    "CLAUDE.md §8). Use run_in_background, or `<command> > <log> 2>&1 &` and poll the log. {hint}"
)


def load_config(path: Path = CONFIG_PATH) -> dict:
    """`guard.json` over the defaults; the defaults alone if the file is missing or broken."""
    try:
        loaded = json.loads(path.read_text())
    except (OSError, ValueError):
        return dict(DEFAULTS)
    if not isinstance(loaded, dict):
        return dict(DEFAULTS)
    return dict(DEFAULTS, **loaded)


def decide(payload, config: dict) -> Optional[str]:
    """Why this tool call is refused, or None to allow it. Never raises on odd input."""
    if not isinstance(payload, dict) or not isinstance(payload.get("tool_input"), dict):
        return None
    tool_input = payload["tool_input"]
    if payload.get("tool_name") == "Read":
        return _whole_read_of_big_file(tool_input, config)
    if payload.get("tool_name") == "Bash":
        return _foreground_long_command(tool_input, config)
    return None


def _whole_read_of_big_file(tool_input: dict, config: dict) -> Optional[str]:
    path = tool_input.get("file_path")
    if not isinstance(path, str) or "offset" in tool_input or "limit" in tool_input:
        return None
    file = Path(path)
    exempt = {suffix.lower() for suffix in config["exempt_suffixes"]}
    if file.suffix.lower() in exempt or not file.is_file():
        return None
    size = file.stat().st_size
    if size <= config["max_whole_read_bytes"]:
        return None
    return READ_MESSAGE.format(name=file.name, kb=size // 1000)


def _foreground_long_command(tool_input: dict, config: dict) -> Optional[str]:
    command = tool_input.get("command")
    patterns = config["background_only"]
    if not isinstance(command, str) or not patterns or tool_input.get("run_in_background") is True:
        return None
    for match in SEGMENT.finditer(command):
        backgrounded = match.group(2) == "&"
        if not backgrounded and any(re.search(pattern, match.group(1)) for pattern in patterns):
            return BASH_MESSAGE.format(hint=config["background_hint"]).strip()
    return None


def main(stdin=sys.stdin, stderr=sys.stderr, config: Optional[dict] = None) -> int:
    """Hook entry point: 2 (with the reason on stderr) blocks the call, 0 allows it."""
    try:
        payload = json.load(stdin)
    except ValueError:
        return 0
    reason = decide(payload, config if config is not None else load_config())
    if reason is None:
        return 0
    stderr.write(reason + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
