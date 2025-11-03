import streamlit as st  # construir dashboards
from streamlit_option_menu import option_menu  # menu de navegação
import pandas as pd  # manipulação de dados
import plotly.express as px  # construir graficos
from controller.AcidenteController import AcidenteController
import re  # para expressões regulares

controller = AcidenteController()

st.set_page_config(page_title="Projeto Big Data - Análise de Acidentes de Trânsito no Pará",
                   page_icon=":car:", layout="wide")

with st.sidebar:
    selected = option_menu(
        menu_title="Projeto Big Data",
        options=["Home", "Análise de dados", "Visualização de Dados",
                 "Acidentes por município", "Classificações", "Período"],
        icons=["house", "bar-chart", "bar-chart", "map", "list", "calendar"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important"},
            "icon": {"color": "#541a83e6", "font-size": "25px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#8A87871F",
            },
            "nav-link-selected": {"background-color": "#8A87871F"},
        }
    )

# Carregar dados
    arquivos_anos = {
        "2023": "datatran2023.csv",
        "2024": "datatran2024.csv",
        "2025": "datatran2025.csv"
    }
    anos = list(arquivos_anos.keys())
    ano_selecionado = st.selectbox("Selecione o ano", anos)
    arquivo_selecionado = arquivos_anos[ano_selecionado]
    df = pd.read_csv(arquivo_selecionado, sep=';',
                     encoding='latin1', low_memory=False)
    multselected_anos = st.multiselect(
        "Selecione os anos para análise comparativa", anos, default=anos)
    # Define uma paleta de cores personalizada
    rocket_palette = [
        "#160141", "#260446", "#3A0453", "#66135C", "#792860", "#A53950", "#a54848", "#A06444", "#9E7E42", "#AC973C"
    ]
# Página inicial
if selected == "Home":
    st.header("👥Cliente e Contexto")
    st.subheader(
        "Informações sobre o cliente, fonte de dados, ferramentas utilizadas e entre outros.")
    st.markdown("Fonte dos dados: [Detran-PA](https://www.detran.pa.gov.br/)")
    st.text("Desenvolvido por: Kemmily Riany, Letícia Keller, Matheus Gaia, Raphael Valentin e João Pedro")
    st.write("Este projeto tem como objetivo analisar os dados de acidentes de trânsito no estado do Pará entre os anos de 2023 e 2025. E fornecendo métodos para visualização de dados do usuário, "
             "buscamos identificar padrões e tendências que possam contribuir para a melhoria da segurança viária na região. Os dados foram coletados a partir de registros oficiais de acidentes de trânsito fornecidos pelo Detran-PA,"
             " abrangendo informações detalhadas sobre os incidentes, incluindo localização, causas, condições climáticas e características dos envolvidos. Segue então duas análises principais: visualização de dados e análise de dados. E ainda, disponibilizamos análises específicas como acidentes por município, classificações e período.")
    st.text("As ferramentas utilizadas incluem Streamlit para a criação da interface web, Pandas para manipulação de dados, Plotly e Matplotlib para visualizações gráficas, SQLite como banco de dados .")
    st.markdown(
        "## Selecione uma opção no menu lateral para explorar diferentes análises correspondentes aos anos de 2023-2025.")

