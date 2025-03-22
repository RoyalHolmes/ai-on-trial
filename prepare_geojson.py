import json
import pandas as pd

# Load your dataset
with open("ai_on_trial_data_static_geo.json") as f:
    data = json.load(f)
df = pd.DataFrame(data)

# Count cases by region
case_counts = df["region"].value_counts().to_dict()

# Load GeoJSON file
with open("countries.geojson") as f:
    geo = json.load(f)

# Optional mapping to fix country name mismatches
name_corrections = {
    "United States of America": "United States",
    "Russian Federation": "Russia",
    "Korea, Republic of": "South Korea",
    "Iran (Islamic Republic of)": "Iran",
    "United Kingdom": "United Kingdom",
    "Viet Nam": "Vietnam",
    "Syrian Arab Republic": "Syria",
    "Democratic Republic of the Congo": "DR Congo",
    "Venezuela (Bolivarian Republic of)": "Venezuela",
    "Lao People's Democratic Republic": "Laos",
    "Republic of Moldova": "Moldova",
    "North Macedonia": "Macedonia",
    "Czechia": "Czech Republic",
    "Slovakia": "Slovak Republic",
    "Bolivia (Plurinational State of)": "Bolivia",
    "Tanzania, United Republic of": "Tanzania"
}

# Define color scale function
def compute_color(cases):
    if cases == 0:
        return [230, 230, 230]  # Light gray
    elif cases <= 5:
        return [180, 200, 240]
    elif cases <= 15:
        return [120, 150, 210]
    elif cases <= 30:
        return [70, 100, 180]
    else:
        return [30, 60, 140]  # Dark blue

# Attach case count and color to each country feature
for feature in geo["features"]:
    geo_name = feature["properties"]["name"]
    region_name = name_corrections.get(geo_name, geo_name)
    count = case_counts.get(region_name, 0)
    feature["properties"]["cases"] = count
    feature["properties"]["fill_color"] = compute_color(count)

# Save updated file
with open("choropleth_ai_cases.geojson", "w") as f:
    json.dump(geo, f)

print("✅ GeoJSON updated with case counts and color fills.")