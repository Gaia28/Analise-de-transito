import streamlit as st
import plotly.express as px

def render(df, ano, rocket_palette, controller):
    st.title("📈 Dashboard de Visualização")
    st.markdown("---")

    if df.empty:
        st.warning("Não há dados para exibir. Selecione um ano na barra lateral ou carregue uma planilha na página 'Análise de dados'.")
        return

    st.header(f"Análise Detalhada - {ano}")
    
    st.subheader("Visão Geral do Ano")
    metricas = controller.get_metricas_gerais(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Acidentes", f"{metricas['total_acidentes']:,}".replace(",", "."))
    col2.metric("Total de Mortes", f"{metricas['total_mortos']:,}".replace(",", "."))
    col3.metric("Feridos Graves", f"{metricas['total_feridos_graves']:,}".replace(",", "."))
    col4.metric("Veículos Envolvidos", f"{metricas['total_veiculos']:,}".replace(",", "."))

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Causas de Acidentes")
        causas = controller.get_dados_agrupados(df, 'causa_acidente', top_n=10)
        if not causas.empty:
            fig_causas = px.bar(
                causas, x='total_acidentes', y='causa_acidente',
                orientation='h', title="Principais Causas",
                color='causa_acidente', color_discrete_sequence=rocket_palette
            )
            fig_causas.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_causas, use_container_width=True)
        else:
            st.warning("Coluna 'causa_acidente' não encontrada.")

    with col2:
        st.subheader("Top 10 Municípios com Mais Acidentes")
        municipios = controller.get_dados_agrupados(df, 'municipio', top_n=10)
        if not municipios.empty:
            fig_municipios = px.bar(
                municipios, x='total_acidentes', y='municipio',
                orientation='h', title="Municípios com Mais Acidentes",
                color='municipio', color_discrete_sequence=rocket_palette
            )
            fig_municipios.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_municipios, use_container_width=True)
        else:
            st.warning("Coluna 'municipio' não encontrada.")