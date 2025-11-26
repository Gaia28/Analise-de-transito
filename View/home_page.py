import streamlit as st


def render():
    st.header("👥 Cliente e Contexto")
    st.subheader(
        "Informações sobre o cliente, fonte de dados, ferramentas utilizadas e entre outros.")
    st.markdown("Fonte dos dados: [Dados abertos PRF](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf)")
    st.text(
        "Desenvolvido por: Kemmily Riany, Letícia Keller, Matheus Gaia e Raphael Valentin")
    st.write("Este projeto tem como objetivo analisar os dados de acidentes de trânsito no estado do Pará entre os anos de 2023 e 2025. E fornecendo métodos para visualização de dados do usuário, "
             "buscamos identificar padrões e tendências que possam contribuir para a melhoria da segurança viária na região. Os dados foram coletados a partir de registros oficiais de acidentes de trânsito fornecidos pelo Detran-PA,"
             " abrangendo informações detalhadas sobre os incidentes, incluindo localização, causas, condições climáticas e características dos envolvidos. Segue então duas análises principais: visualização de dados e análise de dados. E ainda, disponibilizamos análises específicas como acidentes por município, classificações e período.")
    st.text("As ferramentas utilizadas incluem Streamlit para a criação da interface web, Pandas para manipulação de dados, Plotly e Matplotlib para visualizações gráficas, SQLite como banco de dados .")
    st.markdown(
        "## Selecione uma opção no menu lateral para explorar diferentes análises correspondentes aos anos de 2023-2025.")
