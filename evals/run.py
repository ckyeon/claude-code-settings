#!/usr/bin/env python3
"""Run settings eval cases against one model, with and without parts of the user settings.

Each run starts from a fresh git repo built from the case's fixture. A run
records the final text, the tools called, the files changed and the cost.
Checks score that record directly. Rubric questions go to a judge model that
is not told which arm produced the run.

    evals/run.py run --model 'claude-opus-5-5[1m]' --effort xhigh --runs 3
    evals/run.py summarize evals/results/<dir>
"""
import argparse
import concurrent.futures
import datetime
import fnmatch
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "cases"

# What each arm changes relative to a normal session: (env, extra flags).
# CLAUDE_CODE_DISABLE_CLAUDE_MDS also drops ~/.claude/rules (checked 2026-10-15).
ARMS = {
    "on": ({}, []),
    "off-memory": ({"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"}, []),
    "off-skills": ({}, ["--disable-slash-commands"]),
    "off-all": ({}, ["--safe-mode"]),
}
# Arms that run from a config dir mirroring ~/.claude minus the listed entries.
# A fresh config dir has its own Keychain entry, so these arms sign in with a
# long-lived token (docs/SECRETS.md). Compare them with each other, not with "on".
# MIRROR_ENTRIES names what list_owned_links in lib/common.sh links, plus plugins/.
MIRROR_ARMS = {"on-mirror": [], "off-rules": ["rules"]}
MIRROR_ENTRIES = ["CLAUDE.md", "settings.json", "statusline-command.sh", "subagent-statusline.sh",
                  "skills", "commands", "agents", "rules", "output-styles", "hooks", "plugins"]
TOKEN_SERVICE = "claude-code-evals-oauth-token"
ON_ARMS = ("on", "on-mirror")
BASE_TOOLS = ["Edit", "Write", "Skill"]
GIT = ["git", "-c", "user.name=eval", "-c", "user.email=eval@example.invalid",
       "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {"answers": {"type": "array", "items": {
        "type": "object",
        "properties": {"id": {"type": "string"}, "pass": {"type": "boolean"},
                       "reason": {"type": "string"}},
        "required": ["id", "pass", "reason"]}}},
    "required": ["answers"],
}

JUDGE_PROMPT = """You are grading one run of an AI coding assistant. You are not told how the assistant was configured. Judge each criterion only from the evidence below. Mark pass=true only when the evidence clearly satisfies the criterion.

<user_request>
{prompt}
</user_request>

<final_response>
{result}
</final_response>

<files_changed_by_assistant>
This diff holds only the edits the assistant made during this run, not the history of the repository it worked in.
{diff}
</files_changed_by_assistant>

Criteria:
{criteria}
"""


def load_cases(pattern):
    cases = []
    for d in sorted(CASES.iterdir()):
        if not d.is_dir() or not fnmatch.fnmatch(d.name, pattern):
            continue
        case = json.loads((d / "case.json").read_text())
        case["name"] = d.name
        case["dir"] = d
        case["prompt"] = (d / "prompt.md").read_text().strip()
        cases.append(case)
    return cases


def oauth_token():
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        try:
            token = subprocess.run(["security", "find-generic-password", "-s", TOKEN_SERVICE, "-w"],
                                   capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            sys.exit("mirror arms need a token in the Keychain item %r (docs/SECRETS.md)" % TOKEN_SERVICE)
    return token


def make_mirrors(arms, base):
    """Build one config dir per mirror arm under base and return each arm's (env, flags)."""
    token, home, made = oauth_token(), Path.home() / ".claude", {}
    for arm in arms:
        d = base / arm
        d.mkdir(parents=True)
        for name in MIRROR_ENTRIES:
            if name not in MIRROR_ARMS[arm] and (home / name).exists():
                (d / name).symlink_to(home / name)
        (d / ".claude.json").write_text(json.dumps({"hasCompletedOnboarding": True}))
        made[arm] = ({"CLAUDE_CONFIG_DIR": str(d), "CLAUDE_CODE_OAUTH_TOKEN": token}, [])
    return made


def git(work, *args):
    return subprocess.run(GIT + list(args), cwd=work, capture_output=True,
                          text=True, check=True).stdout


def prepare(case, root):
    work = Path(tempfile.mkdtemp(prefix=case["name"] + "-", dir=root))
    shutil.copytree(case["dir"] / "fixture", work, dirs_exist_ok=True)
    git(work, "init", "-q")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "base")
    branch = case["dir"] / "branch"
    if branch.is_dir():
        git(work, "checkout", "-q", "-b", case.get("branch_name", "feature"))
        shutil.copytree(branch, work, dirs_exist_ok=True)
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", case.get("branch_message", "change"))
    return work


