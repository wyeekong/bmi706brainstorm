import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
from vega_datasets import data

# Load the dataset
#this dataframe contain country codes for geospatial data
country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})
#this dataframe contain all the raw data required regarding trials information
df=pd.read_csv('https://raw.githubusercontent.com/wyeekong/bmi706brainstorm/main/country.csv')
df['totaltrials'] = df.groupby(['Study population', 'year', 'phase'])['Study population'].transform('count')
merged_df = pd.merge(df, country_df[['Country', 'country-code']], left_on='Study population',right_on='Country', how='left')
merged_df = merged_df.dropna()
merged_df['year'] = merged_df['year'].astype(int)

#this dataframe contain pharma and country of origin
pharma=pd.read_csv('https://raw.githubusercontent.com/wyeekong/bmi706brainstorm/main/pharma_country.csv', encoding='latin1')
merged_pharma= pd.merge(pharma, country_df[['Country', 'country-code']], left_on='Study population',right_on='Country', how='left')

st.set_page_config(layout="wide")

# Streamlit app layout
st.title('Antiseizure Clinical Trials Dashboard')

year = st.slider('Select Year', min_value=min(merged_df['year']), max_value=max(merged_df['year']), value=(min(merged_df['year']), max(merged_df['year'])))
df_filtered = merged_df[merged_df['year'].between(year[0], year[1])]

selected_phases = st.multiselect('Select Phase(s)', options=df_filtered['phase'].unique(), default=df_filtered['phase'].unique())
df_filtered_by_phase = df_filtered[df_filtered['phase'].isin(selected_phases)]

# Create columns for layout
left_column, right_column = st.columns([2, 15])

with left_column:
    # Country Ranking List
    st.subheader('Country Ranking List')
    country_rank = df_filtered_by_phase.groupby('Study population')['totaltrials'].sum().reset_index().sort_values('totaltrials', ascending=False)
    for _, row in country_rank.iterrows():
        st.write(f"{row['Study population']}: {row['totaltrials']}")

  

with right_column:
    # Geospatial Chart
    st.subheader('Geospatial Chart')
    # Vega_datasets world data
    source = alt.topo_feature(data.world_110m.url, 'countries')
    width = 1600
    height  = 800
    project = 'equirectangular'

    # a gray map using as the visualization background
    background = alt.Chart(source
    ).mark_geoshape(
        fill='#aaa',
        stroke='white'
    ).properties(
        width=width,
        height=height
    ).project(project)
    
    aggregated_data = df_filtered_by_phase.groupby(['Study population','country-code'])['totaltrials'].sum().reset_index()
    pharma_total = merged_pharma.groupby(['Study population', 'country-code']).size().reset_index(name='count')

    selector = alt.selection_single(fields=['Study population'], on='click', empty="all", clear='dblclick')

    chart_base = alt.Chart(source
    ).properties(
        width=width,
        height=height
    ).project(project
    ).add_selection(selector
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(aggregated_data, "country-code", ["Study population","totaltrials"]),
    )

    
    total_trials_sum = aggregated_data['totaltrials'].max()
    rate_scale = alt.Scale(domain=[0, total_trials_sum], scheme='oranges')
    rate_color = alt.Color(field="totaltrials", type="quantitative", scale=rate_scale)

    chart_rate = chart_base.mark_geoshape().encode(
        color=rate_color,
        tooltip=['Study population:N','totaltrials:Q']
    ).transform_filter(selector
    ).properties(
        title=f'Trials by county'
    )

    pharma_chart_base = alt.Chart(source
    ).properties(
        width=width,
        height=height
    ).project(project
    ).add_selection(selector
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(pharma_total, "country-code", ["Study population","count"]),
    )

    pharma_trials_sum = pharma_total['count'].max()
    pharma_rate_scale = alt.Scale(domain=[0, pharma_trials_sum], scheme='yellowgreenblue')
    pharma_rate_color = alt.Color(field="count", type="quantitative", scale=pharma_rate_scale)

    pharma_chart_rate = pharma_chart_base.mark_geoshape().encode(
        color=pharma_rate_color,
        tooltip=['Study population:N','count:Q']
    ).transform_filter(selector
    ).properties(
        title=f'Trials by county'
    )

    chart2 = alt.vconcat(background + chart_rate, background + pharma_chart_rate
    ).resolve_scale(
        color='independent'
    )

    st.altair_chart(chart2)

    # Country Selector
    country_trials = df_filtered_by_phase.groupby('Study population')['totaltrials'].sum()
    top_countries = country_trials.sort_values(ascending=False).index[:20]
    country = st.selectbox('Select Country', options=top_countries)
    df_country = df_filtered_by_phase[df_filtered_by_phase['Study population'] == country]

    # Line and Dot Graph for the selected country
    st.subheader(f'Trials Over Years for {country}')
    line_chart = alt.Chart(df_country).mark_line(point=True).encode(
        x='year',
        y='totaltrials',
        color='phase',
        tooltip=['year', 'phase', 'totaltrials']
    ).properties(
        width=800,
        height=600
    )#.interactive()

    st.altair_chart(line_chart, use_container_width=True)