"""Small helper functions for Earth Engine."""
import ee
import requests

import config as cfg

BANDS = ["B2", "B3", "B4", "B8", "B11", "SCL"]


def init_ee():
    """Start Earth Engine."""
    try:
        ee.Initialize(project=cfg.PROJECT_ID)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=cfg.PROJECT_ID)


def make_region(lat, lon, buffer_km):
    """Square area around a centre point."""
    return ee.Geometry.Point([lon, lat]).buffer(buffer_km * 1000).bounds()


def _mask_clouds(img):
    """Remove clouds and cloud shadows."""
    scl = img.select("SCL")
    bad = scl.eq(3).Or(scl.eq(8)).Or(scl.eq(9)).Or(scl.eq(10)).Or(scl.eq(11))
    return img.updateMask(bad.Not())


def get_composite(region, year, month_start, month_end):
    """Clean Sentinel-2 composite for the given year and months."""
    start = ee.Date.fromYMD(year, month_start, 1)
    end = ee.Date.fromYMD(year, month_end, 1).advance(1, "month")
    col = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cfg.CLOUD_MAX))
        .select(BANDS)
    )
    n = col.size().getInfo()
    if n == 0:
        raise ValueError(f"{year}: no clean image found")
    print(f"   {year}: {n} images")
    return col.map(_mask_clouds).median().clip(region)


def mndwi(img):
    """Water index."""
    return img.normalizedDifference(["B3", "B11"])


def ndvi(img):
    """Vegetation index."""
    return img.normalizedDifference(["B8", "B4"])


def area_km2(mask, region, scale):
    """Total area of a mask in km2."""
    area = mask.rename("a").multiply(ee.Image.pixelArea())
    res = area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=region,
        scale=scale,
        maxPixels=1e10,
        bestEffort=True,
    )
    return ee.Number(res.get("a")).divide(1e6).getInfo()


def save_thumb(image, region, path, dims=800):
    """Save an image as PNG."""
    url = image.getThumbURL({"region": region, "dimensions": dims, "format": "png"})
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)


def risk_level(change_pct):
    """Convert % change into High / Medium / Low."""
    if change_pct <= cfg.RISK_HIGH:
        return "High"
    if change_pct <= cfg.RISK_MEDIUM:
        return "Medium"
    return "Low"
