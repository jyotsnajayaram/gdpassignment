import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px  # Import Plotly for visualization

# Function to scrape GDP data with improved parsing
@st.cache_data
def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})

    st.write(f"Number of tables found: {len(tables)}")

    if not tables:
        st.error("No tables found on Wikipedia page.")
        return pd.DataFrame()

    table = tables[0]
    df = pd.read_html(str(table))[0]

    st.write("Extracted raw DataFrame:", df.head())

    df.columns = ['Country/Territory', 'IMF', '_IMF_Year', 'World Bank', '_WB_Year', 'United Nations', '_UN_Year']
    df = df[['Country/Territory', 'IMF', 'World Bank', 'United Nations']]

    df = df.dropna(subset=['Country/Territory'])

    for col in ['IMF', 'World Bank', 'United Nations']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    st.write("Cleaned DataFrame:", df.head())

    return df

# Streamlit UI
st.title("Global GDP Visualization - Improved Debug Mode")

df = get_gdp_data()

if df.empty:
    st.error("No data extracted. Check debugging info above.")
else:
    st.success("Data successfully extracted!")
    st.dataframe(df)  # ✅ Display cleaned DataFrame

    # ✅ Insert Plotly Visualization Here
    df_sorted = df.sort_values(by="IMF", ascending=False).head(10)  # Top 10 economies
    df_melted = df_sorted.melt(id_vars=["Country/Territory"], 
                               value_vars=["IMF", "World Bank", "United Nations"], 
                               var_name="Source", value_name="GDP")

    fig = px.bar(df_melted, 
                 x="Country/Territory", 
                 y="GDP", 
                 color="Source", 
                 title="Stacked Bar Plot of GDP by Country (IMF, World Bank, UN)", 
                 labels={"GDP": "GDP (in millions)", "Country/Territory": "Country"}, 
                 barmode="stack")

    st.plotly_chart(fig)  # ✅ Display the Plotly figure
