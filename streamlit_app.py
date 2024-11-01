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
import json
start_time = time.perf_counter()

# ======================================================================================================================================== #
# Title and introduction sectie voor de Streamlit app
st.title("""*COVID-19 Data* van 08 en 09 Maart 2023 voor EU-Landen""")

st.write("""Tijdens de pandemie is het bijhouden van data cruciaal geweest om inzicht te krijgen in de verspreiding en impact van COVID-19 in verschillende regio’s. In dit project hebben we een interactieve data-visualisatie ontwikkeld met behulp van Python en de Streamlit-bibliotheek. Ons doel was om gebruikers de mogelijkheid te geven om de COVID-19-gevallen en sterfgevallen in verschillende Europese landen en hun provincies te verkennen.""")
st.write("""Hiervoor hebben we als eerst een grafiek gecreëerd die het aantal gediagnosticeerde gevallen en sterfgevallen per land en provincie toont. Gebruikers kunnen zelf kiezen welke data ze willen bekijken, zowel de gediagnosticeerde gevallen als de sterfgevallen, of slechts één van beide datasets. Op deze manier kunnen gebruikers eenvoudig de verspreiding van COVID-19 binnen specifieke regio's analyseren.""")

st.title('Interactief COVID-19 Dashboard voor EU-landen')

st.subheader('Introductie')

st.write("""
Dit dashboard biedt een overzicht van de verspreiding van COVID-19 in verschillende Europese landen en hun provincies. Het doel van dit dashboard is om gebruikers te voorzien van actuele inzichten over het aantal bevestigde gevallen, sterfgevallen en de procentuele toename van COVID-19 in verschillende regio's.

### Functies van het dashboard:
1. **COVID-19 Gevallen en Sterfgevallen per Provincie**: Visualiseer het aantal bevestigde gevallen en sterfgevallen voor elke provincie in geselecteerde Europese landen. U kunt eenvoudig wisselen tussen landen om de data voor specifieke regio's te bekijken.
2. **Procentuele Toename per Dag**: Analyseer de procentuele toename van bevestigde gevallen, actieve gevallen en sterfgevallen tussen twee datums. Dit biedt inzicht in de snelheid waarmee het virus zich verspreidt in verschillende provincies.
3. **Gediagnosticeerde Gevallen vs. Sterfgevallen**: Vergelijk het aantal bevestigde gevallen met sterfgevallen in elke provincie. Deze visualisatie maakt het mogelijk om te zien welke regio’s harder zijn getroffen door de pandemie.
   
### Hoe het dashboard te gebruiken:
- Selecteer een **land** en **provincie** in de dropdown-menu’s om de data voor een specifieke regio te bekijken.
- Gebruik de **slider** om data voor verschillende datums te vergelijken.
- Vink opties aan of uit met de **checkboxes** om specifieke datapunten te tonen of te verbergen.

Het dashboard is ontworpen om overheden, gezondheidsautoriteiten en burgers te helpen bij het beter begrijpen van de impact van COVID-19 in Europa. Door data te visualiseren, kunnen trends gemakkelijker worden geïdentificeerd, wat leidt tot beter geïnformeerde beslissingen.
""")

# ======================================================================================================================================== #
# Load the CSV file
covid_df_EU = pd.read_csv("Case2vb.csv")

# Check if `region` column needs parsing
def parse_region(region_str):
    try:
        # Convert JSON string to dictionary if needed
        if isinstance(region_str, str):
            return json.loads(region_str.replace("'", "\""))  # Handle single quotes if present
        return region_str  # If already a dictionary, return as is
    except json.JSONDecodeError:
        return {}  # Return an empty dictionary if parsing fails

# Apply parsing to the `region` column
covid_df_EU['region'] = covid_df_EU['region'].apply(parse_region)

# Extract `province` from the parsed `region` dictionaries
covid_df_EU['province'] = covid_df_EU['region'].apply(lambda x: x.get('province', 'Unknown'))

# Filter out rows where province is 'Unknown'
covid_df_EU = covid_df_EU[covid_df_EU['province'] != 'Unknown']

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
#Plotly figure
fig = go.Figure()
# Toevoegen van Bar traces voor de comfirmed cases en deaths for elke land
for country in province_data_EU['country_name'].unique():
    province_data_EU_filtered = province_data_EU[province_data_EU['country_name'] == country]
    fig.add_trace(go.Bar(x=province_data_EU_filtered['province'],
                        y=province_data_EU_filtered['confirmed'],
                        name=f'{country} gediagnosticeerde',
                        visible=False,
                        marker_color='blue'))
    fig.add_trace(go.Bar(x=province_data_EU_filtered['province'],
                        y=province_data_EU_filtered['deaths'],
                        name=f'{country} sterfgevallen',
                        visible=False,
                        marker_color='red'))
