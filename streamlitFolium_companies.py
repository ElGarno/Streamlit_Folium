import pandas as pd
import numpy as np
import json
# convert an address into latitude and longitude values
import requests
import folium
from folium import plugins
import streamlit as st
from streamlit_folium import folium_static
import haversine as hs
from haversine import Unit


def run_app():
    """
    test
    :return:
    """
    url_data = "http://arbeitgeberliste.bplaced.net/#%7B%22col_1%22%3A%7B%7D%7D"
    df_raw = get_data_from_url_html(url_data)
    df_preprocessed = prepare_data(df_raw)

    # for changing type of the maps
    add_select = st.sidebar.selectbox("What data do you want to see?", ("OpenStreetMap", "Stamen Terrain", "Stamen Toner"))
    # for calling the function for getting center of maps
    # showing the maps
    map_companies_bavaria = folium.Map([49.9, 9.2], tiles=add_select, zoom_start=9)
    # design for the app
    st.title('Map of Companies in central Germany')
    # cluster markers?
    chk_show_clusters = st.sidebar.checkbox("Cluster Markers?", key="chk_cluster_markers")
    # get sub df from radio buttons for employees
    feature = 'Mitarbeiter'
    # sub_df = get_sub_df_by_radioselect(df_preprocessed, feature)
    st.sidebar.subheader("Employees")
    chk_filter_employees = st.sidebar.checkbox("Filter by number of employees", key="chk_filter_employees")
    if chk_filter_employees:
        sub_df_ma = get_sub_df_by_slider(df_preprocessed, feature)
    else:
        sub_df_ma = df_preprocessed
    feature = 'Jahresgehalt (AVG)'
    st.sidebar.subheader("Yearly Income")
    chk_filter_income = st.sidebar.checkbox("Filter by yearly income in €", key="chk_filter_income")
    if chk_filter_income:
        sub_df_brutto = get_sub_df_by_slider(sub_df_ma, feature)
    else:
        sub_df_brutto = sub_df_ma
    st.sidebar.subheader("Companies nearby")
    chk_show_companies_radius = st.sidebar.checkbox("Filter by distance in km", key="chk_show_companies_r")
    if chk_show_companies_radius:
        sub_df_r = show_companies_radius(sub_df_brutto)
    else:
        sub_df_r = sub_df_brutto
    map_companies_bavaria = set_markers(sub_df_r, chk_show_clusters, map_companies_bavaria)
    # folium.Marker([49.9, 9.2], popup=popup).add_to(map_companies_bavaria)
    folium_static(map_companies_bavaria)


def show_companies_radius(df):
    lat_i = st.sidebar.number_input("Enter Latitude (GPS)", value=49.989221)
    long_i = st.sidebar.number_input("Enter Longitude (GPS)", value=9.572231)
    loc_i = (lat_i, long_i)
    radius_GPS = st.sidebar.slider("Radius:", value=10)
    loc_i_multiple = [loc_i for i in range(df.shape[0])]
    locations = list(zip(df['Latitude'], df['Longitude']))
    distances = compute_distance(loc_i_multiple, locations)
    return df[distances < radius_GPS]


def get_sub_df_by_slider(df, feature):
    """

    :param feature:
    :param df:
    :return:
    """
    min_val = int(df[feature].min())
    max_val = int(df[feature].max())
    if feature == 'Mitarbeiter':
        upper_bound_slider = st.sidebar.number_input("Select max value for slider:", value=1000, help=f"Max value is {max_val}",
                                                     key=f"Textinput_" + feature + "_max")
        select_range = st.sidebar.slider("Select size of Company", value=[0, upper_bound_slider], key="Slider_" + feature)
    elif feature == 'Jahresgehalt (AVG)':
        lower_bound_slider = st.sidebar.number_input("Select min value for slider:", value=10000, help=f"Min value is {min_val}",
                                                     key=f"Textinput_" + feature + "_min")
        upper_bound_slider = st.sidebar.number_input("Select max value for slider:", value=100000, help=f"Max value is {max_val}",
                                                     key=f"Textinput_" + feature + "_max")
        select_range = st.sidebar.slider("Select yearly income", value=[lower_bound_slider, upper_bound_slider], key="Slider_" +
                                                                                                                     feature)
    # sub_df = df[[select_range[0] < x < select_range[1] for x in df[feature]]]
    sub_df = df[df[feature].between(select_range[0], select_range[1])]
    return sub_df


