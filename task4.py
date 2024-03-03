import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

# Load the datasets
country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype={'country-code': str})
df = pd.read_csv('https://raw.githubusercontent.com/wyeekong/bmi706brainstorm/main/country.csv')
pharma = pd.read_csv('https://raw.githubusercontent.com/wyeekong/bmi706brainstorm/main/pharma_country.csv', encoding='latin1')

# Merge datasets
merged_df = pd.merge(df, country_df[['Country', 'country-code']], left_on='Study population', right_on='Country', how='left').dropna()
merged_df['year'] = merged_df['year'].astype(int)
merged_pharma = pd.merge(pharma, country_df[['Country', 'country-code']], left_on='Study population', right_on='Country', how='left')

# Set page configuration
st.set_page_config(layout="wide")

# Streamlit app layout
st.title('Clinical Trials Dashboard')

# Selector for choosing between different themes
selected_theme = st.sidebar.selectbox("Select Theme", ["Country", "Funding"])

# Common selectors for year and phase
selected_year = st.sidebar.slider('Select Year', min_value=min(merged_df['year']), max_value=max(merged_df['year']), value=(min(merged_df['year']), max(merged_df['year'])))
selected_phases = st.sidebar.multiselect('Select Phase(s)', options=merged_df['phase'].unique(), default=merged_df['phase'].unique())

# Filter data based on selected year and phase
df_filtered_by_phase = merged_df[(merged_df['year'].between(selected_year[0], selected_year[1])) & (merged_df['phase'].isin(selected_phases))]

if selected_theme == "Country":
    # Display charts related to country theme
    st.subheader('Country Theme')
    
    # Add your country-related charts here
    st.write("Charts related to Country theme")
      

elif selected_theme == "Funding":
    # Display charts related to funding theme
    st.subheader('Funding Theme')
    
    # Add your funding-related charts here
    st.write("Charts related to Funding theme")

    # Add additional charts or data related to funding theme here