# Projeto de Análise de Transito nas rodovias do Pará
O projeto consiste em uma Dashboard dinâmica para análise de dados sobre acidentes de Trânsito com base nos Dados Abertos da PRF.
O principal objetivo desse projeto é expôr uma visão geral acerca dos acidentes nas rodovias do estado e proporcionar insights para mitigar tais problemas.

## Principais Funcionalidades
- Upload de Dados: Interface para carregar até 3 planilhas (.csv ou .xlsx) simultaneamente.

- Validação de Dados: O sistema verifica se já existem dados para o ano da planilha (extraído do nome do arquivo) e solicita confirmação do usuário antes de sobrescrever.

- Armazenamento Otimizado: Os dados processados são salvos em bancos de dados SQLite locais, separados por ano para melhor performance e organização.

- Dashboard de KPIs: Apresenta métricas gerais como Total de Acidentes, Total de Mortes e Feridos Graves.

- Análises Visuais: Gráficos interativos para:

    - Top 10 causas de acidentes.

    - Top 10 municípios com mais acidentes.

    - Tipos de acidente e classificação de gravidade.

    - Análise de acidentes por período (mês e dia da semana).

## Tecnologias utilizadas
- Python: Linguagem principal do projeto.
- Streamlit: Framework principal para a construção da interface web.
- Pandas: Para leitura, manipulação e processamento dos dados das planilhas.
- Plotly: Para a criação dos gráficos interativos.
- SQLite3: Banco de dados SQL leve para armazenamento dos dados processados.
- Streamlit Option Menu: Para a criação do menu de navegação na barra lateral.


## Estrutura do Projeto (MVC)

O projeto segue o padrão arquitetural **Model-View-Controller (MVC)** para garantir organização e facilidade de manutenção:
```
/
├── controller/ # Lógica de negócios e orquestração
│ └── AcidenteController.py

├── data/ # Diretório onde os bancos de dados (.db) são salvos

├── model/ # Acesso e manipulação de dados (DAO)
│ └── AcidenteModel.py

├── view/ # Interfaces gráficas (páginas da aplicação)
 ├── components/ # Componentes reutilizáveis da interface
  └── sidebar.py # Lógica da barra lateral e menu de navegação
 ├── classificacao_page.py
 ├── dashboard_page.py
 ├── home_page.py
 ├── municipio_page.py
 ├── periodo_page.py
 └── upload_page.py

├── index.py # Ponto de entrada da aplicação (Router)
└── requirements.txt # Lista de dependências do projeto
```
##  Como Executar (Sem Ambiente Virtual)

1.  **Clone o repositório:**
    ```bash
    git clone https://[URL-DO-SEU-REPOSITORIO-GIT]
    cd Analise-de-transito
    ```

2.  **Instale as dependências:**
    (Certifique-se de ter o `pip` instalado e acessível no seu terminal)
    ```bash
    pip install -r requirements.txt
    ```
    Isso instalará `streamlit`, `pandas`, `plotly` e `streamlit-option-menu`.

3.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run index.py
    ```
    A aplicação será aberta automaticamente no seu navegador.
##  Equipe

Este projeto foi desenvolvido por:

* Kemmily Riany
* Letícia Keller
* Matheus Gaia
* Raphael Valentin
* João Pedro
