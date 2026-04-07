# OAB Bench: Relatório Automatizado com Multi-LLMs (Questões Abertas) ⚖️

Este projeto utiliza um ecossistema de múltiplos modelos de Linguagem de Grande Escala (LLMs) para processar e responder questões abertas do dataset **OAB Bench**, gerando automaticamente um relatório comparativo em PDF.

---

## 🔄 Visão Geral do Pipeline

O sistema realiza a consulta simultânea a três modelos distintos para permitir a comparação de qualidade e semântica das respostas jurídicas.

**Fluxo:**
`[Dataset OAB]` → `[LLM Ensemble (Llama 70B, Llama 8B, Qwen 2.5)]` → `[Tratamento de Encoding]` → `[Relatório PDF]`

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Provedores de IA:** * **Groq API:** Modelos `Llama 3.3 70B` (Alta performance) e `Llama 3.1 8B` (Velocidade).
    * **Hugging Face:** Modelo `Qwen 2.5 7B` (Estabilidade).
* **Dataset:** `maritaca-ai/oab-bench` (Questões abertas).
* **Geração de Documentos:** Bibliotecas `FPDF` e `Pandas`.

---

## 🚀 Como Executar no Google Colab

### 1️⃣ Preparação do Ambiente
Instale as dependências necessárias:
```bash
!pip install groq fpdf huggingface_hub datasets
