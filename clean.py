import pandas as pd, numpy as np

FILES = [r"C:\Users\faris\Downloads\transactions_2026-05-21_02-13-21_1.csv"]   # add other parts here later

EVENT_DATE = pd.Timestamp("2023-11-24")
START_DATE = pd.Timestamp("2021-01-01")
END_DATE   = pd.Timestamp("today").normalize()

usecols = ["instance_date","trans_group_en","property_type_en","property_sub_type_en",
           "property_usage_en","reg_type_en","area_name_en","master_project_en",
           "actual_worth","procedure_area"]

EXPOSED = {
    "Dubai Creek Harbour": ["creek harbour"],
    "Festival City":       ["festival city"],
    "International City":   ["international city"],
    "Dubai Silicon Oasis": ["silicon oasis"],
    "Dubai Academic City": ["academic city"],
    "Mirdif":              ["mirdif"],
    "Al Warqa":            ["al warqa"],
    "Ras Al Khor":         ["ras al khor"],
}
CONTROL = {
    "Jumeirah Village Circle": ["jumeirah village circle"],
    "Arjan":                   ["arjan"],
    "Dubai Sports City":       ["sports city"],
    "Motor City":              ["motor city"],
    "Dubai Studio City":       ["studio city"],
    "Town Square":             ["town square"],
    "Dubai South":             ["dubai south"],
}
def classify(master, area):
    s = (str(master) + " " + str(area)).lower()
    for name, pats in EXPOSED.items():
        if any(p in s for p in pats): return name, "Exposed"
    for name, pats in CONTROL.items():
        if any(p in s for p in pats): return name, "Control"
    return None, None

frames = []
for path in FILES:
    for chunk in pd.read_csv(path, usecols=usecols, dtype=str, chunksize=200_000):
        chunk = chunk[(chunk["trans_group_en"] == "Sales") &
                      (chunk["property_type_en"] == "Unit") &
                      (chunk["property_sub_type_en"] == "Flat") &
                      (chunk["property_usage_en"].str.strip() == "Residential")].copy()
        if chunk.empty: continue
        res = [classify(m, a) for m, a in zip(chunk["master_project_en"], chunk["area_name_en"])]
        chunk["community"] = [r[0] for r in res]
        chunk["group"]     = [r[1] for r in res]
        chunk = chunk[chunk["community"].notna()]
        if not chunk.empty: frames.append(chunk)

df = pd.concat(frames, ignore_index=True)
df["actual_worth"]   = pd.to_numeric(df["actual_worth"], errors="coerce")
df["procedure_area"] = pd.to_numeric(df["procedure_area"], errors="coerce")
df["date"]           = pd.to_datetime(df["instance_date"], format="%Y-%m-%d", errors="coerce")
df = df.dropna(subset=["actual_worth","procedure_area","date"])
df = df[(df["actual_worth"] > 0) & (df["procedure_area"].between(20, 1000))]
df = df[df["date"].between(START_DATE, END_DATE)]
df["ppsqm"] = df["actual_worth"] / df["procedure_area"]
lo, hi = df["ppsqm"].quantile([0.01, 0.99])
df = df[df["ppsqm"].between(lo, hi)]
df["period"] = np.where(df["date"] >= EVENT_DATE, "Post", "Pre")

print("clean apartment rows:", len(df))
print("date range:", df["date"].min().date(), "->", df["date"].max().date(), "\n")

summary = (df.groupby(["group","period"])["ppsqm"].median()
             .unstack("period").reindex(columns=["Pre","Post"]))
summary["growth_%"] = (summary["Post"]/summary["Pre"] - 1)*100
print("=== GROUP: median AED/sqm ===")
print(summary.round(0), "\n")
did = ((summary.loc["Exposed","Post"]/summary.loc["Exposed","Pre"]) -
       (summary.loc["Control","Post"]/summary.loc["Control","Pre"]))*100
print(f"Difference-in-differences (exposed growth - control growth): {did:.1f} pts\n")

comm = (df.groupby(["group","community","period"])["ppsqm"].median()
          .unstack("period").reindex(columns=["Pre","Post"]))
comm["growth_%"] = (comm["Post"]/comm["Pre"] - 1)*100
comm = comm.join(df.groupby("community").size().rename("n"))
print("=== PER COMMUNITY ===")
print(comm.round(0).sort_values("growth_%", ascending=False))

df.to_csv(r"C:\Users\faris\Downloads\apartments_clean.csv", index=False)
print("\nsaved apartments_clean.csv")