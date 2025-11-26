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

    # Se tivermos controller e nome_banco, obter métricas direto do DB (mais confiável)
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

    # Fallback: calcula a partir do DataFrame passado
    if 'municipio' in df.columns:
        df_municipio = df[df['municipio'] == municipio_selecionado]
        total_acidentes = len(df_municipio)
        total_feridos_graves = df_municipio['feridos_graves'].sum(
        ) if 'feridos_graves' in df_municipio.columns else 0
        total_mortos = df_municipio['mortos'].sum(
        ) if 'mortos' in df_municipio.columns else 0
        total_veiculos = df_municipio['veiculos'].sum(
        ) if 'veiculos' in df_municipio.columns else 0
    else:
        total_acidentes = 0
        total_feridos_graves = 0
        total_mortos = 0
        total_veiculos = 0

    if municipio_selecionado:
        st.write(
            f"Estatísticas para o município de **{municipio_selecionado}** no ano de **{ano}**:")
        st.markdown(f"- Total de Acidentes: **{total_acidentes}**")
        st.markdown(f"- Total de Mortos: **{total_mortos}**")
        st.markdown(f"- Total de Feridos Graves: **{total_feridos_graves}**")
        st.markdown(f"- Total de Veículos Envolvidos: **{total_veiculos}**")

        # Gráfico Radar Comparativo
    st.write(f"Comparação Geral do Município de {municipio_selecionado}")

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

    if 'data_inversa' in df.columns:
        try:
            df_municipio = df[df['municipio'] == municipio_selecionado].copy()
            df_municipio['data_inversa'] = pd.to_datetime(
                df_municipio['data_inversa'])
            df_municipio['mes'] = df_municipio['data_inversa'].dt.month

            acidentes_por_mes = df_municipio.groupby(
                'mes').size().reset_index(name='Total de Acidentes')

            meses_pt = {
                1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
                7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
            }
            acidentes_por_mes = acidentes_por_mes.set_index(
                'mes').reindex(range(1, 13)).reset_index()
            acidentes_por_mes['Mês'] = acidentes_por_mes['mes'].map(meses_pt)
            acidentes_por_mes = acidentes_por_mes.fillna(0)

            fig_mes = px.line(acidentes_por_mes, x='Mês', y='Total de Acidentes',
                              title=f"Acidentes por Mês em {municipio_selecionado} ({ano})", markers=True,
                              labels={
                                  'Mês': 'Mês', 'Total de Acidentes': 'Total de Acidentes'},
                              color_discrete_sequence=["#590B7E"])
            fig_mes.update_layout(template='plotly_dark')
            st.plotly_chart(fig_mes, use_container_width=True)
        except Exception as e:
            st.error(
                f"Erro ao analisar data_inversa para {municipio_selecionado}: {e}")
    else:
        st.warning("Coluna 'data_inversa' não encontrada para análise por mês.")

    if 'tipo_acidente' in df.columns:
        df_municipio = df[df['municipio'] == municipio_selecionado]
        tipo = df_municipio['tipo_acidente'].value_counts().reset_index()
        tipo.columns = ['Tipo de Acidente', 'Número de Acidentes']
        tipo = tipo.sort_values(by='Número de Acidentes', ascending=False)
        fig_tipo = px.bar(
            tipo, x='Tipo de Acidente', y='Número de Acidentes',
            title=f"Tipos de Acidentes em {municipio_selecionado} ({ano})",
            color='Tipo de Acidente', color_discrete_sequence=rocket_palette['discrete']
        )
        fig_tipo.update_layout(template='plotly_dark')
        st.plotly_chart(fig_tipo)
