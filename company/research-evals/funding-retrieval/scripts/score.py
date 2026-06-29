#!/usr/bin/env python3
"""
Score each API's funding answers against the golden (Crunchbase) values.

Reads data/golden_set.csv (the 100-company set with the golden total-funding value
and each API's returned value) and writes results/scorecard.csv:

    api, within_10, within_25, within_50, median_err, coverage, n

Methodology (matches the published benchmark):
- error = |api - golden| / golden
- The committed golden_set.csv is already the 93-company comparison set: the subset of
  an original 100 where the reference engine (Linkup) returned a number, with Linkup's
  7 blanks cut so all four engines are scored on the exact same rows. The --reference
  flag re-applies that cut and is a no-op on the committed data.
- within_X = share of the set whose error <= X% (an API blank counts as a miss).
- median_err = median error over the rows where the API returned a number.
- coverage = share of the set where the API returned any number.

Note: golden_set.csv stores values rounded to whole $M (as in the published run
table), while the official scorecard (results/scorecard.csv) was scored on the raw
API floats. Recomputing here therefore lands within ~a few points of the official
card; it is a transparency/verification tool, not a second source of truth.

Usage:
  python3 score.py                 # uses ../data/golden_set.csv -> ../results/scorecard.csv
  python3 score.py --in path.csv --out path.csv --reference linkup
"""
import argparse
import csv
import os
import re
import statistics

APIS = ["linkup", "exa", "perplexity", "parallel"]
HERE = os.path.dirname(os.path.abspath(__file__))


def parse_musd(s):
    """Parse a funding string like '$71M', '$1.50B', '$0M', '—' into millions USD.

    Returns None when no number was returned ('—' / blank).
    """
    if s is None:
        return None
    s = s.strip().replace(",", "")
    if s in ("", "—", "-", "N/A", "na"):
        return None
    m = re.match(r"^\$?\s*([0-9]*\.?[0-9]+)\s*([MBK]?)", s, re.IGNORECASE)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).upper()
    if unit == "B":
        val *= 1000.0          # billions -> millions
    elif unit == "K":
        val /= 1000.0          # thousands -> millions
    return val                  # 'M' or no unit assumed millions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=os.path.join(HERE, "..", "data", "golden_set.csv"))
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "scorecard_recomputed.csv"))
    ap.add_argument("--reference", default="linkup",
                    help="cut rows where this engine returned no number (default: linkup)")
    args = ap.parse_args()

    with open(args.inp, newline="") as f:
        rows = list(csv.DictReader(f))

    # Scored subset: golden present AND the reference engine returned a number.
    subset = [r for r in rows
              if parse_musd(r["golden"]) is not None
              and parse_musd(r[args.reference]) is not None]
    n = len(subset)

    cards = []
    for api in APIS:
        errors = []                 # errors where the API returned a number
        within = {10: 0, 25: 0, 50: 0}
        returned = 0
        for r in subset:
            golden = parse_musd(r["golden"])
            val = parse_musd(r[api])
            if val is None:
                continue            # blank -> counts against the bands, excluded from median
            returned += 1
            err = abs(val - golden) / golden
            errors.append(err)
            for band in within:
                if err <= band / 100.0:
                    within[band] += 1
        cards.append({
            "api": api,
            "within_10": round(100 * within[10] / n),
            "within_25": round(100 * within[25] / n),
            "within_50": round(100 * within[50] / n),
            "median_err": round(100 * statistics.median(errors)) if errors else "",
            "coverage": round(100 * returned / n),
            "n": n,
        })

    cards.sort(key=lambda c: c["within_25"], reverse=True)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fields = ["api", "within_10", "within_25", "within_50", "median_err", "coverage", "n"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(cards)

    print(f"Scored n={n} (rows where golden and {args.reference} both present)\n")
    hdr = f"{'API':<12}{'≤10%':>7}{'≤25%':>7}{'≤50%':>7}{'median':>8}{'cover':>7}"
    print(hdr)
    print("-" * len(hdr))
    for c in cards:
        print(f"{c['api']:<12}{c['within_10']:>6}%{c['within_25']:>6}%"
              f"{c['within_50']:>6}%{str(c['median_err'])+'%':>8}{c['coverage']:>6}%")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
