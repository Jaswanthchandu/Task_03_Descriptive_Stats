"""
pandas_stats.py  (Task 3 - generalized)

Same generalized analysis as the pure-Python version, using pandas. Works on any
CSV; grouping column(s) passed on the command line.

Usage:
    python pandas_stats.py <file.csv> [group_by]
      group_by: optional, comma-separated column names.
"""

import os
import sys
import pandas as pd

MISSING_TOKENS = ["", "NA", "N/A", "null", "NULL", "None", "NaN", "-"]
TOP_N = 15


def clean_numeric(series):
    stripped = (series.astype(str)
                      .str.replace(r"[$,%]", "", regex=True)
                      .str.strip())
    return pd.to_numeric(stripped, errors="coerce")


def main():
    if len(sys.argv) < 2:
        print("Usage: python pandas_stats.py <file.csv> [group_by]")
        sys.exit(1)
    path = sys.argv[1]
    group_cols = sys.argv[2].split(",") if len(sys.argv) > 2 else []

    df = pd.read_csv(path, na_values=MISSING_TOKENS, keep_default_na=True,
                     low_memory=False)
    group_cols = [c for c in group_cols if c in df.columns]

    print("=" * 72)
    print(f"DATASET: {os.path.basename(path)}")
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print("=" * 72)

    numeric_cols, categorical_cols = [], []
    for col in df.columns:
        non_null = df[col].dropna()
        if len(non_null) == 0:
            categorical_cols.append(col)
        elif clean_numeric(non_null).notna().mean() >= 0.8:
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    print("\nCOLUMN OVERVIEW (missing | type)")
    print("-" * 72)
    for col in df.columns:
        miss = int(df[col].isna().sum())
        pct = miss / len(df) * 100
        label = col if len(col) <= 48 else col[:45] + "..."
        ctype = "numeric" if col in numeric_cols else "categorical"
        print(f"{label:<50} {miss:>7,} ({pct:4.1f}%) {ctype}")

    print("\nNUMERIC COLUMNS (dataset level)")
    print("-" * 72)
    num_clean = {}
    for col in numeric_cols:
        num_clean[col] = clean_numeric(df[col])
        nums = num_clean[col].dropna()
        print(f"\n{col}")
        print(f"  count={nums.count():,}  mean={nums.mean():,.4f}  median={nums.median():,.4f}")
        print(f"  min={nums.min():,.4f}  max={nums.max():,.4f}  std={nums.std():,.4f}")

    print("\nCATEGORICAL COLUMNS (dataset level)")
    print("-" * 72)
    for col in categorical_cols:
        s = df[col].dropna().astype(str)
        vc = s.value_counts()
        if len(vc) == 0:
            continue
        print(f"\n{col}")
        print(f"  count={s.count():,}  unique={s.nunique():,}  "
              f"mode='{str(vc.index[0])[:50]}' (x{int(vc.iloc[0]):,})")
        for value, freq in vc.head(5).items():
            disp = str(value) if len(str(value)) <= 55 else str(value)[:52] + "..."
            print(f"    {int(freq):>8,}  {disp}")

    if group_cols:
        num_map = {col: col + "__num" for col in numeric_cols}
        for col in numeric_cols:
            df[num_map[col]] = num_clean[col]
        g = df.groupby(group_cols)
        sizes = g.size()
        means = g[[num_map[col] for col in numeric_cols]].mean()
        print("\n" + "=" * 72)
        print(f"GROUPED BY {', '.join(group_cols)}")
        print("=" * 72)
        print(f"Unique groups: {len(sizes):,}")
        print(f"Rows per group: min={sizes.min():,}  "
              f"median={sizes.median():,.1f}  max={sizes.max():,}")
        top_keys = sizes.sort_values(ascending=False).head(TOP_N).index
        print(f"\nTop {TOP_N} groups by row count (mean of each numeric column):")
        for key in top_keys:
            key_disp = " | ".join(str(k)[:20] for k in (key if isinstance(key, tuple) else (key,)))
            print(f"\n  {key_disp}  (rows={int(sizes[key]):,})")
            row_means = [f"{col}={means.loc[key, num_map[col]]:,.2f}" for col in numeric_cols]
            for i in range(0, len(row_means), 3):
                print("    " + "  ".join(row_means[i:i + 3]))
    else:
        print("\n(No group_by column provided - dataset-level statistics only.)")


if __name__ == "__main__":
    main()
