# -*- coding: utf-8 -*-
"""streamlit_app_debug_v3"""

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# Define debug file path BEFORE using it
debug_file_path_v3 = "/mnt/data/debug_output.txt"  # Define a valid path
os.makedirs(os.path.dirname(debug_file_path_v3), exist_ok=True)

# Function to scrape GDP data with improved parsing
@st.cache_data
def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})

    # Debug: Show number of tables found
    st.write(f"Number of tables found: {len(tables)}")

    if not tables:
        st.error("No tables found on Wikipedia page.")
        return pd.DataFrame()

    # Try different table indexes if needed
    table = tables[0]  # If this fails, change to tables[1] or tables[2]

    # Read table into pandas DataFrame
    df = pd.read_html(str(table))[0]

    # Debug: Show raw extracted DataFrame
    st.write("Extracted raw DataFrame:", df.head())

    # Ensure correct column names (adapt to any changes in Wikipedia's table format)
    expected_columns = ['Country/Territory', 'IMF', '_IMF_Year', 'World Bank', '_WB_Year', 'United Nations', '_UN_Year']
    if len(df.columns) >= len(expected_columns):
        df.columns = expected_columns
        df = df[['Country/Territory', 'IMF', 'World Bank', 'United Nations']]  # Keep only relevant columns
    else:
        st.error("Unexpected table structure. Check extracted columns:", df.columns)
        return pd.DataFrame()

    # Drop rows where 'Country/Territory' is missing (these are header artifacts)
    df = df.dropna(subset=['Country/Territory'])

    # Convert GDP values to numeric (handling non-numeric cases gracefully)
    for col in ['IMF', 'World Bank', 'United Nations']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Debug: Show cleaned DataFrame
    st.write("Cleaned DataFrame:", df.head())

    return df

# Streamlit UI
st.title("Global GDP Visualization - Improved Debug Mode")

# Get data
df = get_gdp_data()

if df.empty:
    st.error("No data extracted. Check debugging info above.")
else:
    st.success("Data successfully extracted!")
    st.dataframe(df)  # Display cleaned DataFrame

# Save the improved debugging script
with open(debug_file_path_v3, "w", encoding="utf-8") as file:
    file.write(__file__)  # Save this script for reference

# Return the new debug script file path for the user
debug_file_path_v3