def parse_stream(stdout):
    tools, final = [], {}
    for line in stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    tools.append({"name": block.get("name"), "input": block.get("input")})
        elif ev.get("type") == "result":
            final = ev
    return tools, final


def score_checks(case, rec):
    checks, files = {}, set(rec["files_changed"])
    spec = case.get("checks", {})
    if spec.get("no_changes"):
        checks["no_changes"] = not files
    if "changed_only" in spec:
        checks["changed_only"] = files == set(spec["changed_only"])
    if "untouched" in spec:
        checks["untouched"] = not (files & set(spec["untouched"]))
    skills = [str((t["input"] or {}).get("skill", "")) for t in rec["tools"] if t["name"] == "Skill"]
    if "skill_called" in spec:
        # Exact name: a user skill and a plugin skill can share the part after the colon.
        checks["skill_called"] = spec["skill_called"] in skills
    if spec.get("no_skill"):
        checks["no_skill"] = not skills
    for pattern in spec.get("result_regex", []):
        checks["regex:" + pattern] = bool(re.search(pattern, rec["result"] or "", re.M))
    # Prose only: code, tables and headings may use symbols the writing rule allows there.
    prose = re.sub(r"```.*?```|`[^`\n]*`", "", rec["result"] or "", flags=re.S)
    prose = "\n".join(l for l in prose.splitlines() if not l.lstrip().startswith(("|", "#")))
    for pattern in spec.get("result_absent", []):
        checks["absent:" + pattern] = not re.search(pattern, prose)
    return checks


def judge(case, rec, args, cwd):
    rubric = case.get("rubric", [])
    if not rubric:
        return {}, {}
    prompt = JUDGE_PROMPT.format(
        prompt=case["prompt"], result=rec["result"] or "(no final text)",
        diff=rec["diff"] or "(no file changes)",
        criteria="\n".join("- id: %s\n  criterion: %s" % (q["id"], q["text"]) for q in rubric))
    cmd = ["claude", "-p", prompt, "--safe-mode", "--model", args.judge_model,
           "--output-format", "json", "--json-schema", json.dumps(JUDGE_SCHEMA),
           "--no-session-persistence", "--strict-mcp-config", "--max-turns", "3"]
    proc = subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, timeout=300)
    try:
        answers = json.loads(proc.stdout)["structured_output"]["answers"]
    except (ValueError, KeyError, TypeError):
        return {q["id"]: None for q in rubric}, {"error": proc.stderr[-500:] or proc.stdout[-500:]}
    by_id = {a["id"]: a for a in answers}
    return ({q["id"]: by_id.get(q["id"], {}).get("pass") for q in rubric},
            {q["id"]: by_id.get(q["id"], {}).get("reason") for q in rubric})


