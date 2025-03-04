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
    selected_table = tables[0]  # First table is usually the GDP table

    # Extract headers and clean them (remove reference numbers)
    raw_headers = [th.text.strip() for th in selected_table.find_all('tr')[0].find_all('th')]
    headers = [re.sub(r'\[\d+\]', '', h) for h in raw_headers]  # Remove reference numbers

    # Mapping for column selection
    source_mapping = {
        "IMF": "IMF",
        "World Bank": "World Bank",
        "UN": "United Nations"
    }

    if source not in source_mapping:
        st.error(f"Invalid source: {source}")
        return pd.DataFrame()

    try:
        source_col_index = headers.index(source_mapping[source])
    except ValueError:
        st.error(f"Column for {source} not found.")
        return pd.DataFrame()

    # Extract data
    data = []
    for row in selected_table.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        if len(cols) > source_col_index:  # Ensure column exists
            country = cols[0].text.strip()
            gdp = cols[source_col_index].text.strip().replace(',', '')

            try:
                gdp = float(gdp)
            except ValueError:
                continue  # Skip invalid rows

            data.append({'Country': country, 'GDP': gdp})

    df = pd.DataFrame(data)

    # Add region mapping
    region_mapping = {
        "United States": "North America",
        "Canada": "North America",
        "Mexico": "North America",
        "Germany": "Europe",
        "United Kingdom": "Europe",
        "France": "Europe",
        "Italy": "Europe",
        "Spain": "Europe",
        "Russia": "Europe",
        "China": "Asia",
        "Japan": "Asia",
        "India": "Asia",
        "South Korea": "Asia",
        "Australia": "Oceania",
        "Brazil": "South America"
    }

    df["Region"] = df["Country"].map(region_mapping)
    df = df.dropna()  # Remove countries without a region

    return df

# Streamlit UI
st.title("GDP by Country & Region Visualization")

# Dropdown for selecting the data source
source = st.selectbox("Select Data Source", ["IMF", "World Bank", "UN"])

# Get GDP data based on selection
gdp_data = get_gdp_data(source)

if gdp_data.empty:
    st.warning("No data available. Please check if the Wikipedia table structure has changed.")
else:
    # Aggregate by region
    region_gdp = gdp_data.groupby(["Region", "Country"], as_index=False).sum()

    # Plot stacked bar chart
    fig = px.bar(
        region_gdp,
        x="Region",
        y="GDP",
        color="Country",
        title=f"Stacked GDP by Region ({source} Data)",
        labels={"GDP": "Gross Domestic Product (USD)", "Region": "Region"},
        barmode="stack"
    )

    st.plotly_chart(fig)
