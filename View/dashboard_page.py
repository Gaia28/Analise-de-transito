import streamlit as st
import plotly.express as px
import pandas as pd


def render(df, ano, rocket_palette, controller):

    st.header("📈 Dashboard de Visualização")
    st.write(
        f"Esta seção apresenta uma visão geral das métricas e visualizações dos acidentes de trânsito no Pará de ({ano}).")

    if df.empty:
        st.warning(
            "Não há dados para exibir. Carregue um arquivo na aba Análise de Dados.")
        return

        # DEBUG: informações básicas para identificar por que o dashboard pode ficar vazio
        try:
            nome_banco = st.session_state.get('nome_banco_selecionado')
        except Exception:
            nome_banco = None
        st.caption(
            f"DEBUG: banco selecionado={nome_banco} | df.shape={getattr(df, 'shape', 'no-df')} | colunas={list(df.columns) if hasattr(df, 'columns') else 'no-df'}")

    st.header("Métricas Gerais do Ano")

    metricas = controller.get_metricas_gerais(df)

    media_veiculos = (
        df["veiculos"].mean() if "veiculos" in df.columns else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Acidentes",
                f"{metricas['total_acidentes']:,}".replace(",", "."))
    col2.metric("Total de Mortes",
                f"{metricas['total_mortos']:,}".replace(",", "."))
    col3.metric("Feridos Graves",
                f"{metricas['total_feridos_graves']:,}".replace(",", "."))
    col4.metric("Média de Veículos", f"{media_veiculos:.2f}".replace(".", ","))

    dados_comp = pd.DataFrame({
        "Indicador": ["Acidentes", "Mortes", "Feridos Graves", "Veículos"],
        "Valores": [
            metricas["total_acidentes"],
            metricas["total_mortos"],
            metricas["total_feridos_graves"],
            metricas["total_veiculos"]
        ]
    })

    fig_comp = px.bar(
        dados_comp, x="Indicador", y="Valores",
        title=f"Comparação Geral de Acidentes ({ano})",
        text="Valores",
        color="Indicador",
        color_discrete_sequence=rocket_palette['discrete'],
        template="plotly_dark"
    )
    fig_comp.update_traces(textposition="outside")
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")
    st.header("Localização dos Acidentes no Pará")

    # Verifica se há dados válidos de latitude/longitude
    if "latitude" in df.columns and "longitude" in df.columns:
        # Filtra apenas linhas com coordenadas válidas
        df_mapa = df[
            (df["latitude"].notna()) &
            (df["longitude"].notna()) &
            (df["latitude"] != 0) &
            (df["longitude"] != 0)
        ].copy()

        if not df_mapa.empty:
            mapa = px.scatter_mapbox(
                df_mapa,
                lat="latitude",
                lon="longitude",
                hover_name="municipio" if "municipio" in df_mapa.columns else None,
                hover_data={
                    "mortos": True if "mortos" in df_mapa.columns else False,
                    "feridos_graves": True if "feridos_graves" in df_mapa.columns else False,
                    "veiculos": True if "veiculos" in df_mapa.columns else False
                },
                zoom=4,
                height=500,
                color_discrete_sequence=["#590B7E"],
                title=f"Mapa de Acidentes e Pontos de Ocorrência ({ano})"
            )
            mapa.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(mapa, use_container_width=True)
        else:
            st.warning(
                f"❌ Nenhuma coordenada válida encontrada. Total de registros com dados de localização: {len(df_mapa)} / {len(df)}")
    else:
        st.warning(
            "⚠️ O arquivo não contém colunas de latitude/longitude para gerar o mapa.")
        st.info("Colunas disponíveis no DataFrame:", df.columns.tolist())

    st.markdown("---")
    st.header("Distribuição de Veículos Envolvidos nos Acidentes")

    if "veiculos" in df.columns:
        veiculos_count = df["veiculos"].value_counts().reset_index()
        veiculos_count.columns = ["Quantidade de Veículos", "Total"]

        fig_pizza = px.pie(
            veiculos_count,
            names="Quantidade de Veículos",
            values="Total",
            title=f"Quantidade de Acidentes por Número de Veículos Envolvidos ({ano})",
            color_discrete_sequence=rocket_palette['discrete']
        )

        st.plotly_chart(fig_pizza, use_container_width=True)
    else:
        st.warning("A coluna 'veiculos' não foi encontrada.")
