"""
Dash App: SpaceX Launch Records Dashboard

What this app does
1. Interactive dashboard to explore SpaceX Falcon 9 launch outcomes.
2. Controls:
    - Launch site dropdown (All Sites or specific site)
    - Payload mass range slider
3. Visualizations:
    - Pie chart of successful launches (All Sites) OR success vs failure (single site)
    - Scatter plot of payload mass vs launch success, colored by a booster category

Input: data/processed/03_dataset_part_2.csv (from previous steps)

Run: From repo root: python src/07_dash_app.py
"""

# Import libraries
from pathlib import Path

import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / 'data' / 'processed' / '03_dataset_part_2.csv'

# Read the data into pandas DataFrame
spacex_df = pd.read_csv(DATA_PATH)

# Adapt Step 03 schema -> original Dash app schema
spacex_df = spacex_df.rename(
    columns = {
        'LaunchSite': 'Launch Site',
        'PayloadMass': 'Payload Mass (kg)',
        'Class': 'class',
    }
)

# Create a new column for Booster Version Category from the BoosterVersion and Block columns
def block_to_category(x):
    if pd.isna(x):
        return 'Unknown'
    try:
        return f'Block {int(x)}'
    except Exception:
        return 'Unknown'

# Add 'Booster Version Category' column and convert 'Payload Mass (kg)' to numeric
spacex_df['Booster Version Category'] = spacex_df['Block'].apply(block_to_category)

legend_rename = {
    'Block 1': 'v1.1',
    'Block 2': 'FT (B2)',
    'Block 3': 'FT (B3)',
    'Block 4': 'FT (B4)',
    'Block 5': 'FT (B5)',
}

spacex_df['Booster Version Category'] = spacex_df['Booster Version Category'].replace(legend_rename)

spacex_df['Payload Mass (kg)'] = pd.to_numeric(spacex_df['Payload Mass (kg)'], errors = 'coerce')

# Get min and max payload mass for slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Dash app setup
app = dash.Dash(__name__)
app.title = 'SpaceX Launch Records Dashboard'

# Layout of the Dash app
app.layout = html.Div(children = [
    html.H1(
        'SpaceX Launch Records Dashboard',
        style = {'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    dcc.Dropdown(
        id = 'site-dropdown',
        options = (
            [{'label': 'All Sites', 'value': 'ALL'}] +
            [{'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())]
        ),
        value = 'ALL',
        placeholder = 'Select a Launch Site here',
        searchable = True
    ),
    html.Br(),

    html.Div(dcc.Graph(id = 'success-pie-chart')),
    html.Br(),

    html.P('Payload range (Kg):'),
    dcc.RangeSlider(
        id = 'payload-slider',
        min = 0,
        max = 10000,
        step = 1000,
        marks = {
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        },
        value = [float(min_payload), float(max_payload)]
    ),

    html.Div(dcc.Graph(id = 'success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output(component_id = 'success-pie-chart', component_property = 'figure'),
    Input(component_id = 'site-dropdown', component_property = 'value')
)

# Pie chart generation function
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        return px.pie(
            spacex_df,
            values = 'class',
            names = 'Launch Site',
            title = 'Total Successful Launches by Site'
        )

    filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
    outcome_counts = filtered_df['class'].value_counts().reset_index()
    outcome_counts.columns = ['class', 'count']

    return px.pie(
        outcome_counts,
        values = 'count',
        names = 'class',
        title = f'Total Success Launches for site {selected_site}'
    )

# Callback for scatter plot
@app.callback(
    Output(component_id = 'success-payload-scatter-chart', component_property = 'figure'),
    [
        Input(component_id = 'site-dropdown', component_property = 'value'),
        Input(component_id = 'payload-slider', component_property = 'value')
    ]
)

# Scatter plot generation function
def get_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        title = f'Correlation between Payload and Success for site {selected_site}'
    else:
        title = 'Correlation between Payload and Success for all sites'
    
    return px.scatter(
        filtered_df,
        x = 'Payload Mass (kg)',
        y = 'class',
        color = 'Booster Version Category',
        hover_data = ['Serial', 'Block', 'BoosterVersion'],
        title = title
    )

# Run the app
if __name__ == '__main__':
    app.run()