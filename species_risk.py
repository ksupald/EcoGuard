"""Species Risk Correlation - area change + species count + IUCN threat."""
import os
import pandas as pd

# Weights from the synopsis (total = 1.0)
W_AREA, W_SPECIES, W_IUCN = 0.4, 0.2, 0.4
AREA_LOSS_CAP = 50   # Area score reaches 1.0 at 50% loss
MAX_SPECIES = 10     # Species score reaches 1.0 at 10 species

# Species for each region: (name, IUCN weight)
SPECIES = {
    "Sambhar Lake": [("Lesser Flamingo", 2), ("Greater Flamingo", 1)],
    "Kolleru Lake": [("Spot-billed Pelican", 2), ("Painted Stork", 2)],
    "Hasdeo Arand": [("Asian Elephant", 4), ("Indian Pangolin", 4),
                     ("Leopard", 3), ("Sloth Bear", 3)],
    "Buxwaha": [("Indian White-rumped Vulture", 5), ("Tiger", 4),
                ("Leopard", 3), ("Sloth Bear", 3), ("Chowsingha", 3)],
    "Talabira": [("Asian Elephant", 4), ("Leopard", 3), ("Sloth Bear", 3)],
}


def calculate_species_risk():
    summary = pd.read_csv("results/summary.csv")

    rows = []
    for _, r in summary.iterrows():
        sp = SPECIES.get(r["region"])
        if not sp:
            print("No species data, skipping:", r["region"])
            continue

        # Three scores, each between 0 and 1
        area_score = min(max(-r["change_pct"], 0) / AREA_LOSS_CAP, 1)
        species_score = min(len(sp) / MAX_SPECIES, 1)
        iucn_score = max(w for _, w in sp) / 5

        score = (W_AREA * area_score
                 + W_SPECIES * species_score
                 + W_IUCN * iucn_score)

        rows.append({
            "module": r["module"],
            "region": r["region"],
            "change_pct": r["change_pct"],
            "total_species": len(sp),
            "max_threat": max(w for _, w in sp),
            "composite_risk_score": round(score, 3),
        })

    out = pd.DataFrame(rows)
    out["species_priority_rank"] = (
        out.groupby("module")["composite_risk_score"]
        .rank(ascending=False, method="min").astype(int)
    )
    out.to_csv("results/species_risk_summary.csv", index=False)
    print("Saved results/species_risk_summary.csv")
    return out


if __name__ == "__main__":
    calculate_species_risk()
