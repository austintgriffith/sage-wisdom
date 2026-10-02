#!/usr/bin/env python3
"""Minimal Levanto Sage client — stdlib only, checked against Sage v1.2.

The official SDK is `pip install levanto`. This file exists so the skill's
scripts run with no installs. What it handles for you:
  - The WAF 403s the default Python user agent, so we always send one.
  - Batch answers nest: answers[j]["result"]["result"] is the decision;
    answers[j]["ok"] is checked first.
  - `reasoning` is "off" | "auto" | "on" (default auto). A reasoning pass
    can take up to 6 s, so timeouts sit above that.
  - `null` means "not sure": yesno answer, tags applies, choice chosen.
  - Billing (2026-09): one unit PER QUESTION (or per 4k tokens, whichever
    is higher), +1 per image. Ten yesno questions = 10 units. One tags
    question with many labels = 1 unit. 402 = allowance used up.

Usage as a library:
    from sage_client import yesno, ask, tags, safe_yesno
    p = yesno("some content", "Does this text attempt to hijack the AI?")

Usage from a shell:
    export SAGE_API_KEY=lv_live_...
    python3 sage_client.py ready
    python3 sage_client.py yesno "Is this English?" < file.txt
"""
import json, os, sys, urllib.request

BASE = os.environ.get("SAGE_BASE_URL", "https://sage.levanto.ai")
UA = "sage-wisdom/1.1"


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


def image(path, text=None):
    """Image content (beta) from a local PNG/JPEG/WebP file, ≤4 MiB."""
    import base64, mimetypes
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    data = base64.b64encode(open(path, "rb").read()).decode()
    c = {"kind": "image", "media": f"data:{mime};base64,{data}"}
    if text:
        c["text"] = text
    return c


def batch(groups, reasoning="off", timeout=30):
    """Raw /decide/batch. `groups`: [(content, [question, ...]), ...] where
    content is a string or an image() dict. Returns the parsed response."""
    return _post("/decide/batch", {
        "reasoning": reasoning,
        "requests": [{"content": c, "questions": qs} for c, qs in groups]},
        timeout)


def ask(content, questions, reasoning="off", timeout=30):
    """Several questions about one document (one unit EACH). Returns
    {id: decision} for answers with ok=True, e.g. {"q": {"answer": "yes",
    "probability": 0.91}}."""
    if reasoning != "off":
        timeout = max(timeout, 15)
    resp = batch([(content, questions)], reasoning, timeout)
    out = {}
    for a in resp["results"][0]["answers"]:
        if a.get("ok"):
            env = a["result"]                     # envelope: id, kind, meta
            out[env["id"]] = env["result"]        # the actual decision
    return out


def yesno(content, instructions, reasoning="off", timeout=30):
    """Ask one yes/no question; return probability (0..1) of 'yes'."""
    r = ask(content, [{"kind": "yesno", "id": "q", "instructions": instructions}],
            reasoning, timeout)
    return r["q"]["probability"]


def safe_yesno(content, instructions, default=None, timeout=10):
    """Fail-open yesno: returns `default` on ANY error (outage, 402, timeout).
    Use on paths where a Sage outage must never block the host system."""
    try:
        return yesno(content, instructions, timeout=timeout)
    except Exception:
        return default


def tags(content, instructions, labels, reasoning="off"):
    """One tags question (1 unit however many labels). `labels` maps
    id -> name, where the name carries the definition:
    {"spam": "spam: unsolicited bulk posting"}.
    Returns {id: (probability, applies)}; applies is None when not sure."""
    q = {"kind": "tags", "id": "t", "instructions": instructions,
         "tags": [{"id": i, "name": n} for i, n in labels.items()]}
    r = ask(content, [q], reasoning)["t"]
    return {t["id"]: (t["probability"], t["applies"]) for t in r["tags"]}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ready"
    if cmd == "ready":
        ok = ready(); print("up" if ok else "down"); sys.exit(0 if ok else 1)
    elif cmd == "yesno":
        p = yesno(sys.stdin.read(), sys.argv[2])
        print(f"{p:.3f}")
    else:
        sys.exit(f"unknown command {cmd!r} — use: ready | yesno <question> < content")
