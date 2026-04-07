# Análise Comparativa de LLMs em Questões da OAB

Este repositório apresenta uma análise comparativa entre três modelos de linguagem aplicados a questões jurídicas da OAB:

- **GPT-5.3**
- **Claude Sonnet 4.6**
- **Gemini**

A comparação foi realizada em dois cenários distintos:

- **questões abertas**, com avaliação qualitativa por inferência comparativa;
- **questões fechadas**, com avaliação quantitativa baseada em gabarito explícito.

O objetivo do projeto é observar como os modelos se comportam em tarefas jurídicas, considerando não apenas acertos, mas também aderência temática, fundamentação legal, estilo de resposta e consistência geral. :contentReference[oaicite:3]{index=3}

---

## Objetivo

Avaliar e comparar o desempenho dos modelos em perguntas da OAB, medindo:

### Questões abertas
- classificação de nível da questão;
- aderência da categoria ao dataset;
- similaridade textual entre respostas;
- completude da base legal;
- divergência por questão.

### Questões fechadas
- acurácia;
- taxa de erro;
- Exact Match (EM).

---

## Bases de dados

Foram utilizados dois conjuntos principais:

### Questões abertas
Dataset derivado do benchmark jurídico da OAB, com seleção das questões discursivas utilizadas no experimento.

### Questões fechadas
Dataset de questões objetivas da OAB com gabarito explícito.

No relatório final, foram analisadas:

- **10 questões abertas**
- **106 questões fechadas** :contentReference[oaicite:4]{index=4} :contentReference[oaicite:5]{index=5}

---

## Metodologia

### 1. Questões abertas
Como não há gabarito oficial estruturado para as respostas abertas, a comparação foi feita por **inferência comparativa** entre os modelos. Cada resposta foi analisada com base em campos padronizados, como:

- `classification`
- `difficulty_level`
- `area_of_expertise`
- `main_legal_reference`
- `model_answer`

As métricas utilizadas foram:

#### Distribuição dos níveis por modelo
Compara como cada IA classifica a dificuldade das questões entre os níveis 1 a 4.

#### Aderência à categoria do dataset
Compara a área jurídica indicada pelo modelo com a categoria original da questão.

#### Similaridade textual
Mede o quanto as respostas dos modelos se parecem entre si, sem avaliar correção jurídica.

#### Completude da base legal
Score heurístico baseado na densidade de referências normativas.

#### Índice de divergência por questão
Métrica composta para identificar onde os modelos mais se afastam entre si. :contentReference[oaicite:6]{index=6} :contentReference[oaicite:7]{index=7}

### 2. Questões fechadas
Nas questões objetivas, cada resposta foi comparada diretamente com o campo `answerKey`.

As métricas foram:

#### Acurácia
`acertos / total de questões`

#### Taxa de erro
`erros / total de questões`

#### Exact Match (EM)
Proporção de respostas que coincidem exatamente com o gabarito.

Como as questões fechadas possuem apenas uma alternativa correta (`A`, `B`, `C` ou `D`), o valor de **EM coincide com a acurácia**. :contentReference[oaicite:8]{index=8}

---

## Principais resultados

## Questões abertas

### Aderência à categoria
- **Claude Sonnet 4.6:** 10/10
- **GPT-5.3:** 9/10
- **Gemini:** 9/10

### Similaridade média entre pares
- **GPT-5.3 × Claude:** 27,78%
- **GPT-5.3 × Gemini:** 15,69%
- **Claude × Gemini:** 17,15%

### Completude média da base legal
- **GPT-5.3:** 5,225
- **Claude Sonnet 4.6:** 9,400
- **Gemini:** 8,525

### Síntese qualitativa
- O **Claude Sonnet 4.6** foi o modelo mais aderente ao dataset e o que apresentou a base legal mais completa.
- O **GPT-5.3** se destacou pela objetividade e concisão.
- O **Gemini** apresentou comportamento intermediário, com respostas mais variáveis.
- A baixa similaridade entre os textos mostra que os modelos têm estilos argumentativos e enquadramentos jurídicos distintos. :contentReference[oaicite:9]{index=9}

---

## Questões fechadas

Total de questões analisadas: **106**

| Modelo | Acertos | Erros | Acurácia | Taxa de Erro | Exact Match (EM) |
|---|---:|---:|---:|---:|---:|
| Claude Sonnet 4.6 | 83 | 23 | 78,30% | 21,70% | 78,30% |
| ChatGPT 5.3 | 69 | 37 | 65,09% | 34,91% | 65,09% |
| Gemini | 45 | 61 | 42,45% | 57,55% | 42,45% |

### Síntese quantitativa
- O **Claude Sonnet 4.6** apresentou o melhor desempenho geral.
- O **ChatGPT 5.3** teve resultado intermediário.
- O **Gemini** obteve o menor desempenho nesta base. :contentReference[oaicite:10]{index=10}

---

## Conclusão geral

A análise conjunta mostra que o **Claude Sonnet 4.6** foi o modelo mais consistente no cenário analisado, reunindo melhor desempenho qualitativo nas questões abertas e melhor desempenho quantitativo nas questões fechadas. O **GPT-5.3** apresentou respostas mais objetivas e concisas, com desempenho intermediário nas questões objetivas. O **Gemini**, embora tenha produzido respostas elaboradas em parte das questões abertas, ficou abaixo dos demais nas métricas fechadas. Em conjunto, os resultados mostram que a avaliação de modelos jurídicos deve considerar tanto métricas quantitativas quanto aspectos qualitativos de fundamentação, aderência temática e consistência argumentativa. :contentReference[oaicite:11]{index=11}

---

## Estrutura sugerida do repositório

```bash
.
├── data/
│   ├── Dataset_extarido.txt
│   ├── respostas_gpt5.3_abertas.json
│   ├── respostas_claud.iaSonnet4.6_abertas.json
│   ├── respostas_gemini_abertas.json
│   └── resultado questões fechadas.pdf
├── outputs/
│   ├── grafico_1_distribuicao_niveis.png
│   ├── grafico_2_aderencia_categoria.png
│   ├── grafico_3_similaridade_pares.png
│   ├── grafico_4_divergencia_questao.png
│   ├── grafico_5_completude_base_legal.png
│   ├── grafico_pizza_acuracia.png
│   ├── metricas_graficos_llms.xlsx
│   ├── metricas_por_questao.csv
│   ├── resultado_questoes_fechadas_metricas.csv
│   └── resultado_questoes_fechadas_metricas.xlsx
├── notebooks/
│   ├── analise_questoes_abertas.ipynb
│   └── analise_questoes_fechadas.ipynb
├── scripts/
│   ├── analise_abertas.py
│   └── analise_fechadas.py
└── README.md
