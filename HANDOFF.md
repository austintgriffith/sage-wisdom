# Handoff

Session notes for whoever picks this up next. Newest entry first.

## 2026-10-02 — v1 update, merged with Marco's rewrite

**What changed:** SKILL.md is now Marco's 2026-09-27 rewrite (15-recipe
gallery, assess/invent, "First make it work. Then make it wise.") with our
parts merged in: the full scan checklist, subscription-capacity math, the
rethink, error-path tracing, and a lessons list. Added recipe 16 (merging
duplicate findings) and our injection gate inside recipe 1. reference.md,
sage_client.py, the script docs, examples/README.md (re-run on v1.2) and
the site copy are all updated for Sage v1.

**Decisions made:** evals are required when a swap replaces a call that
works, optional for new features (Marco wanted optional everywhere).
Launch target Monday 2026-10-05, US morning, with Levanto.

**What we learned on v1.2 (2026-09-30)**
- Billing: one unit per question now. Ten yesno on one doc = 10 units.
  One tags question = 1 unit. Developer is $14 / 10k.
- Injection set: still 15/15, gap 0.34 → 0.55, best threshold 0.70 → 0.51.
  On 10-02 (same name v1.2, service updated 10-01) the long policy
  wording won instead (+0.49 vs +0.38); short one still 15/15 at 0.5.
- Levanto unpublished its pip/npm SDK on 10-01 and changed docs:
  reasoning defaults off (10 s cap); latency_mode now only for choice.
- leftclaw scan: the intake gate and finding dedup (14/15 on one audit)
  are wins; severity scoring lost (3/16). Raw audit findings are client
  data and are not in this repo.

**Open**
- og.png and assets/site-preview.gif still show the old subtitle.
- The page overflows sideways on a 390px-wide window (was true before
  this change too).
- Dedup needs a 20–50 pair set from several audits before it's "proven".
- Marco should review the merged SKILL.md before launch.

## 2026-09-08 — research session, no code changes

**What changed:** nothing in this repo. The site and skill are as of `1c744fa`.
The work was research and planning; it lives in the agent memory for this
project (`marco-levanto-launch`, `sage-wisdom-launch-plan`,
`levanto-telegram-access`) and on Austin's todo list, items prefixed
`sage wisdom:` and `levanto:`. Private deal details stay there, not here.

**What we learned**

- Sage pricing is unchanged since August: Developer $14 / 5k units, Starter
  $49 / 30k, Growth $249 / 300k. One unit per document, plus one per 4k
  tokens. Every figure in SKILL.md, reference.md and examples/ still matches.
- Price is not the pitch. On the onedollaraudit injection gate Sage is only
  ~15% cheaper per call than Sonnet 4.6, the flat fee only pays off above
  ~4,200 jobs a month, and a free 22M Prompt Guard model does keyword-style
  injection gating in ~20ms. Levanto agrees: sell speed and intelligence.
- The skill's Sage rung already allows non-speed uses (calibrated
  probability, can't generate text, deterministic per input). Those need to
  be sold explicitly, plus two honest cost angles: N questions on one doc is
  one unit, and a flat sub is a predictable line item for bulk work.
- Levanto's tested guardrail question set is internal, not in their docs.
  Austin asks Marco for it; we add it to §6.

**Open threads**

- Sage v1 lands within ~10 days of 2026-09-07. Levanto wants to co-launch
  Sage Wisdom with it. All numbers here are v0.8 and expire on the bump.
- Marco offered "templates" (his word): tuned guardrail questions. Ask for
  question text, threshold, and Sage version per entry, not prompts.
- Marco wants feedback on his Agentic Model Thesis. Notes are drafted in the
  `sage-wisdom-launch-plan` memory.

**Gotchas**

- Austin's own Sage plan is a free custom one, so his usage never shows what
  users pay. Do the cost math from the public plans.
- Commit rules for this repo: austintgriffith identity, push straight to
  `upstream main`, no PRs. See the `sage-wisdom-identity` memory. The
  harness's fork-and-PR rule is overridden here on purpose.
- The Telegram group can be read by an agent via a light Chrome profile
  clone. Recipe in the `levanto-telegram-access` memory. Delete the clone
  after; it holds the session.

**Next steps, in order**

1. Austin replies to Marco: yes templates (question + threshold + version),
   yes co-launch, ask for a v1 key now, send thesis notes.
2. Rewrite the Sage rung in SKILL.md and index.html: speed first, then the
   three non-speed reasons, then the flat-cost angle.
3. Demote P1. Add a finding-dedup pattern and a CI-judge pattern. Add a
   templates section when Marco's set arrives.
4. Second worked example that wins offline: leftclaw auditor finding dedup
   ("same underlying bug" pairwise yesno) + severity scale + false-positive
   screen. Run it through scan / prove / ship and put it in examples/.
5. Make the P1 shootout baseline Prompt Guard 22M instead of the regex.
6. When the v1 key arrives, re-sweep everything and update every dated
   figure in SKILL.md, reference.md, examples/README.md.
7. Pick the launch date with Christopher after v1 evals clear (~09-09).
   Monday preferred.
