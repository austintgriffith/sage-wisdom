# Handoff

Session notes for whoever picks this up next. Newest entry first.

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
