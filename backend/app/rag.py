"""Busca na base de conhecimento (data/kb) com TF-IDF.

Cada arquivo .md da base vira vários trechos, um por seção "## ".
Arquivos com nome de medicamento (ex.: metformina.md) marcam o trecho com
esse medicamento; arquivos de UBS (ubs_*.md) ficam com medicamento = None.

A busca tem duas etapas: se a pergunta cita um medicamento da base, só os
trechos dele concorrem e a seção é escolhida pelo conteúdo (sem o nome do
remédio, que pesaria igual em todas); se não cita, a busca é na base toda.
"""
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_DIR = Path(__file__).resolve().parents[2] / "data" / "kb"

# Calibrado com data/casos_teste_rag.json: a pergunta válida de menor score
# ficou em 0.155 e a fora do tema de maior score em 0.144.
# ponytail: margem estreita; recalibrar com o eval e deixar a triagem barrar
# o fora do tema antes da busca
SCORE_MINIMO = 0.15

# Palavras vazias saem antes da busca: sem isso, "qual", "de", "uma" fazem
# perguntas fora do tema parecerem próximas de qualquer trecho.
# "como", "quando" e "onde" ficam de fora da lista porque aparecem nos
# títulos das seções ("Como tomar", "Quando procurar atendimento").
PALAVRAS_VAZIAS = set("""
a o as os um uma uns umas ao aos de da do das dos em na no nas nos num numa
por pra pro para com sem e ou que qual quais quem porque se nao sim
eu voce ele ela me te meu minha seu sua isso esse essa este esta ja mais
muito tem ter ser estar foi sao vou posso pode ta to
""".split())

# "como devo usar X?" precisa achar a seção "Como tomar"
SINONIMOS = {"usar": "tomar", "utilizar": "tomar"}

# Palavras do título que não identificam o remédio ("ácido" aparece em
# "refluxo ácido", "sódica" em vários sais) e por isso não contam como citação.
NAO_IDENTIFICAM = {"acido", "cloridrato", "sodica", "potassica", "monoidratada"}

# Pistas de intenção para escolher a seção de uma bula. Cada pista é o início
# de uma palavra ou expressão, já sem acento ("esquec" pega "esqueci" e
# "esquecer"). Ganha a seção com mais pistas; o TF-IDF só desempata.
# ponytail: lista feita à mão; se o eval mostrar muitas perguntas sem pista,
# trocar por um classificador treinado ou pelo próprio LLM.
PISTAS_POR_SECAO = {
    "Para que serve": ["pra que", "para que", "serve", "indicad", "indicac", "funcao", "trata"],
    "Como tomar": ["como tomar", "como devo tomar", "como tomo", "como usar", "como devo usar",
                   "horario", "que horas", "antes ou depois", "depois de", "antes de comer", "comer",
                   "comida", "jejum", "refeic", "cafe", "partir", "mastig", "engol", "abrir",
                   "triturar", "com agua", "de manha", "a noite"],
    "Esqueci uma dose": ["esquec", "pulei", "dobrad", "dobrar", "perdi a dose", "atrasei"],
    "Álcool e interações": ["alcool", "bebida", "beber", "cerveja", "vinho", "cachaca", "mistur",
                            "interag", "interac", "junto com", "outros remedios", "outro remedio",
                            "suco", "toranja", "grapefruit"],
    "Efeitos colaterais": ["efeito", "colatera", "reac", "faz mal"],
    "Quando procurar atendimento": ["procur", "medico", "urgen", "emergen", "alerta", "demais",
                                    "overdose", "superdose", "dose maior", "intoxic", "gravid",
                                    "gestant", "amament", "alergi", "perigo", "hospital", "samu"],
    "Como guardar": ["guard", "armazen", "geladeira", "vencid", "validade", "temperatura",
                     "conserv", "calor", "umidade"],
}


