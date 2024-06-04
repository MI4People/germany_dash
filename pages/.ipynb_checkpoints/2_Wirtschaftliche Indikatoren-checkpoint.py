import streamlit as st
import pandas as pd 
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import numpy as np
from meteostat import Point, Daily, Monthly
import plost
import json





st.set_page_config(layout='wide', initial_sidebar_state='expanded',page_title="dofe.mi4people",
    page_icon="🇩🇪")
css =  """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    
    .stTabs [data-baseweb="tab"] {
     font-size: calc(1.3rem + .6vw);
        margin: 0;
        width: 100%;
    }

     .button, [type="button"]  {
        font-size: calc(1.3rem + .6vw);
        margin: 0;
        width: 100%;
    }
    
    </style>
    """
st.markdown(css, unsafe_allow_html=True)
with open('exp00.json', 'r', encoding='utf-8') as f:
    exp = json.load(f)


st.sidebar.header('MI4People')
key = 'Inflation'

st.sidebar.markdown('''
---
Made with ❤️  
''')

tab1, tab2 = st.tabs(["Monatlich", "Jährlich"])


with tab1: 
    
    df = pd.read_csv("data_month.csv", index_col=0)

    st.subheader('Wirtschaftliche Indikatoren auf monatlich Basis')
    df = df.dropna()

    state = st.selectbox('Wählen Sie ein Bundesland', set(df.state))





    start = datetime(1980, 1, 1)
    end = datetime.today()
    end = datetime(end.year, end.month, end.day)


    map_month = {'Januar':'01', 'Februar':'02','März':'03' , 'April':'04', 'Mai':'05' , 'Juni':'06', 'Juli':'07',
       'August':'08', 'September':'09', 'Oktober':'10', 'November':'11', 'Dezember':'12'}



    df['time'] =   df['year'].astype(str) + '/' + df['month'].apply(lambda x: map_month[x])

    df['time_s'] = df['month'] + ' ' +  df['year'].astype(str) 
    #df.drop(['index.1', 'index.0'],1, inplace =True)
    df.columns = ['year', 'month', 'state','inflation','time', 'time_s']
    df.dropna(inplace =True)

    df['inflation'] = (df['inflation'] - df.sort_values(by=['state','time'], ascending=True)\
                           .groupby(['state','month'])['inflation'].shift(1)) / (df.sort_values(by=['state','time'], ascending=True)\
                           .groupby(['state', 'month'])['inflation'].shift(1)) * 100

    df['inflation'] = df.inflation.apply(lambda x: round(x, 2))

    end = datetime(int(df.year.max()), int(df[df.year == df.year.max()].time.str[-2:].max()), 1)


    df_cur = df[df.time == end.strftime('%Y/%m')]

    df_se = df[(df.time.str[-2:] == end.strftime('%m')) & (df.state == state)]

    col1, col2, col3, col4 = st.columns(4)


    val = round(df_se[df_se.state == state].inflation.values[-1] - df_se[df_se.state == state].inflation.values[-2],2)

    delta_current ='Die aktuelle Inflation beträgt {} Prozentpunkte {} im Vergleich zum Vorjahr'.format(val,"mehr" if val >= 0 else "weniger" )
    col1.metric("Inf Aktuel", df_se[df_se.state == state].inflation.values[-1],df_se[df_se.state == state].time_s.values[-1] , "inverse" if val >= 0 else "normal",delta_current)


    data_me = df[(df.state == state)&(df.time <= end.strftime('%Y/%m'))].iloc[-24:,:]

    val = round(data_me.tail(12).inflation.mean() - data_me.head(12).inflation.mean(),2)
    delta_current ='Die Inflation zwischen {}-{} beträgt {} Prozentpunkte {} im Vergleich zu {}-{}'.format(data_me.tail(12).time.max(), data_me.tail(12).time.min(), val, "mehr" if val >= 0 else "weniger",data_me.head(12).time.max(), data_me.head(12).time.min())
    col2.metric("Inf in den letzten 12 Monaten",  round(data_me.tail(12).inflation.mean(),2),f'{data_me.tail(12).year.max()}- {data_me.tail(12).year.min()}' ,"inverse" if val >= 0 else "normal", delta_current )

    val = round(df_cur.inflation.max() - df_cur[df_cur.state== state].inflation.values[0],2)

    delta_current ='Die maximale aktuelle Inflation wurde in {} gemessen und betrug {} Prozentpunkte {} im Vergleich zu {}'.format(df_cur[df_cur.inflation == df_cur.inflation.max()]['state'].values[0],val, "mehr" if val >= 0 else "weniger", state)
    col3.metric("Inf Max", df_cur.inflation.max(), df_cur[df_cur.inflation == df_cur.inflation.max()]['state'].values[0], 'inverse', delta_current)

    val = round(df_cur.inflation.min() - df_cur[df_cur.state == state].inflation.values[0],2)

    delta_current ='Die minimale aktuelle Inflation wurde in {} gemessen und betrug {} Prozentpunkte {} im Vergleich zu {}'.format(df_cur[df_cur.inflation == df_cur.inflation.min()]['state'].values[0],val, "mehr" if val >= 0 else "weniger", state)
    col4.metric("Inf Min", df_cur.inflation.min(), df_cur[df_cur.inflation == df_cur.inflation.min()]['state'].values[0],  "normal",delta_current)


    # Filter the data
    df_s = df[(df.year < datetime.today().year) & (df.year> datetime.today().year - 4) & (df.state == state)]
    filtered_df = df_s

    fig = go.Figure()

    for year, group_df in filtered_df.groupby('year'):
        fig.add_trace(go.Bar(
            x=group_df['month'],
            y=group_df['inflation'],
            name=year
        ))

    # Set layout and labels
    fig.update_layout(
        title=f"Inflation für {state}",
        xaxis_title="Monaten",
        yaxis_title="Inflation"
    )




    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f'### {key.title()} für {state} ')
        plost.bar_chart(
            data=df_se,
            bar = 'time_s',
            value = 'inflation',
            height=400,

             use_container_width=True 

           )

        st_exp_gr = st.expander('monatliche Inflation in den letzten 3 Jahren ')

        with st_exp_gr:             
            st.plotly_chart(fig, 
             use_container_width=True )

        st_exp_de = st.expander('Kurze Erklärung')

        with st_exp_de:             
                st.write(exp[key]['Deutsch']['meaning'])



    c2_x = c2.expander('Werte')
    temp = df[(df.state == state)].dropna()[['state', 'time', 'inflation']].sort_values(by='time', ascending=False).reset_index(drop = True).head(13)
    temp.index +=1
    temp.columns = ['Bundesländer', 'Datum','Inflation']
    with c2_x:

        c2_x.table(temp )



    col1, col2 = st.columns((4, 8))
    col1_x = col1.expander('Ranking in Deutschland')


    with col1_x:
        temp = df_cur[['state', 'time', 'inflation']].sort_values(by='inflation', ascending=False).reset_index(drop = True)
        temp.index +=1
        temp.columns = ['Bundesländer', 'Datum','Inflation']
        col1_x.table(data=temp)


    col2_x = col2.expander('Ranking in ausgewählten Staaten')

    with col2_x:
        c = st.multiselect('States', df_cur.state, default = [state])
      #  num = temp[temp.state==state].index[0]

        temp = pd.concat([df_cur[df_cur.state.isin(c)],
                               df_cur[df_cur.state==state]])

        temp.drop_duplicates(inplace=True)


        temp = temp[['state', 'time', 'inflation']].sort_values('inflation',ascending=False).reset_index(drop = True)

        temp.index +=1
        temp.columns = ['Bundesländer', 'Datum','Inflation']
        col2_x.table(temp)
        flag = True
    st.write("*Datenquelle: Destatis")
