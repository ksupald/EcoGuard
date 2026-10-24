"""Run the analysis on all regions and save results to the results/ folder."""
import os

import pandas as pd

import config as cfg
from gee_utils import init_ee
from analysis import analyze_region

OUT = "results"


def main():
    init_ee()
    os.makedirs(f"{OUT}/images", exist_ok=True)

    jobs = [("water", r) for r in cfg.WATER_REGIONS] + \
           [("forest", r) for r in cfg.FOREST_REGIONS]

    rows = []
    for module, reg in jobs:
        print(f"[{module}] {reg['name']} ...")
        try:
            rows.append(analyze_region(module, reg, OUT))
            print("   done")
        except Exception as e:
            print(f"   FAILED: {e}")

    if not rows:
        print("No results were produced.")
        return None

    df = pd.DataFrame(rows)
    # Region with the largest loss = rank 1
    df["priority_rank"] = df.groupby("module")["change_pct"].rank(method="min").astype(int)
    df = df.sort_values(["module", "priority_rank"])
    df.to_csv(f"{OUT}/summary.csv", index=False)
    print(f"\nSaved {OUT}/summary.csv")
    return df


if __name__ == "__main__":
    main()
