
# -*- coding: utf-8 -*-
"""streamlit_app_debug_v2"""

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to scrape GDP data
@st.cache_data
def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})

    # Debug: Show how many tables were found
    st.write(f"Number of tables found: {len(tables)}")

    if not tables:
        st.error("No tables found on Wikipedia page.")
        return pd.DataFrame()

    # Debug: Show raw HTML of the first table
    st.write("First table HTML:", tables[0].prettify()[:1000])  # Show a preview

    return pd.DataFrame()  # Temporary return to debug

# Streamlit UI
st.title("Global GDP Visualization - Debug Mode")

# Get data
df = get_gdp_data()

if df.empty:
    st.error("No data extracted. Check debugging info above.")