#Dit maakt het eerste land zijn data visible by defeault
fig.data[0].visible=True
fig.data[1].visible=True
# Dropdown menu voor kiezen van verschillende landen
dropdown_buttons = []

for country in province_data_EU['country_name'].unique():
    dropdown_buttons.append({
        'label':country,
        'method':'update',
        'args':[{'visible': [name.startswith(country) for name in [trace.name for trace in fig.data]]},
        {'title':f'COVID-19 Gegevens voor {country}'}]
    })
# Update layout voor het plotly figuur, met een dropdown en titles
fig.update_layout(
    title = 'COVID-19 Gediagnosticeerde en Sterfgevallen per Provincie',
    xaxis_title = 'Provincie',
    yaxis_title = 'Aantal',
    barmode = 'group',
    updatemenus = [{'buttons':dropdown_buttons,
                    'showactive':True,
                    'direction':'down'}]
)
#weergeven van plot in streamlit
st.plotly_chart(fig)

# =================================================================================================================================== #
#Doormiddel van streamlit schrijven we headers en een stuk tekst
st.header("""Procentuele Toename van COVID-19 Gevallen en Sterfgevallen in de EU""")
st.write("""De verspreiding van COVID-19 blijft een belangrijke zorg in Europa, waarbij overheden en gezondheidsautoriteiten nauwlettend de dagelijkse stijgingen in besmettingen en sterfgevallen volgen. De onderstaande grafiek biedt een inzichtelijke vergelijking van de procentuele toename van actieve COVID-19-gevallen, bevestigde besmettingen, en sterfgevallen per provincie, tussen 8 en 9 maart 2023.""")
st.write("""Door deze gegevens te analyseren, krijgen we een duidelijker beeld van welke provincies in verschillende landen het hardst worden getroffen door de pandemie. Dit kan beleidsmakers helpen om beter geïnformeerde beslissingen te nemen over interventies en middelen.""")
st.write("""Kies hieronder een land en een provincie om de specifieke stijgingspercentages te bekijken. De kleuren in de grafiek geven de stijgingen weer: blauw voor actieve gevallen, oranje voor bevestigde besmettingen, en rood voor sterfgevallen.""")

# =================================================================================================================================== #
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
# Aanmaken van een staafdiagram met plotly
    fig_check = go.Figure()
# Toevoegen van data aan de staafdiagram
    fig_check.add_trace(go.Bar(
        x=labels, 
        y=values,
        marker_color=['blue', 'orange', 'red']
    ))
# Layout van de grafiek instellen
    fig_check.update_layout(
        title=f'Toename in Percentage voor {selected_province_checkbox}',
        xaxis_title='Meting',
        yaxis_title='Percentage',
        template='plotly_white',
        showlegend=False
    )
 #Display naam instellen op basis van de geselecteerde land of provincie
    if selected_province_checkbox == "":
        display_name = selected_country_checkbox
    else:
        display_name = selected_province_checkbox
# Controle of alle waardes nul zijn (geen toename in data)
    if np.all(values == 0):
        st.write(f'Geen toename van covid-19 percentages bekend in {display_name} tussen de dagen 08-03-2023 en 09-03-2023')
    else:
        st.plotly_chart(fig_check)

# ================================================================================================================================== #
# Titel en text voor de tweede sectie van de analyse doormiddel van streamlit
st.header("""Analyse van COVID-19: Gediagnosticeerde Gevallen versus Sterfgevallen""")
st.write("""Het verloop van de COVID-19-pandemie kan per regio sterk verschillen, afhankelijk van verschillende factoren zoals bevolkingsdichtheid, zorgcapaciteit en overheidsmaatregelen. Het begrijpen van deze regionale verschillen is essentieel voor zowel beleidsmakers als gezondheidsautoriteiten.""")
st.write("""De onderstaande grafiek biedt een visuele weergave van het aantal gediagnosticeerde gevallen in verhouding tot het aantal sterfgevallen in Europese provincies, op zowel 8 als 9 maart 2023. De data per dag zijn apart weergegeven, en met de slider kunt u eenvoudig schakelen tussen beide datums. Elke marker vertegenwoordigt een provincie, en de positie ervan toont hoe deze zich verhoudt tot de andere provincies.""")
st.write("""Door deze informatie te visualiseren, wordt het mogelijk om trends te ontdekken en provincies te identificeren waar sterfgevallen in verhouding tot gediagnosticeerde gevallen hoger zijn, of waar de stijging in besmettingen significant is. Dit type inzicht kan bijdragen aan meer gerichte interventies in de strijd tegen COVID-19.""")

