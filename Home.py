import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from windenergydashboard.utils import make_heatmap, make_donut

# use full width of the page
st.set_page_config(
    page_title="Penmanshiel Wind Farm Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

alt.themes.enable("dark")

# Load the data
df = pd.read_parquet("data/multiple_turbine_data/all_data.parquet")

# Ensure 'DateTime' is a datetime type and set as the index
df["DateTime"] = pd.to_datetime(df["DateTime"])  # Ensure DateTime is datetime type
df.set_index("DateTime", inplace=True)  # Set as index

# Load metadata
meta_data = pd.read_csv("data/multiple_turbine_data/Penmanshiel_WT_static.csv")

# slider to select start amd end date
min_date = df.index.min().to_pydatetime()
max_date = df.index.max().to_pydatetime()

# Create a date range slider using st.slider
start_date, end_date = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(max_date - pd.Timedelta(days=7), max_date),
    format="YYYY-MM-DD",
)


# Filter for the last week of data and where Indicator is 'Active Power'
filtered_df = df.loc[
    (df.index >= start_date)
    & (df.index <= end_date)
    & (df["Indicator"] == "Power (kW)")
]
# aggregate to get the total power for each turbine for the last week
filtered_df = filtered_df.reset_index()
filtered_df["Date"] = filtered_df["DateTime"].dt.date
filtered_df = (
    filtered_df.groupby(["Date", "Turbine", "Indicator"])
    .agg({"Value": "mean"})
    .reset_index()
)

power_data = filtered_df[filtered_df["Indicator"] == "Power (kW)"]

col = st.columns((2, 2), gap="medium")

# Merge with coordinates from meta_data on 'Turbine' and 'Alternative Title'
map_data = filtered_df.merge(
    meta_data[["Alternative Title", "Latitude", "Longitude"]],
    left_on="Turbine",
    right_on="Alternative Title",
)

# Rename columns
map_data.rename(columns={"Value": "Power (kW)"}, inplace=True)

map_data = map_data[["Turbine", "Latitude", "Longitude", "Power (kW)"]]
map_data.reset_index(drop=True, inplace=True)
# assign the color based on the power at the last time point over or under 0, green or red, color in hex
map_data["color"] = map_data["Power (kW)"].apply(
    lambda x: "#33cc33" if x > 0 else "#ff471a"
)

# Map of the last week of data sized by Active Power
with col[1]:
    st.markdown("#### Site Map Online/Offline")
    st.map(
        data=map_data,
        latitude="Latitude",
        longitude="Longitude",
        # size='Power (kW)',
        color="color",
        zoom=11.5,
        use_container_width=True
    )
with col[0]:
    st.markdown('#### Power Timeseries - Mean Daily')
    line_chart = alt.Chart(power_data).mark_line().encode(
        x=alt.X('Date:T', title='Time'),
        y=alt.Y('Value:Q', title='Power (kW)'),
        color='Turbine:N',  # Color by Turbine
        strokeDash='Turbine:N'  # Optionally differentiate lines by dashed style
    ).properties(
        width=700,
        height=400,
    )

    # Display the chart in Streamlit
    st.altair_chart(line_chart, use_container_width=True)
    st.markdown("#### Production Heatmap")
    heatmap = make_heatmap(
        power_data[["Date", "Turbine", "Value"]], "Date", "Turbine", "Value", "viridis"
    )
    st.write(heatmap)