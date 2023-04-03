import streamlit as st
import pandas as pd 
from datetime import datetime
from meteostat import Point, Daily, Monthly
import plost


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

    
st.sidebar.header('Dashboard Germany')
st.subheader('Indicator')
key = st.selectbox('Indicator', ['weather', 'inflation'], 0) 


st.sidebar.markdown('''
---
Created with ❤️ 
''')

df = pd.read_csv('de.csv', engine='python',  encoding = "ISO-8859-1")
cur = pd.read_csv('data.csv', index_col = 0)
cur['date'] = cur.date.apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
max_date = cur.date.max()


c = st.selectbox(label = 'Select your city', options =df.city )

df_c = df[df.city == c].reset_index(drop=True)



start = datetime(1980, 1, 1)
end = datetime.today()
end = datetime(end.year, end.month, end.day)
date_objs = pd.date_range(max_date, end)

if key == 'weather':
    try:
        location = Point(df_c.iloc[0,1], df_c.iloc[0,2])

        data = Daily(location, start, end)
        data = data.fetch()
        data.reset_index(inplace =True)
        data['df_time'] = data.time.apply(lambda x: x.strftime('%m-%d'))
        data['x_time'] = data.time.apply(lambda x: x.strftime('%Y/%m/%d'))
        data = data[data.df_time ==end.strftime('%m-%d')]
        data.reset_index(inplace =True)
        #st.write(data)
        data_m = Monthly(location, start, end)
        data_m = data_m.fetch()
        data_m.reset_index(inplace =True)
        data_m['df_time'] = data_m.time.apply(lambda x: x.strftime('%m'))
        data_m['x_time'] = data_m.time.apply(lambda x: x.strftime('%Y/%m'))
        data_m['Year'] = data_m.time.apply(lambda x: x.strftime('%Y'))

        
        col1, col2, col3, col4 = st.columns(4)
        val = round(data.tavg.max() - data.tavg.values[-1],2)
        delta_current ='The maximum temparture was measure in {}, and it was {} C {} compare to today'.format(data[data.tavg == data.tavg.max()]['time'].dt.year.values[0],val, "higher" if val >= 0 else "less")
        col1.metric("T Max", data.tavg.max(), str(data[data.tavg == data.tavg.max()]['time'].dt.year.values[0]), 'inverse', delta_current)

        val = round(data.tavg.min() - data.tavg.values[-1],2)
        delta_current ='The minumum temparture was measure in {}, and it was {} C {} compare to today'.format(data[data.tavg == data.tavg.min()]['time'].dt.year.values[0],val, "higher" if val >= 0 else "less")
        col2.metric("T Min", data.tavg.min(), str(data[data.tavg == data.tavg.min()]['time'].dt.year.values[0]),'normal', delta_current)

        val = round(data.tavg.values[-1] - data.tavg.values[-2],2)
        delta_current ='The current temprature is {} C {} compare to last year'.format(val, "higher" if val >= 0 else "less")
        col3.metric("T Current",  data[data.time ==data.time.max()]['tavg'].values[0], data.time.max().strftime('%Y'), "inverse" if val >= 0 else "normal", delta_current)

        data_me = data.iloc[-20:,:]
        val = round(data_me.tail(10).tavg.mean() - data_me.head(10).tavg.mean(),2)
        delta_current ='The temprature in between 2023 and 2014 is {} C {} compare to 2013 and 2004'.format(val, "higher" if val >= 0 else "less")
        col4.metric("T in Last Ten Years",  round(data_me.tail(10).tavg.mean(),2),"2023-2014" ,"inverse" if val >= 0 else "normal", delta_current )
        
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f'### {"weather".title()} ')
            plost.bar_chart(
            data=data,
            title = f'Average Temp for {end.strftime("%B %d")} over Years',
            bar = 'time',
            value = 'tavg',
             height=400,
             use_container_width=True 

            )

        c2_x = c2.expander('Values')
        temp = data[['x_time', 'tavg']].tail(12).sort_values('x_time',ascending=False ).reset_index(drop = True)
        temp.index +=1
        with c2_x:
            c2_x.table(temp.style.format({"tavg":"{:.3}"}))
        
        col1, col2 = st.columns([3, 1])
        col1_x = col1.expander('Weather')
        with col1_x:
            
            plost.bar_chart(
            data=data_m[data_m.df_time ==end.strftime('%m')],
            title = f'Average Temp for {end.strftime("%B")} over Years',
            bar = 'Year',
            value = 'tavg',
             height=400,
             use_container_width=True 

            )
        col2_x = col2.expander('values')
        temp = data_m[data_m.df_time ==end.strftime('%m')][['x_time', 'tavg']].tail(12).sort_values('x_time',ascending=False ).reset_index(drop = True)
        
        with col2_x:
            col2_x.table(temp.style.format({"tavg":"{:.3}"}))
    except:
        print(c + ' does not have data')

# elif key == 'currency':
#     if max_date <= end:
#         cur = cur[cur.date != max_date].reset_index(drop=True)
#         date = []
#         ex=[]
#         for i in date_objs:
#             date.append(i)
#             ex.append(get_rates('EUR', i))
#         temp = pd.io.json.json_normalize(ex)
#         temp['date'] = date

