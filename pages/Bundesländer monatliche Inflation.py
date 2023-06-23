import streamlit as st
import pandas as pd 
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import numpy as np
from meteostat import Point, Daily, Monthly
import plost
import json





st.set_page_config(layout='wide', initial_sidebar_state='expanded',page_title="dashgermany",
    page_icon="🇩🇪")
st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
with open('exp00.json', 'r', encoding='utf-8') as f:
    exp = json.load(f)

    
    
st.sidebar.header('Dashboard Deutschland')
st.subheader('monatliche Inflation')
key = 'Inflation'

st.sidebar.markdown('''
---
Made with ❤️  
''')

df = pd.read_csv("data_month.csv", index_col=0)


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
val = round(df_cur.inflation.max() - df_cur[df_cur.state== state].inflation.values[0],2)

delta_current ='Die maximale Inflation wurde in {} gemessen und betrug {} {} im Vergleich zu {}'.format(df_cur[df_cur.inflation == df_cur.inflation.max()]['state'].values[0],val, "mehr" if val >= 0 else "weniger", state)
col1.metric("Inf Max", df_cur.inflation.max(), df_cur[df_cur.inflation == df_cur.inflation.max()]['state'].values[0], 'inverse', delta_current)

val = round(df_cur.inflation.min() - df_cur[df_cur.state == state].inflation.values[0],2)

delta_current ='Die minimale Inflation wurde in {} gemessen und betrug {} {} im Vergleich zu {}'.format(df_cur[df_cur.inflation == df_cur.inflation.min()]['state'].values[0],val, "mehr" if val >= 0 else "weniger", state)
col2.metric("Inf Min", df_cur.inflation.min(), df_cur[df_cur.inflation == df_cur.inflation.min()]['state'].values[0],  "normal",delta_current)

val = round(df_se[df_se.state == state].inflation.values[-1] - df_se[df_se.state == state].inflation.values[-2],2)

delta_current ='Die aktuelle Inflation beträgt {} {} im Vergleich zum Vorjahr'.format(val,"mehr" if val >= 0 else "weniger" )
col3.metric("Inf Aktuel", df_se[df_se.state == state].inflation.values[-1],df_se[df_se.state == state].time_s.values[-1] , "inverse" if val >= 0 else "normal",delta_current)


data_me = df[(df.state == state)&(df.time <= end.strftime('%Y/%m'))].iloc[-24:,:]
# st.write(data_me)
val = round(data_me.tail(12).inflation.mean() - data_me.head(12).inflation.mean(),2)
delta_current ='Die Inflation zwischen {}-{} beträgt {} {} im Vergleich zu {}-{}'.format(data_me.tail(12).time.max(), data_me.tail(12).time.min(), val, "mehr" if val >= 0 else "weniger",data_me.head(12).time.max(), data_me.head(12).time.min())
col4.metric("Inf in den letzten 12 Monaten",  round(data_me.tail(12).inflation.mean(),2),f'{data_me.tail(12).year.max()}- {data_me.tail(12).year.min()}' ,"inverse" if val >= 0 else "normal", delta_current )



# Filter the data
df_s = df[(df.year < 2023) &(df.year>=2019) & (df.state == state)]
filtered_df = df_s.tail(36)

fig = go.Figure()

for year, group_df in filtered_df.groupby('year'):
    fig.add_trace(go.Bar(
        x=group_df['month'],
        y=group_df['inflation'],
        name=year
    ))

# Set layout and labels
fig.update_layout(
    title=f"Inflation in {state}",
    xaxis_title="Month",
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

    st_exp_gr = st.expander('Inflation in den letzten 12 Monaten ')

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

    c2_x.table(temp.style.format({key:"{:.3}"}))



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
