# RELATÓRIO AUTOMATIZADO COM LLMS + CURADORIA (OAB BENCH) ⚖️

Este projeto implementa um pipeline de Inteligência Artificial para o processamento, classificação e análise de performance de questões fechadas do Exame da Ordem (OAB). de 107- 212

---

## 🔄 Visão Geral do Pipeline

O projeto deve ser executado seguindo rigorosamente a ordem dos três scripts abaixo para garantir a geração correta dos dados e do relatório final:

1.  **`inferencia_oab_questoes_fechadas.py`**: Realiza a coleta bruta das respostas da IA (Llama 3.1 8B) para o lote de questões (107 a 212).
2.  **`gerar_relatorio_inferencia_fechado.py`**: Processa as respostas, aplica a curadoria automatizada e gera o arquivo estruturado `curadoria_thomas.xml`.
3.  **`gerar_relatorio_pdf_fechado.py`**: Consome o XML gerado para calcular métricas de precisão e exportar o `Relatorio_Thomas_Final_XML.pdf`.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **IA:** Groq API (Meta Llama 3.1 8B)
* **Datasets:** `eduagarcia/oab_exams` (Hugging Face)
* **Bibliotecas:** `pandas`, `reportlab`, `lxml`, `datasets`, `groq`

---

## ⚖️ Metodologia de Curadoria (Níveis)

As questões são classificadas em quatro níveis de complexidade jurídica:
* **Nível 1 - Estagiário:** Aplicação literal da lei.
* **Nível 2 - Analista:** Conhecimento de ritos e prazos.
* **Nível 3 - Juiz de Direito:** Interpretação de casos práticos.
* **Nível 4 - Ministro (STF/STJ):** Controle de constitucionalidade e súmulas vinculantes.

---

## 📂 Funcionalidades
* **Curadoria Automatizada:** Classificação por área do Direito e nível de dificuldade.
* **LLM-Judge:** Avaliação automática da resposta da IA comparada ao gabarito oficial.
* **Exportação Estruturada:** Geração de base de dados em XML para portabilidade.
* **Relatório Profissional:** Documento PDF com gráficos de precisão e desempenho.

---

## 🧑‍💻 Autor
**Thomás Araujo**

> **Nota:** Certifique-se de instalar as dependências (`pip install reportlab pandas groq datasets`) antes de iniciar a execução no Google Colab.
