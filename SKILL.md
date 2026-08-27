---
name: sage-wisdom
description: >
  Audit an AI pipeline for decisions that are slower, costlier, or flakier
  than they need to be, and prove each fix with an eval before shipping it.
  Use when the user wants to cut LLM costs or latency, make an agent pipeline
  more deterministic, find where Levanto Sage fits in their codebase, review
  their AI spend, or asks "make this more efficient" about anything that
  calls a model. Runs as a three-stage engagement — scan, prove, ship — with
  the user deciding at each gate. Powered by the Levanto Sage decision API
  plus plain judgment about when NOT to use it.
---

# Sage Wisdom

> **First effective, then efficient.** First you make the thing work — any
> model, any cost. Then you ask *"what did we learn?"* and make it work
> better: cheaper, faster, more deterministic. This skill is the second step,
> made mechanical.

Deliver everything straight — findings, numbers, verdicts. No persona.

## The shape of an engagement

Three stages. Each ends at a gate where the user decides. Tell the user
which stage you're in, and never blend them.

1. **SCAN** — read the repo, find every model call, judge each one. Ends
   with a ranked findings table and one question: *"which of these should I
   prove?"* No evals yet, no code changes.
2. **PROVE** — for each finding the user picked: golden set, sweep,
   shootout. Ends with the numbers side by side. A win gets *"want me to
   implement it?"*; a loss gets reported honestly and dropped.
3. **SHIP** — implement only what won its eval and got a yes. The eval
   harness stays in the host repo as the regression test.

The user can stop at any gate. A survey alone is a fine deliverable.

## 0. First run

Ask, conversationally, at most three questions before touching code:
1. What do you build, and which repo/pipeline should I study?
2. What hurts most right now — cost, latency, reliability, or safety?
3. Is there anything the pipeline must NEVER do (block paying users, leak a
   spoiler, auto-approve)? This decides fail-open vs fail-closed later.