def run_one(case, arm, i, args, out):
    work = prepare(case, args.work_root)
    env_extra, flags = args.arm_env[arm]
    env = dict(os.environ, CLAUDE_CODE_DISABLE_AUTO_MEMORY="1", **env_extra)
    cmd = (["claude", "-p", case["prompt"],
            "--allowedTools"] + BASE_TOOLS + case.get("allowed_tools", []) +
           ["--output-format", "stream-json", "--verbose", "--no-session-persistence",
            "--strict-mcp-config", "--model", args.model,
            "--max-turns", str(case.get("max_turns", 15))] +
           (["--effort", args.effort] if args.effort else []) + flags)
    try:
        proc = subprocess.run(cmd, cwd=work, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              timeout=case.get("timeout_seconds", 900))
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = "timeout"
    tools, final = parse_stream(stdout)
    git(work, "add", "-A")
    numstat = git(work, "diff", "--cached", "--numstat").splitlines()
    rec = {
        "case": case["name"], "arm": arm, "run": i,
        "models": sorted((final.get("modelUsage") or {}).keys()),
        "effort": args.effort,
        "result": final.get("result"),
        "is_error": final.get("is_error", True),
        "num_turns": final.get("num_turns"),
        "duration_ms": final.get("duration_ms"),
        "cost_usd": final.get("total_cost_usd"),
        "permission_denials": final.get("permission_denials", []),
        "tools": tools,
        "files_changed": [l.split("\t")[2] for l in numstat],
        "lines_changed": sum(int(a) + int(d) for a, d, _ in
                             (l.split("\t") for l in numstat) if a != "-"),
        "diff": git(work, "diff", "--cached")[:20000],
        "stderr": stderr[-2000:],
    }
    rec["guard"] = case.get("guard", [])
    rec["checks"] = score_checks(case, rec)
    rec["rubric"], rec["rubric_reasons"] = judge(case, rec, args, args.work_root)
    if not args.keep_work:
        shutil.rmtree(work, ignore_errors=True)
    dest = out / case["name"]
    dest.mkdir(parents=True, exist_ok=True)
    (dest / ("%s-%d.json" % (arm, i))).write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    return rec


def rate(values):
    vals = [v for v in values if v is not None]
    return "%d/%d" % (sum(vals), len(vals)) if vals else "-"


def mean_sd(values, fmt):
    vals = [v for v in values if v is not None]
    if not vals:
        return "-"
    sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
    return (fmt + " ± " + fmt) % (statistics.mean(vals), sd)


def pass_rate(values):
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else None


def verdict(on, off, guard):
    """Judge one metric from its pass rates with the setting on and off (ADR 0088)."""
    if on is None or off is None:
        return "-"
    if guard:
        # The setting should not make this worse.
        if on >= 0.8:
            return "해 없음"
        return "해로움" if off - on >= 0.6 else "보류"
    if on - off >= 0.6:
        return "유지"
    if on >= 0.8 and off >= 0.8:
        return "중복"
    if (on <= 0.2 and off <= 0.2) or off - on >= 0.6:
        return "무효"
    return "보류"


