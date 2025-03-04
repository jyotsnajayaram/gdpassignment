# -*- coding: utf-8 -*-
"""streamlit_app"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import re

# Function to scrape GDP data
@st.cache_data
def get_gdp_data(source):
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})

    if not tables:
        st.error("No tables found on Wikipedia page.")
        return pd.DataFrame()

    # Identify the correct table
    selected_table = tables[0]

    # Extract headers and clean them
    raw_headers = [th.text.strip() for th in selected_table.find_all('tr')[0].find_all('th')]
    headers = [re.sub(r'\[\d+\]', '', h) for h in raw_headers]

    # Extract data rows
    rows = []
    for row in selected_table.find_all('tr')[1:]:
        cols = [td.text.strip() for td in row.find_all(['td', 'th'])]
        if len(cols) == len(headers):  # Ensure row has correct number of columns
            rows.append(cols)

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Clean and convert GDP values
    numeric_cols = ['IMF', 'World Bank', 'United Nations']
    for col in numeric_cols:
        df[col] = df[col].str.replace(',', '').str.extract('(\d+)').astype(float)

    return df

# Streamlit UI
st.title("Global GDP Visualization")

# Select data source
source = st.selectbox("Select Data Source", ["IMF", "World Bank", "United Nations"])

# Get data
df = get_gdp_data(source)

# Plot GDP by region (assuming data contains 'Region' column)
if not df.empty:
    fig = px.bar(df, x="Country/Territory", y=source, title=f"GDP by Country ({source})", color="Region", barmode="stack")
    st.plotly_chart(fig)
else:
    st.error("No data available.")
