# Claude Project Starter Kit

**Version 1.0.0**

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
  - **A cost-aware model policy**: a premium model plans and reviews; a cheaper model builds.
- **Three role agents** (`.claude/agents/`): **architect** (plans), **senior-full-stack-dev**
  (implements under TDD), **code-reviewer** (verifies the diff + the rules). Plan → build →
  review, bracketed so quality holds while cost drops.
- **Scaffolding**: a dated plan template, a PR template, a `.claude/settings.json` guardrail
  set (deny secret/protected paths; block agent merges), and a pre-commit config template.

## Quick start

```bash
# 1. Copy this kit's contents into your target repo's root (see SETUP.md for the file map).
# 2. Open Claude Code in that repo and say:
#    "Instantiate the starter kit — follow SETUP.md and interview me for the placeholders."
```

Claude Code will read [`SETUP.md`](SETUP.md) and run it as an **interview** — inventorying your
repo, then **asking you** (with options + a recommended default) how to adapt the opinionated
defaults to your project's structure, stack, and conventions — before it fills every
`{{PLACEHOLDER}}`, removes the guidance blocks, wires the guardrails, and verifies. It won't
silently impose the defaults, and it merges with (never clobbers) anything you already have.

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
  settings.json                    # guardrails: deny secret/protected paths; block `gh pr merge`
docs/
  plans/_TEMPLATE.md               # dated per-task plan template (incl. incremental PR breakdown)
.github/
  pull_request_template.md         # PR checklist mirroring the constitution
.pre-commit-config.yaml            # local gates: secret scan + lint/format (commit), tests (push)
```

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
