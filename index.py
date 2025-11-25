from view import home_page, upload_page, dashboard_page, municipio_page, classificacao_page, periodo_page
from view.components.sidebar import render_sidebar
import streamlit as st
from controller.AcidenteController import AcidenteController
import os
import re

st.set_page_config(
    page_title="Análise de Trânsito PA",
    page_icon="🚦",
    layout="wide"
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
    municipio_page.render(df, ano, palette, controller)

elif selected_page == "Classificações":
    classificacao_page.render(df, ano, palette, controller)

elif selected_page == "Período":
    periodo_page.render(df, ano, palette)
