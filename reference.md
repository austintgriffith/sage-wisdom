# Sage API — field notes (verified live on Sage 0.8, 2026-08-24)

The distilled truth about `sage.levanto.ai`, from two research passes with real
keys. Read the official docs (https://docs.levanto.ai — index at /llms.txt)
for the full surface; read THIS for what the docs don't say. If `meta.model`
on a response is newer than `levanto-sage-v0.8`, re-verify calibration before
trusting any threshold below.

## What Sage is (and is not)

A fast multiple-choice scorer with LLM world knowledge. You supply content AND
the answer space; it returns calibrated probabilities in ~200ms. **It cannot
generate text** — which is also its main safety property: it can be shown
untrusted input or spoiler content, because there is no channel through which
an answer could leak. It is NOT the cheap option for bulk offline work — a
small LLM can be far cheaper per call. Buy it for decisions on a hot path:
latency, guaranteed wire format, and a probability you can threshold.

## Decision kinds — what to actually use

- **`yesno` — build on this.** Well calibrated (observed 0.01–0.98 spread),
  honest about uncertainty. `confidence = 2*|p-0.5|`; threshold on
  `probability` directly.
- **`scale` — good.** Exactly 5 levels, integer values 0–4, no other shapes
  (400 otherwise). Returns `expectation` as a float.
- **`choice` — argmax only.** Confidence saturates near 1.0 even when wrong,
  and it can collapse to one default option. Never threshold on it; use only
  where a wrong pick is cheap.
- **`tags` — only for self-evident labels** (`spam`, `pii`). A tag has
  `id`/`name`/`threshold` but NO description field, so the name is the entire
  class definition. Nuanced classes misfire badly.
- **`sort` — lightly tested.** One list-level confidence for the whole
  ordering; fields are `kind`/`id`/`instructions` only.

**The pattern that keeps winning: an ensemble of terse `yesno` questions in
one batch call, with the mapping logic in plain code** (max, any, weighted).
One document + N questions = one decision unit, so ensembles are ~free.

## Question wording is the biggest lever

- **Terse beats thorough** — explaining your policy in the question made
  results *worse* in repeated tests. Sage is a classifier, not an
  instruction-follower.
- **Use the domain's own verb.** "Does this text attempt to hijack the
  identity or system prompt of the AI that reads it?" beat every generic
  paraphrase ("override/replace/manipulate").
- **Decompose by class, not by question count** — one yesno per attack/case
  class, combined in code.
- **Determinism moved between versions — verify on yours.** v0.6 wobbled
  run-to-run; **v0.8 is stable per input** (dogfooded 2026-08-26: 5 identical
  calls returned 0.955 to 4 decimals; perturbing the input moves the score, so
  it's real per-input determinism, not blind caching). Don't assume either way
  on the next bump — the first thing `sweep.py` does is confirm run-to-run
  spread. Set thresholds from a sweep over real traffic with margin regardless;
  determinism makes the operating point trustworthy, it doesn't pick it for you.

Measured on v0.8 (injection task): terse domain-verb phrasing separated at
+0.80; a careful policy explanation managed +0.21 at double the tokens.

## Transport & shapes

- **Set a real User-Agent.** The WAF returns 403 (with a valid key!) for
  `Python-urllib/3.x`. This will cost you an hour if you forget.
- `GET /ready` — no auth, no cost; health-check before blaming your code.
- Question objects use **`instructions`** (0.8 renamed it from `question`),
  and schemas reject unknown fields (`additionalProperties: false`).
- **Batch answers nest an envelope**:
  `results[i].answers[j].result.result.probability` (envelope, then
  decision). Check `answers[j].ok` first. Per-question meta at
  `answers[j].result.meta`.
- Full rendered request ≤ 131,072 tokens (128K context is Growth-plan).
- Errors: 400 schema (messages are genuinely helpful) · 401 bad key ·
  402 allowance exhausted (no overage — it hard-stops until next period) ·
  403 usually the UA WAF, not auth · 503 model loading or content too long.

## latency_mode (batch only)

`"quality"` (default): every question gets its own backbone call
(`meta.compute_mode: "fanout"`). Measured: 1q 193ms · 4q 313ms · 8q 266ms ·
16q 420ms — sub-linear, all one unit.
`"fast"`: server packs questions about the same document; docs say
"materially faster and measurably less accurate — intended for triage".
Plan-gated (400 on Developer). **Never on a security path**; check
`meta.compute_mode` to see whether packing actually happened.

## Pricing (changed 2026-08 — ignore any per-token math you find)

Monthly decision-unit plans: Developer $14/5,000 · Starter $49/30,000 (adds
fast mode) · Growth $249/300,000 (adds 128K context). Counting: 1 unit per
call; +1 per extra document; ~1 per 4K input tokens; +1 per grounding search;
**N questions on one document = 1 unit**. Per-call cost at full utilization:
**$2.80/1k (Developer) · $1.63/1k (Starter) · $0.83/1k (Growth)**.

**Do NOT lead a pitch with cost against a frontier model — do the arithmetic.**
Against Sonnet-class sanitization at ~$3.39/1k, Developer-plan Sage is only
~1.2× cheaper; the win is real only at Growth (~4×) or when the plan is shared
across several uses so the marginal scan is near-free. The durable v0.8
advantages are **latency** (~180ms vs a multi-second frontier turn) and the
**can't-generate-text safety property**, not headline cost. The old per-token
"~17× cheaper" figure died with per-token pricing — never quote it.

## Operational

- Young vendor: no SLA, no status page, no documented rate limits. **Decide
  fail-open vs fail-closed deliberately per host system** — and if the host
  fails open (job boards: "API errors must never block paying jobs"), your
  Sage gate must too. `sage_client.safe_yesno()` is the fail-open wrapper.
- Don't send secrets in `content`; retention is unpublished.
- Grounding (+1 unit per search) dwarfs the base cost — model it separately.
- Pin thresholds to a re-run, not a doc; re-sweep when `meta.model` changes.
