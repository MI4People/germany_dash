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



st.header("""
DOfE
""")

st.subheader("""
Daten für Alle
""")

st.write("""
In der heutigen vernetzten Welt ist Daten zu einem integralen Bestandteil unseres Lebens geworden und durchdringt jeden Aspekt. Wirtschaftliche Indikatoren haben dabei eine herausragende Rolle in unseren täglichen Routinen eingenommen. Gespräche über Inflation, wirtschaftliche Stabilität und globale Wirtschaftstrends sind alltäglich geworden. Ein häufig auftretendes Problem ist jedoch, dass die Indikatoren, denen wir in unserem Alltag begegnen, oft zu allgemein gehalten sind. Wir hören vielleicht von globalen Phänomenen wie steigenden Temperaturen oder sich ändernden Wettermustern, aber oft fehlt uns ein klares Verständnis dafür, was in unserer unmittelbaren Umgebung geschieht. Diese Website untersucht die Bedeutung der Präsentation von wirtschaftlichen und wetterbezogenen Indikatoren auf lokaler Ebene, am Beispiel deutscher Bundesländer, und bietet Erklärungen, um Bürgerinnen und Bürgern wertvolle Einblicke zu vermitteln.
""")