# Setup guide — instantiate this kit in a repo

This guide is written for a **Claude Code session** (a human can follow it too). Read it top
to bottom and execute it in the **target repository**. Goal: drop the kit's files in, replace
every `{{PLACEHOLDER}}` with real values gathered from the user, remove the guidance blocks,
and wire up the guardrails — leaving a repo whose every Claude Code session is governed by the
constitution and served by the three role agents.

> **Convention.** Placeholders look like `{{THIS}}`. Guidance meant only for setup (not for the
> final files) is wrapped in `<!-- SETUP: ... -->` HTML comments — **delete those comments**
> once you've acted on them, so the shipped `CLAUDE.md` and agents read cleanly.

> **Ask, don't assume — run this as an interview (Claude Code).** This is a collaborative
> setup, not an autopilot. At **every fill-in and every adaptation fork**, ask the user with
> `AskUserQuestion`: state the decision, offer 2–4 concrete options with a **recommended
> default** (mark it), and let **the user's choice win** — never silently impose the kit's
> defaults, especially on an existing repo. Batch related questions (don't fire one at a time),
> propose the sensible default so it's one tap, and only proceed on a default when you've
> inventoried the repo and the answer is unambiguous (e.g. the language is obvious from the
> files). If the user picks "just use good defaults", say which defaults you applied. When you
> finish, show the user the diff of what you changed before committing.

---

## Step 0 — Confirm scope, then copy the files in

1. Confirm with the user that you're setting the kit up in **this** repo (print the repo root).
2. Copy the kit's files to the repo root, preserving structure — `CLAUDE.md`, `.claude/agents/*`,
   `.claude/commands/*`, `.claude/settings.json`, `docs/plans/_TEMPLATE.md`,
   `docs/architecture/code-structure.md`, `docs/learnings/README.md`,
   `.github/pull_request_template.md`, `.pre-commit-config.yaml`. **Do not copy `README.md` or
   this `SETUP.md`** into the target
   (they describe the kit, not the project) unless the user wants them kept under `docs/`.
3. If the repo already has any of these files, **do not clobber** — show the diff and merge
   deliberately with the user (especially an existing `CLAUDE.md`, `settings.json`, or
   `pre-commit` config).

## Step 1 — Run the init interview

Gather the values below from the user (use `AskUserQuestion` for the forks; propose sensible
defaults, don't interrogate). Everything here maps to a placeholder in Step 2.

- **Project** — name, a one-line tagline, and a 2–4 sentence description of what it is and who
  it's for.
- **Tech stack** — primary language(+version), backend framework, frontend stack (or "none"),
  database, other infra (queue/cache/vector store/etc.), test framework(s).
- **Repo layout** — where source modules live (`src/`, `apps/`, …) and where shared packages go.
- **Modules** — 3–6 example feature-module names for the project's domain.
- **Quality bar** — coverage floor (default **90**), lint/format tool, the run/test commands.
- **Domain safety invariants** — any non-negotiable, hardcoded correctness/safety rules the
  domain demands (e.g. for fintech: risk limits & audit trails; for healthcare: PII handling).
  If none, say so and you'll trim that rule (see Step 3).
- **Review/merge humans** — who approves and merges PRs.
- **Model policy** — keep the default (premium model plans+reviews, Sonnet builds, all `xhigh`)
  unless the user wants a change.

## Step 1.5 — Greenfield vs. existing project (adapt, don't impose)

This kit is **opinionated**. Two layers, treated differently:

- **Universal — adopt as-is (fits any codebase):** the process discipline — TDD, the
  documentation surfaces, security (Rule C), the abstraction bar, small atomic commits & small
  incremental PRs, the plan → build → review workflow, and the model policy. These do not
  depend on the project's structure.
- **Opinionated default — ADAPT to the project:** the concrete architecture (§3.1 layer
  names/module-vs-service organisation, §3.6 transport), the tech-stack table (§2), the doc
  taxonomy/paths (§5), and `{{REPO_LAYOUT}}`. These describe a layered modular monolith by
  default; make them match the project's real architecture.

### If the repo is greenfield
Adopt the defaults, fill the placeholders (Step 2), and you're done.

### If the repo already exists (has structure/stack/conventions)
Do **not** impose the default architecture on top of what's there. Instead:
1. **Inventory first.** Read the repo's real structure, language(s), test setup, build/hook
   tooling, and any existing `CLAUDE.md`, `AGENTS.md`, `README`, or documented conventions.
   Fill the placeholders with **what is already true** — do not invent a new layout.
2. **Adapt the opinionated rules to match.** Rewrite §3.1's layer names/organisation to the
   project's real architecture (MVC, hexagonal, Django/Rails apps, services, a library, a
   frontend app, a CLI — whatever it is), set `{{REPO_LAYOUT}}` and `{{PACKAGE_ROOT}}` to the
   actual paths, point §5's taxonomy at the repo's existing `docs/` layout, and mark N/A any
   rule that doesn't apply (e.g. §3.6 transport for a single app, or the DB-centric
   integration-test example for a project with no datastore). Keep every **principle**; change
   only the **shapes**.