def _normalizar(texto: str) -> str:
    """Minúsculas e sem acento."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def _preparar(texto: str) -> str:
    """Normalizado, sem palavras vazias e com sinônimos unificados."""
    return " ".join(SINONIMOS.get(p, p) for p in re.findall(r"\w+", _normalizar(texto))
                    if p not in PALAVRAS_VAZIAS)


def _pistas(pergunta: str, secao: str) -> int:
    """Quantas pistas da seção aparecem na pergunta."""
    texto = _normalizar(pergunta)
    for prefixo, pistas in PISTAS_POR_SECAO.items():
        if secao.startswith(prefixo):
            return sum(1 for p in pistas if re.search(r"\b" + p, texto))
    return 0


def _carregar_trechos(kb_dir: Path = KB_DIR) -> list[dict]:
    """Trechos da base. As chaves com "_" são internas da busca e não saem em buscar()."""
    trechos = []
    for arquivo in sorted(kb_dir.glob("*.md")):
        titulo, fonte, marcas, secao, corpo = arquivo.stem, "", "", None, []
        medicamento = None if arquivo.stem.startswith("ubs") else arquivo.stem

        def fechar_secao():
            if secao and corpo:
                conteudo = "\n".join(corpo).strip()
                nomes = set()
                if medicamento:
                    nomes = ({medicamento} | set(_preparar(f"{titulo} {marcas}").split())) - NAO_IDENTIFICAM
                trechos.append({
                    "texto": f"{titulo} — {secao}\n{conteudo}",
                    "fonte": fonte,
                    "medicamento": medicamento,
                    "_secao": f"{secao}\n{conteudo}",
                    "_titulo_secao": secao,
                    "_nomes": nomes,
                })

        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if linha.startswith("# "):
                titulo = linha[2:].strip()
            elif linha.startswith("Fonte:"):
                fonte = linha[len("Fonte:"):].strip()
            elif linha.startswith("Nomes comerciais:"):
                # marcas só servem para reconhecer o remédio na pergunta; não vão para o texto
                marcas = linha[len("Nomes comerciais:"):].replace(",", " ")
            elif linha.startswith("## "):
                fechar_secao()
                secao, corpo = linha[3:].strip(), []
            elif secao:
                corpo.append(linha)
        fechar_secao()
    return trechos


@lru_cache(maxsize=1)
def _indice():
    trechos = _carregar_trechos()
    if not trechos:
        return None, None, None, []
    # n-gramas de caracteres pegam variações do português
    # ("esqueci" ~ "esquecimento", "álcool" ~ "alcoólica") sem precisar de stemmer
    vetorizador = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                                  preprocessor=_preparar, sublinear_tf=True)
    matriz_completa = vetorizador.fit_transform(t["texto"] for t in trechos)
    matriz_secao = vetorizador.transform(t["_secao"] for t in trechos)
    return vetorizador, matriz_completa, matriz_secao, trechos


def buscar(pergunta: str, k: int = 3) -> list[dict]:
    """Retorna até k trechos mais parecidos com a pergunta.

    Lista vazia quando a pergunta não cita remédio da base e nada passa do
    SCORE_MINIMO: o pipeline deve então responder que a fonte não cobre a
    dúvida (OWASP LLM09), em vez de deixar o modelo inventar.

    "score" é a similaridade TF-IDF; quando a pergunta cita um remédio, soma-se
    o número de pistas da seção (por isso pode passar de 1).
    """
    vetorizador, matriz_completa, matriz_secao, trechos = _indice()
    if not trechos or not pergunta.strip():
        return []
    palavras = _preparar(pergunta).split()
    citados = {i for i, t in enumerate(trechos) if t["_nomes"] & set(palavras)}

    if citados:
        # o nome do próprio remédio sai da pergunta: ele aparece no corpo de
        # várias seções e puxaria a seção errada ("pra que serve" -> "Interações").
        # O nome de outro remédio citado fica, porque aí indica interação.
        scores = {}
        for nomes in {frozenset(trechos[i]["_nomes"]) for i in citados}:
            consulta = vetorizador.transform([" ".join(p for p in palavras if p not in nomes)])
            proprios = [i for i in citados if trechos[i]["_nomes"] == nomes]
            for i, s in zip(proprios, cosine_similarity(consulta, matriz_secao[proprios])[0]):
                scores[i] = _pistas(pergunta, trechos[i]["_titulo_secao"]) + s
        melhores = sorted(citados, key=lambda i: -scores[i])[:k]
    else:
        scores = cosine_similarity(vetorizador.transform([pergunta]), matriz_completa)[0]
        melhores = [i for i in scores.argsort()[::-1][:k] if scores[i] >= SCORE_MINIMO]

    return [{"texto": trechos[i]["texto"], "fonte": trechos[i]["fonte"],
             "medicamento": trechos[i]["medicamento"], "score": round(float(scores[i]), 3)}
            for i in melhores]


if __name__ == "__main__":
    # python -m backend.app.rag             -> roda todos os casos de data/casos_teste_rag.json
    # python -m backend.app.rag "pergunta"  -> mostra os trechos encontrados
    import json
    import sys

    if len(sys.argv) > 1:
        for r in buscar(" ".join(sys.argv[1:])):
            print(f"[{r['score']}] {r['texto'].splitlines()[0]}  ({r['fonte']})")
        sys.exit()

    casos = json.loads((KB_DIR.parent / "casos_teste_rag.json").read_text(encoding="utf-8"))
    falhas = []
    for c in casos:
        resultado = buscar(c["pergunta"])
        if c.get("vazio"):
            ok = resultado == []
        else:
            ok = (bool(resultado) and resultado[0]["medicamento"] == c["medicamento"]
                  and c["secao"] in resultado[0]["texto"].splitlines()[0])
        if not ok:
            veio = resultado[0]["texto"].splitlines()[0] if resultado else "[]"
            falhas.append(f"[{c['categoria']}] {c['pergunta']!r} -> {veio}")
    print("\n".join(falhas))
    print(f"{len(casos) - len(falhas)}/{len(casos)} casos passaram ({len(_indice()[3])} trechos indexados)")
    sys.exit(1 if falhas else 0)
