import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
!pip install vega_datasets
from vega_datasets import data

# Load the dataset
#this dataframe contain country codes for geospatial data
country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})
#this dataframe contain all the raw data required regarding trials information
df=pd.read_csv('https://raw.githubusercontent.com/wyeekong/bmi706brainstorm/main/country.csv')
df['totaltrials'] = df.groupby(['Study population', 'year', 'phase'])['Study population'].transform('count')
merged_df = pd.merge(df, country_df[['Country', 'country-code']], left_on='Study population',right_on='Country', how='left')


st.set_page_config(layout="wide")

# Streamlit app layout
st.title('Antiseizure Clinical Trials Dashboard')

year = st.selectbox('Select Year', options=merged_df['year'].unique())
df_filtered = merged_df[merged_df['year'] == year]

selected_phases = st.multiselect('Select Phase(s)', options=df_filtered['phase'].unique(), default=df_filtered['phase'].unique())
df_filtered_by_phase = df_filtered[df_filtered['phase'].isin(selected_phases)]

# Create columns for layout
left_column, center_column, right_column = st.columns([2, 10, 5])

with left_column:
    # Country Ranking List
    st.subheader('Country Ranking List')
    country_rank = df_filtered_by_phase.groupby('Study population')['totaltrials'].sum().reset_index().sort_values('totaltrials', ascending=False)
    for _, row in country_rank.iterrows():
        st.write(f"{row['Study population']}: {row['totaltrials']} trials")

  

with center_column:
    # Geospatial Chart
    st.subheader('Geospatial Chart')
    # Vega_datasets world data
    source = alt.topo_feature(data.world_110m.url, 'countries')
    
    selector = alt.selection_single(fields=['Study population'], on='click', empty="all", clear='dblclick')

    #Base chart
    chart_base = alt.Chart(source).properties(
        width=600,
        height=300
    ).project('equirectangular').add_selection(selector)
    
    # Geoshape for number of trials by country
    chart_trials = chart_base.mark_geoshape().encode(
        color=alt.Color(field="totaltrials", type="quantitative", scale=alt.Scale(scheme='oranges')),
        tooltip=['Study population:N', 'totaltrials:Q']
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(df_filtered_by_phase, "country-code", ["totaltrials", 'Study population'])
    ).transform_filter(selector).properties(
        title=f'Number of Trials by Country for {year} and {", ".join(selected_phases)} Phase(s)'
    )
    
    # Combine the background map and trials map
    chart2 = alt.layer(background, chart_trials).resolve_scale(color='independent')
    
    st.altair_chart(chart2)




      # Heatmap of trials
    st.subheader('Trials Heatmap')
    # Aggregate data for heatmap
    heatmap_data = df_filtered_by_phase.groupby(['Study population', 'year'])['totaltrials'].sum().reset_index()
    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
        x='year:O',
        y='Study population:N',
        color='totltrials:Q',
        tooltip=['Study population', 'year', 'totaltrials']
    ).properties(
        width=300,
        height=300
    )
    st.altair_chart(heatmap, use_container_width=True)

with right_column:
    # Country Selector
    country = st.selectbox('Select Country', options=df['Study population'].unique())
    df_country = df_filtered_by_phase[df_filtered_by_phase['Study population'] == country]

    # Line and Dot Graph for the selected country
    st.subheader(f'Trials Over Years for {country}')
    line_chart = alt.Chart(df_country).mark_line(point=True).encode(
        x='year',
        y='totaltrials',
        color='phase',
        tooltip=['year', 'phase', 'totaltrials']
    ).properties(
        width=500,
        height=300
    ).interactive()
    st.altair_chart(line_chart, use_container_width=True)