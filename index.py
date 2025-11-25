import streamlit as st
from controller.AcidenteController import AcidenteController
import os
import re

<<<<<<< HEAD
from View.components.sidebar import render_sidebar
from View import home_page, upload_page, dashboard_page, municipio_page, classificacao_page, periodo_page
=======
from view.components.sidebar import render_sidebar
from view import home_page, upload_page, dashboard_page, municipio_page, classificacao_page, periodo_page
>>>>>>> abb12b43783c3da99279a28a2bddc1b6e8c3cc3a

st.set_page_config(
    page_title="Análise de Trânsito PA",
    page_icon="🚦",
<<<<<<< HEAD
    layout="wide"
=======
    layout="wide" 
>>>>>>> abb12b43783c3da99279a28a2bddc1b6e8c3cc3a
)
selected_page, df, ano, palette = render_sidebar()

controller = AcidenteController()

if selected_page == "Home":
    home_page.render()

elif selected_page == "Análise de dados":
    upload_page.render(controller)

elif selected_page == "Visualização de Dados":
    dashboard_page.render(df, ano, palette, controller)

elif selected_page == "Acidentes por município":
<<<<<<< HEAD
    municipio_page.render(df, ano, palette, controller)
=======
    municipio_page.render(df, ano, palette)
>>>>>>> abb12b43783c3da99279a28a2bddc1b6e8c3cc3a

elif selected_page == "Classificações":
    classificacao_page.render(df, ano, palette, controller)

elif selected_page == "Período":
<<<<<<< HEAD
    periodo_page.render(df, ano, palette)
=======
    periodo_page.render(df, ano, palette)
>>>>>>> abb12b43783c3da99279a28a2bddc1b6e8c3cc3a
