"""
polars_stats.py -- Milestone A (Task 2)

Same analysis as pure_python_stats.py / pandas_stats.py, using Polars:
dataset-level descriptive statistics plus grouped analysis by page_id
and by (page_id, ad_id).

Run:
    python polars_stats.py

Expects the dataset at ./data/2024_fb_ads_president_scored_anon.csv

A note on Polars vs. Pandas, up front: Polars enforces strict column
types on read. If any value in a column that otherwise looks numeric
fails to parse, Polars will not silently coerce the whole column to
float/object the way Pandas can -- it will either raise, or (with
`infer_schema_length`/`ignore_errors`) fall back to a string dtype for
that column. This script uses `infer_schema_length=None` (scan the
whole file before deciding types) so both libraries make the same
type decision for every column, which matters for the "do the results
match?" question in REFLECTION.md.
"""

import polars as pl
import polars.selectors as cs

DATA_PATH = "data/2024_fb_ads_president_scored_anon.csv"

pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_width_chars(160)


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    # infer_schema_length=None => scan every row before picking a dtype,
    # instead of Polars' default of only sampling the first N rows. This
    # avoids a column being typed as Int64 from the first 100 rows and
    # then blowing up (or silently downgrading) if a later row contains
    # a non-numeric value.
    df = pl.read_csv(DATA_PATH, infer_schema_length=None)

    print_section("SHAPE & SCHEMA")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(df.schema)

    print_section("MISSING / NULL VALUES PER COLUMN")
    null_counts = df.null_count()
    n = df.shape[0]
    for col in df.columns:
        cnt = null_counts[col][0]
        pct = round(cnt / n * 100, 2)
        print(f"  {col:45s} missing={cnt:>7}  pct={pct}%")

    numeric_cols = df.select(cs.numeric()).columns
    categorical_cols = [c for c in df.columns if c not in numeric_cols]

    print_section("DESCRIBE (NUMERIC COLUMNS)")
    print(df.select(numeric_cols).describe())

    print_section("DESCRIBE (ALL COLUMNS)")
    print(df.describe())

    print_section("CATEGORICAL COLUMNS: value_counts() / n_unique()")
    for col in categorical_cols:
        print(f"\n-- {col} --")
        print(f"  n_unique: {df[col].n_unique()}")
        print(df[col].value_counts(sort=True).head(5))

    print_section("NUMERIC COLUMNS: cross-check vs pure_python_stats.py / pandas_stats.py")
    for col in numeric_cols:
        s = df[col].drop_nulls()
        print(f"\n-- {col} --")
        print(f"  count={s.len()}  mean={s.mean()}  min={s.min()}  "
              f"max={s.max()}  std={s.std()}  median={s.median()}")

    headline_numeric = [c for c in
                         ["estimated_audience_size", "estimated_impressions", "estimated_spend"]
                         if c in numeric_cols]

    print_section("GROUPED ANALYSIS: by page_id")
    grouped = (
        df.group_by("page_id")
        .agg(
            [pl.len().alias("n_rows")]
            + [pl.col(c).mean().alias(f"mean_{c}") for c in headline_numeric]
        )
        .sort("n_rows", descending=True)
    )
    print(f"Number of groups: {grouped.shape[0]}")
    print("\nTop 10 pages by ad count:")
    print(grouped.head(10))

    print_section("GROUPED ANALYSIS: by (page_id, ad_id)")
    print(
        "Note: ad_id is unique per row, so this grouping produces "
        "(almost) one group per row. See REFLECTION.md."
    )
    grouped2 = (
        df.group_by(["page_id", "ad_id"])
        .agg(
            [pl.len().alias("n_rows")]
            + [pl.col(c).mean().alias(f"mean_{c}") for c in headline_numeric]
        )
    )
    print(f"Number of groups: {grouped2.shape[0]} (dataset has {df.shape[0]} rows)")
    print("\nFirst 10 groups:")
    print(grouped2.head(10))


if __name__ == "__main__":
    main()