elif selected == "Análise de dados":
    st.title("Área de Análise de Acidentes")

    st.markdown(
        """
        Aqui está disponivel a geração de relatórios. Siga os passos abaixo para fazer sua análise:

        """
    )
    with st.expander(" Como funciona?"):
        st.info(
            """
                1.  **Carregue os Dados:** Na tela de análise, você poderá carregar até 3 planilhas
                    (.csv ou .xlsx) contendo os registros de acidentes.
                2.  **Visualize os Gráficos:** O sistema irá processar os dados e gerar
                    gráficos interativos sobre as principais causas, locais e características dos acidentes.
                3.  **Obtenha Insights:** Com base nas análises, identifique os pontos críticos e
                    planeje ações preventivas, como melhorias na via ou aumento da fiscalização.
                """
        )

    st.info(
        "Carregue as planilhas para análise. Um banco de dados será criado para cada ano, "
        "nomeie o arquivo com o ano respectivo para que não haja repetições/confusões (ex: 'dados_2022.csv').")

    if "uploads" not in st.session_state:
        st.session_state["uploads"] = [None]

    novos_uploads = []
    controller = AcidenteController()

    for i, file in enumerate(st.session_state["uploads"]):
        uploaded_file = st.file_uploader(
            f"Planilha {i+1}",
            type=["csv", "xlsx"],
            key=f"upload_{i}"
        )
        novos_uploads.append(uploaded_file)

        if uploaded_file is not None:
            with st.expander(f"Analisando Planilha: {uploaded_file.name}", expanded=True):
                try:
                    df_pa, db_path = controller.processar_planilha(
                        uploaded_file)
                    st.success(f"Sucesso! Dados salvos em '{db_path}'.")
                    st.write("Amostra dos dados carregados (UF=PA):")
                    st.dataframe(df_pa.head())
                except Exception as e:
                    st.error(e)

    if len(st.session_state["uploads"]) > 0 and st.session_state["uploads"][-1] is not None:
        if len(st.session_state["uploads"]) < 3:
            novos_uploads.append(None)

    st.session_state["uploads"] = novos_uploads

    st.markdown("---")
    st.header(" Visualização dos Dados Salvos")

    bancos_de_dados = controller.listar_bancos_de_dados()

    if not bancos_de_dados:
        st.warning(
            "Nenhum banco de dados encontrado. Carregue uma planilha para começar.")
    else:
        st.subheader("Bancos de Dados Disponíveis:")
        num_cols = 3
        cols = st.columns(num_cols)
        for i, nome_banco in enumerate(bancos_de_dados):
            with cols[i % num_cols]:
                if st.button(f"Ver dados de {nome_banco}", key=nome_banco, use_container_width=True):
                    st.session_state['df_visualizar'] = controller.listar_dados_por_banco(
                        nome_banco)
                    st.session_state['banco_visualizar'] = nome_banco

    if 'df_visualizar' in st.session_state:
        st.subheader(
            f"Visualizando dados de: {st.session_state['banco_visualizar']}")
        df_view = st.session_state['df_visualizar']
        if df_view.empty:
            st.warning(
                "Não há dados para exibir para a UF='PA' neste banco de dados.")
        else:
            st.dataframe(df_view)


elif selected == "Visualização de Dados":
    st.title(" Dashboard de Visualização")
    st.markdown("---")

    controller = AcidenteController()
    bancos_de_dados = controller.listar_bancos_de_dados()

    if not bancos_de_dados:
        st.warning("Nenhum banco de dados foi encontrado na pasta /data.")
        st.info(
            "Por favor, vá para a aba 'Análise de Dados' para fazer o upload de uma planilha primeiro.")
    else:
        st.header("Selecione o ano para análise:")
        nome_banco_selecionado = st.selectbox(
            "Selecione o banco de dados:",
            options=bancos_de_dados,
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
            else:
                # --- MÉTRICAS GERAIS (KPIs) ---
                st.subheader("Visão Geral do Ano")
                metricas = controller.get_metricas_gerais(df)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total de Acidentes",
                            f"{metricas['total_acidentes']:,}".replace(",", "."))
                col2.metric("Total de Mortes",
                            f"{metricas['total_mortos']:,}".replace(",", "."))
                col3.metric(
                    "Feridos Graves", f"{metricas['total_feridos_graves']:,}".replace(",", "."))
                col4.metric("Veículos Envolvidos",
                            f"{metricas['total_veiculos']:,}".replace(",", "."))

                st.markdown("---")

                # --- GRÁFICOS ---
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Top 10 Causas de Acidentes")
                    causas = controller.get_dados_agrupados(
                        df, 'causa_acidente', top_n=10)
                    if not causas.empty:
                        fig_causas = px.bar(
                            causas,
                            x='total_acidentes',
                            y='causa_acidente',
                            orientation='h',
                            title="Principais Causas",
                            color='causa_acidente',
                            color_discrete_sequence=rocket_palette  # sua paleta personalizada
                        )
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
                        fig_municipios = px.bar(
                            municipios,
                            x='total_acidentes',
                            y='municipio',
                            orientation='h',
                            title="Municípios com Mais Acidentes",
                            color='municipio',
                            color_discrete_sequence=rocket_palette
                        )
                        fig_municipios.update_layout(
                            yaxis={'categoryorder': 'total ascending'})
                        st.plotly_chart(
                            fig_municipios, use_container_width=True)
                    else:
                        st.warning("Coluna 'municipio' não encontrada.")


