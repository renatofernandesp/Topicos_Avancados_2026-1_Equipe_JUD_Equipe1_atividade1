import json
import csv
import io
import pandas as pd


def parse_arquivo(conteudo_bytes: bytes, nome_arquivo: str) -> list:
    ext = nome_arquivo.lower().split(".")[-1]

    if ext == "xlsx":
        return _parse_xlsx(conteudo_bytes)

    conteudo = conteudo_bytes.decode("utf-8", errors="replace")

    if ext == "json":
        return _parse_json(conteudo)
    elif ext == "csv":
        return _parse_csv(conteudo)
    else:
        return _parse_txt(conteudo)


def _find_col(cols_lower: dict, candidates: list):
    """Retorna a primeira chave (lowercase) que contém algum dos candidatos."""
    for candidate in candidates:
        for col_key in cols_lower:
            if candidate in col_key:
                return col_key
    return None


def _detectar_header_row(df_raw: pd.DataFrame) -> int:
    """
    Encontra o índice da linha que contém os cabeçalhos reais.
    Busca por palavras-chave comuns nas primeiras 20 linhas.
    """
    keywords = ["id", "tipo", "quest", "resposta", "alternativa", "choices", "answerkey", "gabarito"]
    for i in range(min(20, len(df_raw))):
        row_vals = [str(v).strip().lower() for v in df_raw.iloc[i].tolist()]
        matches = sum(1 for v in row_vals if any(k in v for k in keywords))
        if matches >= 2:  # pelo menos 2 colunas com palavras-chave
            return i
    return 0  # fallback: linha 0


def _parse_xlsx(conteudo_bytes: bytes) -> list:
    # Primeiro lê sem header para detectar onde está o cabeçalho real
    df_raw = pd.read_excel(io.BytesIO(conteudo_bytes), header=None)
    header_row = _detectar_header_row(df_raw)

    # Relê com o header correto
    df = pd.read_excel(io.BytesIO(conteudo_bytes), header=header_row)

    # Normaliza nomes de colunas (remove espaços extras, converte para str)
    df.columns = [str(c).strip() for c in df.columns]
    cols_lower = {c.lower(): c for c in df.columns}

    # Formato 1: formato interno legado (ID_Question, question_type, question, choices, answerKey)
    esperado_legado = {"id_question", "question_type", "question", "choices", "answerkey"}
    if esperado_legado.issubset(set(cols_lower.keys())):
        rename = {cols_lower[k]: {"id_question": "ID_Question",
                                   "question_type": "question_type",
                                   "question": "question",
                                   "choices": "choices",
                                   "answerkey": "answerKey"}[k]
                  for k in esperado_legado}
        return df.rename(columns=rename).fillna("").to_dict("records")

    # Formato 2: formato da planilha do usuário
    # Colunas: ID | Tipo de Questão | Questão | Respostas | Resposta Escolhida
    key_id        = _find_col(cols_lower, ["id"])
    key_tipo      = _find_col(cols_lower, ["tipo de quest", "question_type", "tipo"])
    key_questao   = _find_col(cols_lower, ["questão", "questao", "question"])
    key_respostas = _find_col(cols_lower, ["respostas", "choices", "alternativas"])
    key_escolhida = _find_col(cols_lower, ["resposta escolhida", "answerkey", "gabarito", "resposta"])

    if key_questao and key_respostas and key_escolhida:
        registros = []
        for _, row in df.iterrows():
            questao_val = str(row[cols_lower[key_questao]]).strip()
            # Pula linhas vazias ou NaN
            if not questao_val or questao_val.lower() in ("nan", "none", ""):
                continue
            registros.append({
                "ID_Question":   str(row[cols_lower[key_id]]).strip()    if key_id    else "",
                "question_type": str(row[cols_lower[key_tipo]]).strip()  if key_tipo  else "",
                "question":      questao_val,
                "choices":       str(row[cols_lower[key_respostas]]).strip(),
                "answerKey":     str(row[cols_lower[key_escolhida]]).strip(),
            })
        return registros

    # Fallback: trata como texto genérico
    textos = []
    for _, row in df.iterrows():
        texto = " | ".join(f"{k}: {v}" for k, v in row.items() if pd.notnull(v) and str(v).strip())
        if texto.strip():
            textos.append(texto)
    return textos


def _parse_json(conteudo: str) -> list:
    data = json.loads(conteudo)
    textos = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                textos.append(item)
            elif isinstance(item, dict):
                texto = " | ".join(str(v) for v in item.values() if v)
                textos.append(texto)
    elif isinstance(data, dict):
        texto = " | ".join(str(v) for v in data.values() if v)
        textos.append(texto)
    return [t for t in textos if t.strip()]


def _parse_csv(conteudo: str) -> list:
    textos = []
    reader = csv.DictReader(io.StringIO(conteudo))
    for row in reader:
        texto = " | ".join(f"{k}: {v}" for k, v in row.items() if v and v.strip())
        if texto.strip():
            textos.append(texto)
    return textos


def _parse_txt(conteudo: str) -> list:
    blocos = [b.strip() for b in conteudo.split("\n\n") if b.strip()]
    if len(blocos) <= 1:
        blocos = [l.strip() for l in conteudo.splitlines() if l.strip()]
    return blocos
