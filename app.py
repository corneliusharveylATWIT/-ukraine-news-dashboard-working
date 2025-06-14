# Step 5: Import libraries
import requests
import pandas as pd
from io import StringIO
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# Step 6: Define Data Range and API Queries
# Define date range
start_day_str = '20211228'  # December 28, 2021
last_day_str = '20221231'   # December 31, 2022

# Create API query URLs for Ukraine and Russia keywords
query_url_ukr = f"https://api.gdeltproject.org/api/v2/tv/tv?query=(ukraine%20OR%20ukrainian%20OR%20zelenskyy%20OR%20zelensky%20OR%20kiev%20OR%20kyiv)%20market:%22National%22&mode=timelinevol&format=html&datanorm=perc&format=csv&timelinesmooth=5&datacomb=sep&timezoom=yes&STARTDATETIME={start_day_str}120000&ENDDATETIME={last_day_str}120000"
query_url_rus = f"https://api.gdeltproject.org/api/v2/tv/tv?query=(kremlin%20OR%20russia%20OR%20putin%20OR%20moscow%20OR%20russian)%20market:%22National%22&mode=timelinevol&format=html&datanorm=perc&format=csv&timelinesmooth=5&datacomb=sep&timezoom=yes&STARTDATETIME={start_day_str}120000&ENDDATETIME={last_day_str}120000"

# Function to convert API response to dataframe
def to_df(queryurl):
    response = requests.get(queryurl)
    content_text = StringIO(response.content.decode('utf-8'))
    df = pd.read_csv(content_text)
    return df

#Step 7: Create Function to Retrieve Data
# Retrieve data from API
df_ukr = to_df(query_url_ukr)
df_rus = to_df(query_url_rus)

# Print debug information
print("Ukraine dataframe columns:", df_ukr.columns.tolist())
print("Russia dataframe columns:", df_rus.columns.tolist())
print("Ukraine dataframe first few rows:")
print(df_ukr.head())

# Step 8: Clean and prepare data
# Rename columns (note: column name might vary, adapt based on debug output)
df_ukr = df_ukr.rename(columns={'Date (Daily +00:00: 12/28/2021 - 12/31/2022)': "date_col"})
df_rus = df_rus.rename(columns={'Date (Daily +00:00: 12/28/2021 - 12/31/2022)': "date_col"})

# Convert strings to datetime
df_ukr['date_col'] = pd.to_datetime(df_ukr['date_col'])
df_rus['date_col'] = pd.to_datetime(df_rus['date_col'])

# Select specific stations (CNN, Fox News, MSNBC)
df_rus = df_rus[[x in ['CNN', 'FOXNEWS', 'MSNBC'] for x in df_rus.Series]]
df_ukr = df_ukr[[x in ['CNN', 'FOXNEWS', 'MSNBC'] for x in df_ukr.Series]]

# Add temporary code to verify our data preparation
print("\nAfter cleaning, we have:")
print(f"Ukraine data: {len(df_ukr)} rows for {df_ukr['Series'].nunique()} TV stations")
print(f"Russia data: {len(df_rus)} rows for {df_rus['Series'].nunique()} TV stations")
print("\nSample of Ukraine data:")
print(df_ukr.head())

#Step 9: Intitalize Dashboard with a theme

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
server = app.server

#Step 10: Create Dashboard Layout
app.layout = dbc.Container(
    [   
        # Title row
        dbc.Row([
            dbc.Col([html.H1('US National Television News Coverage of the War in Ukraine')],
            className="text-center mt-3 mb-1")
        ]),
        
        # Date range label
        dbc.Row([
            dbc.Label("Select a date range:", className="fw-bold")
        ]),
        
        # Date picker
        dbc.Row([
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=df_ukr['date_col'].min().date(),
                max_date_allowed=df_ukr['date_col'].max().date(),
                initial_visible_month=df_ukr['date_col'].min().date(),
                start_date=df_ukr['date_col'].min().date(),
                end_date=df_ukr['date_col'].max().date()
            )
        ]),

        # Ukraine graph
        dbc.Row([
            dbc.Col(dcc.Graph(id='line-graph-ukr'))
        ]),

        # Russia graph
        dbc.Row([
            dbc.Col(dcc.Graph(id='line-graph-rus'))
        ])
    ]
)

# Step 11: Define the callback function for interactivity
@app.callback(
    Output('line-graph-ukr', 'figure'),
    Output('line-graph-rus', 'figure'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')   
)

def update_output(start_date, end_date):
    # Filter dataframes based on date range
    mask_ukr = (df_ukr['date_col'] >= start_date) & (df_ukr['date_col'] <= end_date)
    mask_rus = (df_rus['date_col'] >= start_date) & (df_rus['date_col'] <= end_date)
    df_ukr_filtered = df_ukr.loc[mask_ukr]
    df_rus_filtered = df_rus.loc[mask_rus]
    
    # Create line graphs
    line_fig_ukr = px.line(df_ukr_filtered, x="date_col", y="Value", 
                     color='Series', title="Coverage of Ukrainian Keywords")
    line_fig_rus = px.line(df_rus_filtered, x='date_col', y='Value', 
                     color='Series', title="Coverage of Russian Keywords")

    # Set axis titles
    line_fig_ukr.update_layout(
                   xaxis_title='Date',
                   yaxis_title='Percentage of Airtime')
    line_fig_rus.update_layout(
                   xaxis_title='Date',
                   yaxis_title='Percentage of Airtime')
    
    # Format date labels
    line_fig_ukr.update_xaxes(tickformat="%b %d<br>%Y")
    line_fig_rus.update_xaxes(tickformat="%b %d<br>%Y")
    
    return line_fig_ukr, line_fig_rus

# Step 12: Run the app
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))  # 8050 is a safe fallback for local dev
    app.run_server(host="0.0.0.0", port=port)





