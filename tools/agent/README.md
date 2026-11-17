# tools/agent

## Purpose
Keeps Claude Code sessions and agents within a usage budget (CLAUDE.md §8). It enforces the two
habits that cost the most when forgotten: reading big files whole, and running long commands in
the foreground.

## Responsibilities & boundaries
`guard.py` is a PreToolUse hook, wired in `.claude/settings.json` for `Read` and `Bash`. It refuses:
- a whole Read of a text file over `max_whole_read_bytes` (the default is 48 KB). The agent reads by section instead, or reads `docs/learnings/DIGEST.md` in place of the learnings log;
- a Bash command segment matching a `background_only` pattern unless it is backgrounded (a trailing lone `&`, or `run_in_background`).

Exit code 2 blocks the call and shows the reason to the agent. It is a usage guard, not a security control: bad input or a broken config **fails open**. Not part of any build, not shipped.

## Public interface
- The Claude Code hook contract: the tool call as JSON on stdin; exit 2 with the reason on stderr, or 0.
- `guard.json`:

  | Key | Meaning |
  |---|---|
  | `max_whole_read_bytes` | Biggest text file that may be read whole. |
  | `exempt_suffixes` | Suffixes that may always be read whole (images, PDFs). |
  | `background_only` | Regexes (Python `re.search`) for commands that must run in the background. |
  | `background_hint` | Appended to the refusal, e.g. the name of your retry script. |

## Data it owns
None.

## Configuration
`guard.json`: static values, so a checked-in file. SETUP.md fills `background_only` with the project's slow or hang-prone commands. Examples:
- `"\\bpytest\\b"`
- `"\\bnpm (run )?test\\b"`
- `"gradlew\\b.*\\b(check|test)\\b"`
- `"\\bcargo test\\b"`

## Dependencies
Python 3.9+ standard library.

## How to run & test
`python3 -I -m unittest discover -s tools/agent`. This also runs in the pre-push hook (`tests-agent-guard`).

To try the hook by hand:
`echo '{"tool_name":"Bash","tool_input":{"command":"pytest"}}' | python3 -I tools/agent/guard.py; echo $?`
