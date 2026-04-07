<div align="center">
  <img src="https://img.icons8.com/color/96/scales.png" alt="Analisador Jurídico IA Logo" width="120">
  <h1 align="center">⚖️ Analisador Jurídico IA</h1>
  <p align="center">
    <strong>Plataforma inteligente para classificação, análise e auditoria de blocos massivos de questões jurídicas utilizando Múltiplos LLMs (GPT-4, Nano e Llama).</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white" alt="Python Version">
    <img src="https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg?logo=streamlit&logoColor=white" alt="Streamlit">
    <img src="https://img.shields.io/badge/SQLite-Database-003B57.svg?logo=sqlite&logoColor=white" alt="SQLite">
    <img src="https://img.shields.io/badge/LLMs-Multi%20Model-8A2BE2.svg" alt="Multi-Model">
  </p>
</div>

---

## 📖 Visão Geral

O **Analisador Jurídico IA** é uma solução construída nativamente com *Streamlit*, desenvolvida estruturar, corrigir e classificar questões e textos atrelados à área jurídica do Direito Brasileiro. 

Através da ingestão de arquivos brutos simulados (concursos, OAB, etc.), o sistema consegue identificar o gabarito correto, deduzir qual é a área de especialidade jurídica principal (ex: *Direito Constitucional, Direito Civil*), prover base legal (leis, jurisprudência) e redigir uma justificativa consubstanciada do porquê determinada escolha está correta ou errada, auditando os resultados via abordagens NLP (`METEOR`) e `LLM-as-a-Judge`.

## ✨ Principais Funcionalidades

- **📥 Ingestão Múltipla**: Suporte unificado para planilhas `.xlsx`, `.csv`, e documentos em `.txt` e `.json`. O motor reconhece e mantém o ordenamento cronológico por IDs.
- **🤖 Análise Multi-Model**: Compare a capacidade analítica simulando contra diversos modelos ao mesmo tempo (ex: `GPT-4o Mini`, `GPT-5.4 Nano`, `Llama-4-Maverick`).
- **📊 Dashboard Dinâmico**: Abas e visualizações com `Plotly` para analisar acurácia das inteligências, gráficos de especialidades e tempo de execução.
- **📏 Métricas de Resumo Crítico**: Avaliação de precisão textual e alinhamento do parecer gerado contra a bibliografia via `METEOR` e Juízes IAs.
- **📄 Geração de Reporte Oficial PDF**: Criação on demand de relatórios formatados em PDF altamente profissionais, que consolidam taxas de insucesso e gabaritos comentados para impressão rápida via `ReportLab`.

---

## 🛠️ Tecnologias Utilizadas

| Componente | Foco Principal | Tecnologia |
| --- | --- | --- |
| **Frontend/App** | Interface Gráfica interativa | 🎨 `Streamlit`, `Plotly Express` |
| **Backend/Processamento** | Parsing Inteligente & Lógica | 🐍 `Python 3`, `Pandas` |
| **Banco de Dados** | Armazenamento de Histórico e Contexto | 📂 `SQLite3` |
| **IA & NLP** | Orquestração Generativa Multimodal | 🧠 `OpenAI SDK`, `httpx`, `NLTK` |
| **Engenharia de PDF** | Renderização Geométrica do Relatório | 📄 `ReportLab` |

---

## 🚀 Como Instalar e Rodar o App

### 1. Pré-Requisitos Gerais
Certifique-se de que sua máquina possui o Python 3.9 (ou superior) instalado com o Pip, para lidar com as ferramentas do ecossistema de Data Science.

### 2. Prepare o Ambiente Virtual (`venv`)

Clone o repositório ou navegue até o diretório da aplicação e crie um ambiente virtual:

```bash
python -m venv .venv
```

Em seguida, ative o seu ambiente nativo do Windows:
```bash
.venv\Scripts\activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```
*(Certifique-se de que pacotes de suporte como plotly, streamlit, pandas, openai e nltk também fiquem alocados)*

### 4. Configuração das Chaves (Environment `dotenv`)
Existe um arquivo oculto chamado `.env` (se não existir, deve ser criado). Ele abrigará toda a ponte da OpenAI/Azure segura.
```env
# ── Exemplo do arquivo .env ──
# GPT-4o Mini
AZURE_OPENAI_KEY="suachaveaqui"
AZURE_OPENAI_ENDPOINT="https://seuendepointaqui"
AZURE_OPENAI_CHAT_DEPLOYMENT="gpt-4o-mini"
AZURE_OPENAI_API_VERSION="2025-01-01-preview"

# GPT-5.4-nano
NANO_API_KEY="suachaveaqui"
NANO_ENDPOINT="https://seuendepointaqui"
NANO_DEPLOYMENT="gpt-5.4-nano"
NANO_API_VERSION="2024-12-01-preview"

# Llama 4 Maverick 17B Instruct
LLAMA_API_KEY="suachaveaqui"
LLAMA_ENDPOINT="https://seuendepointaqui"
LLAMA_DEPLOYMENT="Llama-4-Maverick-17B-128E-Instruct-FP8"
```

### 5. Iniciar o Aplicativo Local
Basta acionar a inicialização do container Streamlit:

```bash
streamlit run app.py
```

Você perceberá que será aberta automaticamente uma nova guia no seu navegador apontando para `http://localhost:8501`.

---

## 📂 Arquitetura Central (File Tree)

```plaintext
Analista_juridico-2/
├── app.py               # ➔ Arquivo raiz que roda o visual, sidebar e integra o Dashboard
├── analyzer.py          # ➔ Orquestração que lida com o AzureOpenAi, Llama e os prompts do Sistema
├── parser.py            # ➔ Tratamento de dados para excel, csv, e Json resguardando as formatações
├── database.py          # ➔ Querys, inserts e comandos automáticos de inicialização do SQLite 
├── report.py            # ➔ Arquivo puramente estético e de PDF generator via ReportLab
├── requirements.txt     # ➔ Mapeamento de bibliotecas para pip deployment
├── juridico.db          # ➔ Entidade única rodando em máquina (não commitar versionamento)
└── .env                 # ➔ Variáveis sensíveis e secrets (não commitar)
```

<hr/>

<div align="center">
  <p>
    Desenvolvido para automatização robusta de análises estruturais de direito.<br>
    <i>© 2026 - Analisador Jurídico IA</i>
  </p>
</div>
