"""
polars_stats.py  (Task 3 - generalized)

Same generalized analysis using Polars. Works on any CSV; grouping column(s)
passed on the command line. Reads all columns as strings then casts, so type
handling matches the pure-Python and pandas versions.

Install:  pip install polars
Usage:    python polars_stats.py <file.csv> [group_by]
"""

import os
import sys
import polars as pl

MISSING_TOKENS = ["", "NA", "N/A", "null", "NULL", "None", "NaN", "-"]
TOP_N = 15


def clean_numeric_expr(col):
    return (pl.col(col)
              .str.replace_all(r"[$,%]", "")
              .str.strip_chars()
              .cast(pl.Float64, strict=False))


def main():
    if len(sys.argv) < 2:
        print("Usage: python polars_stats.py <file.csv> [group_by]")
        sys.exit(1)
    path = sys.argv[1]
    group_cols = sys.argv[2].split(",") if len(sys.argv) > 2 else []

    df = pl.read_csv(path, infer_schema_length=0, null_values=MISSING_TOKENS)
    group_cols = [c for c in group_cols if c in df.columns]
    n_rows = df.height

    print("=" * 72)
    print(f"DATASET: {os.path.basename(path)}")
    print(f"Shape: {n_rows:,} rows x {df.width} columns")
    print("=" * 72)

    numeric_cols, categorical_cols = [], []
    for col in df.columns:
        non_null = df.select(pl.col(col).drop_nulls())
        total = non_null.height
        if total == 0:
            categorical_cols.append(col)
            continue
        ok = non_null.select(clean_numeric_expr(col).is_not_null().sum()).item()
        (numeric_cols if ok / total >= 0.8 else categorical_cols).append(col)

    print("\nCOLUMN OVERVIEW (missing | type)")
    print("-" * 72)
    for col in df.columns:
        miss = df.select(pl.col(col).is_null().sum()).item()
        pct = miss / n_rows * 100 if n_rows else 0
        label = col if len(col) <= 48 else col[:45] + "..."
        ctype = "numeric" if col in numeric_cols else "categorical"
        print(f"{label:<50} {miss:>7,} ({pct:4.1f}%) {ctype}")

    print("\nNUMERIC COLUMNS (dataset level)")
    print("-" * 72)
    for col in numeric_cols:
        s = df.select(
            clean_numeric_expr(col).count().alias("count"),
            clean_numeric_expr(col).mean().alias("mean"),
            clean_numeric_expr(col).median().alias("median"),
            clean_numeric_expr(col).min().alias("min"),
            clean_numeric_expr(col).max().alias("max"),
            clean_numeric_expr(col).std().alias("std"),
        ).row(0, named=True)
        print(f"\n{col}")
        print(f"  count={s['count']:,}  mean={s['mean']:,.4f}  median={s['median']:,.4f}")
        print(f"  min={s['min']:,.4f}  max={s['max']:,.4f}  std={s['std']:,.4f}")

    print("\nCATEGORICAL COLUMNS (dataset level)")
    print("-" * 72)
    for col in categorical_cols:
        vc = df.select(pl.col(col).drop_nulls()).get_column(col).value_counts(sort=True)
        if vc.height == 0:
            continue
        cc = "count" if "count" in vc.columns else vc.columns[-1]
        total = vc.select(pl.col(cc).sum()).item()
        top = vc.head(5)
        mode_val = str(top.row(0)[0])
        mode_freq = top.row(0)[vc.columns.index(cc)]
        print(f"\n{col}")
        print(f"  count={total:,}  unique={vc.height:,}  mode='{mode_val[:50]}' (x{mode_freq:,})")
        for r in top.iter_rows(named=True):
            value = str(r[col])
            disp = value if len(value) <= 55 else value[:52] + "..."
            print(f"    {r[cc]:>8,}  {disp}")

    if group_cols:
        df2 = df.with_columns(
            [clean_numeric_expr(c).alias(c + "__num") for c in numeric_cols]
        )
        aggs = [pl.len().alias("rows")]
        aggs += [pl.col(c + "__num").mean().alias(c) for c in numeric_cols]
        grp = df2.group_by(group_cols).agg(aggs).sort("rows", descending=True)
        print("\n" + "=" * 72)
        print(f"GROUPED BY {', '.join(group_cols)}")
        print("=" * 72)
        print(f"Unique groups: {grp.height:,}")
        sizes = grp.get_column("rows")
        print(f"Rows per group: min={sizes.min():,}  median={sizes.median():,.1f}  "
              f"max={sizes.max():,}")
        print(f"\nTop {TOP_N} groups by row count (mean of each numeric column):")
        for r in grp.head(TOP_N).iter_rows(named=True):
            key_disp = " | ".join(str(r[c])[:20] for c in group_cols)
            print(f"\n  {key_disp}  (rows={r['rows']:,})")
            means = [f"{c}={r[c]:,.2f}" if r[c] is not None else f"{c}=-" for c in numeric_cols]
            for i in range(0, len(means), 3):
                print("    " + "  ".join(means[i:i + 3]))
    else:
        print("\n(No group_by column provided - dataset-level statistics only.)")


if __name__ == "__main__":
    main()
