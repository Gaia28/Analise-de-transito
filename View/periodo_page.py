import streamlit as st
import plotly.express as px
import pandas as pd


def render(df, ano, rocket_palette):
    st.header("Análise de Acidentes por Período")

    if df.empty:
        st.warning(
            "Não há dados para exibir. Selecione um ano na barra lateral ou carregue dados primeiro.")
        return

    st.write(
        f"Esta seção apresenta uma análise dos acidentes de trânsito no Pará para o ano de {ano}, categorizados por diferentes períodos.")
    st.subheader(f"Categorização dos Acidentes")
    if 'data_inversa' in df.columns:
        try:
            df_periodo = df.copy()
            df_periodo['data_inversa'] = pd.to_datetime(
                df_periodo['data_inversa'])
            df_periodo['mes'] = df_periodo['data_inversa'].dt.month

            acidentes_por_mes = df_periodo.groupby(
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
                              title=f"Decorrência dos Meses de ({ano})", markers=True,
                              labels={
                                  'Mês': 'Mês', 'Total de Acidentes': 'Total de Acidentes'},
                              color_discrete_sequence=["#590B7E"])
            fig_mes.update_layout(template='plotly_dark')
            st.plotly_chart(fig_mes, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao analisar data_inversa: {e}")
    else:
        st.warning("Coluna 'data_inversa' não encontrada para análise por mês.")

    st.markdown("---")
    if 'dia_semana' in df.columns:
        dias_ordem = ['segunda-feira', 'terça-feira', 'quarta-feira',
                      'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
        dias_pt = {
            'segunda-feira': 'Segunda', 'terça-feira': 'Terça', 'quarta-feira': 'Quarta',
            'quinta-feira': 'Quinta', 'sexta-feira': 'Sexta', 'sábado': 'Sábado', 'domingo': 'Domingo'
        }

        acidentes_por_dia = df['dia_semana'].value_counts().reindex(
            dias_ordem).reset_index()
        acidentes_por_dia.columns = ['Dia da Semana', 'Total de Acidentes']
        acidentes_por_dia['Dia da Semana'] = acidentes_por_dia['Dia da Semana'].map(
            dias_pt)

        fig_dia = px.bar(acidentes_por_dia.dropna(), x='Dia da Semana', y='Total de Acidentes',
                         title=f"Decorrência por Dia da Semana de ({ano})",
                         color='Dia da Semana', color_discrete_sequence=rocket_palette['discrete'],
                         category_orders={'Dia da Semana': list(dias_pt.values())})
        fig_dia.update_layout(template='plotly_dark')
        st.plotly_chart(fig_dia, use_container_width=True)
    else:
        st.warning(
            "Coluna 'dia_semana' não encontrada para análise por dia da semana.")

    st.markdown("---")

    # Verifica se a coluna existe
    if "condicao_metereologica" not in df.columns:
        st.warning(
            "A coluna 'condicao_metereologica' não está disponível no dataset.")
    else:
        dados_clima = (
            df["condicao_metereologica"]
            .value_counts()
            .reset_index()
        )
        dados_clima.columns = ["Condição Meteorológica", "Total de Acidentes"]

        fig_clima = px.bar(
            dados_clima,
            y="Condição Meteorológica",
            x="Total de Acidentes",
            orientation="h",
            text="Total de Acidentes",
            color="Condição Meteorológica",
            color_discrete_sequence=rocket_palette['discrete'],
            title=f"Acidentes por Condição Meteorológica ({ano})",
            template="plotly_dark"
        )

        fig_clima.update_traces(textposition="outside")
        fig_clima.update_layout(yaxis=dict(title=""))

        st.plotly_chart(fig_clima, use_container_width=True)