3. **Reconcile, never clobber.** If the repo already has a `CLAUDE.md`, `.claude/settings.json`,
   a pre-commit/hook config, a PR template, or docs, **merge** with the user's sign-off and show
   the diff — don't overwrite. Keep the project's existing test framework, run commands, and
   lint/format tooling (fill the placeholders with those, don't swap them).
4. **Get explicit sign-off** on anything that changes an established convention before writing.

Notes:
- **Git hooks:** the kit uses `pre-commit`. If the ecosystem uses a different runner (husky,
  lefthook, …), adapt `.pre-commit-config.yaml` to that tool — keep the **intent**: a secret
  scan + lint/format on commit, and the test suite on push.
- **Agent name:** `senior-full-stack-dev` is just a role name. If "full-stack" doesn't fit
  (e.g. a backend-only or frontend-only repo), rename the agent — the file, its `name:` field,
  and the `agent:` line in `.claude/commands/dev.md` must all match.

### Decisions to put to the user (ask each with `AskUserQuestion`)

Don't decide these for the user — surface each as a question with options + a recommended
default, then apply their answer. After inventorying the repo, ask (batched):

- **Architecture (§3.1).** "Your repo looks like `<observed layout>`. How should the constitution
  describe its architecture?" — options e.g. *(a) layered modular monolith (the kit default),
  (b) keep my existing layout & layer names: `<observed>` (recommended for an existing repo),
  (c) services / (d) library / (e) frontend app / (f) other — describe.* Rewrite §3.1 to the
  choice.
- **Layer names & flow.** If they keep a layered style: "Confirm your layer names and the
  one-directional flow" (e.g. `controller→service→dao→db`, or `route→handler→repo`, or MVC).
- **Rules that may not apply.** Ask to **keep / mark N/A / delete** each of: §3.6 transport
  (N/A for a single deployable), the §3.8 domain-safety rule (keep→rewrite for their domain,
  or delete), and the DB-centric integration-test example if there's no datastore.
- **Doc taxonomy (§5).** "Adopt `docs/{plans,features,architecture,learnings,product,roadmap}/`
  as-is, or map onto your existing docs layout at `<observed>`?"
- **Coverage floor & test framework.** "Coverage floor — keep 90%, or set another?" and confirm
  the detected `{{TEST_FRAMEWORK}}` / run commands rather than assuming.
- **Model policy (§8).** "Keep the default split (premium plans+reviews, Sonnet builds, all
  `xhigh`), or change it?"
- **Existing-file conflicts.** For each of an existing `CLAUDE.md` / `settings.json` / hook
  config / PR template: "You already have `<file>` — merge the kit into it, keep yours, or
  replace it?" (default: merge; show the diff).
- **Git-hook runner & agent name** (the two notes above) — ask only if the inventory suggests a
  mismatch (non-`pre-commit` ecosystem; backend/frontend-only repo).

## Step 2 — Placeholder reference (fill every one)

Replace across `CLAUDE.md` and the three agent files. Grep the tree for `{{` afterward to
prove none remain.

| Placeholder | Meaning | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | Project / product name | `NEXUS` |
| `{{PROJECT_TAGLINE}}` | One line: what it is | `AI-enabled geopolitical trading intelligence` |
| `{{PROJECT_DESCRIPTION}}` | 2–4 sentences: what/why/who | *(paragraph)* |
| `{{PROJECT_PHASING}}` | How the build is staged, if at all (phases/milestones) — or "N/A" | `six progressive phases; currently Phase 1` |
| `{{PRIMARY_LANGUAGE}}` | Backend language + version | `Python 3.11+` |
| `{{BACKEND_FRAMEWORK}}` | API/service framework | `FastAPI` |
| `{{FRONTEND_STACK}}` | Frontend stack, or `N/A` | `React + TypeScript + Tailwind` |
| `{{DATABASE}}` | Primary datastore | `PostgreSQL (+ TimescaleDB)` |
| `{{OTHER_INFRA}}` | Queue/cache/vector/etc., or `N/A` | `Celery + Redis` |
| `{{PACKAGING_INFRA}}` | Packaging / local infra, or `N/A` | `Docker + Docker Compose (local)` |
| `{{TEST_FRAMEWORK}}` | Test tooling | `pytest` (+ `Vitest` for FE) |
| `{{COVERAGE_FLOOR}}` | Min line coverage % | `90` |
| `{{LINT_FORMAT_TOOL}}` | Linter/formatter | `ruff` |
| `{{PACKAGE_MANAGER}}` | Dep/vuln tooling | `uv` / `pip-audit` |
| `{{REPO_LAYOUT}}` | Where modules live | `src/<module>/` or `apps/<app>/src/...` |
| `{{PACKAGE_ROOT}}` | Where shared packages live | `packages/` |
| `{{MODULE_EXAMPLES}}` | Domain module names | `ingestion, intelligence, execution` |
| `{{DOMAIN_SAFETY_RULE}}` | The domain's hardcoded invariants (§3) — or remove per Step 3 | `risk controls & 5-yr audit` |
| `{{REVIEW_HUMANS}}` | Who reviews/merges PRs | `Akash / Tandrima` |
| `{{SESSION_MODEL_NOTE}}` | Premium model the session runs (or leave "the session model") | `Opus-tier` |

