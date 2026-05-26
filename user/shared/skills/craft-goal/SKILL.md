---
name: craft-goal
description: Compose a /goal autonomous-mode prompt on the user's behalf. The user wants a prompt STRING written — not the underlying task performed. Key signals: the word "goal" paired with authoring intent (craft, write, make, compose, 짜줘, 만들어줘, 쓰는 법 알려줘). Often the user describes a large task in detail (migration, refactor, bulk test coverage, config changes across many files) then asks for a goal prompt to run it autonomously — the task description is INPUT for composing the prompt, not work to execute directly. Outputs a verified, copy-pasteable /goal command. Skip only when /goal is already followed by a condition string.
---

# Craft Goal

Build a `/goal` condition that a separate evaluator model (Haiku) can objectively judge from the conversation transcript alone.

The evaluator never runs commands, reads files, or calls tools — it only sees what the main agent has already printed in the conversation. Every claim in the condition must therefore be something the main agent will naturally surface (e.g., test output, build exit codes, git status) during its work.

## How to use this skill

### Step 1 — Scan the environment

Before asking the user anything, silently gather project context. Read what's available — not everything will exist, and that's fine:

**Project harness:**
- `CLAUDE.md` (root and nested) — project conventions, guardrails, test/lint commands
- `.claude/settings.json` — permission model, allowed tools
- `package.json` / `pyproject.toml` / `Makefile` / `Cargo.toml` — available scripts (test, lint, build, typecheck)
- `tsconfig.json` / `.eslintrc*` / `biome.json` — toolchain config
- CI config (`.github/workflows/`, `.gitlab-ci.yml`) — what the CI pipeline checks

**Project structure:**
- Top-level directory listing — understand the shape of the codebase
- `docs/` or `docs/adr/` — architectural decisions and context
- `CONTEXT.md` — domain glossary if available

**Session context:**
- What has the user been working on in this conversation?
- Which files have been edited or discussed?
- Are there failing tests or broken builds already mentioned?
- Has a plan been discussed or created?

Collect this silently — don't narrate the scan. Use it to inform your questions and the final prompt.

### Step 2 — Understand the user's intent

From the conversation history and any explicit request, identify:

1. **What** the user wants accomplished (the task)
2. **Why** it matters (context that shapes constraints)
3. **What "done" looks like** in their mind

If the user's request is already in the conversation (e.g., they described a task and then asked for a goal), extract as much as possible before asking questions.

### Step 3 — Ask about gaps

Do not guess. For every gap in the information below, ask the user directly. Group questions logically — don't ask one at a time, but also don't dump 10 questions at once. 3-5 focused questions per round is the sweet spot.

**Always clarify these if not already known:**

| Element | Why it matters | Example question |
|---|---|---|
| **End state** | The evaluator needs a binary pass/fail signal | "성공 기준이 정확히 뭔가요? 예: 특정 테스트 통과, 빌드 성공, 특정 파일 생성 등" |
| **Verification command** | The evaluator only sees transcript output | "이 결과를 확인할 수 있는 명령어가 있나요? (npm test, cargo build, pytest 등)" |
| **Scope boundary** | Without explicit constraints, the agent takes shortcuts | "건드리면 안 되는 파일이나 영역이 있나요?" |
| **Turn budget** | Unbounded goals can run indefinitely | "최대 몇 턴까지 실행해도 괜찮을까요? (보통 10-30턴 권장)" |

**Situationally clarify:**

- If the task involves multiple steps: "우선순위나 순서가 있나요?"
- If the codebase has multiple test suites: "어떤 테스트 스위트를 기준으로 할까요?"
- If there are related files that might be affected: "이 변경으로 영향받을 수 있는 X, Y도 제약 조건에 포함할까요?"
- If the project has CI: "CI 파이프라인의 어떤 단계까지 통과해야 하나요?"
- If the task is vague: "구체적으로 어떤 상태가 되면 '완료'인가요?"

### Step 4 — Compose the goal condition

Assemble a condition with these components, in this order:

