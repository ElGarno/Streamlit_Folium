import pandas as pd
import numpy as np
import json
# convert an address into latitude and longitude values
import requests
import folium
import streamlit as st
from streamlit_folium import folium_static


def create_streamlit():
    """
    test
    :return:
    """
    # for changing type of the maps
    add_select = st.sidebar.selectbox("What data do you want to see?", ("OpenStreetMap", "Stamen Terrain", "Stamen Toner"))
    # for calling the function for getting center of maps
    # showing the maps
    map_companies_bavaria = folium.Map(tiles=add_select, zoom_start=4)
    # design for the app
    st.title('Testmap')
    folium_static(map_companies_bavaria)


if __name__ == "__main__":
    create_streamlit()
