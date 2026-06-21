import pandas as pd, numpy as np, matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch

OUT = r"C:\Users\faris\Downloads"
df = pd.read_csv(OUT + r"\apartments_clean.csv", parse_dates=["date"])
EVENT = pd.Timestamp("2023-11-24")
EXPO, CTRL = "#d81b60", "#1e88e5"
ex = df[df["reg_type_en"]=="Existing Properties"].copy()

# Chart 1: monthly median AED/sqm, exposed vs control, event line
ex["ym"] = ex["date"].dt.to_period("M").dt.to_timestamp()
ts = ex.groupby(["ym","group"])["ppsqm"].median().unstack("group").sort_index().rolling(3, min_periods=1).mean()
fig, ax = plt.subplots(figsize=(9,5))
ax.plot(ts.index, ts["Exposed"], color=EXPO, lw=2, label="Exposed (Blue Line)")
ax.plot(ts.index, ts["Control"], color=CTRL, lw=2, label="Control")
ax.axvline(EVENT, ls="--", color="gray"); ax.text(EVENT, ax.get_ylim()[1]*0.98, " announcement", color="gray", va="top", fontsize=9)
ax.set_title("Median resale price per sqm: exposed vs control", fontweight="bold")
ax.set_ylabel("AED / sqm (existing flats, 3-mo avg)"); ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT + r"\chart1_trend.png", dpi=140); plt.close(fig)

# Chart 2: per-community growth ranking
piv = ex.pivot_table(index=["group","community"], columns="period", values="ppsqm", aggfunc="median").reindex(columns=["Pre","Post"])
cnt = ex.pivot_table(index=["group","community"], columns="period", values="ppsqm", aggfunc="size").reindex(columns=["Pre","Post"]).fillna(0)
piv["growth"] = (piv["Post"]/piv["Pre"]-1)*100
piv = piv[(cnt["Pre"]>=50)&(cnt["Post"]>=50)].dropna(subset=["growth"]).sort_values("growth")
colors = [EXPO if g=="Exposed" else CTRL for g,_ in piv.index]
labels = [c for _,c in piv.index]
fig, ax = plt.subplots(figsize=(9,6))
ax.barh(labels, piv["growth"], color=colors)
ax.set_title("Post-announcement growth by community (existing flats)", fontweight="bold")
ax.set_xlabel("Median AED/sqm growth %")
ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
ax.legend(handles=[Patch(color=EXPO,label="Exposed"),Patch(color=CTRL,label="Control")])
ax.grid(axis="x", alpha=.3); fig.tight_layout(); fig.savefig(OUT + r"\chart2_ranking.png", dpi=140); plt.close(fig)

# Chart 3: DiD decomposition
def did(d):
    s=d.groupby(["group","period"])["ppsqm"].median().unstack("period")
    return ((s.loc["Exposed","Post"]/s.loc["Exposed","Pre"])-(s.loc["Control","Post"]/s.loc["Control","Pre"]))*100
vals={"All\n(naive)":did(df),"Existing\nonly":did(ex),"Off-plan\nonly":did(df[df["reg_type_en"]=="Off-Plan Properties"])}
fig, ax = plt.subplots(figsize=(7,5))
bars=ax.bar(vals.keys(), vals.values(), color=["#888","#2e7d32","#888"]); ax.axhline(0,color="k",lw=.8)
for b,v in zip(bars,vals.values()): ax.text(b.get_x()+b.get_width()/2, v+(0.4 if v>=0 else -0.4), f"{v:.1f}", ha="center", va="bottom" if v>=0 else "top", fontweight="bold")
ax.set_title("Difference-in-differences by sale type", fontweight="bold")
ax.set_ylabel("Exposed minus control growth (pts)"); ax.grid(axis="y", alpha=.3)
fig.tight_layout(); fig.savefig(OUT + r"\chart3_did.png", dpi=140); plt.close(fig)
print("saved chart1_trend.png, chart2_ranking.png, chart3_did.png to Downloads")