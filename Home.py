import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# use full width of the page
st.set_page_config(
    page_title="Penmanshiel Wind Farm Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Load the data
df = pd.read_parquet('data/multiple_turbine_data/all_data.parquet')

# Ensure 'DateTime' is a datetime type and set as the index
df['DateTime'] = pd.to_datetime(df['DateTime'])  # Ensure DateTime is datetime type
df.set_index('DateTime', inplace=True)  # Set as index

# Load metadata
meta_data = pd.read_csv('data/multiple_turbine_data/Penmanshiel_WT_static.csv')

# slider to select start amd end date
min_date = df.index.min().to_pydatetime()
max_date = df.index.max().to_pydatetime()

# Create a date range slider using st.slider
start_date, end_date = st.sidebar.slider(
    'Select Date Range',
    min_value=min_date,
    max_value=max_date,
    value=(max_date - pd.Timedelta(days=7), max_date),
    format="YYYY-MM-DD"
)

def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    return (
        alt.Chart(input_df)
        .mark_rect()
        .encode(
            y=alt.Y(
                f'{input_y}:O',
                axis=alt.Axis(
                    title="Date",
                    titleFontSize=18,
                    titlePadding=15,
                    titleFontWeight=900,
                    labelAngle=0,
                    labelExpr="timeFormat(datum.value, '%Y-%m-%d')",
                ),
            ),
            x=alt.X(
                f'{input_x}:O',
                axis=alt.Axis(
                    title="",
                    titleFontSize=18,
                    titlePadding=15,
                    titleFontWeight=900,
                ),
            ),
            color=alt.Color(
                f'{input_color}:Q',
                legend=None,
                scale=alt.Scale(scheme=input_color_theme),
            ),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        )
        .properties(width=500)
        .configure_axis(labelFontSize=12, titleFontSize=12)
    )

# Filter for the last week of data and where Indicator is 'Active Power'
filtered_df = df.loc[(df.index >= start_date) & (df.index <= end_date) & (df['Indicator'] == 'Power (kW)')]
# aggregate to get the total power for each turbine for the last week
filtered_df = filtered_df.reset_index()
filtered_df['Date'] = filtered_df['DateTime'].dt.date
filtered_df = filtered_df.groupby(['Date', 'Turbine', 'Indicator']).agg({'Value': 'mean'}).reset_index()

power_data = filtered_df[filtered_df['Indicator'] == 'Power (kW)']

col = st.columns((2, 2), gap='medium')

# Heatmap
with col[0]:
    heatmap = make_heatmap(power_data[['Date', 'Turbine', 'Value']], 'Date', 'Turbine', 'Value', 'inferno')
    st.write(heatmap)

# Merge with coordinates from meta_data on 'Turbine' and 'Alternative Title'
map_data = filtered_df.merge(meta_data[['Alternative Title', 'Latitude', 'Longitude']], left_on='Turbine', right_on='Alternative Title')

# Rename columns
map_data.rename(columns={'Value': 'Power (kW)'}, inplace=True)

map_data = map_data[['Turbine', 'Latitude', 'Longitude', 'Power (kW)']]
map_data.reset_index(drop=True, inplace=True)

# Map of the last week of data sized by Active Power
with col[1]:
    st.map(
        data=map_data,
        latitude='Latitude',
        longitude='Longitude',
        # size='Power (kW)',
        # color='Turbine',
        zoom=12,
        # use_container_width=True
    )