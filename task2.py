import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Generate sample data
years = np.random.choice(range(2010, 2021), size=100)
companies = np.random.choice(['Pharma A', 'Pharma B', 'Pharma C', 'Pharma D', 'Pharma E'], size=100)
phases = np.random.choice(['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4'], size=100)

# Create DataFrame
df = pd.DataFrame({'Year': years, 'Company': companies, 'Phase': phases})

import streamlit as st
import altair as alt
import pandas as pd



# Streamlit app layout
st.title('Pharmaceutical Trials Dashboard')

# Creating the main line and dot graph
year_range = range(2010, 2021)
company_summary = df.groupby(['Year', 'Company']).size().reset_index(name='Trials')

line_chart = alt.Chart(company_summary).mark_line(point=True).encode(
    x=alt.X('Year:O', scale=alt.Scale(domain=list(year_range))),
    y='Trials:Q',
    color='Company:N',
    tooltip=['Year', 'Company', 'Trials']
).interactive()

st.altair_chart(line_chart, use_container_width=True)

# Interactive widgets to simulate click tool functionality
selected_year = st.selectbox('Select Year', options=year_range)
selected_company = st.selectbox('Select Company', options=df['Company'].unique())

# Filtering data based on selections
df_filtered = df[df['Year'] == selected_year]
company_trials = df_filtered.groupby('Company').size().reset_index(name='Trials')

# Pie Chart showing total trials by company for the selected year
pie_chart = alt.Chart(company_trials).mark_arc().encode(
    theta=alt.Theta(field="Trials", type="quantitative"),
    color=alt.Color(field="Company", type="nominal"),
    tooltip=['Company', 'Trials']
).properties(title=f'Total Trials in {selected_year}')

st.altair_chart(pie_chart, use_container_width=True)

# Bar Graph showing phase breakdown for the selected company and year
df_company_year = df[(df['Year'] == selected_year) & (df['Company'] == selected_company)]
phase_breakdown = df_company_year.groupby('Phase').size().reset_index(name='Trials')

bar_chart = alt.Chart(phase_breakdown).mark_bar().encode(
    x='Phase:O',
    y='Trials:Q',
    color='Phase:N',
    tooltip=['Phase', 'Trials']
).properties(title=f'Phase Breakdown for {selected_company} in {selected_year}')

st.altair_chart(bar_chart, use_container_width=True)