# {{PROJECT_NAME}} — Development Constitution

This file is the source of truth for **how** we build {{PROJECT_NAME}}. It is loaded into
every Claude Code session. Read it before writing code, planning, or reviewing. Rules here
are non-negotiable unless the user explicitly overrides them for a task.

<!-- SETUP: point these two links at the project's real product spec and roadmap, or remove
     any that don't exist yet. -->
Product spec lives in `docs/product/{{PROJECT_NAME}}.md`.
Phase-by-phase build plan lives in `docs/roadmap/`.

---

## 1. What we are building

{{PROJECT_NAME}} is {{PROJECT_TAGLINE}}. {{PROJECT_DESCRIPTION}}
<!-- SETUP: if the build is staged, describe it; else delete this sentence. -->
It is built as {{PROJECT_PHASING}}.

## 2. Tech stack

| Concern            | Choice                     |
|--------------------|----------------------------|
| Language (backend) | {{PRIMARY_LANGUAGE}}       |
| API layer          | {{BACKEND_FRAMEWORK}}      |
| Database           | {{DATABASE}}               |
| Other infra        | {{OTHER_INFRA}}            |
| Frontend           | {{FRONTEND_STACK}}         |
| Packaging / infra  | {{PACKAGING_INFRA}}       |
| Testing            | {{TEST_FRAMEWORK}}         |

Do not introduce a new framework, database, or heavy dependency without an architect plan
that justifies it against these defaults.

## 3. Architecture rules (cross-cutting)

> **Universal vs. project-specific.** The *principles* in this section are universal and hold
> for any codebase: clear module boundaries with no cross-layer reaching, one canonical schema
> at boundaries, shared code in packages (never copied), config-by-variability, observability,
> and simplicity over abstraction. The *concrete shapes* — the exact layer names, whether it's
> a monolith or services, the transport, the packaging — are a **default (a layered modular
> monolith) that you adapt at setup to this project's real architecture**. Rules marked
> "adapt" below were reconciled with the existing structure during setup; keep the principle,
> match the shape to the repo.

1. **Modular, layered architecture.**
   <!-- SETUP: adapt — describe THIS project's real architecture and layer names. The default
        below is a layered modular monolith; if the project is services, a library, a frontend
        app, a CLI, or uses different layer names (MVC, hexagonal, Django apps, …), rewrite this
        to match — but keep the two principles: modules organised by feature with clear
        ownership, and a one-directional layer flow where a layer calls only the one below it. -->
   Default: one repo, one deployable, organised by **feature module** (e.g. {{MODULE_EXAMPLES}}),
   not by technical layer. Each module owns its models, services, adapters, API, and tests.
   **Within** a module, code flows through explicit layers — **controller/handler → service →
   dao → db** — each calling only the layer directly below. Business logic lives in the service
   layer; controllers/handlers do I/O and validation only; daos do persistence only. No
   controller reaches into a dao, no data-access in a service, no business logic in a dao.
2. **Abstraction first (at service boundaries).** Every external dependency (data source,
   third-party API, provider, model, broker) sits behind an abstract interface. Swapping a
   provider must require only a new implementation class — never a change to core logic.
3. **One canonical internal schema.** Data crossing a module boundary is normalised to a
   shared, versioned schema before entering the pipeline — not passed around in raw
   source-specific shapes.
4. **Shared code lives in packages, not copies.** Common helpers, utilities, and cross-cutting
   functions are never copy-pasted between modules. They live in versioned, reusable packages
   under `{{PACKAGE_ROOT}}`. The moment a helper is needed by a second module, promote it to a
   shared package rather than duplicating it.
5. **Configuration-driven — env or DB by variability.** Thresholds, params, and limits are
   never hardcoded. Choose the store by how the value varies: **static, environment-specific,
   or secret → env config** (typed settings); **runtime-varying, per-user, or operationally
   tuned → the database** (with an audit trail on change). Pick deliberately and document it
   in the module README.
6. **Typed, schema-first service-to-service transport.**
   <!-- SETUP: adapt — applies only to systems with multiple internal services / high-fan-out
        internal paths. For a single app, a library, a CLI, or a frontend, mark this N/A. -->
   When services communicate on high-volume or high-fan-out internal paths, use a **defined,
   versioned schema and an efficient wire format** (e.g. Protobuf/Avro over gRPC), not ad-hoc
   JSON-over-HTTP. Plain REST/JSON stays fine for the external/browser-facing API. (N/A for a
   single-deployable project.)
