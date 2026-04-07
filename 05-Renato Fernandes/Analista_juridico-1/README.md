# ⚖️ Analisador Jurídico IA

> **Plataforma avançada de classificação e auditoria inteligente para textos e pareceres jurídicos, potencializada por múltiplos modelos de Inteligência Artificial.**

---

## 📖 Sobre o Projeto

O **Analisador Jurídico IA** é uma aplicação completa desenvolvida em Python e [Streamlit](https://streamlit.io/) desenhada especificamente para atuar no ecossistema jurídico. O sistema é capaz de ler grandes lotes de casos e relatórios em CSV, JSON e TXT e automatizar a **triagem de complexidade processual**, delegando níveis de atuação para estagiários, analistas, juízes locais e ministros (STF/STJ) de acordo com o teor da solicitação jurídica.

O grande diferencial do projeto está na sua capacidade **Multi-Modelo (MaaS)** escalável, executando análises refinadas e permitindo comparativos usando modelos variados rodando no **Azure AI Studio**, como GPT-4o e Llama 4.

## ✨ Funcionalidades Principais

- **📤 Ingestão de Dados Resiliente:** Processamento dinâmico de arquivos `.csv`, `.json` e `.txt` com detecção de encoding e fallback. As avaliações são automaticamente processadas de forma cronológica garantindo integridade e previsibilidade.
- **🧠 Predição Multi-Modelo Simultânea:** Integração isolada via APIs com os modelos **GPT-4o Mini**, **GPT-5.4 Nano** e **Llama-4 Maverick 17B**. Permite triagem colaborativa e comparação de asserts e justificativas ("Qual modelo analisa melhor qual área?").
- **📐 LLM-as-a-Judge e Métricas NPL:** Usa NLP Nativo (NLTK - METEOR) somado a um LLM juiz que confere a fidelidade factual da IA contra o documento base (evitando alucinações de base legal).
- **📊 Dashboard Interativo e Dinâmico:** Gráficos inteligentes em tempo real criados com **Plotly Express**, mostrando mapas de calor (Complexidade x Área do Direito), e dispersão de volume de avaliações.
- **📄 Relatórios Executivos em PDF:** Motor de renderização que transforma os achados da IA e os metadados visuais em um documento paramétrico e formal para a diretoria, desenvolvido através do `reportlab`.
- **🗃️ Histórico Centralizado (Banco de Dados):** Arquitetura escalável baseada em `SQLite` para listar todo o histórico operacional com opção de filtros por Nível, Base Legal, Assunto e Fonte Original.

---

## 🛠️ Tecnologias Utilizadas

| Ferramenta / Linguagem | Propósito |
| :--- | :--- |
| <img src="https://img.icons8.com/color/48/000000/python.png" width="20"/> **Python 3.10+** | Linguagem principal do ecossistema backend e orquestração. |
| <img src="https://streamlit.io/images/brand/streamlit-mark-color.svg" width="20"/> **Streamlit** | Motor do Frontend e componentes reativos da interface de usuário. |
| <img src="https://img.icons8.com/color/48/000000/azure-1.png" width="20"/> **Azure AI Studio** | Provedor Serverless de Modelos como Serviço (MaaS) (OpenAI & Meta Llama). |
| <img src="https://upload.wikimedia.org/wikipedia/commons/e/ed/Pandas_logo.svg" width="40"/> **Pandas** | Transformação, higienização, identificadores de colunas e data science. |
| <img src="https://upload.wikimedia.org/wikipedia/commons/3/37/Plotly-logo-01-square.png" width="20"/> **Plotly** | Visualizações e métricas gráficas interativas embutidas. |
| <img src="https://img.icons8.com/fluency/48/000000/database.png" width="20"/> **SQLite** | Banco de dados nativo de alta performance via `.db` encapsulado localmente. |

---

## 🚀 Como Executar Localmente

### Pré-requisitos
Asegure-se de que possui o Python >= 3.10 instalado. Crie sua Virtual Environment (`.venv`) idealmente.

1. **Clone do repositório ou entre na pasta:**
   ```bash
   cd Analista_juridico-1
   ```

2. **Instalação das dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as Variáveis de Ambiente:**
   Certifique-se de que o arquivo `.env` possua as chaves dos modelos devidamente provisionadas:
   ```env
   # Azure OpenAI (Exemplo)
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
   ...
   ```

4. **Iniciando o App Streamlit:**
   ```bash
   streamlit run app.py
   ```
   > O terminal lhe fornecerá uma porta na qual a interface da web foi montada (geralmente `http://localhost:8501`).

---

## 📂 Estrutura de Arquivos

```bash
📦 Analista_juridico-1
 ┣ 📜 app.py               # 🚀 Ponto de entrada (Streamlit WebApp)
 ┣ 📜 analyzer.py          # 🧠 Lógica isolada de orquestração de Prompts e Endpoints LLM
 ┣ 📜 database.py          # 🗄️ Inicialização, queries e DAOs para o SQLite
 ┣ 📜 parser.py            # 📤 Lógica tolerante a falhas de file upload e conversão em Dataframes
 ┣ 📜 report.py            # 📄 Motor gerador de relatórios PDF (ReportLab Builder)
 ┣ 📜 requirements.txt     # 📦 Dependências da biblioteca Python
 ┗ 📜 .env                 # 🔑 Credenciais seguras dos conectores Cloud
```

---

## 🤝 Possíveis Melhorias Futuras

- [ ] Implementar integração com sistemas de processos como SAJ, PJe e E-proc.
- [ ] Incorporação de agente base de Conhecimento RAG (Vector Database) com leis atualizadas internamente e não só no peso do modelo.
- [ ] Deploy conteinerizado via Docker.
- [ ] Exportação automática via API Externa para fluxos Power Automate.

> *Desenvolvido com 💼 foco estratégico visando a otimização assertiva de recursos jurídicos escaláveis e segurança preditiva.*
