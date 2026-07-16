# Task_02_Descriptive_Stats (Milestone A)

Descriptive statistics on the 2024 Facebook Presidential Ad dataset, computed
three independent ways -- pure Python, Pandas, and Polars -- plus grouped
analysis by `page_id` and by `(page_id, ad_id)`.

## Project structure

```
Task_02_Descriptive_Stats/
├── data/                    <- put the CSV here (not tracked in git)
├── pure_python_stats.py      <- stdlib only
├── pandas_stats.py
├── polars_stats.py
├── requirements.txt
├── REFLECTION.md              <- comparison of the 3 approaches + research questions
└── README.md
```

## Getting the data

Not included in this repo. Download from:

- Source: Google Drive — 2024 Facebook Political Ads

Save as:

```
data/2024_fb_ads_president_scored_anon.csv
```

**Important:** this is a *different file* from the Task 1 dataset, even
though it covers the same subject. Notable schema changes:

| Task 1 file | This file |
|---|---|
| `page_name` column present | no `page_name` column |
| `spend` / `impressions` / `estimated_audience_size` stored as range-dict strings, e.g. `"{'lower_bound': '100', 'upper_bound': '499'}"` | `estimated_spend` / `estimated_impressions` / `estimated_audience_size` are plain integers |
| no regional/demographic breakdown | adds `delivery_by_region` and `demographic_distribution`, both nested-dict-looking strings |
| `illuminating_*` topic/message columns | same columns, plus two new ones: `freefair_illuminating`, `fraud_illuminating` |

Scripts written for Task 1 will **not** run unmodified against this file.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The pure Python script needs no installation.

## Running

```bash
python pure_python_stats.py
python pandas_stats.py
python polars_stats.py
```

Each script prints, in order: dataset shape, missing-value counts, inferred
column types, numeric column stats (count/mean/min/max/std/median),
categorical column stats (count/unique/mode/top-5), then grouped analysis
by `page_id` and by `(page_id, ad_id)`.

## Summary of findings

- **246,745 rows, 41 columns.** The dataset is unusually clean --
  every column has zero missing values except `bylines` (1,009 missing,
  ~0.4%).
- **`estimated_audience_size`, `estimated_impressions`, and
  `estimated_spend` are now plain numeric columns** (unlike the Task 1
  file, where the equivalent fields were range-dict strings). This made
  the numeric-vs-categorical type inference much less eventful here --
  the real complexity moved into `delivery_by_region` and
  `demographic_distribution`, which store nested dictionaries as strings
  (region/demographic breakdowns of spend and impressions) and are
  correctly classified as categorical/text, since they aren't literal
  numbers.
- **Ad spend is concentrated in a small number of pages.** Grouping by
  `page_id` produces 4,475 groups from 246,745 rows (avg ~55 ads/page),
  but the single most active page alone accounts for 55,503 ads --
  about 22% of the entire dataset.
- **Grouping by `(page_id, ad_id)` is nearly meaningless as a
  "group"** -- `ad_id` is unique per row, so this produces 246,745
  groups from 246,745 rows (average 1.00 rows/group). This is expected
  and is itself worth noting: not every column combination that *looks*
  like a natural grouping key actually groups anything. See
  REFLECTION.md.

## Comparison of the three approaches

See [REFLECTION.md](REFLECTION.md) for the full write-up and responses
to the assigned research questions. Short version: all three approaches
produced identical numeric results (count/mean/min/max/std/median) for
every genuinely numeric column. Polars' stricter, schema-first approach
to CSV parsing is the main point of divergence in *process* (not
results) -- see REFLECTION.md for why that matters.