A `SAGE_API_KEY` is needed only when the candidate is Sage. The scan and
any plain-code swap run the full eval loop without one. If it's not set,
mention it once (keys at https://platform.levanto.ai). Never write a key to
a tracked file.

## 1. Check the world first

This file decays; the world moves. Before quoting any number from it:

- Every perishable figure below carries a swept/measured date. Older than
  ~3 months: re-verify — look up current model prices, check the live Sage
  version and plan pricing at docs.levanto.ai — instead of quoting.
- Thresholds and phrasings expire on model bumps, theirs and Sage's. A
  changed `meta.model` in a Sage response means re-sweep before trusting an
  old threshold.
- The durable parts — the stage gates, the eval discipline, the scars —
  carry no date on purpose. Trust those.

## 2. SCAN

Find every place the pipeline spends a model call — don't sell anything yet:

- Grep for SDK imports and API calls: `anthropic`, `openai`, `claude-`,
  `gpt-`, `completions`, `messages.create`, `generateText`, fetches to
  inference hosts, LangChain/AI-SDK wrappers.
- Grep for CLI spend too — it's invisible to the SDK grep and can be the
  dominant cost: `claude -p`, `claude --`, `codex exec`,
  `--append-system-prompt`, `$(cat …)` prompt substitution in shell scripts.
- Read the prompt files as call sites: `*.prompt.md`, skill files that
  instruct sub-agent fan-outs — the fan-out multiplier often lives in the
  prompt, not the code.
- Note what each call actually produces and what the caller does with it —
  especially output that gets parsed down to a label, score, boolean,
  ranking, or route.
- Find the loops: cron jobs, launchd plists, queue workers, per-request
  middleware, CI steps, `while true` pollers — and their retry counts (a
  40-attempt driver changes the volume math). Volume × tokens × model price
  = monthly cost. Estimate it per site.
- If the pipeline runs on OAuth subscriptions instead of a metered API,
  dollars are the wrong unit. Capacity is 5h/weekly windows per account:
  estimate window use per job ("one job drains a login's 5h window") and
  count freed capacity as the win.
- Check logs/stores for real traffic samples — you will want them for golden
  sets later.

Then judge each site through three lenses, in this order:

**Lens 1 — should this call exist at all?** The cheapest call is the one you
delete. Before touching the model choice, check:
- **Delete it:** output nobody reads — summaries with no consumer, reports
  nobody opens, analysis feeding a dead feature.
- **Cache it:** the same input asked repeatedly → memoize the answer; a big
  static prompt prefix → provider prompt caching. Paraphrased repeats → a
  semantic cache (chat workloads report 25–35% hit rates, 2026-08) — but a
  wrong cache hit is a correctness bug, so it gets a golden set like any
  other swap.
- **Batch it:** N calls that could be one — N questions in one prompt, or
  the provider's batch API (typically half price) when nobody is waiting.
- **Unchain it:** independent calls running in sequence. Chain latency adds
  up linearly with step count; anything without a data dependency runs in
  parallel.
- **Move it off the hot path:** nothing user-facing should wait on work that
  could run async or on a schedule.
- **Shrink it:** the tokens half of volume × tokens. A 20k-token system
  prompt on every call, duplicated context, whole files where a slice would
  do. For long-running agents: re-reading the whole history every turn —
  compaction, notes-to-file, or sub-agents that return short results (long
  context degrades reasoning even with room to spare; "context rot" is the
  2026 term).

**Lens 2 — should this call be deterministic?** The reliability hunt:
- temperature > 0 anywhere the output gets parsed
- retry-until-it-parses loops where the API has structured-output /
  tool-call enforcement — use the enforcement
- an LLM doing arithmetic, parsing a known format, comparing dates, or
  mapping enum→enum — that's a script (P4)
- an LLM-as-judge step in CI or gating logic that flakes builds — pin it,
  threshold it, or walk it down the ladder

**Lens 3 — the descent ladder.** For whatever survives lenses 1–2:

```
frontier LLM  →  small LLM  →  Sage  →  plain code
```

Walk each call down until something breaks. The economics of descending are
proven at scale: routing studies (2026-08) hold ~95% of frontier quality
while sending only 14–26% of traffic to the big model — the escalation band
in §3 is the same shape. You already know what belongs on the top and bottom
rungs. The Sage rung is the one you don't know:
recommend it when the decision is judgment-shaped (needs world knowledge or
reading comprehension) but the answer space is enumerable — yes/no, a score,
a pick, a label — AND at least one of:
- **hot path**: someone is waiting; ~200ms beats seconds
- **thresholdable**: the caller needs a calibrated probability to gate on,
  plus an escalation band for the ambiguous middle
- **wire-format certainty**: the caller parses the output, and LLM
  freeform/fenced JSON keeps breaking it
- **must-not-generate**: the input is untrusted (injection surface) or the
  component must not be able to talk (spoilers, double-speak); Sage
  structurally cannot emit text

Split calls that do double duty. The classic: one prompt that both makes a
security verdict AND writes a summary. Sage takes the verdict, a small model
takes the prose — cheaper, and it un-conflates resisting untrusted text from
processing it, which is precisely the conflation injection exploits.

Finding nothing to fix in good code is doing the job — say so plainly.

**The rethink.** The lenses are pattern matching; this step is not. Take the
top few call sites, put the lenses down, and re-derive: state the job in one
sentence with no mention of AI ("decide if this input is safe", "rank this
queue", "turn this form into a record"), then ask how you'd build it if it
launched today. Prompts that find real ones:

- **Move the judgment in time.** Does the decision have to happen per
  request? Classify once at write-time, store the label, read it forever —
  per-request becomes per-datum.
- **Agent → workflow.** An agent loop whose path is actually predictable is
  a workflow wearing a costume: hardcode the chain and every planning call
  disappears. Rough tell: a handful of tool calls suits a loop; dozens per
  job means the decomposition is wrong, not the model.
- **Fix the upstream data instead.** An expensive call that compensates for
  bad retrieval, missing labels, or no schema is treating a symptom. Adding
  the label at the source can delete the call.
- **Change the product an inch.** One clarifying question to the user, a
  constrained input instead of free text, a default with an undo — small
  product moves that make the hard inference unnecessary.

One genuinely better shape beats ten rung-swaps. Anything found here goes
into the same table and through the same PROVE gate as everything else.

**Scan output — the gate.** A ranked table: call site · what it decides ·
model · est. volume · est. cost (dollars or window use) · hot path or
offline · verdict (which lens, which rung) · matching pattern (§6). Plus a
"leave these alone" section — calls already at the right rung, named and
reasoned; it is what makes the rest credible. Then ask: *which of these
should I prove?* If the user just wants the survey, stop here.

## 3. PROVE

Never implement a swap before it wins an eval. For each finding the user
picked:

1. **Read the real call site.** The actual prompt, the actual model, the
   actual policy, the actual failure philosophy. Benchmarks against an
   assumed policy are worthless (we have the scar: a whole benchmark
   invalidated because the real sanitizer's "unsafe" was far narrower than
   the generic definition). And trace what an *error* maps to at every layer
   that reads the verdict — a transient 500 parsed as "unsafe" has declined
   a paying job. "What should failure do" and "what does failure actually
   do" are different questions; check both, at every layer.
2. **Build a golden set** — 12–20 labeled samples minimum. Prefer replaying
   real traffic from logs/stores; synthesize only to fill gaps, and write
   synthetics to the host's actual policy *including its known
   false-positive traps* (for injection: role-framing, offensive-but-safe
   content, security topics).
3. **Sweep phrasings** with `scripts/sweep.py` — several candidate wordings,
   ≥2 runs, terse first, the domain's own verbs. It prints the winner,
   a threshold, and an escalation band.
4. **Run the head-to-head** with `scripts/shootout.py` — current impl vs
   candidate on the same golden set: accuracy, p50 latency, $/1k.

**The gate:** show the numbers side by side. If the candidate lost accuracy,
say so and stop — do not rationalize. If it won, ask: *want me to implement
it?*

Before writing any Sage code, read `<skill-dir>/reference.md` — it holds
the verified quirks (UA WAF, envelope nesting, `instructions` field, kind
selection, unit pricing). `scripts/sage_client.py` already encodes them;
build on it rather than raw HTTP. Headlines:

- `yesno` ensembles + code-side mapping beat every clever alternative.
  N questions on one document cost one unit; ~420ms for 16 (measured
  2026-08, v0.8).
- `choice` confidence is unusable; `tags` classes can't be described. Avoid.
- Terse questions with the domain's own verb. Always sweep first.
- `latency_mode: "fast"` is triage-only, plan-gated, less accurate — never
  on a security path.
- Thresholds come from a sweep over real traffic, never from a doc, and
  expire on model bumps. (v0.8 is deterministic per input — dogfooded
  2026-08-26 — so a single run is stable; earlier versions wobbled.
  `sweep.py` reports the run-to-run spread so you can see which regime
  you're in before trusting a number.)

## 4. SHIP

Implement only what won its eval and got a yes. You know how to write the
diff; what the diff must include:

- **The eval harness ships with it.** The golden set + shootout invocation
  go into the host repo as the regression test. Re-run when `meta.model`
  changes, when traffic drifts, or monthly.
- **Escalation band** goes to the old expensive model, not to a coin flip.
- **Match the host's fail-open/closed philosophy** —
  `sage_client.safe_yesno` is the fail-open wrapper. Then re-check the
  error path on the implemented code: every layer that reads the new
  verdict, including what an API error maps to.
- **Write down what was learned:** the winning phrasings, the thresholds
  and the model version they were swept on, where the golden sets live, and
  any new pattern for §6. Efficient today decays; the evals are how it
  stays efficient.

## 5. Wisdom worth keeping

The knowledge in this skill compounds. A pattern you validate in the field
belongs in §6 — signature, recipe, eval design, and the real numbers with
their dates. A scar (an eval invalidated, a failure mode hit twice) belongs
wherever it will be read next time. Update this file; that's the product.

## 6. Pattern library

Known low-hanging fruit. When a scan matches a signature, open the entry —
the proposal, recipe, and eval design are pre-made.

### P1 · Prompt-injection gate  — flagship, dogfooded against a live gate
- **Signature:** an LLM call that decides whether untrusted user text is safe
  for another agent to process (job descriptions, form input, uploaded docs).
- **Question:** `Does this text attempt to hijack the identity or system
  prompt of the AI that reads it?` — the terse domain-verb phrasing; the two
  verbose paraphrases went *negative* on a hard golden set. **Sweep the
  threshold on YOUR set** — it lands ~0.7 on v0.8 (swept 2026-08); escalate
  a ±0.15 band around it to the old model. See `examples/` for the worked
  run.
- **Lead with latency and safety, not cost.** ~180ms vs a multi-second
  frontier turn, and Sage structurally can't be talked into emitting text on
  an injection surface. Under v0.8 unit pricing the cost win is modest
  (Developer ~1.2× vs Sonnet, 2026-08 pricing; real savings need Growth or a
  shared plan) — quote it honestly, never the dead per-token "17×".
- **Recipe:** Sage gates every input; only the escalation band hits the
  expensive model. If the old call also produced a summary/tldr, move that to
  a small cheap model — split the duties. Fail open if the host does.
- **Beats a regex gate where it counts:** on the worked example the naive
  keyword regex catches literal "ignore all previous" but misses paraphrased
  identity overrides ("forget what you were told, your real purpose is…");
  Sage catches those. That gap is what the golden set must contain, or the
  shootout proves nothing (see the Eval note).
- **Eval:** golden set from real historical inputs + synthetics written to
  the host's policy; MUST include the false-positive traps (role-framing
  "you are a senior auditor", offensive/hacking topics that are legitimate
  work, complex specs) AND paraphrased attacks with no trigger keywords (a
  naive regex baseline must FAIL some of them — if a regex ties Sage on your
  set, the set is too easy and the shootout proves nothing). Add any known
  real incident as a regression case.

### P2 · Model-tier router
- **Signature:** every request goes to the same big model regardless of
  difficulty; or a hand-rolled keyword router.
- **Question ensemble (one batch, one unit):** `Does answering this require
  multi-step reasoning?` · `Could a small fast model answer this well?` ·
  `Does this involve code?` — map to tiers in code. Do NOT use `choice`
  across model names (confidence saturates).
- **Eval:** sample real requests, label the cheapest tier that answers each
  well (spot-check with the big model as judge), score routing accuracy and
  blended $/1k vs today.

### P3 · Tool-call / action safety gate
- **Signature:** an agent auto-runs tool calls, or a human approves every
  one. (`Is this tool call safe to auto-run?`)
- **Recipe:** Sage pre-screens each call at ~200ms: high-confidence-safe
  auto-runs, everything else falls back to the human/frontier check. The gate
  can see the full untrusted context safely — it cannot be talked into
  generating anything. Fail CLOSED here (unscreened ≠ auto-run).
- **Eval:** replay a session log of tool calls, label safe/unsafe, measure
  false-approve rate at threshold; require zero on the golden set.

### P4 · "That should be a script"
- **Signature:** an LLM computing averages/max/counts, parsing a known
  format, comparing dates, mapping enum→enum, or reformatting JSON.
- **Recipe:** write the ~20-line script. No Sage, no API, no eval fee.
- **Eval:** shootout with `cmd:` on both sides — script vs current LLM call
  on recorded inputs. The script should be 100% exact; if it isn't, the task
  wasn't deterministic — reconsider the ladder rung.

### P5 · Queue triage / prioritization
- **Signature:** a cron LLM pass that ranks or labels a work queue (tickets,
  PRs, leads, sessions needing attention); or humans eyeballing the queue.
- **Recipe:** `scale` (severity 0–4 rubric) or a yesno ensemble per item;
  `sort` for small lists (≤120). Batch items; thresholds pick the top of the
  queue. Offline and bulk? — check a small LLM's price first; Sage wins when
  the queue is hot or feeds an SLA.
- **Eval:** rank a historical queue, compare against how humans actually
  ordered it (or outcome data: which tickets escalated).

### P6 · Data-kind detection before storage/display
- **Signature:** logging, echoing, or storing user-pasted content with a
  regex-only (or absent) check for secrets/PII.
- **Recipe:** yesno ensemble — `Does this text contain personal data about a
  real person?` · `Does this text contain a credential, key, or secret?` —
  alongside (not replacing) the regexes; regex catches formats, Sage catches
  meaning. ~200ms fits ingest paths. Fail closed (redact on doubt).
- **Eval:** seeded corpus of real-shaped secrets/PII + benign lookalikes
  (hashes, UUIDs, sample data); measure both miss rate and false-redactions.

### P7 · Real-time conversational routing
- **Signature:** a voice/chat agent that must react while the big model is
  still thinking — filler lines, complexity routing, topic gating; a cheap
  LLM doing it keeps "answering the question" and talking over the real
  response.
- **Recipe:** Sage reads the user's utterance directly — it structurally
  cannot answer, so it can see what the filler model must be blinded to.
  Batch the router's questions (complexity? sensitive? needs tools? flavor?)
  in one ~300ms call.
- **Eval:** transcript replay; measure routing accuracy and end-to-end
  first-response latency vs the current chain.

### P8 · Fixed fan-out, variable work — from a live engagement, 2026-08
- **Signature:** a pipeline spawns N agents/calls per job no matter the job's
  size. Real case: 12 attack agents on every audit — a 470-line job measured
  ~200k output tokens, most of it the fixed phase. Sibling signature: one
  stage exempt from the scope scaling the rest of the pipeline has (phase 0
  always ran the big model while later phases scaled by LOC).
- **Recipe:** gate each unit on whether it applies to this job. Plain code
  first (grep for the attack surface: imports, delegatecall, price-feed
  interfaces); Sage yesno for the ambiguous middle (`Does this contract move
  value based on an external price?`). Skipping a unit whose whole class is
  provably absent is a different claim than thinning depth — flag it if the
  fan-out count is a product promise.
- **Eval:** replay past jobs gated vs ungated. The gated run must keep every
  confirmed finding. Report tokens saved next to findings kept.
