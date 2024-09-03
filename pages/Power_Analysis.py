import streamlit as st
import pandas as pd

st.title('Power Analysis - Penmanshiel Wind Farm')

df = pd.read_parquet('../data/multiple_turbine_data/all_data.parquet')

# set DateTime as the index and datetime type
df.set_index('DateTime', inplace=True)
df.index = pd.to_datetime(df.index)

turbine_nos = df['Turbine'].unique().sort()
indicators = df.Indicator.unique().sort()

turbine_no = st.selectbox('Turbine Number', turbine_nos)
indicator = st.selectbox('Indicator', indicators)

