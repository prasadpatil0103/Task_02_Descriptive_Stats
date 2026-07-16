# REFLECTION: Pure Python vs. Pandas vs. Polars

## Did the three approaches agree?

Yes, for every numeric column, once a few decisions were made
consistently across all three scripts:

- **Sample standard deviation (`ddof=1`/`n-1`), not population.**
  `statistics.stdev()`, `pandas.Series.std()`, and `polars.Series.std()`
  all default to the sample version, so no correction was needed -- but
  this is exactly the kind of default that would silently break
  agreement if one of the three used a different convention.
- **What counts as numeric.** All three tools agreed that
  `delivery_by_region` and `demographic_distribution` are *not*
  numeric, because their values are nested-dict-looking strings, not
  literal numbers. Polars in particular will not silently coerce a
  column like that to a numeric type -- if every value can't parse, it
  stays a string column. That happens to match what the pure-Python
  `infer_column_type()` function and Pandas' automatic dtype inference
  both decided on their own.
- **`page_id`/`ad_id` grouping.** All three approaches independently
  found the same result: 4,475 groups for `page_id`, and 246,745 groups
  (i.e., essentially one per row) for `(page_id, ad_id)`, because
  `ad_id` is unique per ad. Getting three different tools to agree on
  *group counts*, not just column stats, was a good sanity check that
  the underlying data -- not a tool quirk -- explains the pattern.

## Where the tools differ in philosophy, even when the numbers match

Pandas will read almost anything and figure out types after the fact
via `.info()`/`.describe()`; if a column mixes types, it just becomes
`object` and Pandas moves on without complaint. Polars is far more
insistent about deciding a column's type up front, and (with
`infer_schema_length=None`) it scans the *entire* column before
committing to a dtype rather than sampling the first N rows the way
Pandas can under certain read options. That stricter default is exactly
the kind of thing that matters on the Task 1 dataset, where a range
string like `"{'lower_bound': '0', 'upper_bound': '99'}"` shows up in
every row of a "spend" column -- Polars would refuse to treat that as
numeric, and would make you deal with it explicitly, whereas Pandas
would just call it `object` and let you find out later.

## Was it a challenge to produce identical results?

Less than expected for this particular file, because
`estimated_spend`/`estimated_impressions`/`estimated_audience_size` are
already plain integers here (unlike Task 1's range-dict strings). The
places where disagreement *could* have crept in were: (1) sample vs.
population standard deviation, (2) whether "0" and "0.0" are treated as
the same missing-vs-real value, and (3) whether an empty string counts
as missing. Being explicit about all three in every script is what made
the numbers match exactly rather than approximately.

## Coaching a junior analyst: which tool first?

Pure Python first, briefly -- not to use day-to-day, but because writing
`infer_column_type()` and `compute_numeric_stats()` by hand is what
makes you internalize *why* `describe()` gives the numbers it gives.
After that, **Pandas** for daily work: the ecosystem, documentation, and
Stack Overflow coverage are enormous, and most collaborators will
already know it. **Polars** is worth learning once you're hitting
Pandas' performance ceiling or want its stricter type discipline to
catch data-quality issues earlier -- which, on messier files like the
Task 1 dataset, would have surfaced the range-string columns
immediately instead of quietly downstream.

## Did AI coding tools produce useful starter code?

These three scripts were drafted with AI assistance (Claude), which is
directly relevant to this question. A few honest observations from that
process:

- The AI defaulted to `pandas.DataFrame.describe()` as the go-to for
  "give me summary statistics" -- a reasonable default, but one that
  silently skips non-numeric columns unless you pass
  `include="all"`, which is easy to miss if you don't already know to
  ask for it.
- For Polars, the AI's first instinct was to check column dtypes with
  `dtype.is_numeric()`, which is not reliably available across Polars
  versions; a more robust and current approach is
  `polars.selectors.numeric()`. This is a good example of an AI tool
  producing code that *looks* idiomatic but is quietly using an
  API surface that may not exist on the version you actually have
  installed -- worth checking against the current docs rather than
  trusting on faith.
- **The Polars script in this repo could not be executed in the
  environment it was written in** (no network access to install the
  `polars` package there), so its numeric output has not been verified
  against the pure-Python/Pandas results the way the other two scripts
  were. Please run `polars_stats.py` yourself and confirm its numbers
  match `pandas_stats.py` before trusting it -- this is exactly the
  kind of verification step the assignment is asking you to build the
  habit of doing with AI-generated code, and it applies here too.

## Complex-value columns and what they required

`delivery_by_region`, `demographic_distribution`, `illuminating_mentions`,
and `publisher_platforms` all store Python-literal-looking strings
(dicts or lists) rather than flat values. None of the three scripts
parses these into structured data -- they're treated as opaque
categorical strings, which is enough for count/unique/mode/top-5, but
not enough to answer a question like "which region got the most ad
spend?" Doing that would require `ast.literal_eval()` (pure Python),
`df[col].apply(ast.literal_eval)` (Pandas), or a custom parsing
expression (Polars), and is flagged here as a natural next step rather
than solved in this milestone.
