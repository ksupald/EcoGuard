"""Before/after change detection for one region (water and forest)."""
import ee

import config as cfg
from gee_utils import (make_region, get_composite, mndwi, ndvi,
                       area_km2, save_thumb, risk_level)

SPECS = {
    "water": {
        "index": mndwi,
        "threshold": cfg.WATER_THRESHOLD,
        "months": cfg.WATER_MONTHS,
        "scale": cfg.SCALE_WATER,
        "colors": {"stable": "00B4D8", "lost": "FF0000", "gained": "FFD60A"},
    },
    "forest": {
        "index": ndvi,
        "threshold": cfg.FOREST_NDVI,
        "months": cfg.FOREST_MONTHS,
        "scale": cfg.SCALE_FOREST,
        "colors": {"stable": "1B5E20", "lost": "FF0000", "gained": "76FF03"},
    },
}


def slug(name):
    return name.lower().replace(" ", "_")


def analyze_region(module, reg, out_dir="results"):
    spec = SPECS[module]
    region = make_region(reg["lat"], reg["lon"], reg["buffer_km"])

    # 1. Images for both years
    c1 = get_composite(region, cfg.YEAR_BEFORE, *spec["months"])
    c2 = get_composite(region, cfg.YEAR_AFTER, *spec["months"])

    # 2. Water / forest pixels
    m1 = spec["index"](c1).gt(spec["threshold"]).unmask(0)
    m2 = spec["index"](c2).gt(spec["threshold"]).unmask(0)

    # 3. Area and change
    a1 = area_km2(m1, region, spec["scale"])
    a2 = area_km2(m2, region, spec["scale"])
    change = a2 - a1
    pct = (change / a1 * 100) if a1 > 0 else 0.0

    # 4. Change map: remaining / lost / new
    col = spec["colors"]
    stable = m1.And(m2)
    lost = m1.And(m2.Not())
    gained = m1.Not().And(m2)

    def layer(mask, color):
        return mask.selfMask().visualize(palette=[color], min=0, max=1)

    base = c2.select(["B4", "B3", "B2"]).visualize(min=0, max=3000)
    final = ee.ImageCollection([
        base,
        layer(stable, col["stable"]),
        layer(lost, col["lost"]),
        layer(gained, col["gained"]),
    ]).mosaic()

    img_name = f"{module}_{slug(reg['name'])}.png"
    save_thumb(final, region, f"{out_dir}/images/{img_name}")

    # 5. Return one result row
    return {
        "module": module,
        "region": reg["name"],
        "lat": reg["lat"],
        "lon": reg["lon"],
        "year_before": cfg.YEAR_BEFORE,
        "year_after": cfg.YEAR_AFTER,
        "area_before_km2": round(a1, 2),
        "area_after_km2": round(a2, 2),
        "change_km2": round(change, 2),
        "change_pct": round(pct, 2),
        "risk": risk_level(pct),
        "image": img_name,
    }