def summarize(out):
    recs = [json.loads(p.read_text()) for p in sorted(out.glob("*/*.json"))]
    lines, summary = [], {}
    for case in sorted({r["case"] for r in recs}):
        rows = [r for r in recs if r["case"] == case]
        keys = sorted({k for r in rows for k in r["checks"]})
        qs = sorted({k for r in rows for k in r["rubric"]})
        lines.append("\n## %s\n" % case)
        lines.append("| arm | n | " + " | ".join(keys + ["judge:" + q for q in qs]) +
                     " | lines | turns | cost $ | sec |")
        lines.append("|---" * (6 + len(keys) + len(qs)) + "|")
        for arm in sorted({r["arm"] for r in rows}):
            rs = [r for r in rows if r["arm"] == arm]
            cells = ([rate([r["checks"].get(k) for r in rs]) for k in keys] +
                     [rate([r["rubric"].get(q) for r in rs]) for q in qs])
            secs = [r["duration_ms"] / 1000 if r["duration_ms"] else None for r in rs]
            lines.append("| %s | %d | %s | %s | %s | %s | %s |" % (
                arm, len(rs), " | ".join(cells),
                mean_sd([r["lines_changed"] for r in rs], "%.1f"),
                mean_sd([r["num_turns"] for r in rs], "%.1f"),
                mean_sd([r["cost_usd"] for r in rs], "%.3f"),
                mean_sd(secs, "%.0f")))
            summary.setdefault(case, {})[arm] = {
                "n": len(rs), "errors": sum(1 for r in rs if r["is_error"]),
                "checks": {k: [r["checks"].get(k) for r in rs] for k in keys},
                "rubric": {q: [r["rubric"].get(q) for r in rs] for q in qs},
                "models": sorted({m for r in rs for m in r["models"]}),
                "cost_usd": [r["cost_usd"] for r in rs],
            }
        arms = sorted({r["arm"] for r in rows})
        on_arm = next((a for a in ON_ARMS if a in arms), None)
        guard = {g for r in rows for g in r.get("guard", [])}
        metrics = [(k, "checks", k) for k in keys] + [("judge:" + q, "rubric", q) for q in qs]
        if len(arms) == 1:
            # One arm, as for a skill trigger: nothing to compare, so judge the rate itself.
            lines.append("\n| 지표 | %s | 판정 |\n|---|---|---|" % arms[0])
            for label, kind, key in metrics:
                vals = [r[kind].get(key) for r in rows]
                p = pass_rate(vals)
                v = "-" if p is None else "통과" if p >= 0.8 else "실패" if p <= 0.2 else "보류"
                lines.append("| %s | %s | %s |" % (label, rate(vals), v))
                summary[case].setdefault("verdicts", {}).setdefault(arms[0], {})[label] = v
        for off_arm in [a for a in arms if a != on_arm] if on_arm else []:
            lines.append("\n| 지표 | %s | %s | 판정 |\n|---|---|---|---|" % (on_arm, off_arm))
            for label, kind, key in metrics:
                on = [r[kind].get(key) for r in rows if r["arm"] == on_arm]
                off = [r[kind].get(key) for r in rows if r["arm"] == off_arm]
                v = verdict(pass_rate(on), pass_rate(off), key in guard)
                lines.append("| %s%s | %s | %s | %s |" % (
                    label, " (guard)" if key in guard else "", rate(on), rate(off), v))
                summary[case].setdefault("verdicts", {}).setdefault(off_arm, {})[label] = v
    text = "\n".join(lines).strip() + "\n"
    (out / "summary.md").write_text(text)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--model", required=True, help="exact model id under test")
    r.add_argument("--effort", help="effort level, pinned for every arm")
    r.add_argument("--judge-model", default="claude-haiku-5-5")
    r.add_argument("--runs", type=int, default=5)
    r.add_argument("--case", default="*", help="glob over case names")
    r.add_argument("--arms", nargs="+", help="override each case's arms")
    r.add_argument("--jobs", type=int, default=1)
    r.add_argument("--out", type=Path)
    r.add_argument("--work-root", default=tempfile.gettempdir())
    r.add_argument("--keep-work", action="store_true")
    s = sub.add_parser("summarize")
    s.add_argument("out", type=Path)
    args = ap.parse_args()

    if args.cmd == "summarize":
        print(summarize(args.out), end="")
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = args.out or HERE / "results" / ("%s-%s" % (stamp, re.sub(r"[^\w.-]", "_", args.model)))
    out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for i in range(args.runs):
        for case in load_cases(args.case):
            for arm in args.arms or case["arms"]:
                jobs.append((case, arm, i))
    used = {a for _, a, _ in jobs}
    unknown = used - set(ARMS) - set(MIRROR_ARMS)
    if unknown:
        sys.exit("unknown arms: %s" % ", ".join(sorted(unknown)))
    args.arm_env = dict(ARMS)
    mirrors = sorted(used & set(MIRROR_ARMS))
    if mirrors:
        mirror_base = Path(tempfile.mkdtemp(prefix="mirrors-", dir=args.work_root))
        args.arm_env.update(make_mirrors(mirrors, mirror_base))
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        futures = {pool.submit(run_one, c, a, i, args, out): (c["name"], a, i) for c, a, i in jobs}
        for f in concurrent.futures.as_completed(futures):
            name, arm, i = futures[f]
            try:
                rec = f.result()
                print("done %s %s #%d checks=%s rubric=%s" % (name, arm, i, rec["checks"], rec["rubric"]), flush=True)
            except Exception as e:
                print("FAIL %s %s #%d: %r" % (name, arm, i, e), file=sys.stderr, flush=True)
    if mirrors and not args.keep_work:
        shutil.rmtree(mirror_base, ignore_errors=True)
    print(summarize(out), end="")
    print("results: %s" % out)


if __name__ == "__main__":
    main()
