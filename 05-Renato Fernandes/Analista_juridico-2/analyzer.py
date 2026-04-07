import os
import json
import httpx
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv

load_dotenv()

# Avaliações de Níveis (removidas conforme solicitado)

AREAS = [
    "direito_administrativo",
    "direito_ambiental",
    "direito_civil",
    "direito_constitucional",
    "direito_da_crianca_e_do_adolescente",
    "direito_do_consumidor",
    "direito_do_trabalho",
    "direito_empresarial",
    "direito_internacional",
    "direito_penal",
    "direito_processual_civil",
    "direito_processual_do_trabalho",
    "direito_processual_penal",
    "direito_tributario",
    "etica_profissional"
]

# ── Configurações dos modelos disponíveis ────────────────────────────────────
MODELOS = {
    "gpt-4o-mini": {
        "label": "GPT-4o Mini",
        "client": AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        ),
        "deployment": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini"),
    },
    "gpt-5.4-nano": {
        "label": "GPT-5.4 Nano",
        "client": AzureOpenAI(
            api_key=os.getenv("NANO_API_KEY"),
            azure_endpoint=os.getenv("NANO_ENDPOINT"),
            api_version=os.getenv("NANO_API_VERSION"),
        ),
        "deployment": os.getenv("NANO_DEPLOYMENT", "gpt-5.4-nano"),
    },
    "llama-4-maverick": {
        "label": "Llama 4 Maverick 17B",
        "client": OpenAI(
            api_key=os.getenv("LLAMA_API_KEY", ""),
            base_url=os.getenv("LLAMA_ENDPOINT", ""),
            http_client=httpx.Client(verify=False)
        ),
        "deployment": os.getenv("LLAMA_DEPLOYMENT", "Llama-4-Maverick-17B-128E-Instruct-FP8"),
    }
}

SYSTEM_PROMPT = """Você é um especialista jurídico brasileiro. Analise o texto jurídico fornecido e retorne um JSON com:
- "area": uma das áreas: direito_administrativo, direito_ambiental, direito_civil, direito_constitucional, direito_da_crianca_e_do_adolescente, direito_do_consumidor, direito_do_trabalho, direito_empresarial, direito_internacional, direito_penal, direito_processual_civil, direito_processual_do_trabalho, direito_processual_penal, direito_tributario, etica_profissional
- "base_legal": lista das principais normas, artigos, leis ou súmulas aplicáveis (máximo 5 itens)
- "justificativa": breve justificativa da classificação (máximo 2 frases)

Responda APENAS com o JSON, sem markdown."""

SYSTEM_PROMPT_MCQ = """Você é um especialista em direito brasileiro avaliando questões de múltipla escolha.
Você receberá:
- A questão completa
- As alternativas A, B, C e D (no campo 'Respostas')
- A resposta escolhida/gabarito oficial (no campo 'Resposta Escolhida')

Sua tarefa é analisar as alternativas e verificar se a resposta escolhida está CORRETA.
Se estiver incorreta, identifique qual seria a alternativa correta e explique os motivos jurídicos detalhados.

Sua resposta deve ser estritamente em JSON, contendo:
- "area": identifique a área (ex: direito_penal, direito_civil, etc).
- "gabarito_correto": true se a resposta escolhida estiver correta, false caso contrário.
- "resposta_modelo": a letra da alternativa (A, B, C ou D) que você considera 100% correta.
- "justificativa": explique passo a passo por que a resposta está correta e, se o gabarito estiver errado, detalhe os motivos jurídicos que comprovam o erro e indique explicitamente qual é a resposta correta e por quê.

Responda APENAS com o JSON, sem markdown."""

