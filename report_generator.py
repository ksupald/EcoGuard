"""PDF report generator - one report per region."""
import os
from datetime import date

import pandas as pd
from fpdf import FPDF

try:
    from species_risk import SPECIES
except Exception:
    SPECIES = {}

IUCN_LABEL = {5: "CR", 4: "EN", 3: "VU", 2: "NT", 1: "LC"}
IMG_DIR = "results/images"


def _line(pdf, label, value):
    """One 'label: value' row."""
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(60, 7, label)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")


def _heading(pdf, text):
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")


def build_report(region):
    """Return the PDF (as bytes) for one region."""
    summary = pd.read_csv("results/summary.csv")
    row = summary[summary["region"] == region].iloc[0]

    # Zone info is optional (used only if the file exists)
    zone = None
    if os.path.exists("results/priority_zones.csv"):
        zones = pd.read_csv("results/priority_zones.csv")
        match = zones[zones["region"] == region]
        if not match.empty:
            zone = match.iloc[0]

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "EcoGuard - Region Report", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated on {date.today()}", new_x="LMARGIN", new_y="NEXT")

    _heading(pdf, f"Region: {region}")
    module_name = "Water body shrinkage" if row["module"] == "water" else "Deforestation"
    _line(pdf, "Module:", module_name)
    _line(pdf, "Period:", f"{int(row['year_before'])} to {int(row['year_after'])}")

    _heading(pdf, "Change detection (Sentinel-2)")
    _line(pdf, f"Area in {int(row['year_before'])}:", f"{row['area_before_km2']} km2")
    _line(pdf, f"Area in {int(row['year_after'])}:", f"{row['area_after_km2']} km2")
    _line(pdf, "Change:", f"{row['change_km2']} km2 ({row['change_pct']}%)")
    _line(pdf, "Area-loss risk:", row["risk"])

    _heading(pdf, "Species at risk")
    species = SPECIES.get(region, [])
    if species:
        for name, weight in species:
            _line(pdf, "-", f"{name} ({IUCN_LABEL.get(weight, '?')})")
    else:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, "No species data available.", new_x="LMARGIN", new_y="NEXT")

    if zone is not None:
        _heading(pdf, "Priority and zone")
        _line(pdf, "Species risk score:", zone["composite_risk_score"])
        _line(pdf, "Overall rank:", int(zone["overall_rank"]))
        _line(pdf, "Zone:", zone["zone"])
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, f"Recommended action: {zone['recommended_action']}",
                       new_x="LMARGIN", new_y="NEXT")

    # Change map on its own page
    img_path = os.path.join(IMG_DIR, str(row["image"]))
    if os.path.exists(img_path):
        pdf.add_page()
        _heading(pdf, "Change map")
        pdf.image(img_path, w=170)

    return bytes(pdf.output())
