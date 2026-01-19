"""
07 SpaceX Falcon 9 - Interactive Dashboard with Dash

Purpose
- Provide an interactive dashboard to explore Falcon 9 first-stage landing outcomes.
- Controls:
    - Launch site dropdown (All Sites or a specific site)
    - Payload mass range slider
- Visualizations:
    - Pie chart of successful launches by site (All Sites) or success vs failure (single site)
    - Scatter plot: payload mass vs outcome, colored by booster version category

Running live dashboard (Dash) locally
1) From repo root:
    python src/07_dash_app.py
2) Open:
    http://127.0.0.1:8050

    
Static HTML preview (for GitHub Pages)
- Export a non-interactive preview (no Dash callbacks) to:
    docs/dashboard_preview.html
- Run:
    python src/07_dash_app.py --export-preview

Data
- Input: data/processed/03_dataset_part_2.csv

"""

from __future__ import annotations

import site
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio

# --- PATHS ---

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
DOCS_DIR = REPO_ROOT / 'docs'

INPUT_CSV = PROCESSED_DIR / '03_dataset_part_2.csv'
PREVIEW_HTML = DOCS_DIR / '07_dash_app_preview.html'

# --- CONSTANTS ---

# Load data
def load_data() -> pd.DataFrame:
    return pd.read_csv(INPUT_CSV)

# Compute payload mass bounds
def payload_bounds(df: pd.DataFrame) -> tuple[float, float]:
    s = pd.to_numeric(df['PayloadMass'], errors = 'coerce').dropna()
    return float(s.min()), float(s.max())

def fig_pie(df: pd.DataFrame, site: str):
    if site == 'ALL':
        # Sum of Class (0/1) per site = total successes
        return px.pie(
            df,
            values = 'Class',
            names = 'LaunchSite',
            title = 'Total Successful Launches by Site',
            labels = {'LaunchSite': 'Launch Site', 'Class': 'Success (0/1)'},
        )
    
    d = df[df['LaunchSite'] == site]
    counts = d['Class'].value_counts().reset_index()
    counts.columns = ['Class', 'count']
    counts['Class'] = counts['Class'].map({1: 'Success', 0: 'Failure'}).fillna(counts['Class'])

    return px.pie(
        counts,
        values = 'count',
        names = 'Class',
        title = f'Success vs Failure for {site}',
    )

def fig_scatter(df: pd.DataFrame, site: str, payload_range: tuple[float, float]) -> go.Figure:
    d = df[(df['PayloadMass'] >= payload_range[0]) & (df['PayloadMass'] <= payload_range[1])]

    if site != 'ALL':
        d = d[d['LaunchSite'] == site]
        title = f'Payload vs Landing Outcome ({site})'
    else:
        title = 'Payload vs Landing Outcome (All Sites)'

    color_col = None
    if 'Block' in d.columns:
        d = d.copy()
        d['BlockLabel'] = d['Block'].apply(lambda v: f'Block {int(v)}' if pd.notna(v) else 'Unknown')
        color_col = 'BlockLabel'
    
    fig = px.scatter(
        d,
        x = 'PayloadMass',
        y = 'Class',
        color = color_col,
        hover_data = [c for c in ['LaunchSite', 'Orbit', 'Serial', 'Block'] if c in d.columns],
        title = title,
        labels = {'PayloadMass': 'Payload Mass (kg)', 'Class': 'Landing Outcome', 'BlockLabel': 'Block'},
    )
    fig.update_yaxes(tickmode = 'array', tickvals = [0,1], ticktext = ['Failure (0)', 'Success (1)'])
    return fig

def export_preview() -> Path:
    df = load_data()
    PREVIEW_HTML.parent.mkdir(parents = True, exist_ok = True)
    
    mn, mx = payload_bounds(df)
    pie = fig_pie(df, 'ALL')
    scat = fig_scatter(df, 'ALL', (mn, mx))

    pie_html = pio.to_html(pie, full_html = False, include_plotlyjs = 'cdn')
    scat_html = pio.to_html(scat, full_html = False, include_plotlyjs = False)

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SpaceX Dashboard Preview</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; }}
    .card {{ border: 1px solid #e5e5e5; border-radius: 12px; padding: 16px; margin: 18px 0; }}
    .note {{ color: #444; margin: 0 0 16px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>SpaceX Launch Dashboard — Static Preview</h1>
    <p class="note">Static Plotly figures only. The live Dash dashboard runs locally (or on a Python host), not on GitHub Pages.</p>
    <div class="card">{pie_html}</div>
    <div class="card">{scat_html}</div>
  </div>
</body>
</html>"""
    
    PREVIEW_HTML.write_text(page, encoding = 'utf-8')
    return PREVIEW_HTML

def run_server() -> None:
    # Dash is imported here so --export-preview works even if Dash is not installed in this env.
    import dash
    from dash import dcc, html
    from dash.dependencies import Input, Output

    df = load_data()
    mn, mx = payload_bounds(df)

    app = dash.Dash(__name__)
    app.title = 'SpaceX Falcon 9 - Launch Records Dashboard'

    sites = sorted(df['LaunchSite'].dropna().unique().tolist())

    app.layout = html.Div(
        [
            html.H1('SpaceX Falcon 9 - Launch Records Dashboard', style = {'textAlign': 'center'}),
            # Dropdown for Launch Site selection
            dcc.Dropdown(
                id = 'site-dropdown',
                options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': s, 'value': s} for s in sites],
                value = 'ALL',
                placeholder = 'Select a Launch Site',
                clearable = False,
            ),

            dcc.Graph(id = 'success-pie-chart'),
            html.P('Payload range (kg):'),
            dcc.RangeSlider(
                id = 'payload-slider',
                min = 0,
                max = 10000,
                step = 1000,
                marks = {0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                value = [mn, mx],
            ),
            dcc.Graph(id = 'success-payload-scatter-chart'),
        ],
        style = {'maxWidth': '1100px', 'margin': '0 auto', 'padding': '12px'},
    )

    @app.callback(Output('success-pie-chart', 'figure'), Input('site-dropdown', 'value'))
    def _update_pie(site):
        return fig_pie(df, site)
    
    @app.callback(
        Output('success-payload-scatter-chart', 'figure'),
        [Input('site-dropdown', 'value'), Input('payload-slider', 'value')],
    )

    def _update_scatter(site, rng):
        low, high = float(rng[0]), float(rng[1])
        return fig_scatter(df, site, (low, high))
    
    app.run_server(host = '127.0.0.1', port = 8050, debug = True)

if __name__ == '__main__':
    if '--export-preview' in sys.argv:
        out = export_preview()
        print(f'Wrote: {out.as_posix()}')
    else:
        run_server()