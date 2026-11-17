# {{PROJECT_NAME}} — Learnings digest

The standing rules distilled from the learnings log. **Agents read this instead of the log**
(CLAUDE.md §8). The full log is `docs/learnings/README.md`. Each bullet ends with its source
entry's date, so `grep -n '### <date>' docs/learnings/README.md` finds the detail.

**Maintenance:**
- A learnings entry that adds or changes a standing rule also updates this digest, in the same commit.
- Drop rules that a later entry supersedes.
- Keep it under about 200 lines. If it grows past that, regenerate it from the log with a cheap
  model and review the result.

<!-- Group bullets under short headings as they accumulate, e.g. Testing, UI and accessibility,
Data and migrations, Logging and privacy, Build and lint, Git and commits, Docs and process.
One imperative bullet per rule, naming the files or functions an agent would search for:
- Assert log lines filtered to the app's own logger; the framework writes its own lines [YYYY-MM-DD]
-->
