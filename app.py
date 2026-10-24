"""EcoGuard - Streamlit dashboard (reads from the results/ folder)."""
import os

import pandas as pd
import streamlit as st

CSV = "results/summary.csv"
SPECIES_CSV = "results/species_risk_summary.csv"
IMG_DIR = "results/images"

MODULES = {"water": "💧 Water Body Shrinkage", "forest": "🌳 Deforestation"}
LEGEND = {
    "water": "🔵 Remaining water  |  🔴 Water lost  |  🟡 New water",
    "forest": "🟢 Remaining forest  |  🔴 Forest lost  |  🟩 New vegetation",
}
RISK_ICON = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}

st.set_page_config(page_title="EcoGuard", page_icon="🌍", layout="wide")
st.title("🌍 EcoGuard")
st.caption("Monitoring water bodies and forests using satellite imagery (Sentinel-2)")

if not os.path.exists(CSV):
    st.error("results/summary.csv not found. Please run run_pipeline.py first.")
    st.stop()

df = pd.read_csv(CSV)
module = st.sidebar.radio("Module", list(MODULES), format_func=MODULES.get)
d = df[df["module"] == module].sort_values("priority_rank").reset_index(drop=True)

if d.empty:
    st.warning("No data available for this module.")
    st.stop()

years = f"{int(d.year_before[0])} → {int(d.year_after[0])}"
st.subheader(f"{MODULES[module]}  ({years})")

c1, c2, c3 = st.columns(3)
c1.metric("Regions monitored", len(d))
c2.metric("High-risk regions", int((d.risk == "High").sum()))
c3.metric("Largest decline", f"{d.change_pct.min():.1f}%", d.region[0])

left, right = st.columns([1, 1])
with left:
    st.markdown("**Map**")
    st.map(d.rename(columns={"lat": "latitude", "lon": "longitude"}), size=8000)
with right:
    st.markdown("**Change in area (%) by region**")
    st.bar_chart(d.set_index("region")["change_pct"])

st.markdown("**Priority list** (rank 1 = highest loss)")
table = d[["priority_rank", "region", "area_before_km2", "area_after_km2",
           "change_km2", "change_pct", "risk"]].copy()
table.columns = ["Rank", "Region", "Area before (km²)", "Area after (km²)",
                 "Change (km²)", "Change (%)", "Risk"]
table["Risk"] = table["Risk"].map(lambda r: f"{RISK_ICON.get(r, '')} {r}")
st.dataframe(table, use_container_width=True, hide_index=True)

st.divider()
choice = st.selectbox("Select a region for details", d["region"])
row = d[d["region"] == choice].iloc[0]

m1, m2, m3 = st.columns(3)
m1.metric(f"Area in {int(row.year_before)}", f"{row.area_before_km2} km²")
m2.metric(f"Area in {int(row.year_after)}", f"{row.area_after_km2} km²",
          f"{row.change_km2} km²  ({row.change_pct}%)")
m3.metric("Risk level", f"{RISK_ICON.get(row.risk, '')} {row.risk}")

img_path = os.path.join(IMG_DIR, row["image"])
if os.path.exists(img_path):
    st.image(img_path, caption=LEGEND[module], use_container_width=True)
else:
    st.info("Image not available for this region.")

# ---------- Species Risk Correlation ----------
st.divider()
st.subheader("🦌 Species Risk Correlation")

if os.path.exists(SPECIES_CSV):
    sp = pd.read_csv(SPECIES_CSV)
    sp = sp[sp["module"] == module].sort_values("species_priority_rank")
    if sp.empty:
        st.info("No species risk data for this module.")
    else:
        st.bar_chart(sp.set_index("region")["composite_risk_score"])
        t = sp[["species_priority_rank", "region", "change_pct",
                "total_species", "max_threat", "composite_risk_score"]].copy()
        t.columns = ["Rank", "Region", "Change (%)", "Species count",
                     "Top IUCN threat (1-5)", "Risk score"]
        st.dataframe(t, use_container_width=True, hide_index=True)
        st.caption("Risk score = 0.4 × area loss + 0.2 × species count + 0.4 × IUCN threat")
else:
    st.info("results/species_risk_summary.csv not found. Run species_risk.py first.")
