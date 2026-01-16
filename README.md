# SpaceX Falcon 9 | First-Stage Landing Success Prediction

Predict whether a Falcon 9 first-stage booster will land successfully, and identify the key drivers (payload, orbit, launch site, booster version, etc.).
Built as an end-to-end data science project: data collection -> EDA (SQL + viz) -> interactive analytics (Folium + Dash) -> classification models.

## Key Results
- Landing success rate increases over time; clear differences by launch site/orbit/payload.
- Best model: ~0.83 test accuracy (LogReg/SVM/DT/KNN performed similarly in this dataset).

## Repo structure
- `notebooks/`: numbered project notebooks (data collection, wrangling, EDA, viz, modeling)
- `data/raw/`: raw inputs (API pulls, scraped HTML, etc.)
- `data/processed/`: cleaned datasets, SQLite DB, derived artifacts
- `src/`: Dash app
