"""
pure_python_stats.py -- Milestone A (Task 2)

Descriptive statistics on the 2024 Facebook Presidential Ad dataset,
using ONLY the Python standard library, PLUS grouped analysis by
page_id and by (page_id, ad_id).

Run:
    python pure_python_stats.py

Expects the dataset at ./data/2024_fb_ads_president_scored_anon.csv

NOTE: this is a different file than the one used in Task 1. Same
subject (2024 presidential FB ads) but a different schema -- e.g.
estimated_spend/estimated_impressions/estimated_audience_size are now
plain integers instead of "{'lower_bound': ..., 'upper_bound': ...}"
range strings, and there is no page_name column. See README.md /
REFLECTION.md for more on what changed and why it mattered.
"""

import csv
import statistics
from collections import Counter, defaultdict

DATA_PATH = "data/2024_fb_ads_president_scored_anon.csv"

MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan"}

GROUP_KEY_PRIMARY = ["page_id"]
GROUP_KEY_COMPOUND = ["page_id", "ad_id"]


# ----------------------------------------------------------------------
# Basic helpers (same approach as Task 1)
# ----------------------------------------------------------------------

def is_missing(value):
    return value is None or value.strip().lower() in MISSING_TOKENS


def try_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    return rows, fieldnames


def infer_column_type(values):
    """
    'numeric' if every non-missing value parses as a float, else
    'categorical'. Columns like delivery_by_region / demographic_distribution
    store nested-dict-looking strings and will (correctly) come out
    categorical, because they are not literally numbers.
    """
    non_missing = [v for v in values if not is_missing(v)]
    if not non_missing:
        return "empty"
    numeric_count = sum(1 for v in non_missing if try_float(v) is not None)
    return "numeric" if numeric_count == len(non_missing) else "categorical"


def compute_numeric_stats(values):
    numbers = [n for n in (try_float(v) for v in values if not is_missing(v)) if n is not None]
    stats = {"count": len(numbers), "mean": None, "min": None, "max": None,
             "std": None, "median": None}
    if not numbers:
        return stats
    stats["mean"] = sum(numbers) / len(numbers)
    stats["min"] = min(numbers)
    stats["max"] = max(numbers)
    stats["median"] = statistics.median(numbers)
    stats["std"] = statistics.stdev(numbers) if len(numbers) > 1 else 0.0
    return stats


def compute_categorical_stats(values):
    clean = [v for v in values if not is_missing(v)]
    stats = {"count": len(clean), "unique": 0, "mode": None, "mode_freq": 0, "top5": []}
    if not clean:
        return stats
    counts = Counter(clean)
    stats["unique"] = len(counts)
    top5 = counts.most_common(5)
    stats["top5"] = top5
    stats["mode"], stats["mode_freq"] = top5[0]
    return stats


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ----------------------------------------------------------------------
# Grouped analysis
# ----------------------------------------------------------------------

def group_rows(rows, key_cols):
    """Return {tuple(key values): [rows...]}."""
    groups = defaultdict(list)
    for row in rows:
        key = tuple(row.get(k, "") for k in key_cols)
        groups[key].append(row)
    return groups


def summarize_group(group_rows_list, numeric_cols):
    """Small per-group summary: row count + mean of each numeric column."""
    summary = {"n_rows": len(group_rows_list)}
    for col in numeric_cols:
        values = [row.get(col, "") for row in group_rows_list]
        s = compute_numeric_stats(values)
        summary[col] = s["mean"]
    return summary


def run_grouped_analysis(rows, key_cols, numeric_cols, top_n=10):
    groups = group_rows(rows, key_cols)
    n_groups = len(groups)
    print(f"\nGrouping by {key_cols}: {n_groups} groups from {len(rows)} rows "
          f"(avg {len(rows) / n_groups:.2f} rows/group)")

    # Rank groups by number of rows (a reasonable default "interesting" sort)
    ranked = sorted(groups.items(), key=lambda kv: len(kv[1]), reverse=True)

    print(f"\nTop {top_n} groups by row count:")
    header = " | ".join(key_cols) + " | n_rows | " + " | ".join(f"mean_{c}" for c in numeric_cols)
    print(f"  {header}")
    for key, grp in ranked[:top_n]:
        summary = summarize_group(grp, numeric_cols)
        key_str = " | ".join(str(k) for k in key)
        means_str = " | ".join(
            f"{summary[c]:.2f}" if summary[c] is not None else "NA" for c in numeric_cols
        )
        print(f"  {key_str} | {summary['n_rows']} | {means_str}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    rows, fieldnames = load_rows(DATA_PATH)
    total_rows = len(rows)
    total_cols = len(fieldnames)
    columns = {name: [row.get(name, "") for row in rows] for name in fieldnames}

    print_section("DATASET OVERVIEW")
    print(f"Total rows:    {total_rows}")
    print(f"Total columns: {total_cols}")

    missing_counts = {}
    inferred_types = {}
    for name in fieldnames:
        values = columns[name]
        missing_counts[name] = sum(1 for v in values if is_missing(v))
        inferred_types[name] = infer_column_type(values)

    print("\nMissing values per column:")
    for name in fieldnames:
        print(f"  {name:45s} missing={missing_counts[name]:>7}  "
              f"inferred_type={inferred_types[name]}")

    numeric_cols = [n for n in fieldnames if inferred_types[n] == "numeric"]

    print_section("NUMERIC COLUMNS")
    for name in numeric_cols:
        s = compute_numeric_stats(columns[name])
        print(f"\n-- {name} --")
        print(f"  count : {s['count']}")
        print(f"  mean  : {s['mean']}")
        print(f"  min   : {s['min']}")
        print(f"  max   : {s['max']}")
        print(f"  std   : {s['std']}")
        print(f"  median: {s['median']}")

    print_section("CATEGORICAL COLUMNS")
    for name in fieldnames:
        if inferred_types[name] not in ("categorical", "empty"):
            continue
        s = compute_categorical_stats(columns[name])
        print(f"\n-- {name} --")
        print(f"  count       : {s['count']}")
        print(f"  unique      : {s['unique']}")
        print(f"  mode        : {s['mode']!r} (freq={s['mode_freq']})")
        print("  top 5 values:")
        for value, freq in s["top5"]:
            display = value if len(value) <= 60 else value[:57] + "..."
            print(f"    {display!r:65s} freq={freq}")

    # A small, representative slice of numeric columns for the grouped
    # summaries below -- printing the mean of all ~29 numeric columns per
    # group would be unreadable, so we focus on the columns a researcher
    # would actually care about.
    headline_numeric = [c for c in
                         ["estimated_audience_size", "estimated_impressions", "estimated_spend"]
                         if c in numeric_cols]

    print_section("GROUPED ANALYSIS: by page_id")
    run_grouped_analysis(rows, GROUP_KEY_PRIMARY, headline_numeric)

    print_section("GROUPED ANALYSIS: by (page_id, ad_id)")
    print(
        "\nNote: ad_id is unique per row, so grouping by (page_id, ad_id) "
        "produces (almost) one group per row -- this is expected, and is "
        "itself a useful thing to notice about the data's structure. See "
        "REFLECTION.md."
    )
    run_grouped_analysis(rows, GROUP_KEY_COMPOUND, headline_numeric)


if __name__ == "__main__":
    main()
