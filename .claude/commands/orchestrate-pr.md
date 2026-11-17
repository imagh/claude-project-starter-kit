---
description: Build the next PR of a plan by delegation, review it, and open the PR (one PR per session)
---

You orchestrate **one** PR of an approved plan: delegate the build, review it, verify, and open the
PR. Then stop: **one PR per session** (CLAUDE.md §8), so no context is carried into the next PR.
Arguments: the PR id from the plan's PR table, plus anything the user adds. If none is given, take
the first unmerged PR in the table.

## 1. Orient (cheaply)
- `git fetch origin`. Read the plan **by section**: its PR table, this PR's steps, the decisions
  they cite, and the open-question answers (`grep -n`, then offset/limit).
- State comes from git, not memory. Use `gh pr list --state all --base <base>` and
  `git worktree list`. There must be no open PR for this step and no stray worktree.
- Apply the PR's **tier** (CLAUDE.md §8). It picks the developer's and reviewer's model and effort.
  If the tier wants a premium session and this one isn't, say so before starting. For **T0**, do
  the work yourself and skip to step 4.

## 2. Delegate the build
- Create a worktree for the PR branch off its target branch. Never commit in the shared checkout.
- Spawn **one** `senior-full-stack-dev` with the tier's `model` and `effort`. Brief it with only:
  - the worktree path;
  - the plan step and decision **section names**;
  - decisions the plan doesn't record;
  - this PR's traps;
  - what to stop and ask about.

  Its agent file already carries the reading budget, evidence rules and self-review list, so
  don't repeat them.
- If it stops on a usage limit, wait for the reset, then check `git status` and `git diff` in its
  worktree, and resume **the same agent** with the exact state.

## 3. Review
- Use the reviewer the tier names. When you review it yourself, read the diff and tests against
  the plan, go through every item in `code-reviewer.md`'s "Findings that recur", and **check the
  code, not the report**.
- Send fixes to **the same agent** (`SendMessage`), as numbered blocker, should-fix and nit items,
  each saying exactly what to change. If the same item is missed twice, escalate the step (§8).
- When a finding is new and likely to recur, add it to the self-review list in
  `senior-full-stack-dev.md` and to the reviewer's list, in this PR or the next.

## 4. Verify, then ask
- Run the full suite (in the background if it is slow), so every test really runs. Read the counts
  from the test reports.
- Report to the user:
  - what was built;
  - the findings and how each was resolved;
  - the counts;
  - the proposed commit split.

  **Ask before committing.**

## 5. On the user's go-ahead
- Make small, atomic commits, each green on its own. Check the middle commits in a temporary
  worktree.
- Push, and open the PR with `.github/pull_request_template.md`, with every box ticked or
  explained. **Never merge.**
- Tell the user the PR link and **end the session**. Name the next PR, its tier, and the model to
  start the next session on.

## After the user merges
Remove the PR's worktree and local branch, after confirming nothing is uncommitted or unpushed.

$ARGUMENTS