## Step 3 — Adapt the domain-specific rule

The constitution's architecture section carries one **domain-safety** rule (marked with a
`<!-- SETUP: domain-safety -->` comment). Do one of:
- **Rewrite** it for the project's real invariants (what must be hardcoded and never bypassed,
  and what must be audited), or
- **Delete** the rule and its Definition-of-Done checkbox if the domain has no such invariant.

Everything else in the constitution is universal — keep it.

## Step 4 — Wire the guardrails

1. **`.claude/settings.json`** — this ships with a `permissions.deny` list that blocks the agent
   from reading/writing secret & protected paths (`.env*`, `secrets/`, keys/certs, `.git/`) and
   from running `gh pr merge` (agents open PRs, humans merge). Merge it with any existing
   `settings.json`; keep the deny entries. Adjust the protected globs to the repo's real secret
   locations.
2. **Pre-commit** — the `.pre-commit-config.yaml` template runs a secret scan + lint/format on
   commit and the test suite on push. Replace the placeholder lint/test hooks with the project's
   real tools, then: `pre-commit install && pre-commit install --hook-type pre-push`.
3. **PR template** — `.github/pull_request_template.md` mirrors the constitution's checklist.
4. **Branch protection** (optional, GitHub) — require ≥1 approving review on the default branch
   so the "humans merge, not agents" rule is enforced server-side too. Note it in the repo's
   own README.
5. **Create the doc dirs** referenced by the constitution's taxonomy (§5): `docs/plans/` (keep
   `_TEMPLATE.md`), `docs/features/`, `docs/architecture/` (with `code-structure.md`),
   `docs/learnings/` (with `README.md`), plus `docs/product/` (the spec/PRD, if any) and
   `docs/roadmap/` (only if the build is staged). Remove the `docs/product/` and `docs/roadmap/`
   links at the top of `CLAUDE.md` if those don't apply to this project.

## Step 5 — Verify

- **No placeholders left in any copied file:**
  `grep -rn "{{" CLAUDE.md .claude/ docs/ .github/ .pre-commit-config.yaml` returns nothing.
- **No setup comments left:** `grep -rn "SETUP:" CLAUDE.md .claude/ docs/ .github/` returns
  nothing.
- **Agents load:** the three agents appear in Claude Code's agent list with the right
  `model`/`effort` (architect & code-reviewer `inherit`/`xhigh`; senior-full-stack-dev
  `sonnet`/`xhigh`).
- **Commands load:** `/architect`, `/dev`, and `/review-changes` appear in the slash-command
  list (they come from `.claude/commands/`, not from the agents).
- **Smoke test the loop:** run `/architect` on a tiny first task and confirm it writes a plan to
  `docs/plans/` following `_TEMPLATE.md` (including the PR-breakdown section).

## Step 6 — Commit it

Land the kit as its **own small, single-purpose commit/PR** (practicing the constitution):
"chore: adopt development constitution + role agents". Nothing else in that PR.

---

### The role agents (how they're used after setup)

- **`/architect`** → produces a TDD-ordered plan in `docs/plans/` with an incremental PR
  breakdown. Runs on the session model at `xhigh`.
- **`/dev`** (or the `senior-full-stack-dev` agent) → implements a plan step-by-step under
  strict TDD, then the **`code-reviewer`** fires automatically. Dev runs on Sonnet `xhigh`;
  reviewer on the session model `xhigh`.
- **`/review-changes`** → run the reviewer manually on the current diff.

The model split (premium plans/reviews, Sonnet builds) is documented in `CLAUDE.md §8` and
pinned in each agent's frontmatter. A user's explicit model choice always wins.

> **Agents ≠ slash commands.** An `.claude/agents/<name>.md` file does **not** by itself create
> a `/<name>` command — they're separate mechanisms. The kit ships **both**: the agents (the
> roles) *and* the `.claude/commands/*.md` files that wire `/architect`, `/dev`, and
> `/review-changes` to them. Copy both. If a command frontmatter field used here isn't
> supported by the installed Claude Code version, the fallback always works — invoke the agent
> by name (e.g. "use the `architect` subagent to plan X").
