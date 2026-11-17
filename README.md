# Claude Project Starter Kit

**Version 1.1.0**: adds the usage budget, per-PR model tiers, `/orchestrate-pr`, the learnings
digest and the usage guard hook. See *Usage budget and model tiers* below.

A portable, opinionated setup that gives **any repo** a rigorous engineering workflow that
Claude Code (and humans) follow automatically — a **development constitution** plus three
**role sub-agents** that enforce it.

It packages the workflow proven on a real project into reusable **templates with
`{{PLACEHOLDERS}}`**. You point a Claude Code session at [`SETUP.md`](SETUP.md); it interviews
you for your project's specifics, fills the placeholders, drops the files into your repo, and
wires up the guardrails.

## What it gives your repo

- **A development constitution** (`CLAUDE.md`) — the non-negotiable rules for *how* code is
  built, loaded into every Claude Code session automatically:
  - **Strict TDD** (Red → Green → Refactor; meaningful tests; a coverage floor).
  - **Mandatory documentation** across defined surfaces (inline, module READMEs, feature
    docs, architecture, learnings).
  - **Security built in** (secrets hygiene, protected paths, untrusted-input validation,
    parameterised queries, dependency vetting).
  - **A modular architecture** with a layered flow and an explicit **abstraction bar**
    (interfaces only at real swap boundaries — no gratuitous indirection).
  - **Small, atomic commits & small, incremental PRs**, with a base-feature-branch model for
    larger work.
  - **A cost-aware model policy with per-PR tiers**: the plan gives each PR a tier (T0
    mechanical to T3 high-risk), which picks the developer's and reviewer's model and effort
    and the model to start the session on.
  - **A usage budget**:
    - agents read narrowly, using a learnings digest and docs read by section;
    - developers self-review against past findings before handing back;
    - mutation evidence scales with risk;
    - each session runs one PR.
- **Three role agents** (`.claude/agents/`): **architect** (plans), **senior-full-stack-dev**
  (implements under TDD), **code-reviewer** (verifies the diff + the rules). Plan → build →
  review, bracketed so quality holds while cost drops.
- **Scaffolding**:
  - a dated plan template, with a Tier column in the PR breakdown;
  - a PR template;
  - a `.claude/settings.json` guardrail set (deny secret/protected paths; block agent merges);
  - a pre-commit config template.
- **A usage guard** (`tools/agent/guard.py`, a tested PreToolUse hook). It refuses whole reads of
  big files, and foreground runs of the commands you list as slow or hang-prone.
- **`/orchestrate-pr`**: runs one PR end to end. It delegates the build at the PR's tier,
  reviews the result, verifies, opens the PR, and ends the session.

## Usage / setup

**1. Get the kit's files into your target repo's root.** Any of:

```bash
# a) degit (no git history) — recommended
npx degit imagh/claude-project-starter-kit .starter-kit && cp -R .starter-kit/. . && rm -rf .starter-kit

# b) clone then copy the contents in
git clone https://github.com/imagh/claude-project-starter-kit /tmp/cpsk
cp -R /tmp/cpsk/. .        # copies CLAUDE.md, .claude/, docs/, .github/, .pre-commit-config.yaml, etc.

# c) download the v1.0.0 archive from the Releases page and unzip into the repo root
```

Copy everything **except** `README.md` and `SETUP.md` into the target — those two describe the
kit, not your project. (`SETUP.md` is worth keeping open during setup; delete it after.)

**2. Instantiate it — open Claude Code in the repo and say:**

> "Instantiate the starter kit — follow `SETUP.md` and interview me."

**3. Answer the interview.** Claude Code reads [`SETUP.md`](SETUP.md) and runs it as an
**interview** — inventorying your repo, then **asking you** (with options + a recommended
default) how to adapt the opinionated defaults to your project's structure, stack, and
conventions — before it fills every `{{PLACEHOLDER}}`, removes the guidance blocks, wires the
guardrails, creates the doc dirs, and verifies. It won't silently impose the defaults, and it
merges with (never clobbers) anything you already have.

**4. Verify & commit.** It checks no placeholders remain, the agents/commands load, and
smoke-tests `/architect`, then shows you the diff. Land it as its own small commit
(`chore: adopt development constitution + role agents`).

**5. Use it.** `/architect <task>` → plan · `/dev <plan/task>` → build under TDD, then
auto-review · `/review-changes` → review the current diff. (If a slash command isn't available
in your Claude Code version, invoke the agent by name — e.g. "use the architect subagent".)

