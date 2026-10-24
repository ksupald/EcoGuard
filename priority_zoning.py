"""Priority ranking and zoning - turns the species risk score into zones."""
import pandas as pd

# Zone limits on composite_risk_score (0 to 1)
RED, ORANGE = 0.6, 0.4

ACTION = {
    "Red": "Immediate protection and field verification",
    "Orange": "Close monitoring and local action plan",
    "Green": "Routine monitoring",
}


def get_zone(score):
    if score >= RED:
        return "Red"
    if score >= ORANGE:
        return "Orange"
    return "Green"


def run_priority_zoning():
    risk = pd.read_csv("results/species_risk_summary.csv")
    base = pd.read_csv("results/summary.csv")[["module", "region", "lat", "lon", "risk"]]

    # Add coordinates and area-loss risk level to the species risk table
    df = risk.merge(base, on=["module", "region"], how="left")

    # Highest score = rank 1 (across all regions)
    df["overall_rank"] = df["composite_risk_score"].rank(ascending=False, method="min").astype(int)
    df["zone"] = df["composite_risk_score"].apply(get_zone)
    df["recommended_action"] = df["zone"].map(ACTION)

    df = df.sort_values("overall_rank")
    df.to_csv("results/priority_zones.csv", index=False)
    print("Saved results/priority_zones.csv")
    return df


if __name__ == "__main__":
    run_priority_zoning()
