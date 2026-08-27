# sage-wisdom

![sage intro](scripts/sage-intro-preview.gif)

A skill for your coding agent. Point it at any repo that calls LLMs and it
finds the decisions that should be cheaper, faster, or more deterministic —
then **proves each fix with an eval before shipping it**.

> First effective, then efficient. First you make the thing work, then you
> ask "what did we learn?" and make it work better.

## Use it

Tell your agent (Claude Code, Cursor, etc.):

```
Clone https://github.com/clawdbotatg/sage-wisdom and follow its SKILL.md
to audit this repo.
```

Or install it as a local skill: copy this directory into your skills folder
(e.g. `.claude/skills/sage-wisdom/`).

The audit and plain-code fixes need no API key. Proving a Sage fix does —
the eval runs against [Levanto Sage](https://docs.levanto.ai) (`SAGE_API_KEY`
env var, plans from $14/mo at
[platform.levanto.ai](https://platform.levanto.ai)).

## What's inside

- `SKILL.md` — the skill: a three-stage engagement (scan → prove → ship,
  the user decides at each gate), three scan lenses (delete/cache/batch the
  call · make it deterministic · the descent ladder), a rethink pass that
  questions the pipeline's shape, and a pattern library of known wins
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
