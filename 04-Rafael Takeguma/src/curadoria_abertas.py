import json
import os
import time
import pandas as pd
from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def construir_prompt(texto_enunciado, texto_comandos):
    """Gera o prompt formatado com as variáveis da questão."""
    return f"""Você é um Analista Especialista especialista em classificar questões do Exame de Ordem da OAB.

Estamos realizando a curadoria de um dataset de questões ABERTAS (Discursivas e Peças Profissionais) da OAB. 

Sua tarefa é classificar o enunciado para entender o nível de dificuldade e a área envolvida de cada questão.

O que você deve fazer:
1. Analise o ENUNCIADO e as PERGUNTAS/COMANDOS de cada questão.
2. Classifique a área de especialidade de cada questão.
3. Classifique o nível de dificuldade de cada questão.
4. Sempre indique a referência legal.
5. No campo "dificuldade", utilize apenas o rótulo antes dos dois pontos (ex: "Nível 1 - Estagiário").

Utilize os seguintes Níveis de Dificuldade:
- Nível 1 - Estagiário: Questões discursivas de resposta direta na lei (literalidade).
- Nível 2 - Analista: Exige conhecimento de ritos, prazos ou competência básica.
- Nível 3 - Juiz de Direito: Casos práticos complexos que exigem subsunção do fato à norma e redação de teses jurídicas.
- Nível 4 - Ministro (STF/STJ): Questões envolvendo controle de constitucionalidade, súmulas vinculantes ou peças processuais de alta complexidade.

Áreas de Especialidade Permitidas:
[direito_administrativo, direito_civil, direito_constitucional, direito_do_trabalho, direito_empresarial, direito_penal, direito_tributario]

DADOS DA QUESTÃO:
ENUNCIADO: {texto_enunciado}
PERGUNTAS/COMANDOS: {texto_comandos}

Responda obrigatoriamente no formato JSON puro, sem markdown:
{{
    "area": "nome_da_area",
    "dificuldade": "Nível X - Nome",
    "referencia_principal": "Art. X da Lei Y",
    "tipo_questao": "Peça Profissional ou Discursiva"
}}
"""

def higienizar_retorno_json(texto_bruto):
    """Remove marcações Markdown residuais para evitar erros de parser."""
    texto_limpo = texto_bruto.strip()
    if texto_limpo.startswith("```json"):
        texto_limpo = texto_limpo[7:]
    if texto_limpo.endswith("```"):
        texto_limpo = texto_limpo[:-3]
    return texto_limpo.strip()

# ==========================================
# FLUXO PRINCIPAL
# ==========================================

def executar_pipeline():
    load_dotenv()
    chave_api = os.getenv("GOOGLE_API_KEY")
    
    if not chave_api:
        raise ValueError("ERRO: A variável de ambiente GOOGLE_API_KEY não foi encontrada.")

    cliente_ai = genai.Client(api_key=chave_api)
    
    arquivo_input = os.getenv("CURADORIA_ABERTAS_INPUT_FILE", "dataset_rafael.jsonl")
    arquivo_output = os.getenv("CURADORIA_ABERTAS_OUTPUT_FILE", "curadoria_abertas_rafael.csv")
    modelo_alvo = os.getenv("CURADORIA_ABERTAS_MODEL", "gemini-3-flash-preview")

    print(f"A ler ficheiro de dados: {arquivo_input}...")
    df_perguntas = pd.read_json(arquivo_input, lines=True)
    print(f"Total de registos carregados: {len(df_perguntas)}")

    resultados_finais = []

    configs_geracao = GenerateContentConfig(
        temperature=0.0,
        response_mime_type="application/json"
    )

    for index, linha in df_perguntas.iterrows():
        id_atual = linha.get('question_id', f'ID_falha_{index}')
        print(f"-> A classificar questão [{id_atual}]...")

        texto_enunciado = linha.get('statement', '')
        lista_comandos = linha.get('turns', [])
        texto_comandos = "\n".join(lista_comandos) if isinstance(lista_comandos, list) else str(lista_comandos)

        prompt_formatado = construir_prompt(texto_enunciado, texto_comandos)

        try:
            resposta = cliente_ai.models.generate_content(
                model=modelo_alvo,
                contents=prompt_formatado,
                config=configs_geracao
            )

            texto_seguro = higienizar_retorno_json(resposta.text)
            dicionario_dados = json.loads(texto_seguro)
            
            dicionario_dados['question_id'] = id_atual
            resultados_finais.append(dicionario_dados)
            
            nivel_detetado = dicionario_dados.get('dificuldade', 'Não definido')
            print(f"   [SUCESSO] Nível atribuído: {nivel_detetado}")

        except Exception as erro:
            print(f"   [FALHA CRÍTICA] Erro no processamento de {id_atual}: {erro}")
            resultados_finais.append({
                "question_id": id_atual,
                "area": "FALHA_API",
                "dificuldade": "FALHA_API",
                "referencia_principal": str(erro),
                "tipo_questao": "FALHA_API"
            })


    df_exportacao = pd.DataFrame(resultados_finais)
    df_exportacao.to_csv(arquivo_output, index=False, sep=';', encoding='utf-8-sig')
    print(f"\nPipeline finalizado! O relatório foi guardado em: '{arquivo_output}'.")

if __name__ == "__main__":
    executar_pipeline()