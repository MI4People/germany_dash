import streamlit as st
import pandas as pd
import plost
import json

st.set_page_config(layout='wide', initial_sidebar_state='expanded',page_title="dashgermany",
    page_icon="🇩🇪")

de = pd.read_csv('bun_year_dsh.csv', index_col=0)
de.year = de.year.astype(str)
co = pd.read_csv('total_dsh.csv', index_col=0)

with open('exp.json', 'r', encoding='utf-8') as f:
    exp = json.load(f)



liste = {'Inflation':'inflation','Total Unemployment %':'unemployment_total', 'Male Unemployment %':'unemployment_man','Female Unemployment %':'unemployment_women', 'Gross Domestic Product':'bruttoinland','Population':'population_total',  'GDP Per Capita':'gdp_per','GDP Growth': 'gdp_growth','Population Growth':'pop_growth', 'Change in CO2 (compare to last Year)':'co_1', 'Change in CO2 (compare to before 10 Year)':'co_10'}



with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
st.sidebar.header('Dashboard Germany')


st.subheader('Indicator')
key = st.selectbox('Indicator', liste.keys( )) 
indicator = liste[key]

show_list = {'state':'State', 'year':'Year', 'region':'Region', 'incomeLevel':'Income Level', indicator:key }

show_list_1 = {'state':'State', 'year':'Year', indicator:key }


st.subheader('State')
state = st.selectbox('Select state', set(de.state))

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
st.markdown(f'### {state}')
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
    st_exp_en = st.expander('explanation in English')
    with st_exp_en:
        c = st.selectbox(f'Brief Explanation for {key} in English', exp[indicator]['English'].keys())
        st.write( exp[indicator]['English'][c]) 
            
    st_exp_de = st.expander('explanation in German')
    with st_exp_de:             
        c = st.selectbox(f'Brief Explanation for {key} in German',  exp[indicator]['Deutsch'].keys())
        st.write(exp[indicator]['Deutsch'][c]) 
    
            
        
        
c2_x = c2.expander('Values')
temp = de[(de.state == state)&(de.year > '2012')][['state','year',indicator]].dropna().rename(mapper = show_list_1, axis = 1).reset_index(drop = True)
temp.index +=1
with c2_x:

    c2_x.table(temp.style.format({key:"{:.3}"}))
    
    
    

col1, col2 = st.columns((4, 8))

temp = temp_co.copy()



if indicator in ['bruttoinland','population_total', 'gdp_per', 'pop_growth', 'gdp_growth']:
    
    temp = temp[['state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator,ascending=False)

else:
    temp = temp[['state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator)


col1_x = col1.expander('Order in Germany')


with col1_x:
    col1_x.table(data=temp_de[['state','year',indicator]].rename(mapper = show_list_1, axis = 1).style.format({key:"{:.3}"}))
    
    
col2_x = col2.expander('Order in World with some selected Countries')

with col2_x:
        c = st.multiselect('States', temp.state, default = [state, 'Germany','United States','United Kingdom', 'France','Spain','Italy' ,'China','Japan' ])
      #  num = temp[temp.state==state].index[0]

        temp = pd.concat([temp[temp.state.isin(c)],
                               temp[temp.state==state]])

        temp.drop_duplicates(inplace=True)
        if indicator in ['bruttoinland','population_total', 'gdp_per', 'pop_growth', 'gdp_growth']:

            temp = temp[['state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator,ascending=False)

        else:
            temp = temp[['state', 'year', 'region','incomeLevel', indicator]].sort_values(indicator)
        
        temp.reset_index(drop=True, inplace=True)

        temp.index +=1

        col2_x.table(temp)