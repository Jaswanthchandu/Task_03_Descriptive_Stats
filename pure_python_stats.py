
import csv
import math
import os
import sys
from collections import Counter, defaultdict

MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-"}
SAMPLE_SIZE = 2000
TOP_N = 15


def is_missing(value):
    return value is None or value.strip().lower() in MISSING_TOKENS


def try_number(value):
    if is_missing(value):
        return None
    cleaned = value.strip().replace("$", "").replace(",", "").replace("%", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def infer_types(path, headers):
    samples = {h: [] for h in headers}
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= SAMPLE_SIZE:
                break
            for h in headers:
                v = row.get(h)
                if not is_missing(v):
                    samples[h].append(v)
    types = {}
    for h in headers:
        vals = samples[h]
        if not vals:
            types[h] = "empty"
        else:
            numeric = sum(1 for v in vals if try_number(v) is not None)
            types[h] = "numeric" if numeric / len(vals) >= 0.8 else "categorical"
    return types


def stddev(nums, mean):
    n = len(nums)
    return math.sqrt(sum((x - mean) ** 2 for x in nums) / (n - 1)) if n > 1 else 0.0


def median(sorted_nums):
    n = len(sorted_nums)
    if n == 0:
        return None
    mid = n // 2
    return sorted_nums[mid] if n % 2 else (sorted_nums[mid - 1] + sorted_nums[mid]) / 2


def fmt(x):
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:,.4f}"
    return f"{x:,}" if isinstance(x, int) else str(x)


def main():
    if len(sys.argv) < 2:
        print("Usage: python pure_python_stats.py <file.csv> [group_by]")
        sys.exit(1)
    path = sys.argv[1]
    group_cols = sys.argv[2].split(",") if len(sys.argv) > 2 else []

    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        headers = next(csv.reader(f))
    types = infer_types(path, headers)

    # Validate requested group columns exist.
    group_cols = [c for c in group_cols if c in headers]

    numeric_cols = [h for h in headers if types[h] == "numeric"]
    categorical_cols = [h for h in headers if types[h] != "numeric"]

    numeric_values = {h: [] for h in numeric_cols}
    cat_counters = {h: Counter() for h in categorical_cols}
    missing_counts = {h: 0 for h in headers}
    row_count = 0

    # Grouped accumulators: key -> {"count": n, "sums": {numcol: sum}}
    groups = defaultdict(lambda: {"count": 0, "sums": defaultdict(float)})

    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            for h in headers:
                v = row.get(h)
                if is_missing(v):
                    missing_counts[h] += 1
                    continue
                if types[h] == "numeric":
                    num = try_number(v)
                    if num is not None:
                        numeric_values[h].append(num)
                else:
                    cat_counters[h][v.strip()] += 1
            if group_cols:
                key = tuple(row.get(c, "") for c in group_cols)
                g = groups[key]
                g["count"] += 1
                for nc in numeric_cols:
                    num = try_number(row.get(nc, ""))
                    if num is not None:
                        g["sums"][nc] += num

    # --- Dataset level ---
    print("=" * 72)
    print(f"DATASET: {os.path.basename(path)}")
    print(f"Rows: {row_count:,}    Columns: {len(headers)}")
    print("=" * 72)

    print("\nCOLUMN OVERVIEW (missing | type)")
    print("-" * 72)
    for h in headers:
        pct = (missing_counts[h] / row_count * 100) if row_count else 0
        label = h if len(h) <= 48 else h[:45] + "..."
        print(f"{label:<50} {missing_counts[h]:>7,} ({pct:4.1f}%) {types[h]}")

    print("\nNUMERIC COLUMNS (dataset level)")
    print("-" * 72)
    for h in numeric_cols:
        nums = numeric_values[h]
        if not nums:
            continue
        mean = sum(nums) / len(nums)
        s = sorted(nums)
        print(f"\n{h}")
        print(f"  count={len(nums):,}  mean={fmt(mean)}  median={fmt(median(s))}")
        print(f"  min={fmt(min(nums))}  max={fmt(max(nums))}  std={fmt(stddev(nums, mean))}")

    print("\nCATEGORICAL COLUMNS (dataset level)")
    print("-" * 72)
    for h in categorical_cols:
        c = cat_counters[h]
        total = sum(c.values())
        if total == 0:
            continue
        mode, freq = c.most_common(1)[0]
        print(f"\n{h}")
        print(f"  count={total:,}  unique={len(c):,}  mode='{mode[:50]}' (x{freq:,})")
        for value, f_ in c.most_common(5):
            disp = value if len(value) <= 55 else value[:52] + "..."
            print(f"    {f_:>8,}  {disp}")

    # --- Grouped ---
    if group_cols:
        print("\n" + "=" * 72)
        print(f"GROUPED BY {', '.join(group_cols)}")
        print("=" * 72)
        print(f"Unique groups: {len(groups):,}")
        sizes = sorted(g["count"] for g in groups.values())
        print(f"Rows per group: min={sizes[0]:,}  median={median(sizes):,.1f}  "
              f"max={sizes[-1]:,}")
        top = sorted(groups.items(), key=lambda kv: kv[1]["count"], reverse=True)[:TOP_N]
        print(f"\nTop {TOP_N} groups by row count (mean of each numeric column):")
        for key, g in top:
            key_disp = " | ".join(str(k)[:20] for k in key)
            print(f"\n  {key_disp}  (rows={g['count']:,})")
            means = []
            for nc in numeric_cols:
                mean = g["sums"][nc] / g["count"] if g["count"] else 0
                means.append(f"{nc}={mean:,.2f}")
            # print means wrapped, a few per line
            for i in range(0, len(means), 3):
                print("    " + "  ".join(means[i:i + 3]))
    else:
        print("\n(No group_by column provided - dataset-level statistics only.)")


if __name__ == "__main__":
    main()
