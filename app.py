import streamlit as st
import re
import pandas as pd


def select_excercise():
    """
    test
    :return:
    """
    dict_excercises = {
        'Introduct. to FAFFI DS with Python - Part 1': itdsp1,
        'Introduct. to DS with Python - Part 2': itdsp2
    }
    st.header("My excercises")
    option = st.sidebar.selectbox(
        'Which number do you like best?',
        list(dict_excercises.keys()))

    'You selected:', option
    dict_excercises[option]()


def itdsp1():
    """

    :return:
    """
    # YOUR CODE HERE
    # read excel file and skip header and footer (first 16 rows and last 38 rows)
    df_Energy = pd.read_excel("assets/Energy Indicators.xls", header=17, skipfooter=38)
    # drop first two columns
    df_Energy.drop(['Unnamed: 0', 'Unnamed: 1'], axis=1, inplace=True)
    # rename columns
    df_Energy.rename(columns={
        'Unnamed: 2': 'Country',
        'Petajoules': 'Energy Supply',
        'Gigajoules': 'Energy Supply per Capita',
        '%': '% Renewable'
    }, inplace=True)
    # convert object to float. By this, signs like "..." convert to nan
    df_Energy['Energy Supply'] = pd.to_numeric(df_Energy['Energy Supply'], errors='coerce')
    # convert petajoules to gigajoules
    df_Energy['Energy Supply'] = df_Energy['Energy Supply'].transform(lambda x: x * 1000000)
    # delete "()" and numbers from country name with regex
    # delete 0-n "(" and delete any numbers from names
    df_Energy.replace({
        'Country': {
            "\(*\d+": ""
        }
    }, regex=True, inplace=True)
    # after cleaning replace country names
    df_Energy.replace({
        'Country': {
            "Republic of Korea": "South Korea",
            "United States of America": "United States",
            "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
            "China, Hong Kong Special Administrative Region": "Hong Kong"
        }
    }, inplace=True)
    st.write(df_Energy.tail(50))


def itdsp2():
    st.write('hello guys')


if __name__ == "__main__":
    select_excercise()
