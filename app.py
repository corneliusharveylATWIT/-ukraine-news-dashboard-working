# Step 1: Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
from datetime import datetime

# Step 2: Define date range and API URLs
start_day_str = '20211228'
last_day_str = '20221231'

query_url_ukr = f"https://api.gdeltproject.org/api/v2/tv/tv?query=(ukraine%20OR%20ukrainian%20OR%20zelenskyy%20OR%20zelensky%20OR%20kiev%20OR%20kyiv)%20market:%22National%22&mode=timelinevol&format=csv&datanorm=perc&timelinesmooth=5&datacomb=sep&timezoom=yes&STARTDATETIME={start_day_str}120000&ENDDATETIME={last_day_str}120000"
query_url_rus = f"https://api.gdeltproject.org/api/v2/tv/tv?query=(kremlin%20OR%20russia%20OR%20putin%20OR%20moscow%20OR%20russian)%20market:%22National%22&mode=timelinevol&format=csv&datanorm=perc&timelinesmooth=5&datacomb=sep&timezoom=yes&STARTDATETIME={start_day_str}120000&ENDDATETIME={last_day_str}120000"

# Step 3: Function to retrieve data
@st.cache_data
def fetch_data(query_url):
    response = requests.get(query_url)
    df = pd.read_csv(StringIO(response.content.decode('utf-8')))
    df = df.rename(columns={df.columns[0]: "date_col"})  # Rename date column
    df["date_col"] = pd.to_datetime(df["date_col"])
    df = df[df["Series"].isin(["CNN", "FOXNEWS", "MSNBC"])]
    return df

# Step 4: Fetch and prepare data
df_ukr = fetch_data(query_url_ukr)
df_rus = fetch_data(query_url_rus)

# Step 5: UI layout
st.title("📺 US National News Coverage of the War in Ukraine")
st.write("This dashboard visualizes airtime coverage of Ukrainian and Russian topics on CNN, FOX News, and MSNBC from December 2021 through December 2022.")

# Date range picker
min_date = df_ukr['date_col'].min().date()
max_date = df_ukr['date_col'].max().date()
start_date, end_date = st.date_input("Select a date range:", [min_date, max_date], min_value=min_date, max_value=max_date)

# Step 6: Filter data
mask_ukr = (df_ukr['date_col'] >= pd.to_datetime(start_date)) & (df_ukr['date_col'] <= pd.to_datetime(end_date))
mask_rus = (df_rus['date_col'] >= pd.to_datetime(start_date)) & (df_rus['date_col'] <= pd.to_datetime(end_date))

df_ukr_filtered = df_ukr[mask_ukr]
df_rus_filtered = df_rus[mask_rus]

# Step 7: Plot figures
fig_ukr = px.line(df_ukr_filtered, x="date_col", y="Value", color="Series",
                  title="📊 Coverage of Ukrainian Keywords", labels={"Value": "% of Airtime", "date_col": "Date"})
fig_rus = px.line(df_rus_filtered, x="date_col", y="Value", color="Series",
                  title="📊 Coverage of Russian Keywords", labels={"Value": "% of Airtime", "date_col": "Date"})

fig_ukr.update_xaxes(tickformat="%b %d<br>%Y")
fig_rus.update_xaxes(tickformat="%b %d<br>%Y")

# Step 8: Show plots
st.plotly_chart(fig_ukr, use_container_width=True)
st.plotly_chart(fig_rus, use_container_width=True)





