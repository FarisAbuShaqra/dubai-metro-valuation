# Infrastructure-Driven Real Estate Valuation Model

Does a major transit announcement get priced into nearby home values? This project uses
public Dubai Land Department transaction data to test whether communities along the
announced **Dubai Metro Blue Line** (route announced Nov 2023) saw stronger apartment
price growth than comparable unexposed communities.

## Method
- **Data:** ~1.7M DLD transactions; filtered to residential apartment **sales** (Unit / Flat / Residential).
- **Metric:** median **AED per sqm** (robust to luxury outliers).
- **Design:** difference-in-differences — exposed (Blue-Line) communities vs control communities,
  pre vs post the 24 Nov 2023 announcement.
- **Key control:** split **existing** vs **off-plan** sales, because off-plan medians track
  developer launch pricing, not resale appreciation.

## Key finding
The naive DiD suggested exposed areas *underperformed* by **6.7 pts** — but decomposing by
sale type showed this was almost entirely an off-plan supply artifact:

| Sale type | Exposed growth | Control growth | DiD |
|---|---|---|---|
| All (naive) | +31% | +37% | **-6.7 pts** |
| Existing only | +38% | +37% | **+1.2 pts** |
| Off-plan only | +14% | +29% | -15.3 pts |

On the clean resale signal, exposed and control communities grew **almost identically**.
**Interpretation:** after controlling for supply composition, the Blue Line shows no
distinguishable resale-price premium yet — consistent with the upgrade not being clearly
capitalized into existing stock.

## Charts
- `chart1_trend.png` — monthly median resale price/sqm, exposed vs control, with announcement line
- `chart2_ranking.png` — per-community post-announcement growth (existing flats)
- `chart3_did.png` — DiD by sale type (the decomposition that reverses the naive result)

## Tech stack
Python, pandas, NumPy, matplotlib.

## Limitations
- Exposed vs control groups differ in price tier (premium Creek Harbour skews exposed),
  so parallel-trends is assumed, not formally tested.
- Off-plan medians reflect launch pricing and product mix, not pure appreciation.
- Exposure is defined by RTA's announced station areas, not walking-distance to stations.
- **Not investment advice or a price forecast** — this detects market-response signals only.