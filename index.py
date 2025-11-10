# Substitua o conteúdo em: index.py

import streamlit as st
from controller.AcidenteController import AcidenteController
import os
import re

# Importe os novos componentes e páginas
from view.components.sidebar import render_sidebar
from view import home_page, upload_page, dashboard_page, municipio_page, classificacao_page, periodo_page

st.set_page_config(
    page_title="Análise de Trânsito PA",
    page_icon="🚦",
    layout="wide"  # Layout 'wide' é melhor para dashboards
)

# 1. Renderiza a sidebar e obtém a página selecionada e os dados
selected_page, df, ano, palette = render_sidebar()

# 2. Instancia o controller principal
controller = AcidenteController()

# 3. Roteamento de Página
if selected_page == "Home":
    home_page.render()

elif selected_page == "Análise de dados":
    # A página de upload não precisa dos dados carregados, ela os cria
    upload_page.render(controller)

elif selected_page == "Visualização de Dados":
    dashboard_page.render(df, ano, palette, controller)

elif selected_page == "Acidentes por município":
    municipio_page.render(df, ano, palette)

elif selected_page == "Classificações":
    classificacao_page.render(df, ano, palette, controller)

elif selected_page == "Período":
    periodo_page.render(df, ano, palette)