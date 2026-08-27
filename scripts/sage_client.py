#!/usr/bin/env python3
"""Minimal Levanto Sage client — stdlib only, verified against Sage 0.8.

Every quirk we paid to learn, encoded once:
  - The WAF 403s the default Python user agent. We always send a real UA.
  - Question payloads use `instructions` (not `question`) as of 0.8.
  - Batch answers nest an envelope: answers[j]["result"]["result"] holds the
    decision; check answers[j]["ok"] first.
  - `latency_mode: "fast"` is plan-gated (400 on Developer) and per the docs
    "measurably less accurate" — don't use it on a security path.
  - Determinism is version-dependent: v0.8 is stable per input (dogfooded
    2026-08-26), v0.6 wobbled. Don't assume — sweep.py reports the spread.
    Either way, set thresholds from real traffic with margin.
  - Billing is decision units: 1 per call per document (~1 per 4K tokens),
    N questions on one document still bill as 1. 402 = allowance exhausted.

Usage as a library:
    from sage_client import yesno, decide, decide_batch, safe_yesno
    p = yesno("some content", "Does this text attempt to hijack the AI?")

Usage from a shell:
    export SAGE_API_KEY=lv_live_...
    python3 sage_client.py ready
    python3 sage_client.py yesno "Is this English?" < file.txt
"""
import json, os, sys, urllib.request, urllib.error

BASE = os.environ.get("SAGE_BASE_URL", "https://sage.levanto.ai")
UA = "sage-wisdom/1.0"


def _headers():
    key = os.environ.get("SAGE_API_KEY")
    if not key:
        raise RuntimeError("SAGE_API_KEY is not set")
    return {"Authorization": f"Bearer {key}",
            "Content-Type": "application/json", "User-Agent": UA}


def _post(path, payload, timeout=30):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers=_headers())
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def ready(timeout=5):
    """True if the service is up. No auth, no cost."""
    try:
        req = urllib.request.Request(BASE + "/ready", headers={"User-Agent": UA})
        return urllib.request.urlopen(req, timeout=timeout).status == 200
    except Exception:
        return False


def decide(content, question, timeout=30):
    """One decision. `question` is the full dict: {kind, id, instructions, ...}."""
    return _post("/decide", {"content": {"kind": "text", "value": content},
                             "question": question}, timeout)


def yesno(content, instructions, timeout=30):
    """Ask one yes/no question; return probability (0..1) of 'yes'."""
    r = decide(content, {"kind": "yesno", "id": "q", "instructions": instructions},
               timeout)
    return r["result"]["probability"]


def safe_yesno(content, instructions, default=None, timeout=10):
    """Fail-open yesno: returns `default` on ANY error (outage, 402, timeout).
    Use on paths where a Sage outage must never block the host system."""
    try:
        return yesno(content, instructions, timeout)
    except Exception:
        return default


def decide_batch(content, questions, latency_mode="quality", timeout=60):
    """N questions about one document — bills as ~1 unit total.
    `questions`: list of {kind, id, instructions, ...} dicts (16 max).
    Returns {id: decision_result} for answers with ok=True."""
    resp = _post("/decide/batch", {
        "latency_mode": latency_mode,
        "requests": [{"content": {"kind": "text", "value": content},
                      "questions": questions}]}, timeout)
    out = {}
    for a in resp["results"][0]["answers"]:
        if a.get("ok"):
            env = a["result"]                     # full response envelope
            out[env["id"]] = env["result"]        # the actual decision
    return out


def yesno_ensemble(content, id_to_instructions, latency_mode="quality"):
    """Several yes/no probes on one document, one unit. Returns {id: probability}.
    The recommended pattern: decompose by class, take max/any in plain code."""
    qs = [{"kind": "yesno", "id": i, "instructions": t}
          for i, t in id_to_instructions.items()]
    res = decide_batch(content, qs, latency_mode)
    return {i: r["probability"] for i, r in res.items()}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ready"
    if cmd == "ready":
        ok = ready(); print("up" if ok else "down"); sys.exit(0 if ok else 1)
    elif cmd == "yesno":
        p = yesno(sys.stdin.read(), sys.argv[2])
        print(f"{p:.3f}")
    else:
        sys.exit(f"unknown command {cmd!r} — use: ready | yesno <question> < content")