def analisar_texto(registro, modelo_key: str) -> dict:
    modelo = MODELOS[modelo_key]
    
    is_mcq = isinstance(registro, dict)
    
    if is_mcq:
        texto_usuario = (
            f"ID: {registro.get('ID_Question', '')}\n"
            f"Tipo de Questão: {registro.get('question_type', '')}\n"
            f"Questão: {registro.get('question', '')}\n"
            f"Respostas (alternativas A, B, C, D):\n{registro.get('choices', '')}\n"
            f"Resposta Escolhida (gabarito oficial): {registro.get('answerKey', '')}"
        )
        prompt_sys = SYSTEM_PROMPT_MCQ
    else:
        texto_usuario = f"Texto jurídico:\n{registro[:3000]}"
        prompt_sys = SYSTEM_PROMPT

    kwargs = {
        "model": modelo["deployment"],
        "messages": [
            {"role": "system", "content": prompt_sys},
            {"role": "user", "content": texto_usuario}
        ],
        "temperature": 0.1
    }
    
    # Modelos novos (o1, gpt-4o, etc) usam max_completion_tokens. Modelos antigos max_tokens
    if modelo_key in ["gpt-5.4-nano"]:
        kwargs["max_completion_tokens"] = 500
    else:
        kwargs["max_tokens"] = 500

    response = modelo["client"].chat.completions.create(**kwargs)
    
    content = response.choices[0].message.content.strip()
    # remove markdown code block se o modelo retornar
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON Parsing Error: {str(e)}. Raw model response: {content}")
    
    ret = {
        "nivel": None,
        "descricao_nivel": None,
        "area": result.get("area", "direito_civil"),
        "base_legal": ", ".join(result.get("base_legal", [])) if isinstance(result.get("base_legal"), list) else result.get("base_legal", ""),
        "justificativa": result.get("justificativa", ""),
        "modelo": modelo_key,
    }
    
    if is_mcq:
        ret["questao_id"]       = str(registro.get("ID_Question", ""))
        ret["gabarito_oficial"] = str(registro.get("answerKey", ""))
        ret["gabarito_modelo"]  = str(result.get("resposta_modelo", ""))
        ret["gabarito_correto"] = bool(result.get("gabarito_correto", False))
        ret["question_type"]    = str(registro.get("question_type", ""))
    else:
        ret["questao_id"]       = None
        ret["gabarito_oficial"] = None
        ret["gabarito_modelo"]  = None
        ret["gabarito_correto"] = None
        ret["question_type"]    = None
        
    return ret

def avaliar_com_llm_judge(texto: str, justificativa: str, modelo_judge="gpt-4o-mini") -> float:
    if modelo_judge not in MODELOS:
        modelo_judge = list(MODELOS.keys())[0]
        
    modelo = MODELOS[modelo_judge]
    prompt = f"""TEXTO ORIGINAL:
{texto}
JUSTIFICATIVA GERADA:
{justificativa}
Atribua uma nota rígida de 0.0 a 1.0 representando o quão semanticamente precisa, consistente e factualmente correta a justificativa é considerando apenas os fatos presentes no texto original.
Retorne APENAS o número decimal (ex: 0.85). Não escreva texto."""

    kwargs = {
        "model": modelo["deployment"],
        "messages": [
            {"role": "system", "content": "Você é um robô juiz que só responde com notas float."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
    }
    if modelo_judge in ["gpt-5.4-nano"]:
        kwargs["max_completion_tokens"] = 10
    else:
        kwargs["max_tokens"] = 10

    try:
        response = modelo["client"].chat.completions.create(**kwargs)
        content = response.choices[0].message.content.strip()
        import re
        match = re.search(r"(?:0\.\d+|1\.0|\d+)", content)
        if match:
            nota = float(match.group())
            return min(max(nota, 0.0), 1.0)
    except Exception:
        pass
    return 0.0


def analisar_lote(registros: list, fonte: str, modelos_selecionados: list[str], progress_callback=None) -> list[dict]:
    resultados = []
    total_ops = len(registros) * len(modelos_selecionados)
    contador = 0
    for texto in registros:
        if not texto:
            continue
        if isinstance(texto, str) and not texto.strip():
            continue
        for modelo_key in modelos_selecionados:
            try:
                analise = analisar_texto(texto, modelo_key)
                if isinstance(texto, dict):
                    # Formatar a representação do texto para o DB
                    str_texto = f"Questão [{texto.get('ID_Question')}]: {texto.get('question', '')[:500]}...\nAlternativas: {texto.get('choices', '')}"
                else:
                    str_texto = texto

                analise["texto"] = str_texto
                analise["fonte"] = fonte
                resultados.append(analise)
            except Exception as e:
                resultados.append({
                    "texto": texto if isinstance(texto, str) else str(texto),
                    "nivel": None,
                    "descricao_nivel": None,
                    "area": "indefinido",
                    "base_legal": f"Erro: {str(e)}",
                    "justificativa": "",
                    "modelo": modelo_key,
                    "fonte": fonte,
                    "question_type": None,
                })
            contador += 1
            if progress_callback:
                progress_callback(contador, total_ops)
    return resultados
