# Curadoria de Dados - Exame da OAB ⚖️

Este repositório contém o trabalho de curadoria, classificação e processamento de questões do Exame da Ordem dos Advogados do Brasil (OAB), realizado pelo **Grupo 01**. O projeto utiliza IA para análise jurídica e geração de relatórios estruturados.

## 🚀 Objetivo
Processar lotes de questões utilizando múltiplos modelos de Linguagem de Grande Escala (LLMs) para garantir a precisão na classificação, análise jurídica e geração de relatórios automatizados.

---

## 🔄 Fluxo de Execução (Pipeline)

O projeto deve ser executado em **duas etapas** sequenciais no Google Colab:

### **Etapa 1: Processamento e Inferência**
* **Ação:** Instalar `groq`, `pandas` e `datasets`. Configurar a `CHAVE_GROQ`.
* **O que faz:** Carrega o dataset (`eduagarcia/oab_exams`), envia para o **Llama 3.1 8B**, realiza o "LLM-Judge" para validar o gabarito e classifica a questão (Área, Nível e Base Legal).


---

## 📂 Estrutura de Arquivos do Repositório

### 📝 Questões Abertas (Lote 11 a 20)
* `lote__abertas_thomas_oab_benc-11-20.xml` / `.csv`: Dados brutos e processados.
* `Curadoria_questoes_abertas_thomas_11_a_20.xlsx`: Classificação manual analítica.
* `Relatorio_Thomas_Final_Questoes_Abertas_11_20.pdf`: Inferências consolidadas.

### 🔒 Questões Fechadas (Lote 107 a 212)
* `lote_thomas_oab_bec_fechadas_107__a_212.xml` / `.csv`: Dados brutos e processados.
* `Curadoria_questoes_fechadas_thomas_107_a_212.xlsx`: Classificação manual analítica.
* `Relatorio_Thomas_Final_Questoes_fechadas_107_212.pdf`: Inferências consolidadas.

---

## ⚖️ Metodologia de Curadoria

### 📈 Níveis de Dificuldade (Atribuído)
1.  **Nível 1 - Estagiário:** Aplicação direta da lei (literalidade).
2.  **Nível 2 - Analista:** Conhecimento de ritos processuais ou prazos.
3.  **Nível 3 - Juiz de Direito:** Interpretação de casos práticos e subsunção do fato à norma.
4.  **Nível 4 - Ministro (STF/STJ):** Controle de constitucionalidade e súmulas vinculantes.

### 📚 Áreas de Especialidade
* Direito Constitucional, Penal, Administrativo, Trabalho e Digital.

---

## 🛠️ Tecnologias Utilizadas
* **IA:** Llama 3.3 70B & 3.1 8B (Groq), Qwen 2.5 (Hugging Face).
* **Libs:** `pandas`, `groq`, `huggingface_hub`, `datasets`, `reportlab`, `fpdf`.

## 🧑‍💻 Autor
**Thomás Araujo**