def compute_distance(location_1, location_2, unit="KILOMETERS"):
    """
    Computes the distance (in km) between two locations given as GPS coordinates
    :param unit:
    :param location_1:
    :param location_2:
    :return:
    """
    # check whether locations are only one tuple or list of tuples
    if type(location_1) == "tuple":
        distance = hs.haversine(location_1, location_2, unit=Unit.KILOMETERS)
    else:
        distance = hs.haversine_vector(location_1, location_2, unit=Unit.KILOMETERS)
    return distance


def get_sub_df_by_radioselect(df, feature):
    """

    :param feature:
    :param df:
    :return: sub_df
    """
    dict_company_size = {
        "0 - 20": np.vectorize(lambda x: 0 < x <= 20),
        "21 - 100": np.vectorize(lambda x: 20 < x <= 100),
        "101 - 300": np.vectorize(lambda x: 100 < x <= 300),
        "301 - 1000": np.vectorize(lambda x: 300 < x <= 1000),
        "1001 - 10000": np.vectorize(lambda x: 1000 < x <= 10000),
        "> 10000": np.vectorize(lambda x: x > 10000)
    }
    # get subsets of df
    choice_company_size = st.sidebar.radio("Select Company size:", dict_company_size.keys())
    selected_entries = dict_company_size[choice_company_size](df[feature])
    sub_df = df[selected_entries]
    return sub_df


def set_markers(df, chk_show_clusters, map_companies_bavaria):
    """

    :param df:
    :param chk_show_clusters:
    :param map_companies_bavaria:
    :return:
    """
    company_symbol = "img/company_symbol.png"
    if chk_show_clusters == 'Yes':
        company_clusters = plugins.MarkerCluster().add_to(map_companies_bavaria)
    else:
        feature_group = folium.FeatureGroup("Locations")

    for lat, lng, name, ma, brutto in zip(list(df['Latitude']), list(df['Longitude']),
                                          list(df['Unternehmen']), list(df['Mitarbeiter']),
                                          list(df['Jahresgehalt (AVG)'])):
        if np.isnan(brutto):
            html = f'''Company Name: {name}<br>
                        Number_Employees: {ma}'''
        else:
            html = f'''Company Name: {name}<br>
                        Number_Employees: {ma}<br>
                        Average Income: {brutto}'''

        iframe = folium.IFrame(html,
                               width=200,
                               height=100)

        popup_constructed = folium.Popup(iframe,
                                         max_width=200)
        if chk_show_clusters == "Yes":
            custom_marker = folium.CustomIcon(company_symbol, icon_size=(35, 35), popup_anchor=(0, -22))
            folium.Marker(
                location=[lat, lng],
                icon=custom_marker,
                popup=popup_constructed,
            ).add_to(company_clusters)
        else:
            custom_marker = folium.CustomIcon(company_symbol, icon_size=(25, 25), popup_anchor=(0, -22))
            feature_group.add_child(
                folium.Marker(
                    location=[lat, lng],
                    icon=custom_marker,
                    popup=popup_constructed,
                )
            )
            map_companies_bavaria.add_child(feature_group)
    return map_companies_bavaria


@st.cache
def prepare_data(df):
    df_preprocessed = df.drop(
        columns=['*', 'Links', 'Gegenstand des Unternehmens', 'Geschäfts­jahr', 'Löhne und Gehälter', 'Stadt / Gemeinde'])
    df_preprocessed = df_preprocessed.rename(columns={
        'Lat': 'Latitude',
        'Lon': 'Longitude',
        '⌀ Gehalt / MA': 'Jahresgehalt (AVG)'
    })
    df_preprocessed.replace('k. A.', np.nan, inplace=True)
    if df_preprocessed['Mitarbeiter'].dtype == "object":
        df_preprocessed['Mitarbeiter'] = df_preprocessed['Mitarbeiter'].str.replace(r' MA', '').str.replace('.', '').astype('int')
    if df_preprocessed['Jahresgehalt (AVG)'].dtype == "object":
        df_preprocessed['Jahresgehalt (AVG)'] = df_preprocessed['Jahresgehalt (AVG)'].dropna().str.replace(r' €/MA', '').str.replace('.',
                                                                                                                                     '').astype(
            'float')

    return df_preprocessed


@st.cache
def get_data_from_url_html(url="http://arbeitgeberliste.bplaced.net/#%7B%22col_1%22%3A%7B%7D%7D"):
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    html = r.content
    df_list = pd.read_html(html)
    return df_list[0]


if __name__ == "__main__":
    run_app()
