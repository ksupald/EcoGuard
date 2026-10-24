"""EcoGuard settings - change everything from here."""

PROJECT_ID = "ecoguard-503909"   # <-- change only this

# The two years to compare
YEAR_BEFORE = 2019
YEAR_AFTER = 2024

# Which months to use (10-12 = Oct-Dec)
WATER_MONTHS = (10, 12)
FOREST_MONTHS = (10, 12)

# Skip images with more cloud cover than this (%)
CLOUD_MAX = 30

# Detection settings
WATER_THRESHOLD = 0.0     # MNDWI > 0  => water
FOREST_NDVI = 0.5         # NDVI > 0.5 => dense forest
SCALE_WATER = 20          # meter
SCALE_FOREST = 30         # meter

# Risk level (% change in area)
RISK_HIGH = -25
RISK_MEDIUM = -10

# Water body regions
WATER_REGIONS = [
    {"name": "Sambhar Lake", "lat": 26.97, "lon": 75.08, "buffer_km": 15},
    {"name": "Kolleru Lake", "lat": 16.65, "lon": 81.20, "buffer_km": 18},
]

# Forest regions
FOREST_REGIONS = [
    {"name": "Hasdeo Arand", "lat": 22.55,  "lon": 82.50,  "buffer_km": 20},
    {"name": "Buxwaha",      "lat": 24.25,  "lon": 79.29,  "buffer_km": 6},
    {"name": "Talabira",     "lat": 21.735, "lon": 83.989, "buffer_km": 6},
]
