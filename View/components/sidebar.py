
import streamlit as st
from streamlit_option_menu import option_menu
from controller.AcidenteController import AcidenteController
import pandas as pd
import re


def render_sidebar():
    """
    Renderiza a barra lateral, o menu de navegação e o seletor de banco de dados.

    Retorna:
        tuple: (selected_page, df, ano_selecionado, rocket_palette)
    """

    df = pd.DataFrame()
    ano_selecionado = "Nenhum"

    with st.sidebar:
        # detectar tema atual do Streamlit para ajustar cores do menu (suporte claro/escuro)
        try:
            theme_base = st.get_option("theme.base") or "light"
        except Exception:
            theme_base = "light"

        theme_base = str(theme_base).lower()
        # cor do texto e do ícone dependendo do tema
        text_color = "#FFFFFF" if theme_base == "dark" else "#000000"
        icon_color = "#FFFFFF" if theme_base == "dark" else "#541a83e6"

        styles = {
            "container": {"padding": "5!important"},
            "icon": {"color": icon_color, "font-size": "25px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "color": text_color,
                "--hover-color": "#8A87871F",
            },
            "nav-link-selected": {"background-color": "#8A87871F", "color": text_color},
        }

        selected_page = option_menu(
            menu_title="Projeto Big Data",
            options=["Home", "Análise de dados", "Visualização de Dados",
                     "Acidentes por município", "Classificações", "Período", "Análise Geral"],
            icons=["house", "cloud-upload",
                   "bar-chart", "map", "list", "calendar", "globe"],
            menu_icon="cast",
            default_index=0,
            styles=styles
        )

        controller = AcidenteController()

        if selected_page not in ["Home", "Análise de dados"]:
            bancos_de_dados = controller.listar_bancos_de_dados()

            if not bancos_de_dados:
                st.warning(
                    "Nenhum banco de dados encontrado. Carregue dados na página 'Análise de dados'.")
            else:
                nome_banco_selecionado = st.selectbox(
                    "Selecione o ano para Análise:",
                    options=bancos_de_dados,
                    format_func=lambda x: f"Analisar {re.search(r'\d{4}', x).group(0) if re.search(r'\d{4}', x) else x}"
                )

                if nome_banco_selecionado:
                    df = controller.listar_dados_por_banco(
                        nome_banco_selecionado)
                    ano_selecionado = re.search(r'\d{4}', nome_banco_selecionado).group(
                        0) if re.search(r'\d{4}', nome_banco_selecionado) else "Ano Desconhecido"

    # Paleta de cores utilizada nas páginas (discrete para categorias, continuous para escalas)
    rocket_palette = {
        "discrete": [
            "#160141", "#260446", "#3A0453", "#66135C", "#792860", "#A53950", "#A54848", "#A06444", "#9E7E42", "#AC973C"
        ],
        "continuous": [
            "#160141", "#260446", "#3A0453", "#66135C", "#792860", "#A53950", "#A54848", "#A06444", "#9E7E42", "#AC973C"
        ]
    }

    return selected_page, df, ano_selecionado, rocket_palette
