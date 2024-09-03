import streamlit as st
import pandas as pd

st.title('Site Overview - Penmanshiel Wind Farm')

# Load the data
df = pd.read_parquet('data/multiple_turbine_data/all_data.parquet')

# Ensure 'DateTime' is a datetime type and set as the index
df['DateTime'] = pd.to_datetime(df['DateTime'])  # Ensure DateTime is datetime type
df.set_index('DateTime', inplace=True)  # Set as index

# Load metadata
meta_data = pd.read_csv('data/multiple_turbine_data/Penmanshiel_WT_static.csv')

# Filter for the last week of data and where Indicator is 'Active Power'
# set end date as latest date in the data
end_date = df.index.max()
# set start date as a week prior
start_date = end_date - pd.Timedelta(days=7)
filtered_df = df.loc[(df.index >= start_date) & (df.index <= end_date) & (df['Indicator'] == 'Power (kW)')]
# aggregate to get the total power for each turbine for the last week
filtered_df = filtered_df.groupby(['Turbine', 'Indicator']).mean().reset_index()

# Merge with coordinates from meta_data on 'Turbine' and 'Alternative Title'
last_week = filtered_df.merge(meta_data[['Alternative Title', 'Latitude', 'Longitude']], left_on='Turbine', right_on='Alternative Title')

# Rename columns
last_week.rename(columns={'Value': 'Power (kW)'}, inplace=True)

# Map of the last week of data sized by Active Power
st.map(
    data=last_week[['Turbine', 'Latitude', 'Longitude', 'Power (kW)']],
    latitude='Latitude',
    longitude='Longitude',
    size='Power (kW)',
    color='Turbine',
    zoom=10,
    # use_container_width=True
)