with tab2: 
    st.subheader('Wirtschaftliche Indikatoren auf jahrlicher Basis')
    de = pd.read_csv('bun_year_dsh.csv', index_col=0)
    de.year = de.year.astype(str)
    co = pd.read_csv('total_dsh.csv', index_col=0)

    with open('exp.json', 'r', encoding='utf-8') as f:
        exp = json.load(f)



    liste = liste = {
        'Inflation': 'inflation',
        'Arbeitslosenquote gesamt %': 'unemployment_total',
        'Arbeitslosenquote Männer %': 'unemployment_man',
        'Arbeitslosenquote Frauen %': 'unemployment_women',
        'BIP pro Kopf': 'gdp_per',
        'Bruttoinlandsprodukt': 'bruttoinland',
        'Bevölkerung': 'population_total'
    }

  

    key = st.selectbox('Wählen Sie den Indikator aus', liste.keys( )) 
    indicator = liste[key]

    show_list = {'state':'State', 'year':'Year', 'region':'Region', 'incomeLevel':'Income Level', indicator:key }

    show_list_1 = {'state':'Bundesländer', 'year':'Datum', indicator:key }


    st.subheader('Bundesland')
    state = st.selectbox('Wählen Sie das Bundesland aus', sorted(set(de.state)))

    s_l = list(set(de.state))
    s_l.remove(state)

    c_l = [c for c in set(co.state) if c not in s_l]
    co = co[co.state.isin(c_l)]

    temp_de = de.dropna(subset = [indicator])
    y = temp_de.year.astype(int).max()
    temp_de = temp_de[temp_de.year == str(y)]


    temp= co.dropna(subset = [indicator])
    temp_eu = temp[temp.region == 'Europa & Zentralasien']
    y = temp_de.year.astype(int).max()
    temp_eu = temp_eu[temp_eu.year == y]


    temp_co = co.dropna(subset = [indicator])
    y = temp_de.year.astype(int).max()
    temp_co = temp_co[temp_co.year == y]
    temp_co = temp_co.sort_values(indicator).reset_index(drop=True)
    temp_co.index +=1


    temp = co.dropna(subset = [indicator])
    temp_in = temp[temp.incomeLevel == 'Hohes Einkommen']
    y = temp_de.year.astype(int).max()
    temp_in = temp_in[temp_in.year == y]
    temp_in = temp_in.sort_values(indicator).reset_index(drop=True)
    temp_in.index +=1

    #####sorting 
    if indicator in ['bruttoinland','population_total', 'gdp_per', 'pop_growth', 'gdp_growth','hd', 'gd', 'sc']:

        temp_de = temp_de.sort_values(indicator, ascending=False).reset_index(drop=True)
        temp_de['ranking'] = temp_de[indicator].rank(method='min', ascending=False)
        temp_de.index +=1

        temp_eu = temp_eu.sort_values(indicator, ascending=False).reset_index(drop=True)
        temp_eu['ranking'] = temp_eu[indicator].rank(method='min', ascending=False)
        temp_eu.index +=1

        temp_co = temp_co.sort_values(indicator, ascending=False).reset_index(drop=True)
        temp_co['ranking'] = temp_co[indicator].rank(method='min', ascending=False)
        temp_co.index +=1

        temp_in = temp_in.sort_values(indicator, ascending=False).reset_index(drop=True)
        temp_in['ranking'] = temp_in[indicator].rank(method='min', ascending=False)
        temp_in.index +=1

    else:
        temp_de = temp_de.sort_values(indicator).reset_index(drop=True)
        temp_de['ranking'] = temp_de[indicator].rank(method='min')
        temp_de.index +=1

        temp_eu = temp_eu.sort_values(indicator).reset_index(drop=True)
        temp_eu['ranking'] = temp_eu[indicator].rank(method='min')
        temp_eu.index +=1

        temp_co = temp_co.sort_values(indicator).reset_index(drop=True)
        temp_co['ranking'] = temp_co[indicator].rank(method='min')
        temp_co.index +=1

        temp_in = temp_in.sort_values(indicator).reset_index(drop=True)
        temp_in['ranking'] = temp_in[indicator].rank(method='min')
        temp_in.index +=1







    st.markdown(f'### {state}')

    col1, col2, col3, col4 = st.columns(4)

    question_mark = f'Bei der {key} liegt {state} auf Platz'
    col1.metric("In Deutschland", int(temp_de[temp_de.state == state].ranking.values[0]),'','normal',  f'{question_mark} {int(temp_de[temp_de.state == state].ranking.values[0])} der Bundesländer')
    col2.metric("In Europa & Zentralasien",  int(temp_eu[temp_eu.state == state].ranking.values[0]) , '','normal', f'{question_mark} {int(temp_eu[temp_eu.state == state].ranking.values[0])} der europäischen und zentralasiatischen Länder')
    col3.metric("In der Welt",  int(temp_co[temp_co.state == state].ranking.values[0]) , '','normal',f'{question_mark} {int(temp_co[temp_co.state == state].ranking.values[0])} der Länder')
    col4.metric("In Ländern mit hohem Einkommen", int(temp_in[temp_in.state == state].ranking.values[0]), '','normal',f'{question_mark} {int(temp_in[temp_in.state == state].ranking.values[0])} der Länder mit hohem Einkommen')



   
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f'### {key}')
        plost.bar_chart(
        data=de[de.state == state].rename(mapper = {indicator:key}, axis=1),
        bar = 'year',
        value = key,
         height=400,
         use_container_width=True 

       )
        dc = {'Bedeutung':'meaning', 'Berechnung':'calculation', 'Beispiel':'example', 'Auswirkung':'impact', 'Gründe':'reasons'}
        st_exp_de = st.expander('Kurze Erklärung')
        with st_exp_de:             
            c = st.selectbox(f'Kurze Erklärung für {key}',  dc.keys())
            st.write(exp[indicator]['Deutsch'][dc[c]]) 




    c2_x = c2.expander('Werte')
    temp = de[(de.state == state)&(de.year > '2012')][['state','year',indicator]].dropna().rename(mapper = show_list_1, axis = 1).reset_index(drop = True)
    temp.columns = ['Bundesländer', 'Datum',key]
    temp.index +=1
    with c2_x:

        c2_x.table(temp )




    col1, col2 = st.columns((4, 8))


    temp = temp_co.copy()



    if indicator in ['bruttoinland','population_total', 'gdp_per', 'pop_growth', 'gdp_growth', 'hd', 'gd', 'sc']:

        temp = temp[['ranking','state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator,ascending=False)

    else:
        temp = temp[['ranking','state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator)


    col1_x = col1.expander('Ranking in Deutschland')


    with col1_x:
        col1_x.table(data=temp_de[['state','year',indicator]].rename(mapper = show_list_1, axis = 1) )


    col2_x = col2.expander('Ranking in ausgewählten Ländern')

    with col2_x:
            c = st.multiselect('Länder', temp.state, default = [state, 'Deutschland', 'Österreich','Frankreich', 'Vereinigtes Königreich', 'Vereinigte Staaten', 'China', 'Japan', 'Italien', 'Spanien' ])
          #  num = temp[temp.state==state].index[0]

            temp = pd.concat([temp[temp.state.isin(c)],
                                   temp[temp.state==state]])

            temp.drop_duplicates(inplace=True)
            if indicator in ['bruttoinland','population_total', 'gdp_per', 'pop_growth', 'gdp_growth','hd', 'gd', 'sc']:

                temp = temp[['ranking','state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator,ascending=False)

            else:
                temp = temp[['ranking','state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator)

            temp['ranking'] = temp['ranking'].astype(int)
            temp = temp.reset_index(drop= True)
            temp.index +=1
            temp.columns = ['Ranking','Länder', 'Datum','Region', 'Einkommen Level',key]

            col2_x.table(temp)
            
    st.write("*Datenquelle: World Bank, Destatis")