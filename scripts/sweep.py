#!/usr/bin/env python3
"""Sweep question phrasings against a labeled golden set. Run BEFORE shipping
any Sage question — wording moves results more than any other variable, and a
phrasing that reads well to a human is not necessarily one that separates.

Input JSON (the skill's golden-set format; "samples"/"text"/"label" also works):
{
  "items":     [{"content": "...", "expected": true}, ...],  // true = "yes" expected
  "phrasings": ["Does this text ...?", "Is this ...?", ...]  // optional
}

Usage:
  export SAGE_API_KEY=lv_live_...
  python3 sweep.py golden.json --runs 3
  python3 sweep.py golden.json --phrasing "Does this ...?" --phrasing "Is this ...?"

Output: per-phrasing separation (min yes-labeled probability minus max
no-labeled probability) for each run, plus a recommended threshold and
escalation band for the winner. The sep_min..sep_max range across runs tells
you whether your model version is stable per input (v1.2 nearly is: one
small wobble seen, 2026-09-30) or wobbles (v0.6 did) — if it wobbles, the
spread is your margin of safety and a single run lies. Either way, set the threshold from
real traffic with margin. Cost: len(samples) x len(phrasings) x runs units.
"""
import json, statistics, sys, time
from sage_client import yesno, load_golden


def sweep(samples, phrasing):
    yes_ps, no_ps, lats = [], [], []
    for s in samples:
        t0 = time.time()
        p = yesno(s["text"], phrasing)
        lats.append((time.time() - t0) * 1000)
        (yes_ps if s["label"] else no_ps).append(p)
    return {"sep": min(yes_ps) - max(no_ps), "yes_min": min(yes_ps),
            "no_max": max(no_ps), "p50_ms": statistics.median(lats)}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    samples, phrasings = load_golden(sys.argv[1])
    runs = int(sys.argv[sys.argv.index("--runs") + 1]) if "--runs" in sys.argv else 2
    phrasings = phrasings + [sys.argv[i + 1] for i, a in enumerate(sys.argv)
                             if a == "--phrasing"]
    if not phrasings:
        sys.exit("no phrasings: add a \"phrasings\" list to the file or pass --phrasing")
    results = []

    for ph in phrasings:
        per_run = [sweep(samples, ph) for _ in range(runs)]
        seps = [r["sep"] for r in per_run]
        results.append({"phrasing": ph, "runs": per_run,
                        "sep_min": min(seps), "sep_max": max(seps)})
        print(f"  sep {min(seps):+.2f}..{max(seps):+.2f}  "
              f"p50 {per_run[0]['p50_ms']:.0f}ms  {ph[:70]}")

    results.sort(key=lambda r: r["sep_min"], reverse=True)
    best = results[0]
    print(f"\nWINNER: {best['phrasing']}")
    if best["sep_min"] <= 0:
        print("  DOES NOT SEPARATE on its worst run — do not ship; rephrase "
              "(terse, use the domain's own verbs) or split into an ensemble.")
        return
    # threshold: midpoint of the tightest run's gap; band edges from the gap itself
    worst = min(best["runs"], key=lambda r: r["sep"])
    lo, hi = worst["no_max"], worst["yes_min"]
    thr = (lo + hi) / 2
    # escalation band: the ambiguous middle, but never wider than ±0.15 —
    # a huge gap means confident calls on both sides, not a huge grey zone
    band_lo, band_hi = max(lo, thr - 0.15), min(hi, thr + 0.15)
    print(f"  tightest gap across {runs} runs: {lo:.2f} .. {hi:.2f}")
    print(f"  threshold ~{thr:.2f}; escalate the {band_lo:.2f}-{band_hi:.2f} band "
          f"to your expensive model instead of deciding")
    print("  re-run this sweep whenever meta.model changes — calibration moves "
          "silently across versions.")


if __name__ == "__main__":
    main()