7. **Observability from day one.** Every component emits structured (JSON) logs; every
   significant operation is recorded and auditable from logs alone.
8. **Domain safety & correctness invariants.**
   <!-- SETUP: domain-safety — rewrite this for the project's real invariants, or DELETE this
        rule (and its Definition-of-Done checkbox in §7) if the domain has none. -->
   {{DOMAIN_SAFETY_RULE}} These invariants are **hardcoded and cannot be disabled by config or
   by model output**; every action that touches them is written to an immutable audit trail.
9. **Simplicity over abstraction — do not over-engineer.** The default is simple, clean,
   readable, concrete code. Modular and extensible, but never abstraction hell.

### The abstraction bar (read this before adding an interface)

Abstraction earns its place at **service boundaries we genuinely swap** — external providers,
data sources, models, brokers. That is where interfaces are mandatory.

Everywhere else, prefer the concrete thing:

- **Do not** add an interface/abstract base/factory/wrapper for a class, function, or module
  that has exactly one implementation and no imminent second one on the roadmap.
- **YAGNI.** Build for the requirement in front of you, not a hypothetical future. Introduce
  indirection when the second implementation actually arrives, not before.
- **No premature optimisation.** Write the clear version first; optimise only what a
  measurement shows is too slow.
- Plain functions and concrete classes beat layers of indirection. A reader should follow a
  call path without chasing through five abstractions.

Both the architect (in plans) and the developer (in code) apply this bar. Any added
abstraction must justify itself against this rule.

## 4. The three non-negotiable process rules

### Rule A — TDD is mandatory
No production code is written before a failing test that specifies it. Follow
**Red → Green → Refactor**:

1. **Red** — write the smallest test that expresses the next behaviour; run it; watch it fail
   for the right reason.
2. **Green** — write the minimum code to make it pass.
3. **Refactor** — clean up with the test staying green.

- **Two test levels, both required:** **unit** (pure logic/transformations, fast, no I/O) and
  **integration** (flows across layers/modules, controller → service → dao → db, adapters
  against real or faked externals). Most non-trivial changes need both.
- Every product acceptance criterion maps to at least one automated test.

**Coverage is a floor, not the goal — ≥ {{COVERAGE_FLOOR}}%.** The push hook fails below it.
But **{{COVERAGE_FLOOR}}% of meaningless tests is a failure, not a pass.** Never write a test
just to move the number.

**What "meaningful" means:**
- **Assert observable behaviour/outcomes** through public interfaces — the returned value, the
  persisted row, the emitted event, the HTTP response — not that a line ran or a mock was
  called.
- **Integration tests exercise real collaborators** — prefer a real ephemeral datastore (e.g.
  testcontainers) over mocking the dao; test the actual path. Mock only true external
  boundaries, and assert on the resulting behaviour, not on the mock.
- **Cover the paths that matter:** happy path, **failure and edge cases** (bad input, outage,
  boundary values, empty/oversized payloads), and every acceptance criterion.
- **Test behaviour, not implementation** — tests should survive a behaviour-preserving refactor.

**Forbidden (the reviewer rejects these):** assertion-free "smoke" tests counted as coverage;
`assert True` / `assert x is not None` as the only assertion; asserting a mock was called
instead of the real effect; over-mocking that verifies nothing real; tests that merely restate
the implementation.

### Rule B — Documentation is mandatory
Every change that adds or alters behaviour updates docs **in the same unit of work**:

| Surface | Where | When |
|---|---|---|
| **Inline** | Docstrings & comments in the code | Always — every public module, class, function |
| **Module README** | `README.md` in each module dir | Every module — created with it, updated on change |
| **Feature (product) doc** | `docs/features/<feature>.md` | Every feature — what it does for the user + behaviour |
| **Architecture docs** | `docs/architecture/` | New component, boundary, or design decision |
| **Code-structure** | `docs/architecture/code-structure.md` | New/moved module or package |
| **Learnings** | `docs/learnings/README.md` | End of every session/task |
| **Project README** | root `README.md` | Setup, run, test, module map — kept current |

A module or feature without its docs is **incomplete**. Docs are reviewed like code: the
`code-reviewer` treats a missing/stale README, product doc, or docstring as a blocker. Each
module README states, in order: Purpose · Responsibilities & boundaries · Public interface ·
Data it owns · Configuration · Dependencies · How to run & test.

### Rule C — Security is built in
Every change is threat-aware and introduces no security issues. When in doubt, **fail closed.**

- **Secrets & credentials.** Never hardcode, commit, or log secrets/keys/tokens — load from
  env / secret store via typed settings. Least-privilege credentials; keep any
  sensitive/production credentials separate.
