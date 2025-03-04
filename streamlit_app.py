import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px

# Function to scrape GDP data with improved parsing
@st.cache_data
def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})

    if not tables:
        st.error("No tables found on Wikipedia page.")
        return pd.DataFrame()

    table = tables[0]
    df = pd.read_html(str(table))[0]

    df.columns = ['Country/Territory', 'IMF', '_IMF_Year', 'World Bank', '_WB_Year', 'United Nations', '_UN_Year']
    df = df[['Country/Territory', 'IMF', 'World Bank', 'United Nations']]
    df = df.dropna(subset=['Country/Territory'])

    for col in ['IMF', 'World Bank', 'United Nations']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# Function to assign regions to countries
def assign_regions(df):
    region_map = {
        "United States": "North America",
        "Canada": "North America",
        "Mexico": "North America",
        "Brazil": "South America",
        "Argentina": "South America",
        "Germany": "Europe",
        "France": "Europe",
        "United Kingdom": "Europe",
        "Italy": "Europe",
        "Russia": "Europe",
        "China": "Asia",
        "Japan": "Asia",
        "India": "Asia",
        "South Korea": "Asia",
        "Indonesia": "Asia",
        "Australia": "Oceania",
        "Saudi Arabia": "Middle East",
        "South Africa": "Africa",
        "Nigeria": "Africa",
    }

    df["Region"] = df["Country/Territory"].map(region_map).fillna("Other")
    return df

# Streamlit UI
st.title("Global GDP Visualization - Stacked Bar Chart by Region")

df = get_gdp_data()

if df.empty:
    st.error("No data extracted. Check debugging info above.")
else:
    df = assign_regions(df)  # Assign regions
    st.dataframe(df)  # Display cleaned DataFrame

    # Allow user to select data source
    gdp_source = st.selectbox("Select GDP Data Source:", ["IMF", "World Bank", "United Nations"])

    # Aggregate GDP within regions
    df_grouped = df.groupby(["Region", "Country/Territory"])[gdp_source].sum().reset_index()

    # Plot stacked bar chart
    fig = px.bar(df_grouped, 
                 x="Region", 
                 y=gdp_source, 
                 color="Country/Territory", 
                 title=f"Stacked Bar Plot of GDP by Region ({gdp_source})", 
                 labels={gdp_source: "GDP (in millions)", "Region": "World Region"}, 
                 barmode="stack")

    st.plotly_chart(fig)  # Display the Plotly figure