> **Note:** this is a guided adaptation, not a blind drop-in — expect the short interview above,
> especially on an existing repo. See [`SETUP.md`](SETUP.md) for the full step-by-step and the
> placeholder reference.

## Files

```
CLAUDE.md                          # the development constitution (templatized)
SETUP.md                           # instantiation guide + placeholder reference + init interview
.claude/
  agents/
    architect.md                   # plans (model: inherit, effort: xhigh)
    senior-full-stack-dev.md       # implements under TDD (model: sonnet, effort: xhigh)
    code-reviewer.md               # reviews the diff + the constitution (model: inherit, effort: xhigh)
  commands/                        # slash commands that invoke the agents (agents alone don't make one)
    architect.md                   # /architect      → forks to the architect subagent
    dev.md                         # /dev            → runs senior-full-stack-dev, then auto code-reviewer
    review-changes.md              # /review-changes → forks to the code-reviewer subagent
    orchestrate-pr.md              # /orchestrate-pr → one PR end to end at its tier, then end the session
  settings.json                    # guardrails: deny secret/protected paths; block `gh pr merge`; usage-guard hook
docs/
  plans/_TEMPLATE.md               # dated per-task plan template (incl. incremental PR breakdown + tiers)
  learnings/README.md              # the learnings log
  learnings/DIGEST.md              # the standing rules agents read instead of the log
tools/
  agent/guard.py, guard.json       # PreToolUse usage guard + its config (tested: test_guard.py)
.github/
  pull_request_template.md         # PR checklist mirroring the constitution
.pre-commit-config.yaml            # local gates: secret scan + lint/format (commit), tests + guard tests (push)
```

## Usage budget and model tiers

These come from measuring a real project on a Claude Pro plan, where sessions kept hitting usage
limits. **Most of a PR's usage was reading, then re-sending what was read**:
- **Re-sent context:** every tool call re-sends the agent's whole context. A developer that had read
  about 125k tokens of docs used about 290k tokens to build one PR, and about 320k more for a fix
  round of only 20 calls.
- **Repeated findings:** most review findings repeated earlier PRs' findings.
- **Lost rules:** rules pasted into briefs reached agents only when someone remembered to paste them.

What the kit does about it:
- **Rules live where Claude Code loads them by itself**, never only in a brief:
  - `CLAUDE.md` for every session;
  - each agent's file, which is its system prompt;
  - commands;
  - hooks for the rules that must not be forgotten.

  Agent files, commands and hooks load from the **session's** checkout, so they must be on the
  branch sessions start from.
- **Read narrowly.** `docs/learnings/DIGEST.md` keeps the standing rules short. Large docs are
  read by section. `guard.py` refuses whole reads over 48 KB.
- **Get the first hand-back clean.** The developer's agent file carries a self-review list built
  from past review findings. Grow it whenever a finding repeats.
- **Scale evidence to risk.** Mutation evidence is required for tests that guard validation,
  semantics, ordering, concurrency, persistence or logging, not for plain wiring.
- **Tiers.** The architect tiers each PR (T0–T3), and the tier picks the models. A diff touching
  risky paths bumps a tier; a Sonnet developer that misses the same item twice is escalated.
- **One session per PR** (`/orchestrate-pr`), so no context is carried between PRs.

## Design notes

- **The rules are generic; you make them specific.** Roles, TDD, docs, security, the
  abstraction bar, commit/PR sizing, and the model policy are universal. Your **project name,
  tech stack, module names, domain invariants, test commands, and coverage floor** are
  placeholders you fill at setup.
- **Adapt, don't fight it.** Some rules (e.g. a domain-safety invariant) are examples to
  rewrite for your domain, or delete. SETUP.md flags every such point.
- **Greenfield *or* existing repo.** The process discipline (TDD, docs, security, sizing,
  workflow, model policy) is universal and fits any codebase as-is. The architecture is an
  **opinionated default** (a layered modular monolith) you **adapt** at setup — SETUP.md's
  *Greenfield vs. existing project* step inventories an existing repo's real structure/stack/
  conventions and adapts the constitution to them (merging with, never clobbering, any existing
  `CLAUDE.md`/config). So it works on arbitrary layouts — but it is not a no-op drop-in for an
  existing repo; expect a short adaptation pass, not a blind copy.
- **Provenance.** This kit generalizes a working setup; nothing in it is tied to the origin
  project once the placeholders are filled.

## License

MIT — see [`LICENSE`](LICENSE). Use it, fork it, adapt it freely.
