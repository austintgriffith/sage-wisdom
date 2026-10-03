# Sage API — field notes (checked live on levanto-sage-v1.2, 2026-10-02)

What we learned by calling `sage.levanto.ai` with a real key. The official
docs are at https://docs.levanto.ai (index: /llms.txt). This file holds the
parts the docs don't stress. If a response's `meta.model` is newer than
v1.2, re-check before trusting a threshold here.

## What Sage is

A fast scorer. You send content, a question, and the possible answers; it
returns a calibrated probability for each, or `null` when it isn't sure.
It can't write text, which is also a safety property: you can show it
untrusted input and nothing can leak back out as text.

## The kinds

- **`yesno`** — `answer` ("yes", "no", `null`) and `probability`.
  Threshold on `probability` when you need a stricter bar than Sage's own
  answer.
- **`tags`** — 1–120 labels, any number can apply. Each tag returns
  `probability` and `applies` (`null` = not sure). The tag `name` is what
  Sage reads, so put the definition in it: `"promotion: advertises the
  poster's own product"`. `threshold` on a tag is ignored now.
- **`choice`** — exactly one of 2–120 options (20 with an image).
  `chosen` is `null` when the top two are too close. Option probabilities
  don't sum to 1.
- **`scale`** — exactly 5 levels, 0–4. Returns `expectation`. Check it
  spreads on your data before trusting it.
- **`sort`** — rank up to 120 items. No images.

## Wording

- Short vs long isn't settled. On our injection set the short question
  with the domain's verb ("attempt to hijack the identity or system
  prompt of the AI that reads it") separated on both runs (+0.55, then
  +0.38). The long policy wording failed on one run (−0.07) and won the
  other (+0.49). See `examples/README.md`.
- Always sweep at least three wordings on real data.

## Transport

- POST `/decide` (one question) or `/decide/batch` (groups of content +
  questions). Batch answers are at
  `results[i].answers[j].result.result`; check `answers[j].ok` first.
- **Send a real User-Agent.** The default `Python-urllib` agent gets 403.
- `GET /ready` — free, no key.
- Unknown fields → 400 with a clear message. 401 bad key. 402 allowance
  used up (hard stop until next month). 503 loading or content too long;
  retry after a couple of seconds.
- `reasoning`: `off` (default) | `auto` | `on`. Up to 10 s, not billed.
  Answers carry `meta.reasoning.ran`. Set client timeouts above 10 s
  unless you use `off`.
- Images (beta): `{"kind": "image", "media": "data:image/jpeg;base64,…",
  "text": "optional context"}`. Max 4 MiB. Not with `sort` or grounding.
- `latency_mode` (top level) only affects `choice`: `fast` (default) or
  `quality` (~100 ms slower per choice, more accurate; use it for
  rules-heavy picks).
- Levanto's SDK packages (`levanto` on pip/npm) were unpublished on
  2026-10-01. Use HTTPS or `scripts/sage_client.py`.

## Measured on v1.2 (2026-09-30)

- yesno, reasoning off: ~65–90 ms on Sage's server, ~200 ms end to end
  from a US home connection.
- Same input, same answer almost every time. One wobble seen: 0.92 then
  0.88 on repeats.
- Reasoning `auto` didn't fire on simple gates. On harder pairwise
  questions it ran on 3 of 15 and pushed "no" answers further from 0.5,
  at ~4× the time.

## Pricing (2026-09)

`units = ceil(input tokens / 4000) + unique images + grounding
searches`. The document is the unit, not the question: ten yes/no
questions on one document cost 1. One `tags` question with many labels
also costs 1.

| plan | price | units/month | $ per 1k units |
|---|---|---|---|
| Developer | $14 | 10,000 | 1.40 |
| Starter | $49 | 60,000 | 0.82 |
| Pro | $99 | 175,000 | 0.57 |
| Growth | $249 | 600,000 | 0.42 |

A short Sonnet 4.6 verdict (~1k tokens in, ~60 out) is about $3.90 per
1k calls, so Sage is ~2.8× cheaper on Developer and ~9× on Growth. Units
don't roll over.

## Operational

- Young vendor: no published SLA or rate limits. Decide fail-open or
  fail-closed per host on purpose, and match the host. `safe_yesno()` in
  `scripts/sage_client.py` is a fail-open wrapper.
- Don't send secrets in `content`.
- Re-sweep thresholds when `meta.model` changes. Since v1 Levanto uses
  the same calibration for every release, so shifts should be small.
