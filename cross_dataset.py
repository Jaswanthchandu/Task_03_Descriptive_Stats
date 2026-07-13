
import os
import sys
import pandas as pd

MISSING_TOKENS = ["", "NA", "N/A", "null", "NULL", "None", "NaN", "-"]


def load(path):
    return pd.read_csv(path, na_values=MISSING_TOKENS, low_memory=False)


def clean_numeric(series):
    stripped = (series.astype(str)
                      .str.replace(r"[$,%]", "", regex=True)
                      .str.strip())
    return pd.to_numeric(stripped, errors="coerce")


def main():
    if len(sys.argv) != 4:
        print("Usage: python cross_dataset.py <ads.csv> <fb_posts.csv> <tw_posts.csv>")
        sys.exit(1)

    names = ["Ads", "FB_Posts", "TW_Posts"]
    frames = {n: load(p) for n, p in zip(names, sys.argv[1:4])}

    print("=" * 72)
    print("CROSS-DATASET COLUMN COMPARISON")
    print("=" * 72)
    for n, df in frames.items():
        print(f"{n:<10} {df.shape[0]:>8,} rows   {df.shape[1]:>3} columns")

    # Columns shared by ALL three.
    col_sets = [set(df.columns) for df in frames.values()]
    shared = sorted(set.intersection(*col_sets))
    print(f"\nColumns shared by all three datasets: {len(shared)}")
    for c in shared:
        print(f"  {c}")

    # Unique-to-one-dataset columns (for context).
    for n, df in frames.items():
        others = set.union(*[set(f.columns) for m, f in frames.items() if m != n])
        only = sorted(set(df.columns) - others)
        print(f"\nColumns unique to {n} ({len(only)}):")
        for c in only:
            print(f"  {c}")

    # Compare means of shared columns that are numeric in all three.
    print("\n" + "=" * 72)
    print("SHARED NUMERIC COLUMNS - mean by platform")
    print("(flags are 0/1, so mean = share of items with that trait)")
    print("=" * 72)
    print(f"{'column':<44} {'Ads':>10} {'FB_Posts':>10} {'TW_Posts':>10}")
    print("-" * 76)
    for c in shared:
        means = {}
        numeric_everywhere = True
        for n, df in frames.items():
            vals = clean_numeric(df[c]).dropna()
            if len(vals) == 0 or clean_numeric(df[c]).notna().mean() < 0.8:
                numeric_everywhere = False
                break
            means[n] = vals.mean()
        if numeric_everywhere:
            label = c if len(c) <= 42 else c[:39] + "..."
            print(f"{label:<44} {means['Ads']:>10.4f} "
                  f"{means['FB_Posts']:>10.4f} {means['TW_Posts']:>10.4f}")


if __name__ == "__main__":
    main()