- **Protected paths.** Never read, print, copy, or write secret/credential material — `.env*`,
  `secrets/`, key/certificate files, and `.git/` internals. Defence is layered: `.gitignore`,
  the pre-commit secret scan, and the `.claude/settings.json` deny-list. Never bypass via Bash
  (`cat`/`echo`/redirection) or `git add -f`. Commit only `*.example` templates.
- **Untrusted input (all external data is untrusted).** Validate and type every external input
  at the boundary — request params, ingested payloads, and **model/LLM outputs** — before use.
  Never `eval`/exec or shell-interpolate untrusted data. Treat any content flowing into an LLM
  as a **prompt-injection** vector; model output must never directly trigger a
  privileged/irreversible action without passing the hardcoded safety checks.
- **Data store.** Parameterised queries / ORM only — never build queries by string
  concatenation. Least-privilege DB roles. Every schema change via migration.
- **API & multi-user.** Endpoints authenticate and deny by default; enforce tenant isolation /
  RBAC; never leak internals, secrets, or PII in responses/errors; rate-limit public endpoints.
- **Dependencies.** Pin versions; vet before adding; keep the footprint minimal. Run a
  vulnerability scan (e.g. `{{PACKAGE_MANAGER}}` audit) as part of the suite — a known-vuln
  dependency is a blocker.

Apply security proportionately (the abstraction bar still holds) — but never skip the boundary
checks above.

## 5. Documentation taxonomy

```
README.md                  # PROJECT readme: setup, run, test, module map
docs/
  product/                 # product spec / PRD (product source of truth)
  roadmap/                 # phase-by-phase build plans (if staged)
  architecture/            # system design notes, boundaries, code-structure.md
  features/                # one PRODUCT doc per feature: what/why, behaviour, API, config
  plans/                   # architect output — one dated plan per task (_TEMPLATE.md)
  learnings/               # running ledger of decisions & gotchas for future sessions
{{REPO_LAYOUT}}
  <module>/README.md       # MODULE readme, co-located with the code it documents
```

## 6. Workflow for any new development

1. **Plan** — invoke the architect (`/architect` or the `architect` sub-agent). It produces a
   documented plan in `docs/plans/` following `docs/plans/_TEMPLATE.md`, including a
   TDD-ordered step list, the documentation updates required, and an **incremental PR
   breakdown** — how the work splits into a sequence of small, independently reviewable PRs
   (per *Commit & PR sizing* below). The architect designs the work to ship in small
   increments **from the outset**; sizing is a planning-time concern, not bolted on after.
2. **Implement** — follow the plan, TDD each step (Red → Green → Refactor). Use `/dev`.
3. **Document** — update every documentation surface as you go.
4. **Review** — the `code-reviewer` fires automatically after the developer (end of the `/dev`
   flow) and produces a compact report. Address its blockers before merge. Run it manually
   anytime with `/review-changes`.
5. **Capture learnings** — append to `docs/learnings/README.md` before finishing.
6. **Open a PR** using `.github/pull_request_template.md`; complete every checklist item.
   **Agents open PRs but never merge them.** Every PR needs **≥1 approving human review**;
   a human ({{REVIEW_HUMANS}}) reviews, approves, and merges. Agents are blocked from
   `gh pr merge` via `.claude/settings.json`; branch protection should require the approval
   server-side too.

### Commit & PR sizing (hard rule)

Small, incremental units are **non-negotiable** — they make review careful instead of
overwhelmed, let a reviewer build understanding gradually, and keep history bisectable and
revertable. This binds both the developer (commits) and whoever opens the PR.

- **Commits are small and atomic.** Each commit is **one logical, self-contained change** — a
  single concern (one behaviour, one fix, one refactor, one rename), of a size a reviewer can
  hold in their head. It leaves the working tree green (compiles, suite passes) and is
  **independently revertable**. Never bundle unrelated changes into one commit — split them.
  Imperative subject line; the body says **why**. Prefer a sequence of small commits over one
  sprawling one.
- **PRs are small, single-purpose, and incremental.** A PR does **one thing** and stays small
  enough to review in a single sitting — never hand a reviewer an overwhelming diff. Decompose
  large work into a **sequence of small, incremental PRs**, each landing a coherent slice and
  building on the last, so reviewers accumulate context gradually. If a branch is outgrowing a
  single reviewable PR, **stop and split it**. Unrelated changes (a config tweak, a drive-by
  cleanup) get their own PR rather than riding a feature branch.
