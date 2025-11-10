import streamlit as st
import plotly.express as px
import pandas as pd

def render(df, ano, rocket_palette):
    st.header("Análise de Acidentes por Município")
    
    if df.empty:
        st.warning("Não há dados para exibir. Selecione um ano na barra lateral ou carregue dados primeiro.")
        return

    st.write(f"Esta seção apresenta uma análise dos acidentes de trânsito no Pará para o ano de {ano}, categorizados pelos municípios com mais acidentes registrados.")
    
    top_municipios = df['municipio'].value_counts().nlargest(10)
    df_grafico = pd.DataFrame({'municipio': top_municipios.index, 'acidentes': top_municipios.values})

    fig = px.bar(df_grafico, x='municipio', y='acidentes', title=f"10 Municípios Com Mais Acidentes no Pará ({ano})",
                 color='municipio', color_discrete_sequence=rocket_palette,
                 category_orders={'municipio': df_grafico['municipio'].tolist()},
                 template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)