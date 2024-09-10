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
max_date = df.index.max().to_pydatetime()
# min date is 6 months before the max date
min_date = max_date - pd.Timedelta(days=180)

# Create a date range slider using st.slider
start_date, end_date = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(max_date - pd.Timedelta(days=7), max_date),
    format="YYYY-MM-DD",
)


power_data = df.loc[
    (df.index >= start_date)
    & (df.index <= end_date)
    & (df["Indicator"] == "Power (kW)")
]
power_data = power_data.reset_index()
power_data["Date"] = power_data["DateTime"].dt.date
power_data = (
    power_data.groupby(["Date", "Turbine", "Indicator"])
    .agg({"Value": "mean"})
    .reset_index()
)

temp_data = df.loc[
    (df.index >= (end_date - pd.Timedelta(days=1)))
    & (df.index <= end_date)
    & (df["Indicator"] == "Gear oil temperature (°C)")
]
temp_data = temp_data.reset_index()
# count per turbine of the number of times the temperature is above 50
temp_data["Above 50"] = temp_data["Value"] > 50

col = st.columns((2, 2), gap="medium")

# Merge with coordinates from meta_data on 'Turbine' and 'Alternative Title'
map_data = power_data.merge(
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
        use_container_width=True,
    )
    st.markdown("#### Temperature Flags")
    columns = st.columns(5)

    for i in range(1, 6):
        value = temp_data[temp_data["Turbine"] == f"T0{i}"]["Above 50"].sum()
        previous = [0,0,0,0,0]
        delta_value = value - previous[i-1]
        
        delta_color = "inverse" if delta_value >= 1 else "normal"
        
        with columns[i - 1]:  # Access each column to place the metric
            st.metric(
                label=f"T0{i}",
                value=value,
                delta=str(delta_value),
                delta_color=delta_color,
            )
with col[0]:
    st.markdown("#### Power Timeseries - Mean Daily")
    line_chart = (
        alt.Chart(power_data)
        .mark_line()
        .encode(
            x=alt.X("Date:T", title="Time"),
            y=alt.Y("Value:Q", title="Power (kW)"),
            color="Turbine:N",  # Color by Turbine
            strokeDash="Turbine:N",  # Optionally differentiate lines by dashed style
        )
        .properties(
            width=700,
            height=400,
        )
    )

    # Display the chart in Streamlit
    st.altair_chart(line_chart, use_container_width=True)
    st.markdown("#### Production Heatmap")
    heatmap = make_heatmap(
        power_data[["Date", "Turbine", "Value"]], "Date", "Turbine", "Value", "viridis"
    )
    st.write(heatmap)
