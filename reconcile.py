#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json

# txn_id -> latest event seen for that payment
latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  # truncated / corrupt line

        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        # ts is ISO 8601 UTC with the same format everywhere, so string compare works
        prev = latest.get(txn_id)
        if prev is None or event["ts"] > prev["ts"]:
            latest[txn_id] = event


def parse_amount(value):
    # some amounts come through as strings like "12,345.67"
    if isinstance(value, str):
        value = value.replace(",", "")
    return float(value)


total = 0.0
count = 0
for event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
