# 🧠 Inferência com Modelos de Linguagem no Domínio Jurídico  
## Curadoria, Avaliação e Análise de Desempenho em Exames da OAB

---

## 📌 Descrição do Projeto

Este projeto tem como objetivo investigar o desempenho de Modelos de Linguagem de Grande Escala (LLMs) no domínio jurídico, utilizando questões do Exame da Ordem dos Advogados do Brasil (OAB) como benchmark.

A proposta envolve:
- Curadoria de datasets jurídicos (questões abertas e fechadas)
- Classificação semântica e estrutural das questões
- Avaliação quantitativa e qualitativa das respostas geradas por LLMs

O estudo busca compreender a capacidade desses modelos em:
- Interpretar legislação
- Resolver problemas jurídicos
- Produzir respostas coerentes e juridicamente fundamentadas

---

## 🎯 Objetivos

### Objetivo Geral
Avaliar a performance de modelos de linguagem no domínio jurídico, com base em métricas formais e curadoria especializada.

### Objetivos Específicos
- Construir um pipeline de inferência com LLMs
- Curar e estruturar datasets jurídicos (OAB)
- Classificar questões por:
  - Área do Direito
  - Nível de dificuldade
  - Tipo de questão
- Aplicar métricas de avaliação (quantitativas e qualitativas)
- Analisar limitações e vieses dos modelos

---

## 📂 Estrutura do Projeto

```bash
├── data/
│   ├── raw/                # Dados originais (datasets da OAB)
│   ├── processed/          # Dados curados e anotados
│
├── notebooks/
│   ├── inference.ipynb     # Execução dos modelos
│   ├── evaluation.ipynb    # Cálculo de métricas
│
├── src/
│   ├── preprocessing.py    # Tratamento dos dados
│   ├── inference.py        # Interface com LLMs
│   ├── metrics.py          # Implementação das métricas
│
├── results/
│   ├── outputs/            # Respostas geradas pelos modelos
│   ├── analysis/           # Análises e comparações
│
├── README.md
└── requirements.txt
```

---

### Curadoria

Cada questão foi anotada manualmente com:

- 📚 Área do Direito (ex: Constitucional, Penal, Administrativo)
- 🎓 Nível de dificuldade:
  - Intuitiva
  - Conceitual
  - Aplicada
  - Analítica
  - Especialista
- ⚖️ Referência legal (base normativa associada)

---

## 🤖 Modelos Utilizados

Os experimentos consideram modelos disponíveis via Hugging Face ou APIs externas, incluindo:

- LLMs generalistas
- Modelos instruídos (instruction-tuned)
- Modelos quantizados (quando necessário)

---

## ⚙️ Pipeline de Inferência

1. Entrada: questão jurídica
2. Prompt estruturado
3. Inferência via modelo
4. Pós-processamento da resposta
5. Armazenamento do resultado

---

## 📏 Métricas de Avaliação

### 🔢 Quantitativas
- **Exact Match (EM)**  
  Verifica correspondência exata com o gabarito

- **BLEU**  
  Mede similaridade lexical entre resposta gerada e referência

- **ROUGE**  
  Avalia cobertura do conteúdo da resposta esperada

- **Acurácia** (questões fechadas)

---

### 🧠 Qualitativas
- Coerência jurídica
- Adequação da fundamentação legal
- Clareza da argumentação

---

## ⚖️ LLM as a Judge

Em cenários sem especialista humano disponível, utilizamos um LLM adicional como avaliador automático para:

- Julgar qualidade das respostas
- Classificar nível de adequação jurídica
- Identificar inconsistências

---

## 📈 Resultados Esperados

- Comparação entre modelos em diferentes tipos de questão
- Identificação de limitações em raciocínio jurídico
- Avaliação do impacto de prompt engineering
- Análise de trade-offs entre custo e desempenho

---

## 🚧 Limitações

- Dependência de qualidade do dataset
- Avaliação qualitativa parcialmente subjetiva
- Possíveis vieses nos modelos

---

## 🔮 Trabalhos Futuros

- Fine-tuning específico para domínio jurídico
- Uso de embeddings jurídicos especializados
- Integração com bases legais reais (ex: jurisprudência)
- Avaliação com especialistas humanos

---

## 🧾 Referências

- OAB Bench Dataset  
- OAB Exams Dataset  
- Papéis sobre avaliação de LLMs  
- Literatura sobre NLP jurídico

---

## 👩‍💻 Autoria

Helena Carvalho Leal  
Mestrado em Computação / Pesquisa em IA e Computação Quântica  
