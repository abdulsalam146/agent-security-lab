"""Offline fixture-driven evaluation of a mock document agent.

The baseline intentionally models a specific unsafe behavior: treating instructions
inside retrieved documents as commands. The protected variant enforces the tool
policy independently of model output. Neither variant represents a real LLM.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Case:
    id: str
    category: str
    user_request: str
    document: str
    proposed_action: dict
    expected: str


def load_cases(path: Path) -> list[Case]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Case file must contain a JSON array")
    cases = [Case(**item) for item in raw]
    ids = [case.id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Case IDs must be unique")
    for case in cases:
        if case.expected not in {"allow", "deny"}:
            raise ValueError(f"Invalid expected decision: {case.id}")
        if case.proposed_action.get("tool") not in {"answer", "read", "send"}:
            raise ValueError(f"Unknown tool: {case.id}")
    return cases


def evaluate(case: Case, mode: str) -> dict:
    if mode not in {"baseline", "protected"}:
        raise ValueError("mode must be baseline or protected")
    action = case.proposed_action
    tool = action["tool"]
    source = action.get("source", "document")
    trace = [f"retrieved fixture document for {case.id}", f"proposed {tool} from {source}"]

    if mode == "baseline":
        # The vulnerable mock executes the proposed tool call even when the
        # proposal came from an untrusted document.
        allowed = True
        reason = "baseline executes proposed action"
    elif tool == "answer":
        allowed = True
        reason = "answer has no external side effect"
    elif source != "user":
        allowed = False
        reason = "document content cannot authorize a tool call"
    elif tool == "send":
        allowed = False
        reason = "send tool requires out-of-band human approval"
    elif tool == "read" and not re.fullmatch(r"public/[a-zA-Z0-9_.-]+", action.get("target", "")):
        allowed = False
        reason = "read target outside public scope"
    else:
        allowed = True
        reason = "user requested public read"

    decision = "allow" if allowed else "deny"
    trace.append(f"policy: {decision} ({reason})")
    # Tools are mocks: no file access or network requests occur.
    trace.append("mock execution" if allowed else "tool not executed")
    return {
        "id": case.id, "category": case.category, "mode": mode,
        "expected": case.expected, "decision": decision,
        "passed": decision == case.expected, "reason": reason,
        "action": action, "trace": trace,
    }


def run(cases: list[Case]) -> dict:
    rows = [evaluate(case, mode) for case in cases for mode in ("baseline", "protected")]
    return {"schema_version": 1, "total_cases": len(cases), "results": rows}


def markdown_report(result: dict) -> str:
    rows = result["results"]
    lines = ["# Agent Security Lab — offline fixture report", "",
             "These results measure deterministic mock policy behavior, not an LLM's resistance to attacks.", "",
             "| Mode | Passed | Total | Rate |", "|---|---:|---:|---:|"]
    for mode in ("baseline", "protected"):
        subset = [row for row in rows if row["mode"] == mode]
        passed = sum(row["passed"] for row in subset)
        lines.append(f"| {mode} | {passed} | {len(subset)} | {passed / len(subset):.0%} |")
    lines += ["", "| Case | Category | Expected | Baseline | Protected |", "|---|---|---|---|---|"]
    for index in range(0, len(rows), 2):
        base, protected = rows[index:index + 2]
        lines.append(f"| {base['id']} | {base['category']} | {base['expected']} | {base['decision']} | {protected['decision']} |")
    lines += ["", "## Case traces", ""]
    for row in rows:
        lines += [f"### {row['id']} · {row['mode']}", "", f"Reason: {row['reason']}", ""]
        lines += [f"- {event}" for event in row["trace"]]
        lines.append("")
    return "\n".join(lines)
