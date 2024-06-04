import streamlit as st
import pandas as pd
import plost
import json

st.set_page_config(layout='wide', initial_sidebar_state='expanded',page_title="dofe.mi4people",
    page_icon="🇩🇪")

de = pd.read_csv('bun_year_dsh.csv', index_col=0)
de.year = de.year.astype(str)
co = pd.read_csv('total_dsh.csv', index_col=0)

with open('exp.json', 'r', encoding='utf-8') as f:
    exp = json.load(f)



liste = liste = {
    'Index der menschlichen Entwicklung':'hd',
    'Index der geschlechtsspezifischen Entwicklung':'gd', 
    'Durchschnittliche Schuljahre':'sc',
    'Bevölkerungswachstum': 'pop_growth',
    'Bruttoinlandsprodukt': 'bruttoinland',
    'Bevölkerung': 'population_total'
}



css =  """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    

    
    .stButton>button {
        background-color: rgb(240, 242, 246) !important; /* Background color when button is clicked */
        color: black !important; /* Text color when button is clicked */
    }
    .stButton>button:focus {
        background-color: red !important; /* Background color when button is clicked */
        color: white !important; /* Text color when button is clicked */
    }
    

   
    </style>
    """
st.markdown(css, unsafe_allow_html=True)
st.sidebar.header('MI4People')


st.subheader('Soziale Indikatoren auf jahrlicher Basis')
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



######

st.sidebar.markdown('''
---
Made with ❤️ 
''')



st.markdown(f'### {state}')

col1, col2, col3, col4 = st.columns(4)

question_mark = f'Bei der {key} liegt {state} auf Platz'
col1.metric("In Deutschland", int(temp_de[temp_de.state == state].ranking.values[0]),'','normal',  f'{question_mark} {int(temp_de[temp_de.state == state].ranking.values[0])} der Bundesländer')
col2.metric("In Europa & Zentralasien",  int(temp_eu[temp_eu.state == state].ranking.values[0]) , '','normal', f'{question_mark} {int(temp_eu[temp_eu.state == state].ranking.values[0])} der europäischen und zentralasiatischen Länder')
col3.metric("In der Welt",  int(temp_co[temp_co.state == state].ranking.values[0]) , '','normal',f'{question_mark} {int(temp_co[temp_co.state == state].ranking.values[0])} der Länder')
col4.metric("In Ländern mit hohem Einkommen", int(temp_in[temp_in.state == state].ranking.values[0]), '','normal',f'{question_mark} {int(temp_in[temp_in.state == state].ranking.values[0])} der Länder mit hohem Einkommen')


# Row B
#bar_df = de[de.state == state].rename(mapper = {indicator:key}, axis=1)
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

      

        temp = temp.reset_index(drop= True)
        temp.index +=1
        temp.columns = ['Ranking','Länder', 'Datum','Region', 'Einkommen Level',key]
        
        temp['Ranking'] = temp['Ranking'].astype(int)
        
        col2_x.table(temp)
        
st.write("*Datenquelle: World Bank, Destatis")

# except IndexError:
   
#     st.write('Es liegen nicht genügend Daten vor, bitte wählen Sie einen anderen Indikator oder ein anderes Bundesland aus')
# except:
#     st.write('Etwas ist schief gelaufen, bitte wählen Sie einen anderen Indikator oder ein anderes Bundesland')
    