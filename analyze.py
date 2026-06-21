import pandas as pd, numpy as np

df = pd.read_csv(r"C:\Users\faris\Downloads\apartments_clean.csv", parse_dates=["date"])
MINN = 50

def did_table(d, label):
    s = (d.groupby(["group","period"])["ppsqm"].median()
           .unstack("period").reindex(columns=["Pre","Post"]))
    s["growth_%"] = (s["Post"]/s["Pre"]-1)*100
    print(f"=== {label}: median AED/sqm ===")
    print(s.round(0))
    if {"Exposed","Control"}.issubset(s.index) and s.loc["Exposed","Pre"]>0 and s.loc["Control","Pre"]>0:
        did = ((s.loc["Exposed","Post"]/s.loc["Exposed","Pre"]) -
               (s.loc["Control","Post"]/s.loc["Control","Pre"]))*100
        print(f"DiD: {did:.1f} pts\n")
    else:
        print("(one group missing a period)\n")

did_table(df, "ALL (existing + off-plan)")
did_table(df[df["reg_type_en"]=="Existing Properties"], "EXISTING only")
did_table(df[df["reg_type_en"]=="Off-Plan Properties"], "OFF-PLAN only")

ex = df[df["reg_type_en"]=="Existing Properties"]
piv = ex.pivot_table(index=["group","community"], columns="period", values="ppsqm", aggfunc="median").reindex(columns=["Pre","Post"])
cnt = ex.pivot_table(index=["group","community"], columns="period", values="ppsqm", aggfunc="size").reindex(columns=["Pre","Post"]).fillna(0)
piv["growth_%"] = (piv["Post"]/piv["Pre"]-1)*100
piv["n_pre"]  = cnt["Pre"].astype(int)
piv["n_post"] = cnt["Post"].astype(int)
ok = piv[(piv["n_pre"]>=MINN)&(piv["n_post"]>=MINN)].sort_values("growth_%", ascending=False)
print(f"=== PER COMMUNITY (existing flats only, n>={MINN} in both periods) ===")
print(ok.round(0))
dropped = piv[(piv["n_pre"]<MINN)|(piv["n_post"]<MINN)]
if len(dropped):
    print("\nDropped (thin or no pre-period):", [t[1] for t in dropped.index.tolist()])