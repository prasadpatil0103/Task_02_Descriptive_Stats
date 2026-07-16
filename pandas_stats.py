"""
pandas_stats.py -- Milestone A (Task 2)

Same analysis as pure_python_stats.py, using Pandas: dataset-level
descriptive statistics plus grouped analysis by page_id and by
(page_id, ad_id).

Run:
    python pandas_stats.py

Expects the dataset at ./data/2024_fb_ads_president_scored_anon.csv
"""

import pandas as pd

DATA_PATH = "data/2024_fb_ads_president_scored_anon.csv"

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 140)


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    df = pd.read_csv(DATA_PATH, low_memory=False)

    print_section("SHAPE & DTYPES")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    df.info()

    print_section("MISSING VALUES PER COLUMN")
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    print(pd.DataFrame({"missing_count": missing_count, "missing_pct": missing_pct}))

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

    print_section("DESCRIBE (NUMERIC COLUMNS)")
    print(df[numeric_cols].describe())

    print_section("DESCRIBE (ALL COLUMNS, include='all')")
    print(df.describe(include="all").T)

    print_section("CATEGORICAL COLUMNS: value_counts() / nunique()")
    for col in categorical_cols:
        print(f"\n-- {col} --")
        print(f"  nunique: {df[col].nunique(dropna=True)}")
        print(df[col].value_counts().head(5).to_string())

    print_section("NUMERIC COLUMNS: cross-check vs pure_python_stats.py")
    for col in numeric_cols:
        s = df[col]
        print(f"\n-- {col} --")
        print(f"  count={s.count()}  mean={s.mean()}  min={s.min()}  "
              f"max={s.max()}  std={s.std()}  median={s.median()}")

    headline_numeric = [c for c in
                         ["estimated_audience_size", "estimated_impressions", "estimated_spend"]
                         if c in numeric_cols]

    print_section("GROUPED ANALYSIS: by page_id")
    grouped = df.groupby("page_id").agg(
        n_rows=("ad_id", "count"),
        **{f"mean_{c}": (c, "mean") for c in headline_numeric},
    )
    print(f"Number of groups: {grouped.shape[0]}")
    print("\nTop 10 pages by ad count:")
    print(grouped.sort_values("n_rows", ascending=False).head(10))

    print_section("GROUPED ANALYSIS: by (page_id, ad_id)")
    print(
        "Note: ad_id is unique per row, so this grouping produces "
        "(almost) one group per row. See REFLECTION.md."
    )
    grouped2 = df.groupby(["page_id", "ad_id"]).agg(
        n_rows=("ad_id", "count"),
        **{f"mean_{c}": (c, "mean") for c in headline_numeric},
    )
    print(f"Number of groups: {grouped2.shape[0]} (dataset has {len(df)} rows)")
    print("\nFirst 10 groups:")
    print(grouped2.head(10))


if __name__ == "__main__":
    main()