elif selected == "Acidentes por município":
    st.header("Análise de Acidentes por Município")
    st.write("Esta seção apresenta uma análise dos acidentes de trânsito no Pará, categorizados pelos municípios com mais acidentes registrados.")

    # Filtrar apenas registros do estado do Pará (uf == 'PA').
    # Trata tanto 'uf' quanto 'UF', se presente.
    if 'uf' in df.columns:
        df = df[df['uf'] == 'PA']
    elif 'UF' in df.columns:
        df = df[df['UF'] == 'PA']
    top_municipios = df['municipio'].value_counts().nlargest(10)
    df_grafico = pd.DataFrame(
        {'municipio': top_municipios.index, 'acidentes': top_municipios.values})

    fig = px.bar(df_grafico, x='municipio', y='acidentes', title=f"10 Municípios Com Mais Acidentes no Pará ({ano_selecionado})",
                 color='municipio', color_discrete_sequence=rocket_palette,
                 category_orders={
                     'municipio': df_grafico['municipio'].tolist()},
                 template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Classificações":
    st.header("Análise de Acidentes por Classificação")
    st.write("Esta seção apresenta uma análise dos acidentes de trânsito no Pará, categorizados por diferentes classificações como tipo de acidente, gravidade e condição da via.")
    st.subheader("Acidentes por Tipo")
    if 'uf' in df.columns:
        df = df[df['uf'] == 'PA']
    elif 'UF' in df.columns:
        df = df[df['UF'] == 'PA']

    # Gráfico principal: Tipos de Acidentes
    col_esq, col_central, col_dir = st.columns(
        [0.5, 5, 0.5])  # mais largura pro meio
    with col_central:
        # Verifica se a coluna existe
        if 'tipo_acidente' in df.columns:
            # Agrupa os dados por tipo de acidente
            tipo = df['tipo_acidente'].value_counts().reset_index()
            tipo.columns = ['Tipo de Acidente', 'Número de Acidentes']
            tipo = tipo.sort_values(by='Número de Acidentes', ascending=False)

            # Gráfico de barras
            fig_tipo = px.bar(
                tipo,
                x='Tipo de Acidente',
                y='Número de Acidentes',
                title=f"Tipos de Acidentes no Pará ({ano_selecionado})",
                color='Tipo de Acidente',
                color_discrete_sequence=rocket_palette,
            )

            fig_tipo.update_layout(template='plotly_dark')

            st.plotly_chart(fig_tipo)
        else:
            st.warning("Coluna 'tipo_acidente' não encontrada no arquivo.")

    # Espaço entre seções
    st.markdown("---")

    # Gráficos secundários lado a lado
    st.markdown("### Outros Detalhes dos Acidentes")
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # Verifica se a coluna existe
    with col1:
        if 'classificacao_acidente' in df.columns:
            # Agrupa os dados por classificação
            classificacao = df['classificacao_acidente'].value_counts(
            ).reset_index()
            classificacao.columns = ['Classificação', 'Número de Acidentes']

            # Gráfico de pizza
            fig_classificacao = px.pie(
                classificacao,
                names='Classificação',
                values='Número de Acidentes',
                title=f"Classificação de Acidentes no Pará por gravidade ({ano_selecionado})",
                color='Classificação',
                color_discrete_sequence=rocket_palette,
                hole=0.3  # pizza com buraco no centro
            )

            fig_classificacao.update_traces(
                textposition='inside', textinfo='percent+label')
            fig_classificacao.update_layout(template='plotly_dark')
            fig_classificacao.update_layout(xaxis_tickangle=-45)

            st.plotly_chart(fig_classificacao, use_container_width=True)
        else:
            st.warning(
                "Coluna 'classificacao_acidente' não encontrada no arquivo.")

    with col2:
        if 'tipo_pista' in df.columns:
            tipo_pista = df['tipo_pista'].value_counts().reset_index()
            tipo_pista.columns = ['Tipo de Pista', 'Número de Acidentes']

            fig_tipo_pista = px.bar(
                tipo_pista,
                x='Tipo de Pista',
                y='Número de Acidentes',
                title=f"Tipo de Pista nos Acidentes no Pará ({ano_selecionado})",
                color='Tipo de Pista',
                color_discrete_sequence=rocket_palette,
            )

            fig_tipo_pista.update_layout(template='plotly_dark')

            st.plotly_chart(fig_tipo_pista)
        else:
            st.warning("Coluna 'tipo_pista' não encontrada no arquivo.")

    
    col_esq, col_central, col_dir = st.columns([0.5, 5, 0.5])
    with col_central:
        # Agrupar por causa e contar número de casos
        causa_acidente = df['causa_acidente'].value_counts().reset_index()
        causa_acidente.columns = ['Causa do Acidente', 'Número de Casos']

        # Criar treemap
        fig = px.treemap(
            causa_acidente,
            path=['Causa do Acidente'],
            values='Número de Casos',
            color='Número de Casos',
            color_continuous_scale=rocket_palette,
            title=f'Causas de Acidentes no Pará ({ano_selecionado})'
        )
        fig.update_layout(template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)


elif selected == "Período":
    df = pd.read_csv("acidentes_para.csv")
    st.header("Análise de Acidentes por Período")
    st.write("Esta seção apresenta uma análise dos acidentes de trânsito no Pará, categorizados por diferentes períodos incluindo dia, mês e ano, além de interferências do clima.")
    st.subheader("Acidentes por Ano")