#         cur = pd.concat([cur, temp]).reset_index(drop=True)
#         cur.to_csv('data.csv')
        
#         plost.bar_chart(
#         data=cur[['USD', 'date']],
#         bar = 'date',
#         value = 'USD',

#          use_container_width=True 

#        )

else:
    map_month = {'Januar':'01', 'Februar':'02','März':'03' , 'April':'04', 'Mai':'05' , 'Juni':'06', 'Juli':'07',
       'August':'08', 'September':'09', 'Oktober':'10', 'November':'11', 'Dezember':'12'}
    df = pd.read_csv("data_month.csv", index_col=0)
    
    
    df['time'] =   df['year'].astype(str) + '/' + df['month'].apply(lambda x: map_month[x])

    df['time_s'] = df['month'] + ' ' +  df['year'].astype(str) 
    #df.drop(['index.1', 'index.0'],1, inplace =True)
    df.columns = ['year', 'month', 'state','inflation','time', 'time_s']
    df.dropna(inplace =True)

    df['inflation'] = (df['inflation'] - df.sort_values(by=['state','time'], ascending=True)\
                           .groupby(['state','month'])['inflation'].shift(1)) / (df.sort_values(by=['state','time'], ascending=True)\
                           .groupby(['state', 'month'])['inflation'].shift(1)) * 100
   
    df['inflation'] = df.inflation.apply(lambda x: round(x, 2))
    state = df_c['admin_name'].values[0]
    end = datetime(int(df.year.max()), int(df[df.year == df.year.max()].time.str[-2:].max()), 1)

    df_cur = df[df.time == end.strftime('%Y/%m')]
    
    df_se = df[(df.time.str[-2:] == end.strftime('%m')) & (df.state == state)]
    
    col1, col2, col3, col4 = st.columns(4)
    val = round(df_cur.inflation.max() - df_cur[df_cur.state== state].inflation.values[0],2)
    
    delta_current ='The maximum inflation was measure in {}, and it was {}  {} compare to {}'.format(df_cur[df_cur.inflation == df_cur.inflation.max()]['state'].values[0],val, "higher" if val >= 0 else "less", state)
    col1.metric("Inf Max", df_cur.inflation.max(), df_cur[df_cur.inflation == df_cur.inflation.max()]['state'].values[0], 'inverse', delta_current)
    
    val = round(df_cur.inflation.min() - df_cur[df_cur.state == state].inflation.values[0],2)
    
    delta_current ='The min inflation was measure in {}, and it was {}  {} compare to {}'.format(df_cur[df_cur.inflation == df_cur.inflation.min()]['state'].values[0],val, "higher" if val >= 0 else "less", state)
    col2.metric("Inf Min", df_cur.inflation.min(), df_cur[df_cur.inflation == df_cur.inflation.min()]['state'].values[0],  "normal",delta_current)
    
    val = round(df_se[df_se.state == state].inflation.values[-1] - df_se[df_se.state == state].inflation.values[-2],2)

    delta_current ='The current inflation was measure is {} {} compare to last year'.format(val,"higher" if val >= 0 else "less" )
    col3.metric("Inf Current", df_se[df_se.state == state].inflation.values[-1],df_se[df_se.state == state].time_s.values[-1] , "inverse" if val >= 0 else "normal",delta_current)
    

    data_me = df[(df.state == state)&(df.time <= end.strftime('%Y/%m'))].iloc[-24:,:]
   # st.write(data_me)
    val = round(data_me.tail(12).inflation.mean() - data_me.head(12).inflation.mean(),2)
    delta_current ='The temprature in between {}-{} is {} {} compare to {}-{}'.format(data_me.tail(12).time.max(), data_me.tail(12).time.min(), val, "higher" if val >= 0 else "less",data_me.head(12).time.max(), data_me.head(12).time.min())
    col4.metric("Inf in last 12 Months",  round(data_me.tail(12).inflation.mean(),2),"2023-2014" ,"inverse" if val >= 0 else "normal", delta_current )
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f'### {key.title()} for {state} ')
        plost.bar_chart(
            data=df_se,
            bar = 'time_s',
            value = 'inflation',
            height=400,
     
             use_container_width=True 

           )
        
    c2_x = c2.expander('Values')
    temp = df[(df.state == state)].dropna()[['state', 'time', 'inflation']].sort_values(by='time', ascending=False).reset_index(drop = True).head(13)
    temp.index +=1
    with c2_x:

        c2_x.table(temp.style.format({key:"{:.3}"}))
        
    

    col1, col2 = st.columns((4, 8))
    col1_x = col1.expander('Order in Germany')


    with col1_x:
        temp = df_cur[['state', 'time', 'inflation']].sort_values(by='inflation', ascending=False).reset_index(drop = True)
        temp.index +=1
        col1_x.table(data=temp)
        

    col2_x = col2.expander('Order in with selected States')

    with col2_x:
        c = st.multiselect('States', df_cur.state, default = [state])
      #  num = temp[temp.state==state].index[0]

        temp = pd.concat([df_cur[df_cur.state.isin(c)],
                               df_cur[df_cur.state==state]])

        temp.drop_duplicates(inplace=True)

        
        temp = temp[['state', 'time', 'inflation']].sort_values('inflation',ascending=False).reset_index(drop = True)

        temp.index +=1

        col2_x.table(temp)