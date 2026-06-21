import pandas as pd
from collections import Counter

PATH = r"C:\Users\faris\Downloads\transactions_2026-05-21_02-13-21_1.csv"

usecols = ["instance_date","trans_group_en","property_type_en","property_sub_type_en",
           "property_usage_en","reg_type_en","area_name_en","master_project_en",
           "actual_worth","procedure_area","meter_sale_price"]
cat_cols = ["trans_group_en","property_type_en","property_sub_type_en","property_usage_en","reg_type_en"]
counters = {c: Counter() for c in cat_cols}
areas, mprojects = set(), set()
dmin = dmax = None
sample_dates, total = [], 0

for chunk in pd.read_csv(PATH, usecols=usecols, dtype=str, chunksize=200_000):
    total += len(chunk)
    for c in cat_cols:
        counters[c].update(chunk[c].dropna())
    areas.update(chunk["area_name_en"].dropna().unique())
    mprojects.update(chunk["master_project_en"].dropna().unique())
    d = pd.to_datetime(chunk["instance_date"], errors="coerce", dayfirst=True)
    if d.notna().any():
        dmin = d.min() if dmin is None else min(dmin, d.min())
        dmax = d.max() if dmax is None else max(dmax, d.max())
    if len(sample_dates) < 5:
        sample_dates += chunk["instance_date"].dropna().head(5).tolist()

print("TOTAL ROWS:", total)
print("DATE RANGE:", dmin, "->", dmax)
print("SAMPLE RAW DATES:", sample_dates[:5], "\n")
for c in cat_cols:
    print(f"--- {c} ---")
    for val, n in counters[c].most_common(15):
        print(f"   {val!r}: {n}")
    print()

targets = ["creek","festival","ras al khor","international city","silicon","academic",
           "mirdif","warqa","village circle","jvc","arjan","sports city","production city",
           "motor city","studio city","town square","dubai south"]
match = lambda names: [n for n in sorted(names) if any(t in n.lower() for t in targets)]
print("UNIQUE area_name_en:", len(areas))
print("matching:", match(areas), "\n")
print("UNIQUE master_project_en:", len(mprojects))
print("matching:", match(mprojects))