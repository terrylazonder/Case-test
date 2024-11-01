import streamlit as st
import requests
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objects as go
import plotly.express as px
import numpy
import numpy as np
import time

start_time = time.perf_counter()

# Voegt sidebar toe
st.sidebar.title('Blog categorieën')
blog_post = st.sidebar.selectbox(
    'Selecteer een onderwerp',
    ('Introductie', 'Procentuele Toename van COVID-19 Gevallen en Sterfgevallen in de EU', 'Procentuele Toename van COVID-19', 'Gediagnosticeerde Gevallen versus Sterfgevallen', 'Data kwaliteit'))
# API URL for COVID-19 statistics
url = "https://covid-19-statistics.p.rapidapi.com/reports"
# Headers for the API request with API key
headers = {
    'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
    'x-rapidapi-key': "89dc140db7mshf142d6f86d6ce14p1c3e02jsn2c6a8f31519e"
}
# List of European country codes for the API request
country_code_EU = ['BEL', 'DNK', 'BGR', 'CYP', 'DEU', 'EST', 'FIN', 'FRA', 'GRC', 'HUN', 'IRL', 'ITA', 'HRV', 'LVA', 'LTU',
                   'LUX', 'MLT', 'NLD', 'AUT', 'POL', 'PRT', 'ROU', 'SVN', 'SVK', 'ESP', 'CZE', 'SWE']
querystring_EU = {'iso': country_code_EU}

headers = {
    'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
    'x-rapidapi-key': "89dc140db7mshf142d6f86d6ce14p1c3e02jsn2c6a8f31519e"
}
# Dictionary voor de volledige naam van de map country
country_names = {
    'BEL': 'België','DNK': 'Denemarken','BGR': 'Bulgarije','CYP': 'Cyprus','DEU': 'Duitsland','EST': 'Estland','FIN': 'Finland',
    'FRA': 'Frankrijk','GRC': 'Griekenland','HUN': 'Hongarije','IRL': 'Ierland','ITA': 'Italië','HRV': 'Kroatië','LVA': 'Letland',
    'LTU': 'Litouwen','LUX': 'Luxemburg','MLT': 'Malta','NLD': 'Nederland','AUT': 'Oostenrijk','POL': 'Polen','PRT': 'Portugal',
    'ROU': 'Roemenië','SVN': 'Slovenië','SVK': 'Slovakije','ESP': 'Spanje','CZE': 'Tsjechië','SWE': 'Zweden'
}
    #Makan van een dataframe voor verzamelen van data
EU_data = []
for country_code in country_code_EU:
    querystring_EU = {'iso':country_code}
    response_EU = requests.get(url, headers=headers, params=querystring_EU)
    data_EU = response_EU.json()
#Checken of de data beschikbaar is om samentevoegen met de EU_data list
    if 'data' in data_EU:
        for report in data_EU['data']:
            report['country'] = country_code
            report['country_name'] = country_names[country_code]
            EU_data.append(report)

#Makan van een dataframe voor verzamelen van data
covid_df_EU = pd.DataFrame(EU_data)
covid_df_EU.set_index('country', inplace = True)

# Zoekt naar missende data
missing_data = covid_df_EU.isnull().sum()
missing_data_count = missing_data.sum()

# Toont missende data
st.subheader('Missende Data Overzicht')
#Boolean statement voor weergave betreft missende waardes
if missing_data_count == 0:
    st.write('Geen missende data gevonden. Alle onderdelen zijn compleet.')
else:
    st.write(' een overzicht van de missende data in de dataset:')
    st.dataframe(missing_data)
# Extract province data en haalt de entries weg waar province is 'Unknown'
covid_df_EU['province'] = covid_df_EU['region'].apply(lambda x: x.get('province'))
covid_df_EU = covid_df_EU[covid_df_EU['province'] != 'Unknown']
# Groepeer de data bij province en calculate de som van confirmed cases en deaths
province_data_EU = covid_df_EU.groupby(['province', 'country_name']).agg({'confirmed': 'sum', 'deaths': 'sum', 'fatality_rate': 'mean'}).reset_index()
province_data_EU = province_data_EU.reindex(columns=['country_name', 'province', 'confirmed', 'deaths', 'fatality_rate'])
province_data_EU = province_data_EU.sort_values(by='country_name', ascending=True)
# Berekend verhoogde percentage voor confirmed cases, deaths, en active cases
covid_df_EU_con_diff = covid_df_EU[['province', 'country_name', 'confirmed', 'confirmed_diff']].copy()
covid_df_EU_con_diff['2023-03-08'] = covid_df_EU_con_diff['confirmed'] - covid_df_EU_con_diff['confirmed_diff']
covid_df_EU_con_diff['confirmed_increase_%'] = (((covid_df_EU_con_diff['confirmed'] - covid_df_EU_con_diff['2023-03-08']) / covid_df_EU_con_diff['2023-03-08']) * 100)
covid_df_EU_con_diff.rename(columns={'confirmed':'2023-03-09'}, inplace=True)
covid_df_EU_con_diff = covid_df_EU_con_diff.reindex(columns=['country_name', 'province', 'confirmed_diff','confirmed_increase_%', '2023-03-08', '2023-03-09',])
#herhalen van soortgelijke berekeningen voor de deaths en active cases
covid_df_EU_dea_diff = covid_df_EU[['province', 'country_name', 'deaths', 'deaths_diff']].copy()
covid_df_EU_dea_diff['2023-03-08'] = covid_df_EU_dea_diff['deaths'] - covid_df_EU_dea_diff['deaths_diff']
covid_df_EU_dea_diff['deaths_increase_%'] = (((covid_df_EU_dea_diff['deaths'] - covid_df_EU_dea_diff['2023-03-08']) / covid_df_EU_dea_diff['2023-03-08']) * 100)
covid_df_EU_dea_diff.rename(columns={'deaths':'2023-03-09'}, inplace=True)
covid_df_EU_dea_diff = covid_df_EU_dea_diff.reindex(columns=['country_name', 'province', 'deaths_diff', 'deaths_increase_%', '2023-03-08', '2023-03-09'])
covid_df_EU_dea_diff['deaths_increase_%'] = covid_df_EU_dea_diff['deaths_increase_%'].fillna(0)

