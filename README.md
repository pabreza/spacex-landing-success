# SpaceX Falcon 9 | First-Stage Landing Success Prediction

Predict whether a Falcon 9 first-stage booster will land successfully, and identify key drivers (payload mass, orbit, launch site, booster version category, reuse features, etc.).

This repo is an end-to-end data science project:
**data collection ➡︎ data wrangling ➡︎ EDA (SQL + visualization) ➡︎ interactive analytics (Folium + Dash) ➡︎ ML classification**.

---

## Key Results (from saved artifacts)
- Landing success rate increases over time; clear differences by **launch site**,**orbit**, and **payload mass**.
- Model comparison (test split): **SVM / Logistic Regression / KNN ≈ 0.78 test accuracy** on this dataset.
- Best saved model snapshot: **SVM ≈ 0.78 test accuracy**, **~0.86 best CV score (10-fold)**.

See:
- `data/processed/08_model_performance.csv`
- `data/processed/08_best_model.json`

---

## Live demos (GitHub Pages)
This repo includes static HTML outputs in `docs/`:
- `docs/06_launch_site_map.html` (Folium map)
- `docs/07_dash_app_preview.html` (static Plotly preview of the Dash dasboard)

---

## Repo structure
- `notebooks/`: numbered notebooks (data collection, wrangling, EDA, visualization, modeling)
- `src/`: Dash app (`07_dash_app.py`)
- `data/raw/`: raw inputs (API pulls, scraped HTML)
- `data/processed/`: cleaned datasets, SQLite DB, derived artifacts, trained model
- `docs/`: static HTML outputs for GitHub Pages

---

## Quickstart (local)
### 1. Install dependencies
```bash
conda activate datasc3135
pip install -r requirements.txt
```

### 2. Run notebooks
From repo root:
```bash
jupyter lab
```

Run notebooks in order:
1. `01_data_collection_api.ipynb`
2. `02_webscraping_wikipedia.ipynb`
3. `03_data_wrangling.ipynb`
4. `04_eda_sql.ipynb`
5. `05_eda_visualization.ipynb`
6. `06_interactive_map_folium.ipynb`
7. `08_ml_modeling.ipynb`

### 3. Run Dash app (interactive)
```bash
python src/07_dash_app.py
```

Then open: `http://127.0.0.1:8050`

### 4. Export static dashboard preview (for GitHub Pages)
```bash
python src/07_dash_app.py --export-preview
```
Writes: `docs/07_dash_app_preview.html`

---

## Main artifacts produced
- `data/processed/03_dataset_part_2.csv`: cleaned dataset used across EDA + visualization
- `data/processed/04_spacex_launches.db`: SQLite database for SQL EDA
- `data/processed/06_launch_site_map.html`: interactive Folium map output (also copied to `docs/`)
- `data/processed/08_best_model.joblib`: best model pipeline
- `data/processed/08_best_model.json` + `08_model_performance.csv`: reproducible model summary