import streamlit as st
import pandas as pd
import plost

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

de = pd.read_csv('bun_year_dsh.csv', index_col=0)
de.year = de.year.astype(str)
co = pd.read_csv('total_dsh.csv', index_col=0)



liste = {'Total Unemployment %':'unemployment_total', 'Male Unemployment %':'unemployment_man','Female Unemployment %':'unemployment_women','Inflation':'inflation', 'Gini Index':'gini', 'Gross Domestic Product':'bruttoinland','Population':'population_total',  'GDP Per Capita':'gdp_per','GDP Growth': 'gdp_growth','Population Growth':'pop_growth', 'Change in CO2 (compare to last Year)':'co_1', 'Change in CO2 (compare to before 10 Year)':'co_10'}



with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
st.sidebar.header('Dashboard `version 1`')


st.sidebar.subheader('Indicator')
key = st.sidebar.selectbox('Indicator', liste.keys( )) 
indicator = liste[key]

show_list = {'state':'State', 'year':'Year', 'region':'Region', 'incomeLevel':'Income Level', indicator:key }

show_list_1 = {'state':'State', 'year':'Year', indicator:key }


st.sidebar.subheader('State')
state = st.sidebar.selectbox('Select state', set(de.state))

s_l = list(set(de.state))
s_l.remove(state)

c_l = [c for c in set(co.state) if c not in s_l]
co = co[co.state.isin(c_l)]

temp_de = de.dropna(subset = [indicator])
y = temp_de.year.astype(int).max()
temp_de = temp_de[temp_de.year == str(y)]


temp= co.dropna(subset = [indicator])
temp_eu = temp[temp.region == 'Europe & Central Asia']
y = temp_de.year.astype(int).max()
temp_eu = temp_eu[temp_eu.year == y]


temp_co = co.dropna(subset = [indicator])
y = temp_de.year.astype(int).max()
temp_co = temp_co[temp_co.year == y]
temp_co = temp_co.sort_values(indicator).reset_index(drop=True)
temp_co.index +=1


temp = co.dropna(subset = [indicator])
temp_in = temp[temp.incomeLevel == 'High income']
y = temp_de.year.astype(int).max()
temp_in = temp_in[temp_in.year == y]
temp_in = temp_in.sort_values(indicator).reset_index(drop=True)
temp_in.index +=1

#####sorting 
if indicator in ['bruttoinland','population_total', 'gdp_per', 'pop_growth', 'gdp_growth']:
    
    temp_de = temp_de.sort_values(indicator, ascending=False).reset_index(drop=True)
    temp_de.index +=1
    
    temp_eu = temp_eu.sort_values(indicator, ascending=False).reset_index(drop=True)
    temp_eu.index +=1
    
    temp_co = temp_co.sort_values(indicator, ascending=False).reset_index(drop=True)
    temp_co.index +=1
    
    temp_in = temp_in.sort_values(indicator, ascending=False).reset_index(drop=True)
    temp_in.index +=1

else:
    temp_de = temp_de.sort_values(indicator).reset_index(drop=True)
    temp_de.index +=1
    
    temp_eu = temp_eu.sort_values(indicator).reset_index(drop=True)
    temp_eu.index +=1
    
    temp_co = temp_co.sort_values(indicator).reset_index(drop=True)
    temp_co.index +=1
    
    temp_in = temp_in.sort_values(indicator).reset_index(drop=True)
    temp_in.index +=1



######

st.sidebar.markdown('''
---
Created with ❤️ 
''')


# Row A
st.markdown('### Metrics')
col1, col2, col3, col4 = st.columns(4)

col1.metric("In Germany", temp_de[temp_de.state == state].index[0],'')
col2.metric("In Europa",  temp_eu[temp_eu.state == state].index[0] , '')
col3.metric("In World",  temp_co[temp_co.state == state].index[0] , '')
col4.metric("In High Income Countries",  temp_in[temp_in.state == state].index[0] , '')

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
c2_x = c2.expander('Values')
temp = de[(de.state == state)&(de.year > '2012')][['state','year',indicator]].dropna().rename(mapper = show_list_1, axis = 1).reset_index(drop = True)
temp.index +=1
with c2_x:

    c2_x.table(temp.style.format({key:"{:.3}"}))
    
    
    

col1, col2 = st.columns((4, 8))

temp = temp_co.copy()
num = temp[temp.state==state].index[0]

temp = pd.concat([temp.head(2),temp.loc[[temp[temp.state=='Germany'].index[0]]],
                           temp.loc[[temp[temp.state=='Spain'].index[0]]],
                           temp.loc[[temp[temp.state=='France'].index[0]]],
                          temp.loc[[temp[temp.state=='China'].index[0]]],
                          temp.loc[[temp[temp.state=='United States'].index[0]]],
                          temp.loc[[temp[temp.state=='United Kingdom'].index[0]]],
                          temp.loc[[temp[temp.state=='Russian Federation'].index[0]]],
                           temp.loc[[i for i in range(num-2, num+3)]], 
              temp.tail(2)])
temp.drop_duplicates(inplace=True)

if indicator in ['bruttoinland','population_total', 'gdp_per', 'pop_growth', 'gdp_growth']:
    
    temp = temp[['state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator,ascending=False)

else:
    temp = temp[['state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator)


col1_x = col1.expander('Order in Germany')


with col1_x:
    col1_x.table(data=temp_de[['state','year',indicator]].rename(mapper = show_list_1, axis = 1).style.format({key:"{:.3}"}))
    
    
col2_x = col2.expander('Order in World with some selected Countries')

with col2_x:
    col2_x.table(temp.rename(mapper = show_list, axis = 1).style.format({key:"{:.3}"}))