# =================================================================================================================================== #
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
covid_df_EU_slider = covid_df_EU_slider[~((covid_df_EU_slider['country_name'] == 'Frankrijk') & (covid_df_EU_slider['province'] == ""))]
# Aanmaken van de scatter plot met plotly
fig_scat = go.Figure()
# Data toevoegen voor 8 maart 2023
fig_scat.add_trace(go.Scatter(
    x=covid_df_EU_slider['2023-03-08_con'],# X-as: aantal gediagnosticeerde gevallen
    y=covid_df_EU_slider['2023-03-08_dea'],# Y-as: aantal sterfgevallen
    mode='markers',# Markers (punten) voor elke provincie
    marker=dict(color=covid_df_EU_slider['country_name'].astype('category').cat.codes),  # Kleuren op basis van land
    text=covid_df_EU_slider['country_name'],  # Hover-informatie: landnaam
    name='2023-03-08'# Legenda label voor deze datum
))
# Data toevoegen voor 9 maart 2023
fig_scat.add_trace(go.Scatter(
    x=covid_df_EU_slider['2023-03-09_con'],
    y=covid_df_EU_slider['2023-03-09_dea'],
    mode='markers',
    marker=dict(color=covid_df_EU_slider['country_name'].astype('category').cat.codes),
    text=covid_df_EU_slider['country_name'],
    name='2023-03-09',
    visible=False # Standaard onzichtbaar maken van deze data
))
# Layout en slider voor het wisselen tussen 8 en 9 maart
fig_scat.update_layout(
    title='Aantal gediagnosticeerde uitgezet tegen het aantal sterfgevallen',
    xaxis_title='Aantal gediagnosticeerde',
    yaxis_title='Aantal sterfgevallen',
    template='plotly_white',
    sliders=[{
        'steps': [
            {
                'method': 'update',
                'label': '2023-03-08',
                'args': [{'visible': [True, False]}, {'title': 'Data van 2023-03-08'}]
            },
            {
                'method': 'update',
                'label': '2023-03-09',
                'args': [{'visible': [False, True]}, {'title': 'Data van 2023-03-09'}]
            }
        ],
        'currentvalue': {'prefix': 'Datum: '},# Huidige waarde van de slider
        'pad': {'t': 50} # Afstand tussen slider en grafiek
    }]
)
# Weergeven van de scatter plot in de app
st.plotly_chart(fig_scat)

# Tekst omtrent data kwaliteit
st.subheader('Discussie over Data Kwaliteit')
st.write("""
De dataset die in deze analyse is gebruikt, bevat geen ontbrekende waarden, wat betekent dat alle statistieken volledig zijn vertegenwoordigd. Dit vormt een solide basis voor een nauwkeurige analyse van COVID-19 gevallen en sterfgevallen.

Daarnaast zijn mogelijke uitschieters gemarkeerd tijdens de verkenning, wat kan duiden op provincies met ongewoon hoge of lage aantallen gevallen. Deze uitschieters zijn opgenomen in de analyse, maar worden gemarkeerd voor verdere beoordeling.

Door de volledigheid en betrouwbaarheid van de data te waarborgen, zullen de inzichten die uit dit dashboard worden getrokken waarschijnlijk de ware COVID-19 trends in de Europese regio’s weerspiegelen.
""")
#Disclaimer

st.subheader('Disclaimer')
st.write("""Ook al bevat de dataset geen ontbrekenden waarden, zijn de provincies niet altijd accuraat. Zo zijn er EU-landen die wel provincies/regio's bevatten, maar dat niet is aangegeven in de dataset. Zo lijkt het dus alsof sommige landen geen provincies hebben terwijl dit wel het geval is.""")
end_time = time.perf_counter()

st.write(f"Total execution time: {end_time - start_time} seconds")
