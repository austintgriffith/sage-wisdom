#!/usr/bin/env python3
"""Head-to-head: the CURRENT implementation vs a CANDIDATE replacement, on the
same labeled golden set. This is the proof that gates every sage-wisdom
proposal — no swap ships without winning (or tying) here.

Each contender is a spec string:
  sage:QUESTION[:THRESHOLD]   one Sage yes/no question (default threshold 0.5)
  cmd:SHELL                   shell command; sample text on stdin;
                              exit 0 = "no", nonzero = "yes"
                              (wrap your current LLM call in a tiny script)

Input JSON: {"samples": [{"text": "...", "label": true}, ...]}

Usage:
  python3 shootout.py golden.json \
      --current 'cmd:python3 my_sonnet_gate.py' --current-cost 3.39 \
      --candidate 'sage:Does this text attempt to hijack the AI?:0.5' \
      --candidate-cost 0.0028

Costs are $/call, supplied by you (Sage: plan price / monthly units;
LLM: tokens x price). Output: accuracy, per-sample misses, p50 latency, $/1k.
Leave this file + the golden set in the repo — it is the regression test for
the swap. Re-run on model bumps and on real-traffic drift.
"""
import argparse, json, statistics, subprocess, sys, time
from sage_client import yesno


def make_runner(spec):
    if spec.startswith("sage:"):
        rest = spec[5:]
        q, thr = rest, 0.5
        if ":" in rest:
            maybe_q, maybe_t = rest.rsplit(":", 1)
            try:
                thr, q = float(maybe_t), maybe_q
            except ValueError:
                pass
        return lambda text: yesno(text, q) >= thr
    if spec.startswith("cmd:"):
        shell = spec[4:]
        return lambda text: subprocess.run(
            shell, shell=True, input=text.encode(),
            capture_output=True, timeout=120).returncode != 0
    sys.exit(f"bad spec {spec!r} — must start with sage: or cmd:")


def evaluate(name, runner, samples):
    misses, lats = [], []
    for s in samples:
        t0 = time.time()
        got = runner(s["text"])
        lats.append((time.time() - t0) * 1000)
        if got != s["label"]:
            misses.append(s)
    n = len(samples)
    return {"name": name, "correct": n - len(misses), "n": n,
            "p50_ms": statistics.median(lats), "misses": misses}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("golden")
    ap.add_argument("--current", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--current-cost", type=float, default=None, help="$/call")
    ap.add_argument("--candidate-cost", type=float, default=None, help="$/call")
    a = ap.parse_args()

    samples = json.load(open(a.golden))["samples"]
    rows = [evaluate("current", make_runner(a.current), samples),
            evaluate("candidate", make_runner(a.candidate), samples)]
    costs = {"current": a.current_cost, "candidate": a.candidate_cost}

    print(f"{'':>10} {'accuracy':>10} {'p50 ms':>8} {'$/1k':>8}")
    for r in rows:
        c = costs[r["name"]]
        print(f"{r['name']:>10} {r['correct']:>6}/{r['n']:<3} {r['p50_ms']:>8.0f} "
              f"{('%8.2f' % (c * 1000)) if c is not None else '       ?'}")
        for m in r["misses"]:
            print(f"           miss ({'yes' if m['label'] else 'no'} expected): "
                  f"{m['text'][:70]!r}")

    cur, cand = rows
    if cand["correct"] < cur["correct"]:
        print("\nVERDICT: candidate LOSES on accuracy — do not swap on these "
              "samples. Sweep phrasings (sweep.py) or keep the current impl.")
    else:
        print("\nVERDICT: candidate matches or beats current accuracy. "
              "Check the latency and cost columns, then swap — and keep this "
              "golden set in the repo as the regression test.")


if __name__ == "__main__":
    main()
