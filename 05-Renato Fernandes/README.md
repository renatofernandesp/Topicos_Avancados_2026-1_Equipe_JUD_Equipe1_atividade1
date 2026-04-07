⚖️Avaliação de Modelos de Linguagem em Contexto Jurídico
Repositório destinado à Atividade 1 da disciplina Tópicos Avançados em Engenharia de Software e Sistemas de Informação I (T01). O projeto explora a capacidade de inferência de Large Language Models (LLMs) aplicados ao domínio do Direito, utilizando diferentes datasets e métricas de avaliação semântica.

📂 Estrutura de Dados (Datasets)
O projeto utiliza dois perfis de análise baseados em datasets específicos:

Analista Jurídico 1: Processamento de questões abertas (Renato-Q-Abertas.txt).

Analista Jurídico 2: Processamento de questões fechadas (Renato-Q-Fechadas_v4.xlsx).

🛠️ Metodologia e Critérios de Análise
1. Classificação Hierárquica (Dificuldade)
As questões são categorizadas por níveis de complexidade, simulando a carreira jurídica:

Níveis: Estagiário ➔ Analista ➔ Juiz de Direito ➔ Ministro (STF/STJ).

Especialidades: Administrativo, Civil, Constitucional, Trabalho, Empresarial, Penal e Tributário.

Referência: Legislação base

2. Modelos em Avaliação
A análise de inferência é realizada comparando a performance dos seguintes modelos:

OpenAI: GPT-4o Mini e GPT-5.4 Nano.

Meta: Llama 4 Maverick.

3. Métricas de Performance e Qualidade
Para garantir a precisão dos resultados, utilizamos duas abordagens complementares:

METEOR (app.py): Avaliação de correspondência semântica e sinônimos via PLN dinâmico (NLTK), focando na fluidez e significado.

LLM-Judge (analyzer.py): Avaliação qualitativa onde um modelo superior julga a consistência factual e a precisão das justificativas geradas.

📊 Resultados
O relatório consolidado com o desempenho dos modelos em ambos os cenários (questões abertas e fechadas) pode ser acessado aqui:
👉 Questos-Abertas-e-Fechadas-Renato-Fernandes.pdf
