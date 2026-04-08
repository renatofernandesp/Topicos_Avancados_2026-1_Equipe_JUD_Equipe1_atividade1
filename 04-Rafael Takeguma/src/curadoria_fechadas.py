import json
import os
import time
import pandas as pd
from google import genai
from google.genai.types import GenerateContentConfig
from datasets import load_dataset
from dotenv import load_dotenv

# ==========================================
# FUNÇÕES DE FORMATAÇÃO E PROMPT
# ==========================================

def agrupar_alternativas(dicionario_choices):
    """Extrai as alternativas do formato Hugging Face e converte numa string legível."""
    rotulos = dicionario_choices['label']
    textos = dicionario_choices['text']
    
    linhas_alternativas = []
    for idx in range(len(rotulos)):
        linhas_alternativas.append(f"{rotulos[idx]}) {textos[idx]}")
        
    return "\n".join(linhas_alternativas)

def construir_prompt_objetivas(texto_enunciado, alternativas_formatadas, letra_gabarito):
    """Gera o prompt final injetando os dados da questão."""
    return f"""Você é um Analista Especialista em classificar questões do Exame de Ordem da OAB.

Estamos realizando a curadoria de um dataset de questões FECHADAS (Múltipla Escolha) da OAB. 

Sua tarefa é classificar o enunciado para entender o nível de dificuldade e a área envolvida de cada questão.

O que você deve fazer:
1. Analise o ENUNCIADO, as ALTERNATIVAS e o GABARITO de cada questão.
2. Classifique a área de especialidade de cada questão.
3. Classifique o nível de dificuldade de cada questão.
4. Sempre indique a referência legal que fundamenta o GABARITO.
5. No campo "dificuldade", utilize apenas o rótulo antes dos dois pontos (ex: "Nível 1 - Estagiário").

Utilize os seguintes Níveis de Dificuldade:
- Nível 1 - Estagiário: Questões objetivas de resposta direta na lei (literalidade).
- Nível 2 - Analista: Exige conhecimento de ritos processuais, prazos ou competência básica.
- Nível 3 - Juiz de Direito: Casos práticos que exigem subsunção do fato à norma para encontrar a alternativa correta.
- Nível 4 - Ministro (STF/STJ): Questões complexas envolvendo controle de constitucionalidade ou jurisprudência consolidada.

Áreas de Especialidade Permitidas:
[direito_administrativo, direito_civil, direito_constitucional, direito_do_trabalho, direito_empresarial, direito_penal, direito_tributario]

DADOS DA QUESTÃO:
ENUNCIADO: {texto_enunciado}
ALTERNATIVAS: {alternativas_formatadas}
GABARITO: {letra_gabarito}

Responda obrigatoriamente no formato JSON puro, sem markdown:
{{
    "area": "nome_da_area",
    "dificuldade": "Nível X - Nome",
    "referencia_principal": "Art. X da Lei Y"
}}
"""

def limpar_retorno_json(resposta_bruta):
    """Remove blocos de formatação Markdown que a API possa devolver por engano."""
    texto = resposta_bruta.strip()
    if texto.startswith("```json"):
        texto = texto[7:]
    if texto.endswith("```"):
        texto = texto[:-3]
    return texto.strip()

# ==========================================
# FLUXO PRINCIPAL DE CURADORIA
# ==========================================

def processar_dataset():
    load_dotenv()
    chave_acesso = os.getenv("GOOGLE_API_KEY")
    if not chave_acesso:
        raise ValueError("Atenção: A chave GOOGLE_API_KEY não está definida no ficheiro .env.")

    cliente_ia = genai.Client(api_key=chave_acesso)

    idx_inicio = int(os.getenv("CURADORIA_FECHADAS_RANGE_START", "530"))
    idx_fim = int(os.getenv("CURADORIA_FECHADAS_RANGE_END", "636"))
    modelo_ia = os.getenv("CURADORIA_FECHADAS_MODEL", "gemini-3-flash-preview")
    ficheiro_saida = os.getenv("CURADORIA_FECHADAS_OUTPUT_FILE", "curadoria_fechadas_rafael.csv")

    print("A estabelecer ligação com o Hugging Face para transferir o dataset...")
    repositorio_dados = load_dataset("eduagarcia/oab_exams")
    dados_treino = repositorio_dados['train']
    
    subconjunto_alvo = dados_treino.select(range(idx_inicio, idx_fim))
    print(f"Sucesso! Lote delimitado a {len(subconjunto_alvo)} questões para processamento.\n")

    parametros_geracao = GenerateContentConfig(
        temperature=0.0,
        response_mime_type="application/json"
    )

    lista_resultados = []

    for indice_relativo, registo in enumerate(subconjunto_alvo):
        numero_da_questao = (idx_inicio + 1) + indice_relativo
        id_banco_dados = registo['id']
        
        print(f"[{numero_da_questao}] A classificar a questão {id_banco_dados}...")

        bloco_alternativas = agrupar_alternativas(registo['choices'])
        gabarito_oficial = registo['answerKey']
        texto_pergunta = registo['question']

        prompt_estruturado = construir_prompt_objetivas(texto_pergunta, bloco_alternativas, gabarito_oficial)

        try:
            resposta_api = cliente_ia.models.generate_content(
                model=modelo_ia,
                contents=prompt_estruturado,
                config=parametros_geracao
            )

            conteudo_limpo = limpar_retorno_json(resposta_api.text)
            dicionario_classificacao = json.loads(conteudo_limpo)

            lista_resultados.append({
                "question_number": numero_da_questao,
                "id_original": id_banco_dados,
                "area": dicionario_classificacao.get('area', 'FALHA_NA_EXTRACAO'),
                "dificuldade": dicionario_classificacao.get('dificuldade', 'FALHA_NA_EXTRACAO'),
                "referencia_principal": dicionario_classificacao.get('referencia_principal', 'FALHA_NA_EXTRACAO'),
                "gabarito": gabarito_oficial
            })
            
            print(f"    -> Área: {dicionario_classificacao.get('area')} | Dificuldade: {dicionario_classificacao.get('dificuldade')}")

        except Exception as erro:
            print(f"    -> [ERRO CRÍTICO] Falha ao processar a questão {numero_da_questao}: {erro}")
            time.sleep(5)


    tabela_final = pd.DataFrame(lista_resultados)
    tabela_final.to_csv(ficheiro_saida, index=False, sep=';', encoding='utf-8-sig')
    print(f"\nOperação concluída com êxito! Ficheiro gerado: '{ficheiro_saida}'")

if __name__ == "__main__":
    processar_dataset()