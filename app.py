import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
from controller.AcidenteController import AcidenteController
import re
import os

# Instancia o controller que gerencia a lógica do banco de dados
controller = AcidenteController()

st.set_page_config(page_title="Projeto Big Data - Análise de Acidentes de Trânsito no Pará",
                   page_icon=":car:", layout="wide")

# Inicializa um DataFrame vazio. Ele será preenchido na barra lateral.
df = pd.DataFrame()
ano_selecionado = "Nenhum"

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    selected = option_menu(
        menu_title="Projeto Big Data",
        options=["Home", "Análise de dados", "Visualização de Dados",
                 "Acidentes por município", "Classificações", "Período"],
        # Ícone de "Upload" para a página de "Análise de dados"
        icons=["house", "cloud-upload", "bar-chart", "map", "list", "calendar"],
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

    # --- LÓGICA DE SELEÇÃO DE DADOS UNIFICADA ---
    # Se a página selecionada NÃO for "Home" ou "Análise de dados" (upload),
    # mostra a seleção de banco de dados.
    if selected not in ["Home", "Análise de dados"]:
        # Busca os arquivos .db disponíveis na pasta /data
        bancos_de_dados = controller.listar_bancos_de_dados()
        
        if not bancos_de_dados:
            st.warning("Nenhum banco de dados encontrado. Carregue dados na página 'Análise de dados'.")
        else:
            # Menu para selecionar qual banco de dados analisar
            nome_banco_selecionado = st.selectbox(
                "Selecione o ano para Análise:",
                options=bancos_de_dados,
                format_func=lambda x: f"Analisar {re.search(r'\d{4}', x).group(0) if re.search(r'\d{4}', x) else x}"
            )
            
            # Carrega o DataFrame do banco de dados selecionado
            if nome_banco_selecionado:
                df = controller.listar_dados_por_banco(nome_banco_selecionado)
                ano_selecionado = re.search(r'\d{4}', nome_banco_selecionado).group(0) if re.search(r'\d{4}', nome_banco_selecionado) else "Ano Desconhecido"

    # Paleta de cores (mantida do seu código)
    rocket_palette = [
        "#160141", "#260446", "#3A0453", "#66135C", "#792860", "#A53950", "#a54848", "#A06444", "#9E7E42", "#AC973C"
    ]

# --- FIM DA BARRA LATERAL ---


# --- PÁGINA INICIAL ---
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

# --- PÁGINA DE UPLOAD (Análise de dados) ---
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
                1.  **Carregue os Dados:** Nesta tela, você poderá carregar até 3 planilhas
                    (.csv ou .xlsx) contendo os registros de acidentes.
                2.  **Geração do Banco:** O sistema irá processar os dados, filtrar pelo Pará (PA)
                    e salvar um arquivo de banco de dados (`.db`) na pasta `data/` para cada ano.
                3.  **Visualize as Análises:** Use as outras abas no menu lateral 
                    (Visualização de Dados, Municípios, etc.) para ver os gráficos.
            """
        )

    st.info(
        "Carregue as planilhas para análise. Um banco de dados será criado para cada ano, "
        "nomeie o arquivo com o ano respectivo (ex: 'dados_2022.csv').")

    # Lógica de validação e upload que criamos anteriormente
    if 'confirmation_state' not in st.session_state:
        st.session_state.confirmation_state = {}

    if "uploads" not in st.session_state:
        st.session_state["uploads"] = [None]

    novos_uploads = []
    # controller já foi instanciado globalmente

    for i, file in enumerate(st.session_state.get("uploads", [None])):
        uploaded_file = st.file_uploader(
            f"Planilha {i+1}",
            type=["csv", "xlsx"],
            key=f"upload_{i}"
        )
        novos_uploads.append(uploaded_file)

        if uploaded_file is not None:
            st.markdown("---")
            ano = controller.extrair_ano_do_nome(uploaded_file.name)
            
            if not ano:
                st.error(f"Não foi possível extrair um ano (4 dígitos) do nome do arquivo '{uploaded_file.name}'.")
                continue

            db_path_esperado = f"data/acidentes_{ano}.db"
            db_existe = os.path.exists(db_path_esperado)

            # Função auxiliar para processar o arquivo
            def processar_arquivo(arquivo_para_processar):
                with st.spinner(f"Processando e salvando dados de {ano}..."):
                    try:
                        df_pa, db_path = controller.processar_planilha(arquivo_para_processar)
                        st.success(f"Sucesso! Dados para o ano de {ano} foram salvos em '{db_path}'.")
                        with st.expander("Ver amostra dos dados carregados (UF=PA)"):
                            st.dataframe(df_pa.head())
                    except Exception as e:
                        st.error(e)
            
            # Lógica de confirmação
            if db_existe and st.session_state.confirmation_state.get(i) is None:
                st.warning(f"⚠️ Já existem dados para o ano de {ano}. Deseja sobrescrevê-los com o arquivo '{uploaded_file.name}'?")
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("Sim, sobrescrever", key=f"overwrite_{i}"):
                        st.session_state.confirmation_state[i] = 'overwrite'
                        st.rerun()
                with col2:
                    if st.button("Não, cancelar", key=f"cancel_{i}"):
                        st.session_state.confirmation_state[i] = 'cancel'
                        st.rerun()
            
            # Se a decisão foi "sobrescrever"
            elif st.session_state.confirmation_state.get(i) == 'overwrite':
                processar_arquivo(uploaded_file)
                st.session_state.confirmation_state[i] = 'done'
            
            # Se a decisão foi "cancelar"
            elif st.session_state.confirmation_state.get(i) == 'cancel':
                st.info(f"Operação para o arquivo '{uploaded_file.name}' cancelada.")
                st.session_state.confirmation_state[i] = 'done'
            
            # Se o banco de dados não existe, processa diretamente
            elif not db_existe:
                 processar_arquivo(uploaded_file)
                 st.session_state.confirmation_state[i] = 'done' # Marca como feito para não reprocessar

    # Limpa o estado de confirmação se o arquivo for removido
    for i in list(st.session_state.confirmation_state.keys()):
        if i >= len(novos_uploads) or novos_uploads[i] is None:
            del st.session_state.confirmation_state[i]

    # Adiciona novo campo de upload se necessário
    if len(st.session_state.get("uploads", [])) > 0 and st.session_state["uploads"][-1] is not None:
        if len(st.session_state["uploads"]) < 3:
            novos_uploads.append(None)

    st.session_state["uploads"] = novos_uploads
    
    # Remove a visualização de dados duplicada desta página
    st.markdown("---")
    st.header(" Visualização dos Dados Salvos")
    st.info("Para visualizar os dados salvos e gerar relatórios, acesse as outras abas no menu lateral (ex: 'Visualização de Dados').")


# --- PÁGINA DE DASHBOARD (Visualização de Dados) ---
elif selected == "Visualização de Dados":
    st.title(" Dashboard de Visualização")
    st.markdown("---")

    # Verifica se o DataFrame (carregado na sidebar) está vazio
    if df.empty:
        st.warning("Não há dados para exibir. Selecione um ano na barra lateral ou carregue uma planilha na página 'Análise de dados'.")
    else:
        st.header(f"Análise Detalhada - {ano_selecionado}")
        
        # --- MÉTRICAS GERAIS (KPIs) ---
        st.subheader("Visão Geral do Ano")
        metricas = controller.get_metricas_gerais(df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Acidentes", f"{metricas['total_acidentes']:,}".replace(",", "."))
        col2.metric("Total de Mortes", f"{metricas['total_mortos']:,}".replace(",", "."))
        col3.metric("Feridos Graves", f"{metricas['total_feridos_graves']:,}".replace(",", "."))
        col4.metric("Veículos Envolvidos", f"{metricas['total_veiculos']:,}".replace(",", "."))

        st.markdown("---")

        # --- GRÁFICOS ---
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


# --- PÁGINA DE MUNICÍPIOS ---
elif selected == "Acidentes por município":
    st.header("Análise de Acidentes por Município")
    
    # Verifica se o df carregado na sidebar está vazio
    if df.empty:
        st.warning("Não há dados para exibir. Selecione um ano na barra lateral ou carregue dados primeiro.")
    else:
        st.write(f"Esta seção apresenta uma análise dos acidentes de trânsito no Pará para o ano de {ano_selecionado}, categorizados pelos municípios com mais acidentes registrados.")
        
        # Lógica de análise (usa o 'df' do SQLite)
        top_municipios = df['municipio'].value_counts().nlargest(10)
        df_grafico = pd.DataFrame({'municipio': top_municipios.index, 'acidentes': top_municipios.values})

        fig = px.bar(df_grafico, x='municipio', y='acidentes', title=f"10 Municípios Com Mais Acidentes no Pará ({ano_selecionado})",
                     color='municipio', color_discrete_sequence=rocket_palette,
                     category_orders={'municipio': df_grafico['municipio'].tolist()},
                     template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)


# --- PÁGINA DE CLASSIFICAÇÕES ---
elif selected == "Classificações":
    st.header("Análise de Acidentes por Classificação")

    if df.empty:
        st.warning("Não há dados para exibir. Selecione um ano na barra lateral ou carregue dados primeiro.")
    else:
        st.write(f"Esta seção apresenta uma análise dos acidentes de trânsito no Pará para o ano de {ano_selecionado}, categorizados por diferentes classificações.")
        st.subheader("Acidentes por Tipo")

        # Gráfico principal: Tipos de Acidentes (usa o 'df' do SQLite)
        col_esq, col_central, col_dir = st.columns([0.5, 5, 0.5])
        with col_central:
            if 'tipo_acidente' in df.columns:
                tipo = df['tipo_acidente'].value_counts().reset_index()
                tipo.columns = ['Tipo de Acidente', 'Número de Acidentes']
                tipo = tipo.sort_values(by='Número de Acidentes', ascending=False)
                fig_tipo = px.bar(
                    tipo, x='Tipo de Acidente', y='Número de Acidentes',
                    title=f"Tipos de Acidentes no Pará ({ano_selecionado})",
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
                    title=f"Classificação de Acidentes por gravidade ({ano_selecionado})",
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
                    title=f"Tipo de Pista nos Acidentes ({ano_selecionado})",
                    color='Tipo de Pista', color_discrete_sequence=rocket_palette
                )
                fig_tipo_pista.update_layout(template='plotly_dark')
                st.plotly_chart(fig_tipo_pista)
            else:
                st.warning("Coluna 'tipo_pista' não encontrada no arquivo.")

        col_esq, col_central, col_dir = st.columns([0.5, 5, 0.5])
        with col_central:
            if 'causa_acidente' in df.columns:
                causa_acidente = df['causa_acidente'].value_counts().reset_index()
                causa_acidente.columns = ['Causa do Acidente', 'Número de Casos']
                fig = px.treemap(
                    causa_acidente, path=['Causa do Acidente'], values='Número de Casos',
                    color='Número de Casos', color_continuous_scale=rocket_palette,
                    title=f'Causas de Acidentes no Pará ({ano_selecionado})'
                )
                fig.update_layout(template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Coluna 'causa_acidente' não encontrada no arquivo.")


# --- PÁGINA DE PERÍODO ---
elif selected == "Período":
    st.header("Análise de Acidentes por Período")
    
    if df.empty:
        st.warning("Não há dados para exibir. Selecione um ano na barra lateral ou carregue dados primeiro.")
    else:
        st.write(f"Esta seção apresenta uma análise dos acidentes de trânsito no Pará para o ano de {ano_selecionado}, categorizados por diferentes períodos.")
        
        # --- NOVA LÓGICA DE ANÁLISE (usando 'df' do SQLite) ---
        
        # Gráfico de Acidentes por Mês
        st.subheader(f"Acidentes por Mês ({ano_selecionado})")
        if 'data_inversa' in df.columns:
            try:
                # Converte a coluna para datetime
                df_periodo = df.copy()
                df_periodo['data_inversa'] = pd.to_datetime(df_periodo['data_inversa'])
                df_periodo['mes'] = df_periodo['data_inversa'].dt.month
                
                # Agrupa por mês e conta
                acidentes_por_mes = df_periodo.groupby('mes').size().reset_index(name='Total de Acidentes')
                
                # Mapeia números de mês para nomes em Português
                meses_pt = {
                    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
                }
                acidentes_por_mes['Mês'] = acidentes_por_mes['mes'].map(meses_pt)
                acidentes_por_mes = acidentes_por_mes.set_index('mes').reindex(range(1, 13)).reset_index()
                acidentes_por_mes['Mês'] = acidentes_por_mes['mes'].map(meses_pt) # Reaplica o map
                acidentes_por_mes = acidentes_por_mes.fillna(0) # Preenche meses sem acidentes

                fig_mes = px.line(acidentes_por_mes, x='Mês', y='Total de Acidentes',
                                  title=f"Acidentes por Mês ({ano_selecionado})", markers=True,
                                  labels={'Mês': 'Mês', 'Total de Acidentes': 'Total de Acidentes'})
                fig_mes.update_layout(template='plotly_dark')
                st.plotly_chart(fig_mes, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao analisar data_inversa: {e}")
        else:
            st.warning("Coluna 'data_inversa' não encontrada para análise por mês.")

        # Gráfico de Acidentes por Dia da Semana
        st.subheader(f"Acidentes por Dia da Semana ({ano_selecionado})")
        if 'dia_semana' in df.columns:
            # Ordem correta dos dias
            dias_ordem = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
            dias_pt = {
                'segunda-feira': 'Segunda', 'terça-feira': 'Terça', 'quarta-feira': 'Quarta',
                'quinta-feira': 'Quinta', 'sexta-feira': 'Sexta', 'sábado': 'Sábado', 'domingo': 'Domingo'
            }
            
            acidentes_por_dia = df['dia_semana'].value_counts().reindex(dias_ordem).reset_index()
            acidentes_por_dia.columns = ['Dia da Semana', 'Total de Acidentes']
            acidentes_por_dia['Dia da Semana'] = acidentes_por_dia['Dia da Semana'].map(dias_pt)

            fig_dia = px.bar(acidentes_por_dia.dropna(), x='Dia da Semana', y='Total de Acidentes',
                             title=f"Acidentes por Dia da Semana ({ano_selecionado})",
                             color='Dia da Semana', color_discrete_sequence=rocket_palette,
                             category_orders={'Dia da Semana': dias_pt.values()})
            fig_dia.update_layout(template='plotly_dark')
            st.plotly_chart(fig_dia, use_container_width=True)
        else:
            st.warning("Coluna 'dia_semana' não encontrada para análise por dia da semana.")