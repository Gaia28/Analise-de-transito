import streamlit as st
from controller.AcidenteController import AcidenteController
import plotly.express as px
import re


def tela_visualizacao():
    with st.sidebar:
        st.title("Navegação")
        if st.button("⬅️ Voltar à Tela Inicial"):
            st.session_state["tela"] = "inicial"
            st.rerun()
        if st.button("➡️ Visualização de Dados"):
            st.session_state["tela"] = "visualizacao"
            st.rerun()
    st.title("Dashboard de Visualização")
    st.markdown("---")

    controller = AcidenteController()
    bancos_de_dados = controller.listar_bancos_de_dados()

    if not bancos_de_dados:
        st.warning("Nenhum banco de dados foi encontrado na pasta /data.")
        st.info("Por favor, vá para a página de 'Análise e Carregamento' para fazer o upload de uma planilha primeiro.")
        return

    st.header("Selecione o ano para análise:")
    nome_banco_selecionado = st.selectbox(
        "Selecione o banco de dados:",
        options=bancos_de_dados,
        # Melhora a exibição
        format_func=lambda x: f"Analisar dados de {re.search(r'\d{4}', x).group(0) if re.search(r'\d{4}', x) else x}"
    )

    if nome_banco_selecionado:
        ano = re.search(r'\d{4}', nome_banco_selecionado).group(0) if re.search(
            r'\d{4}', nome_banco_selecionado) else "Ano Desconhecido"

        st.header(f"Análise Detalhada - {ano}")

        df = controller.listar_dados_por_banco(nome_banco_selecionado)

        if df.empty:
            st.warning(
                "Não foram encontrados dados para o estado do Pará (PA) neste arquivo.")
            return

        st.subheader("Visão Geral do Ano")
        metricas = controller.get_metricas_gerais(df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Acidentes",
                    f"{metricas['total_acidentes']:,}".replace(",", "."))
        col2.metric("Total de Mortes",
                    f"{metricas['total_mortos']:,}".replace(",", "."))
        col3.metric("Feridos Graves",
                    f"{metricas['total_feridos_graves']:,}".replace(",", "."))
        col4.metric("Veículos Envolvidos",
                    f"{metricas['total_veiculos']:,}".replace(",", "."))

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 10 Causas de Acidentes")
            causas = controller.get_dados_agrupados(
                df, 'causa_acidente', top_n=10)
            if not causas.empty:
                fig_causas = px.bar(causas, x='total_acidentes', y='causa_acidente',
                                    orientation='h', title="Principais Causas")
                fig_causas.update_layout(
                    yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_causas, use_container_width=True)
            else:
                st.warning("Coluna 'causa_acidente' não encontrada.")

        with col2:
            st.subheader("Top 10 Municípios com Mais Acidentes")
            municipios = controller.get_dados_agrupados(
                df, 'municipio', top_n=10)
            if not municipios.empty:
                fig_municipios = px.bar(municipios, x='total_acidentes', y='municipio',
                                        orientation='h', title="Municípios com Mais Acidentes")
                fig_municipios.update_layout(
                    yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_municipios, use_container_width=True)
            else:
                st.warning("Coluna 'municipio' não encontrada.")
        st.markdown("---")