covid_df_EU_act_diff = covid_df_EU[['province', 'country_name', 'active', 'active_diff']].copy()
covid_df_EU_act_diff['2023-03-08'] = covid_df_EU_act_diff['active'] - covid_df_EU_act_diff['active_diff']
covid_df_EU_act_diff['active_increase_%'] = (((covid_df_EU_act_diff['active'] - covid_df_EU_act_diff['2023-03-08']) / covid_df_EU_act_diff['2023-03-08']) * 100)
covid_df_EU_act_diff.rename(columns={'active':'2023-03-09'}, inplace=True)
covid_df_EU_act_diff = covid_df_EU_act_diff.reindex(columns=['country_name', 'province', 'active_diff', 'active_increase_%', '2023-03-08', '2023-03-09'])
covid_df_EU_act_diff['active_increase_%'] = covid_df_EU_act_diff['active_increase_%'].fillna(0)
#Samenvoegen van de data in een dataframe voor toename percentage
covid_df_EU_increase_pct = covid_df_EU_act_diff[['province', 'country_name', 'active_increase_%']].merge(
    covid_df_EU_con_diff[['province', 'country_name', 'confirmed_increase_%']],
    on=['province', 'country_name'],
    how='inner').merge(
        covid_df_EU_dea_diff[['province', 'country_name', 'deaths_increase_%']],
        on=['province', 'country_name'],
        how='inner'
    )
# Herschikken van de kolommen in de dataset
covid_df_EU_increase_pct = covid_df_EU_increase_pct.reindex(
    columns=['country_name', 'province', 'active_increase_%', 'confirmed_increase_%', 'deaths_increase_%'])
# Titel voor het dashboard
st.header('COVID-19 Toename Percentage Dashboard')
# Dropdown voor het selecteren van een land
selected_country_checkbox = st.selectbox('Selecteer een land', covid_df_EU_increase_pct['country_name'].unique())
# Filteren van de dataset op basis van het geselecteerde land
filtered_df = covid_df_EU_increase_pct[covid_df_EU_increase_pct['country_name'] == selected_country_checkbox]
# Dropdown voor het selecteren van een provincie binnen het geselecteerde land
selected_province_checkbox = st.selectbox('Selecteer een provincie', filtered_df['province'].unique())
# Filteren van de dataset op basis van de geselecteerde provincie
province_data_checkbox = filtered_df[filtered_df['province'] == selected_province_checkbox]
# Controle of er data beschikbaar is voor de geselecteerde provincie
if not province_data_checkbox.empty:
    # Dutch translations for the x-axis labels
    labels = ['Actieve Toename (%)', 'Gediagnosticeerde Toename (%)', 'Sterfgevallen Toename (%)']
    values = province_data_checkbox[['active_increase_%', 'confirmed_increase_%', 'deaths_increase_%']].values[0]
    # Samenvoegen van verschillende datasets voor de scatter plot
    covid_df_EU_slider = covid_df_EU[['country_name', 'province']].merge(
        covid_df_EU_con_diff[['province', 'country_name', '2023-03-08', '2023-03-09']],
        on=['province', 'country_name'],
        how='inner').merge(
        covid_df_EU_dea_diff[['province', 'country_name', '2023-03-08', '2023-03-09']],
        on=['province', 'country_name'],
        how='inner',
        suffixes=('_con', '_dea')
    )
    # Filteren van de dataset voor Frankrijk (geen provincies beschikbaar)
    covid_df_EU_slider = covid_df_EU_slider[
        ~((covid_df_EU_slider['country_name'] == 'Frankrijk') & (covid_df_EU_slider['province'] == ""))]
    # Aanmaken van de scatter plot met plotly
    fig_scat = go.Figure()
    # Data toevoegen voor 8 maart 2023
    fig_scat.add_trace(go.Scatter(
        x=covid_df_EU_slider['2023-03-08_con'],  # X-as: aantal gediagnosticeerde gevallen
        y=covid_df_EU_slider['2023-03-08_dea'],  # Y-as: aantal sterfgevallen
        mode='markers',  # Markers (punten) voor elke provincie
        marker=dict(color=covid_df_EU_slider['country_name'].astype('category').cat.codes),  # Kleuren op basis van land
        text=covid_df_EU_slider['country_name'],  # Hover-informatie: landnaam
        name='2023-03-08'  # Legenda label voor deze datum
    ))
    # Data toevoegen voor 9 maart 2023
    fig_scat.add_trace(go.Scatter(
        x=covid_df_EU_slider['2023-03-09_con'],
        y=covid_df_EU_slider['2023-03-09_dea'],
        mode='markers',
        marker=dict(color=covid_df_EU_slider['country_name'].astype('category').cat.codes),
        text=covid_df_EU_slider['country_name'],
        name='2023-03-09',
        visible=False )) # Standaard onzichtbaar maken van deze data

end_time = time.perf_counter()

print(f"Total execution time: {end_time - start_time} seconds")