```
1. [End state]        — what must be true when done
2. [Verification]     — how the agent proves it (commands to run)
3. [Constraints]      — what must NOT change
4. [Progress tracking] — optional: scratchpad for long tasks
5. [Turn limit]       — safety bound
```

#### Writing rules

**End state — make it binary.**
The evaluator returns yes or no. Conditions like "improve performance" or "clean up the code" are unjudgeable. Convert to: "`lighthouse performance score >= 90`", "`no function longer than 50 lines in src/utils/`".

**Verification — name the exact command.**
"`npm test` exits 0" is evaluable. "Tests pass" is ambiguous — which tests? what runner? The agent might not run them at all. Use commands you found in the project's package.json / Makefile / CI config.

**Constraints — be explicit about boundaries.**
The agent optimizes for the end state. Without constraints, it may:
- Delete failing tests instead of fixing them
- Modify unrelated files to make things compile
- Take destructive shortcuts (reset, force-push)

Write constraints as "do not" clauses: "do not modify files outside `src/auth/`", "do not delete any existing test", "do not change the public API signature".

**Progress tracking — for tasks over ~10 turns.**
Tell the agent to maintain a scratchpad file (e.g., `progress.md`) with what's done and what's left. This gives the evaluator something concrete to read and helps the agent maintain coherence across context compactions.

**Turn limit — always include one.**
Even well-scoped goals can loop. A turn limit is a safety valve. Suggest 10-20 for focused tasks, 20-40 for larger migrations. Phrase as: "stop after N turns if not complete and report remaining work".

#### Quality checklist

Before presenting the goal, verify:

- [ ] Every claim in the condition can be proved by running a command and printing its output
- [ ] The condition uses specific command names from this project (not generic "tests pass")
- [ ] Constraints cover files/areas the user would be upset to see changed
- [ ] The turn limit is proportional to the task size
- [ ] No subjective terms (good, clean, improved, better, nice)
- [ ] The condition is under 4,000 characters

### Step 5 — Present the result

Show the user the complete `/goal` command they can copy-paste. Format it as a fenced code block. Below it, briefly explain:

1. **Why each part is there** — one sentence per component
2. **Complementary setup** — suggest enabling auto mode (`/auto-approve`) if the task will run unattended, or doing `/plan` first if the task is complex and no plan exists yet
3. **What to watch for** — any risks specific to this task (e.g., "if the migration touches the DB schema, watch for lock contention")

If you identified multiple valid approaches during the scan, present the recommended goal first, then briefly note alternatives.

## Patterns for common tasks

Use these as building blocks — adapt to the specific project's toolchain.

**Test-driven fix:**
```
/goal `npm test -- --testPathPattern=auth` exits 0
with no changes to files outside src/auth/ and test/auth/,
no existing tests deleted, and stop after 15 turns
```

**Migration:**
```
/goal every import of OldApi in src/ is replaced with NewApi,
`npx tsc --noEmit` exits 0, `npm test` exits 0,
no files outside src/ are modified,
maintain progress.md with completed and remaining files,
stop after 30 turns if not complete and report remaining work
```

**Multi-check refactor:**
```
/goal all functions in src/utils/ are under 50 lines,
`npm run lint` exits 0, `npm test` exits 0,
no public API signatures change (exports remain identical),
stop after 20 turns
```

**Documentation generation:**
```
/goal every public function in src/lib/ has a JSDoc comment,
`npx tsc --noEmit` exits 0 (no type errors introduced),
no runtime code is modified, stop after 15 turns
```

## Anti-patterns to avoid

**Subjective conditions** — "make the code cleaner" → the evaluator can't judge this.

**Missing verification** — "all tests pass" without specifying which test command → the agent might skip running tests entirely and the evaluator has nothing to check.

**Overly broad scope** — "refactor the entire codebase" → no clear end state, will exhaust the turn budget doing unfocused work.

**No constraints** — "make X work" without boundary clauses → the agent may break Y to fix X.

**Compound goals without priority** — "fix auth AND add logging AND update docs" → if they conflict, the agent thrashes. Break into sequential goals or prioritize.
