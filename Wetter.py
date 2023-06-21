import streamlit as st
import pandas as pd 
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import numpy as np
from meteostat import Point, Daily, Monthly
import meteostat
import plost
import json


map_months = {"January": "Januar", "February": "Februar", "March": "März", "April": "April", "May": "Mai", "June": "Juni", "July": "Juli", "August": "August", "September": "September", "October": "Oktober", "November": "November", "December": "Dezember"
}



st.set_page_config(layout='wide', initial_sidebar_state='expanded',page_title="dashdeutschland",
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
#st.subheader('Indicator')
key = 'Weather'


st.sidebar.markdown('''
---
Made with ❤️ 
''')

df = pd.read_csv('de.csv', engine='python',  encoding = "ISO-8859-1", index_col=0)
cur = pd.read_csv('data.csv', index_col = 0)
cur['date'] = cur.date.apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
max_date = cur.date.max()


c = st.selectbox(label = 'Wählen Sie eine Stadt aus', options =df.city )

df_c = df[df.city == c].reset_index(drop=True)



start = datetime(1980, 1, 1)
end = datetime.today()
end = datetime(end.year, end.month, end.day)
date_objs = pd.date_range(max_date, end)

if key.lower() == 'weather':
    
    #key = st.selectbox('Weather', ['Temperature'], 0) 
    key = 'Temperature'
    value_dic = {'Temperature':'tavg', 'Rain':'prcp'}
    val_key = value_dic[key]
    location = Point(df_c.iloc[0,1], df_c.iloc[0,2])
    data = Daily(location, start, end)
    data = data.fetch()
    data.reset_index(inplace =True)
    data['df_time'] = data.time.apply(lambda x: x.strftime('%m-%d'))
    data['x_time'] = data.time.apply(lambda x: x.strftime('%Y/%m/%d'))
    data = data[data.df_time ==end.strftime('%m-%d')]
    data = data.dropna(subset = ['tavg'])
    data.reset_index(inplace =True)
  
    data_m = Monthly(location, start, end)
    data_m = data_m.fetch()
    data_m.reset_index(inplace =True)
    data_m['df_time'] = data_m.time.apply(lambda x: x.strftime('%m'))
    data_m['x_time'] = data_m.time.apply(lambda x: x.strftime('%Y/%m'))
    data_m['Year'] = data_m.time.apply(lambda x: x.strftime('%Y'))

    df_g = data_m[data_m.df_time ==end.strftime('%m')]
  
    df_g = df_g.dropna(subset = ['tavg']).reset_index(drop=True)
    
    # log regression

    df_log=pd.DataFrame({'X':df_g.Year,
                         'Y': df_g[val_key]})
    df_log.set_index('X', inplace = True)
    
    #df_log = df_log.dropna()
    
    reg = LinearRegression().fit(np.vstack(df_log.index), df_log['Y'])

    df_log['bestfit'] = reg.predict(np.vstack(df_log.index))
    
    df_new=pd.DataFrame({'X':df_g.Year,
                         'Y':df_g[val_key],
                         'trend':df_log['bestfit'].reset_index(drop=True)})

   
    #df_new.set_index('X', inplace=True)
   

    col1, col2, col3, col4 = st.columns(4)
    val = round(data[val_key].max() - data[val_key].values[-1],2)
    delta_current ='Die maximale {} wurde in {} gemessen und betrug im Vergleich zu heute {} °C {}'.format(key, data[data[val_key] == data[val_key].max()]['time'].dt.year.values[0],val, "mehr" if val >= 0 else "weniger")
    col1.metric("T Max", f'{data[val_key].max()} °C', str(data[data[val_key] == data[val_key].max()]['time'].dt.year.values[0]), 'inverse', delta_current)

    val = round(data[val_key].min() - data[val_key].values[-1],2)
    delta_current ='Die maximale {} wurde in {} gemessen und betrug im Vergleich zu heute {} °C {}'.format(key, data[data[val_key] == data[val_key].min()]['time'].dt.year.values[0],val, "mehr" if val >= 0 else "weniger")
    col2.metric("T Min", f'{data[val_key].min()} °C', str(data[data[val_key] == data[val_key].min()]['time'].dt.year.values[0]),'normal', delta_current)

    val = round(data[val_key].values[-1] - data[val_key].values[-2],2)
    delta_current ='Die aktuelle Temperatur beträgt {} °C {} im Vergleich zum letzten Jahr'.format(val, "mehr" if val >= 0 else "weniger")
    col3.metric("T Aktuel",  f'{data[data.time ==data.time.max()][val_key].values[0]} °C', data.time.max().strftime('%Y'), "inverse" if val >= 0 else "normal", delta_current)

    data_me = data.iloc[-20:,:]
    val = round(df_new.trend.values[-1] - df_new.trend.values[-2],2)
    val_all = round(df_new.trend.values[-1] - df_new.trend.values[0],2)
    delta_current ='Die Trendtemperatur für {} pro Jahr beträgt {} basierend auf den Werten {} und beträgt {} °C {} in {} im Vergleich zu {}'.format(end.strftime("%B"), val, f"{data_m['Year'].min()}-{int(data_m['Year'].max()) -1}", val_all,"mehr" if val >= 0 else "weniger" , int(data_m['Year'].max()) -1, data_m['Year'].min() )
    col4.metric("Trend über Jahre",  f'{val_all} °C',f"{data_m['Year'].min()}-{int(data_m['Year'].max())-1}" ,"inverse" if val >= 0 else "normal", delta_current )

    ### Temparture for days
    c1, c2 = st.columns([3, 1])
    
    with c1:
        if '1988' not in [ i[:4] for i in data.x_time.tolist()]:
            data = data[data.x_time.str[:4]>='1990']
        st.markdown(f'### {"Temperature".title()} ')
        plost.bar_chart(
        data=data.dropna(subset = ['tavg']).reset_index(drop=True).rename(columns= {'time':'Datum', 'tavg':'Durchschnittliche Temperatur'}),
        title = f'Durchschnittliche Temperatur für {map_months[end.strftime("%B")]} {end.strftime("%d")} über Jahre',
        bar = 'Datum',
        value = 'Durchschnittliche Temperatur',
         height=400,
         use_container_width=True 

        )
        

        st_exp_de = st.expander('Kurze Erklärung')

        with st_exp_de:             
                st.write(exp[key]['Deutsch']['meaning']) 



    c2_x = c2.expander('Werte')
    temp = data[['x_time', val_key]].tail(12).sort_values('x_time',ascending=False ).reset_index(drop = True)
    temp.index +=1
   #temp[val_key] = temp[val_key].astype(float)
    temp.columns = ['Datum','Durch. Temp.']
   #st.write(temp)
    with c2_x:

        c2_x.table(temp.style.format({"Durch. Temp.":"{:.3}"}))

    col1, col2 = st.columns([3, 1])



    ### Temparture for months
    fig=go.Figure()
    fig.add_trace(go.Bar( name = 'Durchschnittliche Temperatur',x=df_new.X.astype('str'), y=df_g[val_key],))
    fig.add_trace(go.Scatter(name=f'Trend im {map_months[end.strftime("%B")]} nach Jahre', x=df_new.X, y=df_new['trend'], mode='lines', marker_color='red'))


    fig.update_layout(xaxis_title = 'Datum', yaxis_title = 'Durchschnittliche Temperatur',legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1

    ))

    col1_x = col1.expander(f'Temperature für {map_months[end.strftime("%B")]} ')
    with col1_x:

        st.plotly_chart(fig, 
         use_container_width=True )

    col2_x = col2.expander('Werte')
    temp = data_m[data_m.df_time ==end.strftime('%m')][['x_time', val_key]].tail(12).sort_values('x_time',ascending=False ).reset_index(drop = True)
    temp.columns = ['Datum', 'Durch. Temp.']
    temp.index +=1 
    with col2_x:
        col2_x.table(temp.style.format({"Durch. Temp.":"{:.3}"}))


    col1, col2 = st.columns([3, 1])
    col1_x = col1.expander('Temperature über Jahre')
    df_year = data_m[data_m.Year != end.strftime('%Y')]
    df_year = df_year.dropna(subset=['tavg']).reset_index(drop = True)
    df_year_gr = df_year.groupby('Year').mean()[val_key].reset_index()
    



    df_log=pd.DataFrame({'X':df_year_gr.Year,
                         'Y': df_year_gr[val_key]})
    df_log.set_index('X', inplace = True)

    reg = LinearRegression().fit(np.vstack(df_log.index), df_log['Y'])
    df_log['bestfit'] = reg.predict(np.vstack(df_log.index))
    df_new=pd.DataFrame({'X':df_year.Year,
                         'Y':df_year[val_key],
                         'trend':df_log['bestfit'].reset_index(drop=True)})
    

 


    fig=go.Figure()
    fig.add_trace(go.Bar( name = 'Durchschnittliche Temperature' ,x=df_new.X, y=df_year[val_key]))
    fig.add_trace(go.Scatter(name='Trend über Jahre', x=df_new.X, y=df_new['trend'], mode='lines', marker_color='red'))

    ### Temparture for years
    fig.update_layout(xaxis_title = 'Datum', yaxis_title = 'Durchschnittliche Temperatur',legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1

    ))
    with col1_x:
        st.plotly_chart(fig,  
         use_container_width=True )


    col2_x = col2.expander('Werte')
    temp = data_m[data_m.Year != end.strftime('%Y')].groupby('Year').mean()[val_key].tail(12).reset_index().sort_values('Year',ascending=False ).reset_index(drop=True)
    temp.index +=1
    temp.columns = ['Datum', 'Durch. Temp.']
    with col2_x:
        col2_x.table(temp.style.format({"Durch. Temp.":"{:.3}"}))


    ###Rain
    key = 'Rain'
    val_key = value_dic[key]

    ###Rain for months

    df_g = data_m[data_m.df_time ==end.strftime('%m')].reset_index(drop=True)
    df_g = df_g[df_g.Year != end.strftime('%Y')]
    df_g = df_g.dropna(subset = ['prcp']).reset_index(drop=True)

    df_log=pd.DataFrame({'X':df_g.Year,
                         'Y': df_g[val_key]})

    df_log.set_index('X', inplace = True)

   # st.write(sklearn.__version__)
    reg = LinearRegression().fit(np.vstack(df_log.index), df_log['Y'])
    df_log['bestfit'] = reg.predict(np.vstack(df_log.index))
    df_new=pd.DataFrame({'X':df_g.Year,
                         'Y':df_g[val_key],
                         'trend':df_log['bestfit'].reset_index(drop=True)})

    df_new_rain  = df_new.copy()
    
    fig=go.Figure()
    fig.add_trace(go.Bar( name = 'Durchschnittliche Niederschlag' ,x=df_new_rain.X.astype('str'), y=df_new_rain.Y))
    fig.add_trace(go.Scatter(name=f'Trend im {map_months[end.strftime("%B")]} nach Jahre', x=df_new_rain.X.astype('str'), y=df_new_rain['trend'], mode='lines', marker_color='red'))
    col1, col2 = st.columns([3, 1])
    col1_x = col1.expander(f'Niederschlag für {map_months[end.strftime("%B")]} ')
    # plotly figure layout
    fig.update_layout(xaxis_title = 'Datum', yaxis_title = 'Durchschnittliche Niederschlag',legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1

    ), xaxis = dict(
      tickmode = 'linear')
                     )
    with col1_x:
        st.plotly_chart(fig,  
         use_container_width=True )


    col2_x = col2.expander('Werte')
    temp = df_g[['Year',val_key]].tail(12).reset_index(drop=True).sort_values('Year',ascending=False ).reset_index(drop=True)
    temp.index +=1
    temp.columns = ['Datum', 'Durch. Nider.']
    with col2_x:
        col2_x.table(temp.style.format({"Durch. Nider.":"{:.5}"}))

    ### Rain for years
    col1, col2 = st.columns([3, 1])
    col1_x = col1.expander('Niederschlag über Jahren')
    df_g = data_m[data_m.Year != end.strftime('%Y')]
    df_g = df_g.dropna(subset = ['prcp']).reset_index(drop=True)
    df_g = df_g.groupby('Year').mean()[val_key].reset_index()

    df_log=pd.DataFrame({'X':df_g.Year,
                         'Y': df_g[val_key]})

    df_log.set_index('X', inplace = True)

   # st.write(sklearn.__version__)
    reg = LinearRegression().fit(np.vstack(df_log.index), df_log['Y'])
    df_log['bestfit'] = reg.predict(np.vstack(df_log.index))
    df_new=pd.DataFrame({'X':df_g.Year,
                         'Y':df_g[val_key],
                         'trend':df_log['bestfit'].reset_index(drop=True)})

  

    # plotly figure setup
    fig=go.Figure()
    fig.add_trace(go.Bar( name = 'Durchschnittliche Niederschlag' ,x=df_new.X, y=df_new.Y))
    fig.add_trace(go.Scatter(name='Trend über Jahre', x=df_new.X, y=df_new['trend'], mode='lines', marker_color='red'))

    # plotly figure layout
    fig.update_layout(xaxis_title = 'Datum', yaxis_title = 'Durchschnittliche Niederschlag',legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        
        x=1),  xaxis = dict(
      tickmode = 'linear')
                     )
    with col1_x:
        st.plotly_chart(fig,  
         use_container_width=True )


    col2_x = col2.expander('Werte')
    temp = data_m[data_m.Year != end.strftime('%Y')].groupby('Year').mean()[val_key].tail(12).reset_index().sort_values('Year',ascending=False ).reset_index(drop=True)
    temp.index +=1
    temp.columns = ['Datum', 'Durch. Nider.']
    with col2_x:
        col2_x.table(temp.style.format({"Durch. Nider.":"{:.5}"}))
#     except:
#         print(c + ' does not have data')
