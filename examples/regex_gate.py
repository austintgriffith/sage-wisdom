#!/usr/bin/env python3
"""Naive keyword-regex injection gate — the cheap baseline for the shootout.
Reads text on stdin. Exit 0 = "safe/no", 1 = "unsafe/yes" (shootout's
convention). It exists to be beaten: it catches literal trigger phrases and
misses everything paraphrased, which is the whole point of the P1 golden set.
"""
import sys

TRIGGERS = [
    "ignore all previous", "ignore previous", "you are now", "you are no longer",
    "system:", "system override", "disregard", "dan",
]

text = sys.stdin.read().lower()
sys.exit(1 if any(t in text for t in TRIGGERS) else 0)
