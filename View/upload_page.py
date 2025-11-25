import streamlit as st
import os

def render(controller):
    st.header("Área de Análise e Carregamento de Dados")
    st.markdown(
        """
        Aqui está disponivel a geração de relatórios. Siga os passos abaixo para fazer sua análise:
        """
    )
    with st.expander("Como funciona?"):
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

    if 'confirmation_state' not in st.session_state:
        st.session_state.confirmation_state = {}

    if "uploads" not in st.session_state:
        st.session_state["uploads"] = [None]

    novos_uploads = []

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

            def processar_arquivo(arquivo_para_processar):
                with st.spinner(f"Processando e salvando dados de {ano}..."):
                    try:
                        df_pa, db_path = controller.processar_planilha(arquivo_para_processar)
                        st.success(f"Sucesso! Dados para o ano de {ano} foram salvos em '{db_path}'.")
                        with st.expander("Ver amostra dos dados carregados (UF=PA)"):
                            st.dataframe(df_pa.head())
                    except Exception as e:
                        st.error(e)
            
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
            
            elif st.session_state.confirmation_state.get(i) == 'overwrite':
                processar_arquivo(uploaded_file)
                st.session_state.confirmation_state[i] = 'done'
            
            elif st.session_state.confirmation_state.get(i) == 'cancel':
                st.info(f"Operação para o arquivo '{uploaded_file.name}' cancelada.")
                st.session_state.confirmation_state[i] = 'done'
            
            elif not db_existe:
                 processar_arquivo(uploaded_file)
                 st.session_state.confirmation_state[i] = 'done'

    for i in list(st.session_state.confirmation_state.keys()):
        if i >= len(novos_uploads) or novos_uploads[i] is None:
            del st.session_state.confirmation_state[i]

    if len(st.session_state.get("uploads", [])) > 0 and st.session_state["uploads"][-1] is not None:
        if len(st.session_state["uploads"]) < 3:
            novos_uploads.append(None)

    st.session_state["uploads"] = novos_uploads