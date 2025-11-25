import streamlit as st
import plotly.express as px
import pandas as pd


def render(df, ano, rocket_palette, controller=None):
    st.header("Análise de Acidentes por Município")

    if df.empty:
        st.warning(
            "Não há dados para exibir. Selecione um ano na barra lateral ou carregue dados primeiro.")
        return

    st.write(
        f"Esta seção apresenta uma análise dos acidentes de trânsito no Pará para o ano de {ano}, categorizados pelos municípios com mais acidentes registrados.")

    top_municipios = df['municipio'].value_counts().nlargest(10)
    df_grafico = pd.DataFrame(
        {'municipio': top_municipios.index, 'acidentes': top_municipios.values})

    fig = px.bar(df_grafico, x='municipio', y='acidentes', title=f"10 Municípios Com Mais Acidentes no Pará ({ano})",
                 color='municipio', color_discrete_sequence=rocket_palette['discrete'],
                 category_orders={
                     'municipio': df_grafico['municipio'].tolist()},
                 template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.subheader("Detalhes por Município")
    st.text("Selecione um município para ver estatísticas detalhadas sobre acidentes, mortes, feridos graves e veículos envolvidos.")

    col_esq, col_central, col_dir = st.columns([0.5, 5, 0.5])

    with col_central:
        # Tenta obter lista de municípios pelo controller usando o banco selecionado
        municipios_disponiveis = []
        nome_banco = st.session_state.get('nome_banco_selecionado')
        if controller is not None and nome_banco:
            try:
                municipios_disponiveis = controller.listar_municipios(
                    nome_banco)
            except Exception:
                municipios_disponiveis = []

        # Fallback para lista a partir do DataFrame passado
        if not municipios_disponiveis and not df.empty and 'municipio' in df.columns:
            municipios_disponiveis = sorted(
                df['municipio'].dropna().astype(
                    str).str.strip().unique().tolist()
            )

        if not municipios_disponiveis:
            st.warning("Nenhum município disponível para seleção.")
            return

        municipio_selecionado = st.selectbox(
            "Selecione o município:", municipios_disponiveis)

        if municipio_selecionado:
            nome_banco = st.session_state.get('nome_banco_selecionado')

    # Inicializa variáveis de resumo para garantir que existam sempre
    total_acidentes = 0
    total_mortos = 0
    total_feridos_graves = 0
    total_veiculos = 0

    # Se tivermos controller e nome_banco, obter métricas direto do DB
    if controller is not None and nome_banco:
        try:
            resumo = controller.dados_por_municipio(
                nome_banco, municipio_selecionado)
            if not resumo.empty:
                total_acidentes = int(
                    resumo.loc[0, 'total_acidentes']) if 'total_acidentes' in resumo.columns else 0
                total_feridos_graves = int(
                    resumo.loc[0, 'total_feridos_graves']) if 'total_feridos_graves' in resumo.columns else 0
                total_mortos = int(
                    resumo.loc[0, 'total_mortos']) if 'total_mortos' in resumo.columns else 0
                total_veiculos = int(
                    resumo.loc[0, 'total_veiculos']) if 'total_veiculos' in resumo.columns else 0
            else:
                total_acidentes = 0
                total_feridos_graves = 0
                total_mortos = 0
                total_veiculos = 0
        except Exception:
            # Se falhar, cai no fallback a seguir
            pass
        else:
            st.subheader(f"Resumo para {municipio_selecionado} ({ano})")
            st.markdown(f"- Total de Acidentes: **{total_acidentes}**")
            st.markdown(
                f"- Total de Feridos Graves: **{total_feridos_graves}**")
            st.markdown(f"- Total de Mortos: **{total_mortos}**")
            st.markdown(
                f"- Total de Veículos Envolvidos: **{total_veiculos}**")

    st.markdown("---")
    st.subheader(f"Análise Detalhada para {municipio_selecionado} ({ano})")

    st.write("Comparação Geral do Município")

    df_radar = pd.DataFrame({
        "categoria": ["Acidentes", "Mortes", "Feridos Graves", "Veículos"],
        "valores": [total_acidentes, total_mortos, total_feridos_graves, total_veiculos]
    })

    fig_radar = px.line_polar(
        df_radar,
        r="valores",
        theta="categoria",
        line_close=True,
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=rocket_palette["discrete"]
    )

    fig_radar.update_traces(fill="toself", opacity=0.7)

    st.plotly_chart(fig_radar, use_container_width=True)
