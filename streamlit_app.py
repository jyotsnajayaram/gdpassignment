import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import pycountry_convert as pc

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

# Function to automatically assign regions using pycountry_convert
def assign_regions(df):
    def get_continent(country):
        try:
            # Remove "World" before processing
            if country.lower() == "world":
                return None  # Exclude this row from the dataset

            country_code = pc.country_name_to_country_alpha2(country, cn_name_format="default")
            continent_code = pc.country_alpha2_to_continent_code(country_code)

            continent_map = {
                "NA": "North America",
                "SA": "South America",
                "EU": "Europe",
                "AF": "Africa",
                "AS": "Asia",
                "OC": "Oceania"
            }
            return continent_map.get(continent_code, "Other")
        except:
            return "Other"

    df["Region"] = df["Country/Territory"].apply(get_continent)
    
    # Drop any rows where Region is None (removes "World")
    df = df.dropna(subset=["Region"])
    
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
