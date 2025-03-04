# -*- coding: utf-8 -*-
"""streamlit_app"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup

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

    # Identify the correct table by checking headers
    target_headers = ["Country/Territory", "Forecast", "Estimate"]
    selected_table = None

    for table in tables:
        headers = [th.text.strip() for th in table.find_all('tr')[0].find_all('th')]
        if any(header in headers for header in target_headers):
            selected_table = table
            break

    if selected_table is None:
        st.error("Could not find the correct GDP table.")
        return pd.DataFrame()

    headers = [th.text.strip() for th in selected_table.find_all('tr')[0].find_all('th')]
    st.write("Table Headers:", headers)  # Debugging

    # Corrected source mapping based on Wikipedia's table
    source_mapping = {
        "IMF": "Forecast",
        "World Bank": "Estimate",
        "UN": "Estimate"
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
        if len(cols) > source_col_index:  # Ensure we have enough columns
            country = cols[0].text.strip()
            gdp = cols[source_col_index].text.strip().replace(',', '')

            try:
                gdp = float(gdp)
            except ValueError:
                continue  # Skip if conversion fails

            data.append({'Country': country, 'GDP': gdp, 'Source': source})

    return pd.DataFrame(data)

# Streamlit UI
st.title("GDP by Country Visualization")

# Dropdown for selecting the data source
source = st.selectbox("Select Data Source", ["IMF", "World Bank", "UN"])

# Get GDP data based on selection
gdp_data = get_gdp_data(source)

if gdp_data.empty:
    st.warning("No data available. Please check if the Wikipedia table structure has changed.")
else:
    # Plot stacked bar chart
    fig = px.bar(
        gdp_data,
        x="Country",
        y="GDP",
        color="Source",
        title=f"GDP by Country ({source} Data)",
        labels={"GDP": "Gross Domestic Product (USD)", "Country": "Country"},
    )
    st.plotly_chart(fig)