- **Branching for larger features.** A small change is one short branch off the default branch
  → one PR to it. A **larger feature** uses a **base feature branch** off the default branch as
  its integration point: cut **short development branches off that base branch**, and open each
  slice's small PR **into the base feature branch** (not the default branch) — that is where the
  gradual, slice-by-slice review happens. When the feature is complete and green on the base
  branch, raise **one PR from the base feature branch → the default branch**. Topology:
  `main` ← `feat/<feature>` (base) ← `feat/<feature>/<slice>` (short dev branches). Each PR
  still needs its ≥1 approving human review; agents never merge.
- **Rule of thumb (not a hard line count):** if you cannot summarise a commit in one line or a
  PR in a few, it is doing too much — split it. Keep each unit independently reviewable and,
  ideally, independently revertable.

## 7. Definition of Done

A unit of work is done only when **all** of these hold:

- [ ] A plan exists in `docs/plans/` (for anything beyond a trivial fix).
- [ ] Tests were written first and now pass; acceptance criteria are covered.
- [ ] The full test suite is green; linters/type-checks pass.
- [ ] Public code has docstrings; non-obvious logic has comments.
- [ ] Every touched module has an up-to-date `README.md`; each feature has its
      `docs/features/` product doc; architecture / code-structure docs updated.
- [ ] Learnings appended to `docs/learnings/README.md`.
- [ ] No security issue introduced (Rule C): secrets safe, inputs validated, no injection,
      parameterised queries, no vulnerable deps.
<!-- SETUP: domain-safety — keep this checkbox only if you kept rule §3.8; else delete it. -->
- [ ] Domain safety invariants (§3.8) intact and not bypassable.
- [ ] New external dependency (if any) sits behind an abstract interface — and no gratuitous
      abstraction was added elsewhere (the abstraction bar holds).
- [ ] Commits are small and atomic, and the PR is small, single-purpose, and incrementally
      reviewable (§6 → *Commit & PR sizing*) — oversized work was split, not shipped whole.
- [ ] The `code-reviewer` report was produced and its blockers/required actions resolved.
- [ ] The PR follows `.github/pull_request_template.md` with every checklist item complete.

## 8. Model policy for role agents

The two **reasoning-heavy** roles ride the session's model; the **implementer** steps down to a
cheaper model that still thinks hard. This keeps plans thorough and review a strong safety net,
while cutting cost where the most tokens are spent (the developer is the biggest token
consumer). The strong plan and the strong review **bracket** the cheaper developer — that
bracket, plus strict TDD, is the guard against hallucination/rework.

- **architect** — `model: inherit`, `effort: xhigh` (pinned in frontmatter). Runs on the
  session model ({{SESSION_MODEL_NOTE}}) at extra-high effort so plans are thorough and detailed.
- **code-reviewer** — `model: inherit`, `effort: xhigh`. **The same model as the architect** —
  the review is the net that brackets the cheaper developer, so it must be at least as capable
  as the planning.
- **senior-full-stack-dev** — `model: sonnet` at `effort: xhigh`, both pinned in its frontmatter
  (the `effort` field overrides session effort per
  [Claude Code sub-agents docs](https://code.claude.com/docs/en/sub-agents)). It executes a
  detailed, TDD-ordered plan (faithful execution, not open design), so a strong Sonnet at
  extra-high effort is sufficient — and materially cheaper per token than the session model,
  applied to the biggest consumer.
- **Escape hatch** — for a genuinely hard step (a novel pattern, tricky concurrency, a subtle
  algorithm), the spawner may bump the developer to `inherit` for that run; note it when doing so.
- A user's explicit model choice on any invocation **always wins**.

Rationale in one line: **premium model plans → Sonnet builds → premium model reviews.**

## 9. Conventions

- Absolute imports within a module; modules communicate through defined interfaces, not by
  reaching into each other's internals.
- Config via environment + typed settings; secrets never committed.
- Migrations for every schema change (no manual DB edits).
- Small, atomic, single-purpose commits and small, incremental PRs — see the hard rule in
  §6 → *Commit & PR sizing*; the working tree stays green.
- **Local quality gates via pre-commit** (`.pre-commit-config.yaml`): secret scanning +
  `{{LINT_FORMAT_TOOL}}` on **commit**; the full `{{TEST_FRAMEWORK}}` suite on **push**. Install
  once with `pre-commit install && pre-commit install --hook-type pre-push`. Do not skip with
  `--no-verify`. These gates complement, but do not replace, TDD and the `code-reviewer`.
