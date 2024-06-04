from datetime import datetime as ddt
import datetime
import pandas as pd
from prophet import Prophet
import requests
import io
import matplotlib.pyplot as plt
import matplotlib
from prophet.plot import add_changepoints_to_plot
import streamlit as st
import plotly.tools
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout='wide', initial_sidebar_state='expanded',page_title="currency",
    )
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

    

#df = pd.read_csv('data.csv')


API_CUR = st.secrets["API_CUR"]
API_NEWS = st.secrets["API_NEWS"]
payload = {}
headers= {
  "apikey": API_CUR
}
try:

    c = "USD"
    end_date = ddt.today().strftime('%Y-%m-%d')
    dt = ddt.today()
    dt = dt.replace(month=dt.month-1 if dt.month > 1 else 12, year=dt.year if dt.month > 1 else dt.year-1)
    start_date = dt.strftime('%Y-%m-%d')
    url = f"https://api.apilayer.com/exchangerates_data/timeseries?start_date={start_date}&end_date={end_date}&base=EUR&symbols={c}"
    urlData = requests.request("GET", url, headers=headers, data = payload).content
    rawData = pd.read_json(io.StringIO(urlData.decode('utf-8')))
    df = rawData.rates.apply(lambda x: x[c]).reset_index()
    df.columns = ['ds','y']


    df['ds'] = pd.to_datetime(df['ds'])

    col1, col2, col3, col4 = st.columns(4)


    now = df.y.values[-1]
    now_show = round(df.y.values[-1], 2)
    key = c
    base = 'EUR'
    val = round(  now - df.y.values[0],2)
    delta_current ='Der aktuelle {} ist {} {}, und {} {} im Vergleich zu vor einem Monat'.format(base, now_show,key,val, "mehr" if val >= 0 else "weniger")
    col1.metric("Aktuell",  f'{round(now,2)}', df[df.ds == df.ds.max()]['ds'].dt.strftime("%d %b, %Y").values[0], "inverse" if val >= 0 else "normal", delta_current)

    val = round(df.y.max() - now,2)
    delta_current ='Der Höchstwert für {} in diesem Monat was {}, und im Vergleich zu heute {} {}'.format(base, df[df.y == df.y.max()]['ds'].dt.strftime('%d %b').values[0],val, "mehr" if val >= 0 else "weniger")
    col2.metric("Max", f'{round(df.y.max(),2)}', df[df.y == df.y.max()]['ds'].dt.strftime("%d %b, %Y").values[0], 'inverse', delta_current)

    val = round(df.y.min() - now,2)
    delta_current ='Der niedrigste Wert für {} in diesem Monat war {},  und im Vergleich heute {} {}'.format(base,df[df.y == df.y.min()]['ds'].dt.strftime('%d-%m').values[0],val, "mehr" if val >= 0 else "weniger")
    col3.metric("Min", f'{round(df.y.min(), 2)}', df[df.y == df.y.min()]['ds'].dt.strftime("%d %b, %Y").values[0], 'normal', delta_current)


    val = round(df.y.rolling(7).mean().values[-1],2)
    delta_current ='Mittelwert der letzten 7 Tage {} ist {}'.format(base,val )
    col4.metric("Mittelwert der letzten 7 Tage",  val, '' ,"inverse" if val >= 0 else "normal", delta_current )

    m = Prophet(changepoint_prior_scale=0.01, changepoint_range=0.95, n_changepoints=3 )
    m.fit(df)

    future = m.make_future_dataframe(periods=2, freq="B")
    forecast = m.predict(future)



    fig_ = m.plot(forecast)

    a = add_changepoints_to_plot(fig_.gca(), m, forecast, threshold= 0.01)
    plt.title('EUR-USD Wechselkursentwicklung: Ein-Monats Übersicht mit Zwei Tages Prognose')
    plt.xlabel('Datum')


    plt.ylabel('Werte')


    plt.legend(['Aktuell', 'Vorhersage', 'Vorhersage Komponenten', 'Tendenz', 'Trendwende'])


    c1, c2 = st.columns([3, 1])
    frc = forecast.iloc[:, [0,15]].rename(columns = {'yhat':'y'}).tail(2)
    df = pd.concat([df,frc], ignore_index=True)

    df['str_time'] = df.apply(lambda x: x.ds.strftime("%d %b, %Y"), 1)

    with c1:
        st.pyplot(fig_)
        exp = st.expander('Erläuterung')
        with exp:

            st.write("""Die vorliegende Grafik bietet eine detaillierte Analyse des Wechselkurses zwischen Euro (EUR) und US-Dollar (USD). Die blaue Linie stellt die historischen Wechselkurstrends dar und zeigt die Werte im Laufe der Zeit. Die rote Linie repräsentiert das zugrunde liegende Prognosemodell, das Einblicke in langfristige Muster bietet. Wichtige Merkmale sind der schattierte Bereich um die Prognoselinie, der die Unsicherheit der Vorhersage veranschaulicht. Beachtenswert ist, dass der Graph über einen Zeitraum von zwei Tagen hinausgeht und eine Vorwärtsprojektion auf Grundlage historischer Muster bietet. Hervorgehobene Bereiche im Graphen kennzeichnen signifikante Änderungen in den Trends. Weiter unten auf der Seite finden Sie Nachrichtenschlagzeilen, die kontextbezogene Informationen zu Ereignissen bieten, die möglicherweise die vorliegenden Verschiebungen in den Wechselkurstrends beeinflusst haben.""")
    with c2:
        c2_x = c2.expander('Werte')
        temp = df.rename(columns = {'str_time':'Datum', 'y':'Werte'}).tail(14).sort_values('ds',ascending=False)[['Datum', 'Werte']].reset_index(drop = True)
        temp.index +=1
        with c2_x:
            c2_x.table(temp)




    col1, col2 = st.columns((4, 8))
    col1_x = col1.expander('Trendwende')


    chage_points_year = df.loc[df["ds"].isin(m.changepoints)].ds.dt.year.values
    chage_points_month = df.loc[df["ds"].isin(m.changepoints)].ds.dt.month.values

    df_m= df.loc[df["ds"].isin(m.changepoints)]
    df_m['chages'] = m.params['delta'].mean(0)
    df_m['chages_abs'] = abs(m.params['delta'].mean(0))

    df_ny = df_m[df_m.chages_abs > 0.01]
    chage_points_year = df_ny.ds.dt.year.values
    chage_points_month = df_ny.ds.dt.month.values
    points = df_ny.apply(lambda x: x.ds.strftime("%y%m%d"), 1)
    points_list = points.values

    def make_clickable(link,text):
        # target _blank to open new window
        # extract clickable text to display for your link
        return f'<a target="_blank" href="{link}">{text}</a>'

    df_m = df_m[df_m.chages_abs > 0.01].rename(columns = {'str_time':'Datum', 'y':'Werte'})[['Datum', 'Werte']].reset_index(drop = True)



    with col1_x:
        if len(points_list) > 0:
            df_m.index +=1
            col1_x.table(df_m.head(3))
        else:
            st.write("Keine Trendänderung")



    with col1_x:
        if len(points_list) > 0:
            expand00 = df_m['Datum'].values[0]
            col2_00 = col2.expander(f"**Nachrichten vom {expand00}**")
            with col2_00:
                url = f"https://www.tagesschau.de/api2u/news?date={points_list[0]}&ressort=wirtschaft"


                request = requests.get(url)
                response = request.json()

                title_list = []
                date_list = []
                web_list = []

                news_num = len(response['news'])

                for i in range(news_num):
                    date_list.append(response['news'][i]['date'])
                    title_list.append(response['news'][i]['title'])
                    web_list.append(response['news'][i]['detailsweb'])


                news = pd.DataFrame({'Date': date_list,
                                   'Titel': title_list,
                                   'Web': web_list,
                                   })



                news['URL'] = news[['Web', 'Titel']].apply(lambda x: f'<a href="{x.Web}" target="_blank">Zur Nachricht:: {x.Titel}</a>', 1)



                news['Date'] = news['Date'].apply(lambda x: pd.to_datetime(x).strftime("%d %b,%Y"))
                news.index +=1

                news_ = news[['Titel', 'URL']]

                news_ = news_.to_html(escape=False)
                st.write(news_, unsafe_allow_html=True, index = False)


            if len(points_list) > 1:
                expand01 = df_m['Datum'].values[1]
                col2_01 = col2.expander(f"**Nachrichten vom {expand01}**")
                with col2_01:
                    url = f"https://www.tagesschau.de/api2u/news?date={points_list[1]}&ressort=wirtschaft"


                    request = requests.get(url)
                    response = request.json()

                    title_list = []
                    date_list = []
                    web_list = []

                    news_num = len(response['news'])

                    for i in range(news_num):
                        date_list.append(response['news'][i]['date'])
                        title_list.append(response['news'][i]['title'])
                        web_list.append(response['news'][i]['detailsweb'])


                    news = pd.DataFrame({'Date': date_list,
                                       'Titel': title_list,
                                       'Web': web_list,
                                       })
                    news['URL'] = news[['Web', 'Titel']].apply(lambda x: f'<a href="{x.Web}" target="_blank">Zur Nachricht:: {x.Titel}</a>', 1)


                    news['Date'] = news['Date'].apply(lambda x: pd.to_datetime(x).strftime("%d %b,%Y"))
                    news.index +=1
                    news_ = news[['Titel', 'URL']]

                    news_ = news_.to_html(escape=False, index=True)
                    st.write(news_, unsafe_allow_html=True)

        else:
            col2_00 = col2.expander("")
            with col2_00:
                st.write("Keine Trendänderung")
except requests.exceptions.RequestException as e:
    st.write('Beim API-Aufruf ist ein Fehler aufgetreten')

except Exception as e:
    
    st.write('Etwas ist schief gelaufen')
