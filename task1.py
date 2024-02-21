import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt

# Load the dataset
url='https://raw.githubusercontent.com/wyeekong/bmi706brainstorm/main/clinical_trials_sample_dataset.csv'
df = pd.read_csv(url)
country_coords = {
    'USA': (37.0902, -95.7129),
    'UK': (55.3781, -3.4360),
    'Spain': (40.4637, -3.7492),
    'Germany': (51.1657, 10.4515),
    'France': (46.2276, 2.2137),
    'Italy': (41.8719, 12.5674),
    'Canada': (56.1304, -106.3468),
    'Australia': (-25.2744, 133.7751),
    'Brazil': (-14.2350, -51.9253),
    'India': (20.5937, 78.9629)
}

# Add latitude and longitude to the DataFrame based on the country
df['Latitude'] = df['Country'].apply(lambda x: country_coords[x][0])
df['Longitude'] = df['Country'].apply(lambda x: country_coords[x][1])

st.set_page_config(layout="wide")

# Streamlit app layout
st.title('Antiseizure Clinical Trials Dashboard')

# Create columns for layout
left_column, center_column, right_column = st.columns([2, 10, 5])

with left_column:
    # Country Ranking List
    st.subheader('Country Ranking List')
    country_rank = df.groupby('Country')['Trials'].sum().reset_index().sort_values('Trials', ascending=False)
    for _, row in country_rank.iterrows():
        st.write(f"{row['Country']}: {row['Trials']} trials")

  

with center_column:
    # Geospatial Chart
    st.subheader('Geospatial Chart')
    view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1)
    layer = pdk.Layer(
        'ScatterplotLayer',
        df,
        get_position='[Longitude, Latitude]',
        get_color='[200, 30, 0, 160]',
        get_radius='Trials * 50000',
    )
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, map_style='mapbox://styles/mapbox/light-v9'))


      # Heatmap of trials
    st.subheader('Trials Heatmap')
    # Aggregate data for heatmap
    heatmap_data = df.groupby(['Country', 'Year'])['Trials'].sum().reset_index()
    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
        x='Year:O',
        y='Country:N',
        color='Trials:Q',
        tooltip=['Country', 'Year', 'Trials']
    ).properties(
        width=300,
        height=300
    )
    st.altair_chart(heatmap, use_container_width=True)

with right_column:
    # Year Selector
    year = st.slider('Select Year', min_value=min(df['Year']), max_value=max(df['Year']), value=(min(df['Year']), max(df['Year'])))
    df_filtered = df[df['Year'].between(year[0], year[1])]

    # Country Selector
    country = st.selectbox('Select Country', options=df['Country'].unique())
    df_country = df_filtered[df_filtered['Country'] == country]

    # Line and Dot Graph for the selected country
    st.subheader(f'Trials Over Years for {country}')
    line_chart = alt.Chart(df_country).mark_line(point=True).encode(
        x='Year',
        y='Trials',
        color='Phase',
        tooltip=['Year', 'Phase', 'Trials']
    ).properties(
        width=500,
        height=300
    ).interactive()
    st.altair_chart(line_chart, use_container_width=True)