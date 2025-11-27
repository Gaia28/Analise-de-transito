import streamlit as st
import plotly.express as px
import pandas as pd


def render(controller, rocket_palette):

    st.header("Análise Geral - Todos os Anos")
    st.write(
        "Esta seção apresenta uma visão consolidada de todos os arquivos de dados carregados, "
        "abrangendo múltiplos anos de acidentes de trânsito no estado do Pará."
    )

    df_geral = controller.listar_dados_consolidados_todos_anos()

    if df_geral.empty:
        st.warning(
            "❌ Não há dados carregados para análise geral. "
            "Carregue arquivos de dados na aba 'Análise de dados' primeiro."
        )
        return

    st.header("Métricas Consolidadas")
    
    metricas_por_ano = df_geral.groupby("ano").agg({
        "data_inversa": "count",
        "mortos": "sum",
        "feridos_graves": "sum",
        "veiculos": "sum",
        "pessoas": "sum",
        "feridos": "sum"
    }).rename(columns={"data_inversa": "total_acidentes"}).reset_index()

    total_acidentes = len(df_geral)
    total_mortos = df_geral["mortos"].sum() if "mortos" in df_geral.columns else 0
    total_feridos_graves = df_geral["feridos_graves"].sum() if "feridos_graves" in df_geral.columns else 0
    total_veiculos = df_geral["veiculos"].sum() if "veiculos" in df_geral.columns else 0
    media_veiculos = (
        df_geral["veiculos"].mean() if "veiculos" in df_geral.columns else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total de Acidentes", f"{total_acidentes:,}".replace(",", "."))
    col2.metric("Total de Mortes", f"{int(total_mortos):,}".replace(",", "."))
    col3.metric("Feridos Graves", f"{int(total_feridos_graves):,}".replace(",", "."))
    col4.metric("Média de Veículos", f"{media_veiculos:.2f}".replace(".", ","))
    col5.metric("Anos Analisados", f"{df_geral['ano'].nunique()}")

    st.markdown("---")

    st.header("Evolução Temporal - Comparação por Ano")

    fig_linha = px.line(
        metricas_por_ano,
        x="ano",
        y="total_acidentes",
        markers=True,
        title="Evolução do Total de Acidentes por Ano",
        labels={"ano": "Ano", "total_acidentes": "Total de Acidentes"},
        text="total_acidentes",
        color_discrete_sequence=["#541a83"]
    )
    fig_linha.update_traces(textposition="top center")
    st.plotly_chart(fig_linha, use_container_width=True)

    dados_comparacao = metricas_por_ano[["ano", "total_acidentes", "mortos", "feridos_graves"]].copy()
    dados_comparacao = dados_comparacao.rename(columns={
        "total_acidentes": "Acidentes",
        "mortos": "Mortos",
        "feridos_graves": "Feridos Graves"
    })

    fig_barras = px.bar(
        dados_comparacao,
        x="ano",
        y=["Acidentes", "Mortos", "Feridos Graves"],
        title="Comparação de Indicadores por Ano",
        labels={"ano": "Ano", "value": "Quantidade"},
        barmode="group",
        color_discrete_sequence=rocket_palette["discrete"][:3],
        template="plotly_dark"
    )
    st.plotly_chart(fig_barras, use_container_width=True)

    st.markdown("---")

    st.header("Top Municípios com Maior Número de Acidentes")

    if "municipio" in df_geral.columns:
        top_municipios = df_geral["municipio"].value_counts().head(10).reset_index()
        top_municipios.columns = ["municipio", "total_acidentes"]

        fig_top_municipios = px.bar(
            top_municipios,
            x="total_acidentes",
            y="municipio",
            orientation="h",
            title="Top 10 Municípios com Maior Número de Acidentes (Consolidado)",
            labels={"municipio": "Município", "total_acidentes": "Total de Acidentes"},
            color="total_acidentes",
            color_continuous_scale=rocket_palette["continuous"],
            template="plotly_dark"
        )
        fig_top_municipios.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_top_municipios, use_container_width=True)

    st.markdown("---")

    st.header("Localização dos Acidentes - Mapa Geral")

    if "latitude" in df_geral.columns and "longitude" in df_geral.columns:
        df_mapa = df_geral[
            (df_geral["latitude"].notna()) &
            (df_geral["longitude"].notna()) &
            (df_geral["latitude"] != 0) &
            (df_geral["longitude"] != 0)
        ].copy()

        if not df_mapa.empty:
            mapa = px.scatter_mapbox(
                df_mapa,
                lat="latitude",
                lon="longitude",
                hover_name="municipio" if "municipio" in df_mapa.columns else None,
                hover_data={
                    "ano": True,
                    "mortos": True if "mortos" in df_mapa.columns else False,
                    "feridos_graves": True if "feridos_graves" in df_mapa.columns else False,
                },
                zoom=4,
                height=600,
                color="ano",
                color_discrete_sequence=rocket_palette["discrete"],
                title="Mapa Consolidado de Acidentes (Todos os Anos)"
            )
            mapa.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(mapa, use_container_width=True)
        else:
            st.warning(
                f"⚠️ Nenhuma coordenada válida encontrada. "
                f"Total de registros com dados de localização: {len(df_mapa)} / {len(df_geral)}"
            )
    else:
        st.warning("⚠️ Os arquivos não contêm colunas de latitude/longitude para gerar o mapa.")

    st.markdown("---")

    st.header("Causas de Acidentes - Consolidado")

    if "causa_acidente" in df_geral.columns:
        top_causas = df_geral["causa_acidente"].value_counts().head(10).reset_index()
        top_causas.columns = ["causa_acidente", "total_acidentes"]

        fig_causas = px.bar(
            top_causas,
            x="total_acidentes",
            y="causa_acidente",
            title="Top 10 Causas de Acidentes (Consolidado)",
            labels={"causa_acidente": "Causa", "total_acidentes": "Total de Acidentes"},
            color="total_acidentes",
            color_continuous_scale=rocket_palette["continuous"],
            template="plotly_dark"
        )
        fig_causas.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_causas, use_container_width=True)

    st.markdown("---")

    st.header("Tipos de Acidentes - Consolidado")

    if "tipo_acidente" in df_geral.columns:
        tipos_acidentes = df_geral["tipo_acidente"].value_counts().reset_index()
        tipos_acidentes.columns = ["tipo_acidente", "total_acidentes"]

        fig_tipos = px.pie(
            tipos_acidentes,
            names="tipo_acidente",
            values="total_acidentes",
            title="Distribuição de Tipos de Acidentes (Consolidado)",
            color_discrete_sequence=rocket_palette["discrete"]
        )
        st.plotly_chart(fig_tipos, use_container_width=True)

    st.markdown("---")

    st.header("Resumo por Ano")
    st.dataframe(metricas_por_ano, use_container_width=True)
