import streamlit as st

#set the page config
st.set_page_config(layout='wide', initial_sidebar_state='expanded',page_title="dofe.mi4people",
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

#set the each item at the page
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    
    
st.sidebar.header('MI4People')
#st.subheader('Indicator')


st.sidebar.markdown('''
---
Made with ❤️ 

''')