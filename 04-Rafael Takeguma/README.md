# Tópicos de IA - Curadoria e Inferência para Questões da OAB

Este projeto automatiza tarefas de curadoria e inferência com modelos Gemini para questões do Exame de Ordem (OAB), cobrindo:

- questões fechadas (múltipla escolha),
- questões abertas (discursivas e peça profissional),
- comparação de respostas entre diferentes modelos.

Os scripts processam datasets jurídicos, enviam prompts estruturados para a API da Google e exportam os resultados em CSV.

## Objetivos

- Classificar questões por área jurídica.
- Estimar nível de dificuldade em escala padronizada.
- Indicar referência legal principal associada à resposta.
- Gerar saídas tabulares para análise posterior.

## Estrutura do Projeto

```text
topicos-ia-rafael/
|- src/
|  |- curadoria_fechadas.py
|  |- curadoria_abertas.py
|  `- inferencia.py
|- dataset_rafael.jsonl
|- curadoria_fechadas_rafael.csv
|- curadoria_abertas_rafael.csv
|- resultados_inferencia.csv
|- requirements.txt
`- README.md
```

## Requisitos

- Python 3.10+ (recomendado 3.12)
- Chave de API Google (`GOOGLE_API_KEY`)
- Dependências listadas em `requirements.txt`

## Instalação

No diretório raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuração de Ambiente

Crie um arquivo `.env` na raiz do projeto com, no mínimo:

```env
GOOGLE_API_KEY=sua_chave_aqui
```

Os scripts aceitam variáveis opcionais para customização de entrada, saída e modelos.

## Como Executar

### 1) Curadoria de questões fechadas

Script: `src/curadoria_fechadas.py`

Função principal:
- Carrega o dataset `eduagarcia/oab_exams` via Hugging Face.
- Seleciona uma faixa de índices.
- Classifica cada questão (área, dificuldade e referência legal).
- Exporta CSV com separador `;`.

Execução:

```powershell
python .\src\curadoria_fechadas.py
```

Variáveis opcionais:

- `CURADORIA_FECHADAS_RANGE_START` (padrão: `530`)
- `CURADORIA_FECHADAS_RANGE_END` (padrão: `636`)
- `CURADORIA_FECHADAS_MODEL` (padrão: `gemini-3-flash-preview`)
- `CURADORIA_FECHADAS_OUTPUT_FILE` (padrão: `curadoria_fechadas_rafael.csv`)

### 2) Curadoria de questões abertas

Script: `src/curadoria_abertas.py`

Função principal:
- Lê questões de um arquivo JSONL.
- Classifica área, dificuldade, referência legal e tipo de questão.
- Exporta CSV com separador `;`.

Execução:

```powershell
python .\src\curadoria_abertas.py
```

Variáveis opcionais:

- `CURADORIA_ABERTAS_INPUT_FILE` (padrão: `dataset_rafael.jsonl`)
- `CURADORIA_ABERTAS_OUTPUT_FILE` (padrão: `curadoria_abertas_rafael.csv`)
- `CURADORIA_ABERTAS_MODEL` (padrão: `gemini-3-flash-preview`)

### 3) Inferência comparativa entre modelos

Script: `src/inferencia.py`

Função principal:
- Lê questões de um arquivo JSONL.
- Envia cada questão para uma lista de modelos Gemini.
- Consolida as respostas de cada modelo em CSV.

Execução:

```powershell
python .\src\inferencia.py
```

Variáveis opcionais:

- `INFERENCIA_INPUT_FILE` (padrão: `dataset_rafael.jsonl`)
- `INFERENCIA_OUTPUT_FILE` (padrão no código: `resultados_gemini_rafael.csv`)
- `INFERENCIA_MODELS`  
  (padrão: `gemini-3.1-flash-lite-preview,gemini-3-flash-preview,gemini-3.1-pro-preview`)

## Formato de Entradas e Saídas

### Entrada principal (`dataset_rafael.jsonl`)

Esperado (campos usados pelos scripts):

- `question_id`
- `statement`
- `turns` (lista de perguntas/comandos)
- `category` (usado no pipeline de inferência)

### Saídas CSV

- `curadoria_fechadas_rafael.csv`: curadoria de questões objetivas.
- `curadoria_abertas_rafael.csv`: curadoria de questões discursivas/peças.
- `resultados_gemini_rafael.csv` ou `resultados_inferencia.csv`: respostas por modelo.

Observação: os CSVs são gerados com encoding `utf-8-sig` e separador `;`.

## Boas Práticas

- Mantenha o `.env` fora de versionamento.
- Ajuste os ranges de processamento para execuções incrementais.
- Valide manualmente uma amostra dos resultados para controle de qualidade.
- Evite versionar artefatos temporários (`__pycache__`, ambiente virtual).

## Solução de Problemas

- **Erro de chave de API ausente**  
  Verifique se `GOOGLE_API_KEY` está definido no `.env`.

- **Falha ao carregar dataset Hugging Face**  
  Confirme conexão com internet e disponibilidade do dataset remoto.

- **Campos ausentes no JSONL**  
  Revise o esquema de entrada para conter os campos esperados pelos scripts.

## Licença

Defina aqui a licença do projeto (por exemplo: MIT, Apache-2.0, uso acadêmico interno).
