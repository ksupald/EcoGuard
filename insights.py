"""Plain-language insights for each region (rule-based; an LLM can replace this later)."""
import os

import pandas as pd

try:
    from species_risk import SPECIES
except Exception:
    SPECIES = {}

IUCN_LABEL = {5: "CR", 4: "EN", 3: "VU", 2: "NT", 1: "LC"}


def explain_region(region):
    """Return a short plain-language explanation for one region."""
    summary = pd.read_csv("results/summary.csv")
    row = summary[summary["region"] == region].iloc[0]
    what = "water body" if row["module"] == "water" else "forest"

    # 1. What changed
    pct = float(row["change_pct"])
    km2 = abs(float(row["change_km2"]))
    direction = "decreased" if pct < 0 else "increased"
    text = [
        f"Between {int(row['year_before'])} and {int(row['year_after'])}, the {what} "
        f"area in {region} {direction} by {abs(pct):.1f}% ({km2:.2f} km2), from "
        f"{row['area_before_km2']} km2 to {row['area_after_km2']} km2. "
        f"This is classified as {row['risk']} risk."
    ]

    # 2. Species
    species = SPECIES.get(region, [])
    if species:
        top_weight = max(w for _, w in species)
        top_names = [n for n, w in species if w == top_weight]
        threatened = [n for n, w in species if w >= 3]
        text.append(
            f"{len(threatened)} of {len(species)} listed species are threatened "
            f"(CR/EN/VU). The most threatened: {', '.join(top_names)} "
            f"({IUCN_LABEL.get(top_weight, '?')})."
        )

    # 3. Zone and action
    if os.path.exists("results/priority_zones.csv"):
        zones = pd.read_csv("results/priority_zones.csv")
        match = zones[zones["region"] == region]
        if not match.empty:
            z = match.iloc[0]
            text.append(
                f"Priority zone: {z['zone']} (rank {int(z['overall_rank'])} of {len(zones)}). "
                f"Recommended action: {z['recommended_action']}."
            )

    text.append("Note: satellite data shows where change happened, not why. "
                "Field verification is needed before any action.")
    return "\n\n".join(text)
