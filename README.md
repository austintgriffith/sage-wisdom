# Sage Wisdom

![sagewisdom.bot](assets/site-preview.gif)

**[sagewisdom.bot](https://sagewisdom.bot)** — a skill for your coding agent.
It finds the decisions in your AI pipeline that should be cheaper, faster, or
more deterministic — then **proves each fix with an eval before shipping it**.

> First effective, then efficient. First you make the thing work, then you
> ask "what did we learn?" and make it work better.

## Use it

Paste this into a Claude Code or Codex session in your project folder:

```
Read https://sagewisdom.bot/SKILL.md and follow the steps to audit this repo's ai pipeline.
```

Or install it as a local skill: copy this directory into your skills folder
(e.g. `.claude/skills/sage-wisdom/`).

The audit and plain-code fixes need no API key. Proving a Sage fix does —
the eval runs against [Levanto Sage](https://docs.levanto.ai) (`SAGE_API_KEY`
env var, plans from $14/mo at
[platform.levanto.ai](https://platform.levanto.ai)).

## What is Sage?

![sage intro](scripts/sage-intro-preview.gif)

[Levanto Sage](https://docs.levanto.ai) is a classifier+LLM decision API. You
ask it enumerable judgment questions — yes/no, a score, a pick, a label — and
it answers in ~200ms with a calibrated probability. It structurally cannot
generate text, which makes it safe to point at untrusted input. The skill
walks every model call in your repo down the descent ladder and finds where
it fits:

```
frontier llm  →  small llm  →  sage  →  plain code
```

## What's inside

- `SKILL.md` — the skill: a three-stage engagement (scan → prove → ship,
  the user decides at each gate), three scan lenses (delete/cache/batch the
  call · make it deterministic · the descent ladder), a rethink pass that
  questions the pipeline's shape, and a pattern library of known wins
- `index.html` + assets — the [sagewisdom.bot](https://sagewisdom.bot) site
  (static, deploys on Vercel; serves `SKILL.md` alongside the page)
- `scripts/sage_client.py` — minimal stdlib Sage client, quirks pre-paid
- `scripts/sweep.py` — sweep question phrasings against a golden set
- `scripts/shootout.py` — current impl vs candidate, head to head
- `scripts/sage-intro.sh` — the animated intro above. Human-only eye candy:
  it needs a real TTY, so agents can't run it — run it yourself in a plain
  terminal
- `reference.md` — field notes on the Sage API, verified live on v0.8
- `examples/` — a worked run of the whole loop against a live production
  injection gate: golden set, regex baseline, and the real sweep/shootout
  numbers. Start here to see what an engagement produces.
