import streamlit as st
import plotly.express as px

def render(df, ano, rocket_palette, controller):
    st.header("Análise de Acidentes por Classificação")

    if df.empty:
        st.warning("Não há dados para exibir. Selecione um ano na barra lateral ou carregue dados primeiro.")
        return

    st.write(f"Esta seção apresenta uma análise dos acidentes de trânsito no Pará para o ano de {ano}, categorizados por diferentes classificações.")
    st.subheader("Acidentes por Tipo")

    col_esq, col_central, col_dir = st.columns([0.5, 5, 0.5])
    with col_central:
        if 'tipo_acidente' in df.columns:
            tipo = df['tipo_acidente'].value_counts().reset_index()
            tipo.columns = ['Tipo de Acidente', 'Número de Acidentes']
            tipo = tipo.sort_values(by='Número de Acidentes', ascending=False)
            fig_tipo = px.bar(
                tipo, x='Tipo de Acidente', y='Número de Acidentes',
                title=f"Tipos de Acidentes no Pará ({ano})",
                color='Tipo de Acidente', color_discrete_sequence=rocket_palette
            )
            fig_tipo.update_layout(template='plotly_dark')
            st.plotly_chart(fig_tipo)
        else:
            st.warning("Coluna 'tipo_acidente' não encontrada no arquivo.")

    st.markdown("---")
    st.markdown("### Outros Detalhes dos Acidentes")
    col1, col2 = st.columns(2)

    with col1:
        if 'classificacao_acidente' in df.columns:
            classificacao = df['classificacao_acidente'].value_counts().reset_index()
            classificacao.columns = ['Classificação', 'Número de Acidentes']
            fig_classificacao = px.pie(
                classificacao, names='Classificação', values='Número de Acidentes',
                title=f"Classificação de Acidentes por gravidade ({ano})",
                color='Classificação', color_discrete_sequence=rocket_palette, hole=0.3
            )
            fig_classificacao.update_traces(textposition='inside', textinfo='percent+label')
            fig_classificacao.update_layout(template='plotly_dark')
            st.plotly_chart(fig_classificacao, use_container_width=True)
        else:
            st.warning("Coluna 'classificacao_acidente' não encontrada no arquivo.")

    with col2:
        if 'tipo_pista' in df.columns:
            tipo_pista = df['tipo_pista'].value_counts().reset_index()
            tipo_pista.columns = ['Tipo de Pista', 'Número de Acidentes']
            fig_tipo_pista = px.bar(
                tipo_pista, x='Tipo de Pista', y='Número de Acidentes',
                title=f"Tipo de Pista nos Acidentes ({ano})",
                color='Tipo de Pista', color_discrete_sequence=rocket_palette
            )
            fig_tipo_pista.update_layout(template='plotly_dark')
            st.plotly_chart(fig_tipo_pista)
        else:
            st.warning("Coluna 'tipo_pista' não encontrada no arquivo.")

    col_esq, col_central, col_dir = st.columns([0.5, 5, 0.5])
    with col_central:
        if 'causa_acidente' in df.columns:
            # Usando o método do controller para pegar o top N (ex: top 15)
            causa_acidente = controller.get_dados_agrupados(df, 'causa_acidente', top_n=15)
            causa_acidente.columns = ['Causa do Acidente', 'Número de Casos'] # Renomeia para o gráfico

            fig = px.treemap(
                causa_acidente, path=['Causa do Acidente'], values='Número de Casos',
                color='Número de Casos', color_continuous_scale=rocket_palette,
                title=f'Causas de Acidentes no Pará ({ano})'
            )
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Coluna 'causa_acidente' não encontrada no arquivo.")