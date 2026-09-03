# Quality-gate + repair for Grill-API (loaded into app.py via exec).
# Conservative: only reject/repair BAD labels. Good noun phrases stay as-is.
# Tras Temas listos: consistencia reusa last_grupos (no reconstruye el grafo)
# y generate_output_excel no re-audita filas que ya traen Contexto analizado.

MODELO_CLASIF_DEFAULT = "gpt-4.1-nano-2025-04-14"
_MODELO_OVERRIDE_MSG = ""
MAX_LLM_CALLS_POR_ETIQUETA = 0
MAX_PALABRAS_FRASE_EVENTO = 8
MAX_PALABRAS_SUBTEMA = 8
TAMANO_LOTE_LLM_SUBTEMA = 30
TAMANO_LOTE_LLM_TEMA = 30
MAX_TOKENS_LOTE_SUBTEMA = 800
MAX_TOKENS_LOTE_TEMA = 600
MAX_BLOQUE_TOKEN = 80
_PARES_GRAFO_REVISADOS = 0
_LAST_PHASE_TIMINGS = []

COLUMNAS_XLSX_OBLIGATORIAS = (
    "ID Noticia", "Fecha", "Hora", "Medio", "Tipo de Medio",
    "Sección - Programa", "Región", "Título", "Tono IA", "Tema", "Subtema",
    "Link Nota", "Resumen - Aclaracion", "Link (Streaming - Imagen)",
    "Menciones - Empresa", "ID duplicada", "Cuerpo Completo",
    "Contexto analizado", "Coincidencia marca", "Origen coincidencia",
    "Tono", "Grupo noticia",
)
COLUMNAS_XLSX_EXTRA = (
    "Autor - Conductor", "Nro. Pagina", "Dimensión",
    "Duración - Nro. Caracteres", "CPE", "Audiencia", "Tier",
)

# Affiliation / byline (generic for any client, not only UAO)
TEMA_ESTUDIANTES_EGRESADOS = "Estudiantes y egresados"
SUBTEMA_AUTORIA = "Afiliación académica de egresados"
_TEMA_AUTORIA_EGRESADOS = TEMA_ESTUDIANTES_EGRESADOS
_TEMA_AUTORIA_ESTUDIANTES = TEMA_ESTUDIANTES_EGRESADOS
_TEMA_AUTORIA_GENERAL = TEMA_ESTUDIANTES_EGRESADOS

_RE_CREDITO_ROL = re.compile(
    r'\b(editor(?:a)?(?:\s+web)?|periodista|comunicador(?:a)?|redactor(?:a)?|'
    r'fotograf[oa]|corresponsal|estudiante(?:s)?|egresad[oa]s?|'
    r'en formaci[oó]n|realizado por|producci[oó]n de|conduccion de)\b',
    re.I,
)
_RE_SPLIT_CREDITOS = re.compile(
    r'(?=(?:Estudiante en formaci[oó]n|Editor(?:a)? web|Periodista egresad|'
    r'Editora web|Comunicador(?:a)? (?:egresad|de)|Redactor(?:a)? (?:egresad|de)|'
    r'Egresad[oa]s?\s+de))',
    re.I,
)

_CABEZAS_SUBTEMA_VALIDAS = {
    "lanzamiento", "apertura", "inauguracion", "estreno", "presentacion", "anuncio",
    "convenio", "acuerdo", "alianza", "pacto", "firma", "colaboracion", "cooperacion",
    "inversion", "proyecto", "programa", "plan", "campana", "iniciativa", "propuesta",
    "foro", "congreso", "cumbre", "encuentro", "feria", "festival", "evento",
    "seminario", "taller", "capacitacion", "formacion", "educacion", "visita",
    "premio", "premiacion", "reconocimiento", "distincion", "condecoracion", "homenaje",
    "nombramiento", "designacion", "renuncia", "contratacion", "investigacion",
    "denuncia", "demanda", "sancion", "multa", "regulacion", "reforma", "aprobacion",
    "renovacion", "ampliacion", "operacion", "publicacion", "informe", "estudio",
    "articulo", "ranking", "desarrollo", "experiencia", "pronostico", "consulta",
    "acreditacion", "certificacion", "afiliacion", "credito", "autoria",
    "construccion", "infraestructura", "modernizacion", "exportacion", "comercializacion",
    "laboratorio", "carrera", "convenio",
}

_ADJ_MULETILLA_ETIQUETA = {
    "unico", "unica", "unicos", "unicas", "nuevo", "nueva", "nuevos", "nuevas",
    "gran", "grande", "grandes", "especial", "especiales",
    "exclusivo", "exclusiva", "este", "esta", "estos", "estas",
    "ese", "esa", "esos", "esas", "primer", "primera", "primero",
}
_CABEZAS_CONTENEDORAS_DEBILES = {
    "experiencia", "entorno", "espacio", "ambiente", "propuesta", "iniciativa",
    "oferta", "apuesta", "concepto", "opcion", "alternativa", "manera", "forma",
}
_RE_ESLOGAN_SUBTEMA = re.compile(
    r"(?i)\b("
    r"unic[oa]s?\s+en\s+su\s+(tipo|clase|genero|estilo)|"
    r"nueva\s+forma\s+de\s+(habitar|vivir|invertir|ser|estar)|"
    r"invita(?:n)?\s+a\s+descubrir|forma\s+de\s+habitar"
    r")\b"
)
_CONECTORES_ETIQUETA = {
    "de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas", "al", "lo",
    "y", "e", "o", "u", "en", "sobre", "para", "por", "con", "sin", "ante", "bajo",
    "hacia", "hasta", "entre", "tras", "contra", "desde", "segun", "mediante", "a",
    "que", "como", "cuando", "donde", "su", "sus",
}
_PREP_ETIQUETA = {"de", "del", "para", "sobre", "en", "con", "por", "ante", "hacia", "entre"}
_ETIQUETAS_GENERICAS = {
    "sin tema", "varios", "n/a", "na", "nan", "-",
    "cobertura de informacion relevante", "cobertura informativa general",
    "cobertura de informacion", "cobertura informativa", "cobertura general",
    "informacion relevante", "informacion general", "actividad institucional",
    "actividad corporativa", "gestion corporativa", "gestion institucional",
    "impacto reputacional", "tema general", "asuntos varios", "hechos diversos",
    "noticias", "informacion", "actualidad", "general",
    "hecho de la noticia", "asuntos relacionados",
}
_ACCIONES_SUBTEMA = [
    (r"\b(lanzamiento|lanza|lanzo|estrena|estreno|presenta|presento|presentacion)\b", "Lanzamiento"),
    (r"\b(anuncia|anuncio)\b", "Anuncio"),
    (r"\b(inaugura|inauguro|apertura|abre|abrio)\b", "Apertura"),
    (r"\b(firma|firmo|suscribe|suscribio|convenio|alianza|acuerdo)\b", "Convenio"),
    (r"\b(recibe|recibio|premio|reconocimiento|reconocida|reconocido|reconocio|"
     r"galardon|distincion|renueva|renovo|renovacion)\b", "Reconocimiento"),
    (r"\b(acreditacion|acredita|acreditada|certificacion)\b", "Renovación"),
    (r"\b(investiga|investigacion|sancion|denuncia|demanda|multa)\b", "Investigación"),
    (r"\b(proyecto|programa|plan)\b", "Proyecto"),
    (r"\b(encuentro)\b", "Encuentro"),
    (r"\b(foro|congreso|cumbre|seminario|taller)\b", "Foro"),
    (r"\b(desarrollo|desarrolla)\b", "Desarrollo"),
]
_ACCION_CANON = {
    "lanzamiento": "Lanzamiento", "lanza": "Lanzamiento", "lanzo": "Lanzamiento",
    "estrena": "Lanzamiento", "estreno": "Lanzamiento", "presenta": "Lanzamiento",
    "anuncia": "Anuncio", "anuncio": "Anuncio",
    "inaugura": "Apertura", "apertura": "Apertura", "abre": "Apertura",
    "firma": "Convenio", "convenio": "Convenio", "alianza": "Convenio",
    "recibe": "Reconocimiento", "recibio": "Reconocimiento",
    "reconocimiento": "Reconocimiento", "premio": "Reconocimiento",
    "renueva": "Renovación", "renovo": "Renovación", "renovacion": "Renovación",
    "acreditacion": "Renovación", "acredita": "Renovación",
    "investiga": "Investigación", "investigacion": "Investigación",
    "proyecto": "Proyecto", "encuentro": "Encuentro", "foro": "Foro",
    "desarrollo": "Desarrollo",
}
_VERBOS_NARRATIVOS_EVENTO = {
    "reunio", "reune", "reunieron", "congrego", "congrega", "convoco", "convoca",
    "conto", "participo", "asistio", "asistieron",
}
_VERBOS_CONJUGADOS_RESTANTES = {
    "hara", "haran", "jugara", "jugaran", "tendra", "tendran",
    "tengo", "tiene", "tienen", "necesita", "necesito", "sabe", "saben",
    "confirma", "llega", "llegan", "gana", "ganan", "sera", "estara",
}
_RE_VERBO_SUBTEMA = re.compile(
    r"(aron|ieron|aban|ian|ando|iendo|ara|era|ira|aran|eran|iran)$"
)
_DOMINIOS_TEMA = [
    (r"\b(acreditaci|certificaci|alta calidad|renovacion de acredit)\b", "Acreditación institucional"),
    (r"\b(egresad|alumni|graduad|estudiante en formacion|afiliacion academica)\b", TEMA_ESTUDIANTES_EGRESADOS),
    (r"\b(carrera|formacion profesional|medicina deportiva|beca|matricula)\b", "Formación profesional"),
    (r"\b(salud|hospital|clinica|medico|paciente|vacun)\b", "Salud pública"),
    (r"\b(via|vial|carretera|transporte|movilidad|puerto)\b", "Infraestructura vial"),
    (r"\b(convenio|alianza|acuerdo|cooperacion)\b", "Alianzas institucionales"),
    (r"\b(premio|reconocimiento|galardon|ranking)\b", "Reconocimientos institucionales"),
    (r"\b(investigacion|denuncia|demanda|sancion|multa)\b", "Procesos de investigación"),
    (r"\b(inversion|financi|presupuesto|credito)\b", "Inversión y financiamiento"),
    (r"\b(laboratorio|ciencia|tecnolog|innovacion|digital)\b", "Ciencia y tecnología"),
    (r"\b(deporte|carrera deportiva|atleta|olimp)\b", "Actividad deportiva"),
    (r"\b(cultura|patrimonio|festival|libro)\b", "Cultura y patrimonio"),
    (r"\b(empleo|trabajo|laboral|contratacion)\b", "Empleo y trabajo"),
    (r"\b(ambiental|sostenib|clima|energia)\b", "Sostenibilidad ambiental"),
    (r"\b(residencial|lujo|inmobili|vivienda|proyecto residencial)\b", "Desarrollo inmobiliario"),
    (r"\b(protesta|marcha|paro|movilizacion)\b", "Protesta estudiantil"),
    (r"\b(encuentro|foro|congreso|cumbre)\b", "Eventos del sector"),
    (r"\b(exportacion|avicol|volatil)\b", "Sector productivo"),
]
_NUCLEOS_TEMA_INCOMPATIBLES = (
    ({"acredit", "certific"}, {"estudiant", "egresad", "alumn", "afiliacion", "autoria", "periodist"}),
    ({"acredit", "certific"}, {"protest", "marcha", "paro"}),
    ({"estudiant", "egresad"}, {"protest", "marcha", "paro"}),
    ({"residencial", "inmobili", "lujo"}, {"acredit", "estudiant"}),
)
_NUCLEOS_MISMO_HECHO = (
    {"acredit", "calidad"},
    {"acredit", "certific"},
    {"acredit", "renov"},
    {"laboratorio", "biotecnolog"},
    {"carrera", "deportiv"},
    {"residencial", "lujo"},
)

# Titular verbs only — event nouns like "Lanzamiento" must remain valid heads.
_PATRON_TITULAR = re.compile(
    r"^(nuevo|nueva|anuncia|lanza|presenta|inaugura|llega|abre|inicia|"
    r"logra|alcanza|supera|confirma|destaca|revela|señala|advierte)\b",
    re.IGNORECASE,
)


def _flag_env(nombre, default="0") -> bool:
    v = str(os.environ.get(nombre, default)).strip().lower()
    return v in ("1", "true", "yes", "on", "si", "sí")


def _es_gpt5_nano(nombre) -> bool:
    return "gpt-5-nano" in unidecode(str(nombre or "")).lower()


def _resolver_modelo_clasificacion():
    global _MODELO_OVERRIDE_MSG
    raw = os.environ.get("OPENAI_CLASIF_MODEL")
    if not raw:
        try:
            raw = st.secrets.get("OPENAI_CLASIF_MODEL")
        except Exception:
            raw = None
    raw = str(raw or "").strip()
    if raw and raw != MODELO_CLASIF_DEFAULT:
        _MODELO_OVERRIDE_MSG = (
            f"OPENAI_CLASIF_MODEL={raw} se ignora; se usa {MODELO_CLASIF_DEFAULT}."
        )
    else:
        _MODELO_OVERRIDE_MSG = ""
    return MODELO_CLASIF_DEFAULT


def refrescar_modelo_clasificacion():
    global OPENAI_MODEL_CLASIFICACION
    OPENAI_MODEL_CLASIFICACION = _resolver_modelo_clasificacion()
    return OPENAI_MODEL_CLASIFICACION


def advertencia_modelo_clasificacion() -> str:
    return _MODELO_OVERRIDE_MSG


class _PBarNulo:
    def progress(self, *args, **kwargs):
        return None


class _FaseTimer:
    def __init__(self, pbar=None):
        self.t0 = time.perf_counter()
        self.last = self.t0
        self.marks = []
        self.pbar = pbar

    def mark(self, name, frac=None, detail=""):
        now = time.perf_counter()
        dt = now - self.last
        tot = now - self.t0
        self.marks.append((name, dt, tot))
        self.last = now
        msg = f"{name}: {dt:.2f}s"
        if detail:
            msg += f" · {detail}"
        if self.pbar is not None and frac is not None:
            try:
                self.pbar.progress(frac, msg)
            except Exception:
                pass
        try:
            st.caption(msg)
        except Exception:
            pass
        return msg

    def report(self):
        total = self.marks[-1][2] if self.marks else 0.0
        parts = [f"{n}={dt:.2f}s" for n, dt, _ in self.marks]
        return f"total={total:.2f}s | " + " | ".join(parts)


def _registrar_timings(timer):
    global _LAST_PHASE_TIMINGS
    _LAST_PHASE_TIMINGS = list(timer.marks)
    return timer.report()


def _sin_comas_etiqueta(texto: str) -> str:
    s = re.sub(r"[,，;|/]+", " ", str(texto or ""))
    return re.sub(r"\s+", " ", s).strip()


def _normaliza_token(w):
    return re.sub(r"[^a-z0-9]", "", unidecode(str(w or "").lower()))


def _stem_es(w):
    s = _normaliza_token(w)
    if s.endswith("es") and len(s) - 2 >= 4:
        return s[:-2]
    if s.endswith("s") and len(s) - 1 >= 4 and s[-2] in "aeiou":
        return s[:-1]
    for suf in ("cion", "sion", "mente", "ando", "iendo"):
        if len(s) > len(suf) + 3 and s.endswith(suf):
            return s[: -len(suf)]
    return s


def _es_etiqueta_generica(etiqueta: str) -> bool:
    raw = str(etiqueta or "").strip().strip("\"'")
    if not raw:
        return True
    n = string_norm_label(raw)
    if not n:
        return True
    if n in {string_norm_label(x) for x in _ETIQUETAS_GENERICAS}:
        return True
    parts = n.split()
    if parts and parts[0] == "cobertura" and any(
        x in parts for x in ("relevante", "general", "informacion", "noticia", "noticias")
    ):
        return True
    return False


def _es_cabeza_nominal_valida(n) -> bool:
    if not n:
        return False
    if n in _CABEZAS_SUBTEMA_VALIDAS:
        return True
    if n.endswith("es") and n[:-2] in _CABEZAS_SUBTEMA_VALIDAS:
        return True
    if n.endswith("s") and n[:-1] in _CABEZAS_SUBTEMA_VALIDAS:
        return True
    return False


def _es_participio_cabeza(w) -> bool:
    n = _normaliza_token(w)
    if not n or _es_cabeza_nominal_valida(n):
        return False
    return bool(re.search(r"(ada|ado|idas|idos|iendo|ando)$", n)) and len(n) >= 6


def _es_resto_verbal(token) -> bool:
    n = _normaliza_token(token)
    if not n or _es_cabeza_nominal_valida(n):
        return False
    if n in _VERBOS_LEAD_SUBTEMA or n in _VERBOS_NARRATIVOS_EVENTO:
        return True
    if n in _VERBOS_CONJUGADOS_RESTANTES:
        return True
    if _RE_VERBO_SUBTEMA.search(n) and len(n) >= 5:
        return True
    if n.startswith(("enfrent", "present", "anunci", "firm", "lanz", "inaugur", "investiga")):
        return True
    if len(n) >= 4 and re.search(r"(ara|era|ira|aran|eran|iran|aria|eria|iria)$", n):
        if n not in {"cara", "manera", "bandera", "frontera", "primavera", "espera"}:
            return True
    return False


def _es_verbo_cabeza(w) -> bool:
    n = _normaliza_token(w)
    if not n or _es_cabeza_nominal_valida(n):
        return False
    return _es_resto_verbal(w)


def _norm_autoria_key(s) -> str:
    return re.sub(r"[^a-z]+", "", unidecode(str(s or "").lower()))


def _es_subtema_autoria(etiqueta) -> bool:
    n = _norm_autoria_key(etiqueta)
    if not n:
        return False
    if n in {"articuloperiodistico", "articuloperiodista"} or n.startswith("articuloperiodistic"):
        return True
    return any(
        tok in n
        for tok in (
            "afiliacionacademica", "afiliaciondeestudiante", "estudianteenformacion",
            "periodistaegresado", "creditoperiodistico", "estudiantesegresados",
            "egresadodelainstitucion", "estudianteyegresado",
        )
    )


def _subtema_autoria_frase(contexto) -> str:
    """4+ word noun phrase about affiliation/formación — never accreditation glue."""
    blob = unidecode(str(contexto or "").lower())
    est = bool(re.search(r"estudiante", blob))
    egr = bool(re.search(r"egresad", blob))
    form = bool(re.search(r"en formacion", blob))
    per = bool(re.search(r"periodista|editor|comunicador|redactor", blob))
    if est and egr and form:
        return "Estudiante y egresado en formación"
    if est and form:
        return "Estudiante en formación universitaria"
    if egr and per:
        return "Periodista egresado de la institución"
    if egr:
        return "Afiliación académica de egresados"
    if est:
        return "Afiliación de estudiante universitario"
    if per:
        return "Crédito periodístico de la institución"
    return "Afiliación académica en formación"


def _es_oracion_credito(oracion):
    s = unidecode((oracion or "").strip().lower())
    if not s:
        return False
    if s.startswith((
        "estudiante en formacion", "estudiante de", "editor ", "editora ",
        "periodista ", "comunicador", "redactor", "egresado", "egresada",
    )):
        return True
    if re.search(r"\b(egresad[oa]s?|estudiante(?:s)?|en formacion)\b", s):
        if _RE_CREDITO_ROL.search(s) or re.search(r"\b(universidad|instituci|colegio|marca)\b", s):
            if not re.search(r"\b(acredit|certific|investiga|sancion|lanza|inaugur|convenio)\b", s):
                return True
    return False


def _segmentar_creditos(texto) -> list:
    s = re.sub(r"\s+", " ", str(texto or "")).strip()
    if not s:
        return []
    partes = [p.strip() for p in _RE_SPLIT_CREDITOS.split(s) if p and p.strip()]
    if len(partes) >= 2:
        return partes
    return _partir_oraciones(s) or [s]


def _ventana_mencion_es_credito(texto, marca, aliases=None) -> bool:
    raw = unidecode(str(texto or "").lower())
    if not raw:
        return False
    halladas = False
    for nombre in _variantes_marca(marca, aliases):
        nn = unidecode(str(nombre or "").lower()).strip()
        if len(nn) < 3:
            continue
        start = 0
        while True:
            i = raw.find(nn, start)
            if i < 0:
                break
            halladas = True
            win = raw[max(0, i - 100): i + len(nn) + 100]
            if not _RE_CREDITO_ROL.search(win):
                return False
            start = i + max(1, len(nn))
    return halladas


def _es_texto_solo_autoria(texto, marca="", aliases=None) -> bool:
    src = str(texto or "").strip()
    if not src or not marca or not _menciona_marca_o_alias(src, marca, aliases):
        return False
    if re.search(r"\b(acredit|certific|investiga|sancion|lanza|inaugur|convenio de formacion profesional)\b",
                 unidecode(src.lower())):
        if not re.search(r"\b(egresad|estudiante|en formacion|periodista|editor)\b", unidecode(src.lower())):
            return False
        # Mixed: real event + byline. Only authorship if EVERY brand mention is byline.
    segs = _segmentar_creditos(src)
    menciones = 0
    creditos = 0
    for seg in segs:
        if not _menciona_marca_o_alias(seg, marca, aliases):
            continue
        menciones += 1
        if _es_oracion_credito(seg) or _ventana_mencion_es_credito(seg, marca, aliases):
            creditos += 1
    if menciones and creditos == menciones:
        return True
    return _ventana_mencion_es_credito(src, marca, aliases) and not re.search(
        r"\b(acredit|certific|investiga|sancion|lanza|inaugur)\b", unidecode(src.lower())
    )


def _es_contexto_solo_autoria(titulo, contexto, marca="", aliases=None) -> bool:
    if _menciona_marca_o_alias(titulo, marca, aliases) and not _es_oracion_credito(titulo):
        return False
    ctx = str(contexto or "").strip()
    if not ctx:
        return False
    return _es_texto_solo_autoria(ctx, marca, aliases)


def _mapear_tema_autoria_pkl(candidato, blob, clases) -> str:
    if not clases:
        return candidato
    scored = []
    blob_n = unidecode(f"{candidato} {blob}".lower())
    for c in clases:
        nc = unidecode(str(c).lower())
        score = 0.0
        if "egresad" in nc and "egresad" in blob_n:
            score += 5.0
        if "estudiant" in nc and "estudiant" in blob_n:
            score += 4.0
        if any(k in nc for k in ("autoria", "autoría", "periodis", "alumni", "egres")):
            score += 3.0
        score += _score_clase_pkl(candidato + " " + blob, c)
        scored.append((score, not _es_etiqueta_generica(c), c))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return scored[0][2]


def _tema_autoria(contexto, marca="", aliases=None, clases_pkl=None) -> str:
    cand = TEMA_ESTUDIANTES_EGRESADOS
    if clases_pkl:
        return _mapear_tema_autoria_pkl(cand, str(contexto or ""), clases_pkl)
    return capitalizar_etiqueta(cand)


def _aplicar_etiquetas_autoria(titulos, textos, temas, subtemas, marca, aliases=None, clases_pkl=None):
    temas = list(temas)
    subtemas = list(subtemas)
    n = len(subtemas)
    for i in range(n):
        tit = titulos[i] if titulos is not None and i < len(titulos) else ""
        tx = textos[i] if i < len(textos) else ""
        if _es_contexto_solo_autoria(tit, tx, marca, aliases) or _es_texto_solo_autoria(tx, marca, aliases):
            subtemas[i] = _subtema_autoria_frase(tx)
            temas[i] = _tema_autoria(tx, marca, aliases, clases_pkl)
    return temas, subtemas


def _tokens_marca_set(marca, aliases=None) -> set:
    toks = set()
    for n in _variantes_marca(marca, aliases):
        for t in _normalizar_mencion(n).split():
            if len(t) >= 3:
                toks.add(t)
    return toks


def _tokens_distintivos_historia(texto: str, marca="", aliases=None, min_len: int = 4) -> set:
    return _tokens_distintivos(texto, min_len=min_len) - _tokens_marca_set(marca, aliases)


def _stems_contenido(texto) -> set:
    return {_stem_es(t) for t in re.findall(r"[a-z]{4,}", unidecode(str(texto or "").lower()))}


def _nucleo_evento_compartido(texto_a, texto_b) -> bool:
    sa, sb = _stems_contenido(texto_a), _stems_contenido(texto_b)
    for grupo in _NUCLEOS_MISMO_HECHO:
        def _hit(stems, tok):
            return any(x.startswith(tok) or tok.startswith(x) for x in stems if len(x) >= 4)
        if all(_hit(sa, t) for t in grupo) and all(_hit(sb, t) for t in grupo):
            return True
    return False


def _historias_son_el_mismo_hecho(texto_a, texto_b, marca="", aliases=None, min_overlap=0.40) -> bool:
    a = str(texto_a or "").strip()
    b = str(texto_b or "").strip()
    if not a or not b:
        return False
    if marca and (
        _es_texto_solo_autoria(a, marca, aliases)
        or _es_texto_solo_autoria(b, marca, aliases)
    ):
        return False
    if _hay_conflicto_accion(a, b):
        return False
    na = normalize_title_for_comparison(a)
    nb = normalize_title_for_comparison(b)
    title_sim = SequenceMatcher(None, na, nb).ratio() if na and nb else 0.0
    if na and nb and title_sim >= 0.96:
        return True
    oa = _tokens_distintivos_historia(a, marca, aliases)
    ob = _tokens_distintivos_historia(b, marca, aliases)
    inter = oa & ob if oa and ob else set()
    ratio = (len(inter) / max(1, min(len(oa), len(ob)))) if oa and ob else 0.0
    nucleo = _nucleo_evento_compartido(a, b)
    # Same-fact paraphrases (UAO acreditación pair): shared event nucleus +
    # some title/token overlap. Do not require ratio ≥ 0.60 — that leak kept
    # "Reconocimiento de alta calidad académica" vs "...institucional" apart.
    if nucleo and (title_sim >= 0.48 or len(inter) >= 2 or ratio >= 0.28):
        return True
    if not oa or not ob:
        return False
    if len(inter) < 2:
        return False
    if ratio < min_overlap:
        return False
    excl_a, excl_b = oa - ob, ob - oa
    if len(excl_a) >= 2 and len(excl_b) >= 2 and ratio < 0.60:
        return False
    return True


def _hechos_nucleo_distinto(texto_a, texto_b, marca="", aliases=None) -> bool:
    if _hay_conflicto_accion(texto_a, texto_b):
        return True
    if _nucleo_evento_compartido(texto_a, texto_b):
        return False
    oa = _tokens_distintivos_historia(texto_a, marca, aliases)
    ob = _tokens_distintivos_historia(texto_b, marca, aliases)
    if not oa or not ob:
        return True
    inter = oa & ob
    excl_a, excl_b = oa - ob, ob - oa
    ratio = len(inter) / max(1, min(len(oa), len(ob)))
    if len(excl_a) >= 2 and len(excl_b) >= 2 and ratio < 0.45:
        return True
    if len(inter) < 2 and ratio < 0.30:
        return True
    return False


def _pueden_compartir_subtema(texto_a, texto_b, marca="", aliases=None, estricto=True) -> bool:
    if _hay_conflicto_accion(texto_a, texto_b):
        return False
    if _historias_son_el_mismo_hecho(texto_a, texto_b, marca, aliases):
        return True
    if estricto:
        return False
    return not _hechos_nucleo_distinto(texto_a, texto_b, marca, aliases)


def _grupo_mismo_hecho(textos, idxs, marca="", aliases=None) -> bool:
    if not idxs:
        return False
    base = textos[idxs[0]]
    return all(
        _historias_son_el_mismo_hecho(base, textos[i], marca, aliases)
        for i in idxs[1:]
    )


def _prefijo_bloqueo(texto, n=12) -> str:
    compact = re.sub(r"[^a-z0-9]+", "", unidecode(str(texto or "").lower()))
    return compact[:n]


def _es_clave_prefijo_bloqueo(k: str) -> bool:
    return str(k).startswith(("#p:", "#r:", "#eq:", "#re:", "#1:", "#n:"))


def _claves_bloqueo_fila(titulo_norm, texto="", marca="", aliases=None, resumen_norm="") -> set:
    claves = set()
    t = str(titulo_norm or "").strip()
    if t:
        claves.add("#eq:" + t[:160])
        pref = _prefijo_bloqueo(t, 12)
        if pref:
            claves.add("#p:" + pref)
            claves.add("#1:" + pref)
        for tok in list(_tokens_distintivos_historia(t, marca, aliases))[:8]:
            claves.add(tok)
    r = str(resumen_norm or "").strip()
    if r:
        claves.add("#re:" + r[:200])
        rp = _prefijo_bloqueo(r, 12)
        if rp:
            claves.add("#r:" + rp)
    if texto:
        for tok in list(_tokens_distintivos_historia(str(texto), marca, aliases))[:6]:
            claves.add("tx:" + tok)
        stems = _stems_contenido(texto)
        for grupo in _NUCLEOS_MISMO_HECHO:
            if all(
                any(x.startswith(t) or t.startswith(x) for x in stems if len(x) >= 4)
                for t in grupo
            ):
                claves.add("#n:" + "+".join(sorted(grupo)))
    return claves


def _pares_bloqueados(claves_por_fila, max_bloque=MAX_BLOQUE_TOKEN, max_pares=None):
    indice = defaultdict(list)
    for i, claves in enumerate(claves_por_fila):
        for k in claves or ():
            if k:
                indice[k].append(i)
    pares = set()
    for k, idxs in indice.items():
        if len(idxs) < 2:
            continue
        u = sorted(set(idxs))
        if not _es_clave_prefijo_bloqueo(k) and len(u) > max_bloque:
            continue
        for a in range(len(u)):
            for b in range(a + 1, len(u)):
                pares.add((u[a], u[b]))
    return pares


def _ratio_norm(a, b) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if min(len(a), len(b)) >= 20 and (a in b or b in a):
        return 0.96
    return SequenceMatcher(None, a, b).ratio()


def _cos_par(a, b) -> float:
    if a is None or b is None:
        return 0.0
    va = np.asarray(a, dtype=np.float64)
    vb = np.asarray(b, dtype=np.float64)
    na = np.linalg.norm(va)
    nb = np.linalg.norm(vb)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (na * nb))


def _norm_cmp_texto(texto) -> str:
    return re.sub(r"\W+", " ", unidecode(str(texto or "").lower())).strip()


def _embeddings_reusar(textos, embs=None):
    n = len(textos)
    if embs is not None and len(embs) == n:
        missing = [i for i, e in enumerate(embs) if e is None]
        if not missing:
            return list(embs)
        filled = get_embeddings_batch([textos[i] for i in missing])
        out = list(embs)
        for j, i in enumerate(missing):
            out[i] = filled[j]
        return out
    return get_embeddings_batch(list(textos))


def _subtema_grounded(etiqueta, fuentes, estricto=False):
    if not etiqueta or not fuentes:
        return False
    fuente_tokens, fuente_stems = set(), set()
    for f in fuentes:
        for w in re.findall(r"[a-z0-9]{4,}", unidecode(str(f).lower())):
            fuente_tokens.add(w)
            fuente_stems.add(_stem_es(w))
    contenido = []
    for w in str(etiqueta).split():
        wt = _normaliza_token(w)
        if not wt or len(wt) < 4 or wt in _CONECTORES_ETIQUETA:
            continue
        contenido.append(wt)
    if not contenido:
        return True
    no_coinciden = 0
    for i, w in enumerate(contenido):
        ws = _stem_es(w)
        if w in fuente_tokens or ws in fuente_tokens or ws in fuente_stems:
            continue
        if any((fs.startswith(w) or w.startswith(fs)) and min(len(fs), len(w)) >= 4 for fs in fuente_stems):
            continue
        if i == 0 and _es_cabeza_nominal_valida(w):
            continue
        no_coinciden += 1
    if estricto:
        return no_coinciden == 0
    return no_coinciden * 2 <= len(contenido)


def _etiqueta_pertenece_al_texto(etiqueta, texto) -> bool:
    if not etiqueta or _es_etiqueta_generica(etiqueta):
        return False
    if not str(texto or "").strip():
        return False
    if _es_subtema_autoria(etiqueta) or string_norm_label(etiqueta) == string_norm_label(TEMA_ESTUDIANTES_EGRESADOS):
        return True
    return _subtema_grounded(etiqueta, [texto], estricto=True)


def _contiene_eslogan_subtema(etiqueta: str) -> bool:
    et = str(etiqueta or "").strip()
    if not et:
        return True
    if _RE_ESLOGAN_SUBTEMA.search(et):
        return True
    n = unidecode(et.lower())
    if re.search(
        r"(?:^|\b(?:de|del)\s+)(este|esta|ese|esa|estos|estas)\s+"
        r"(desarrollo|proyecto|propuesta|iniciativa|experiencia|entorno)\s*$",
        n,
    ):
        return True
    return False


def _de_adjetivo_huerfano(etiqueta: str) -> bool:
    m = re.search(
        r"(?i)\b(?:de|del)\s+("
        + "|".join(sorted(_ADJ_MULETILLA_ETIQUETA, key=len, reverse=True))
        + r")\b(?:\s+(\S+))?",
        str(etiqueta or ""),
    )
    if not m:
        return False
    siguiente = m.group(2)
    if not siguiente:
        return True
    ns = _normaliza_token(siguiente)
    if not ns or ns in STOPWORDS_ES or ns in _PREP_ETIQUETA or ns in _ADJ_MULETILLA_ETIQUETA:
        return True
    return ns in _TRAILING_INCOMPLETE


def _empieza_por_adj_muletilla(etiqueta: str) -> bool:
    toks = str(etiqueta or "").split()
    if not toks:
        return True
    return _normaliza_token(toks[0]) in _ADJ_MULETILLA_ETIQUETA


def _parece_adjetivo_et(w) -> bool:
    n = _normaliza_token(w)
    if not n or n in STOPWORDS_ES or _es_cabeza_nominal_valida(n):
        return False
    if n in _ADJ_MULETILLA_ETIQUETA:
        return True
    return bool(re.search(
        r"(al|ales|ico|ica|icos|icas|ivo|iva|ivos|ivas|oso|osa)$", n
    )) and len(n) >= 5


def _es_pegamento_de_tokens(etiqueta, texto) -> bool:
    """Reject keyword collage: nouns glued only by de/en/y without a real event head."""
    et = str(etiqueta or "").strip()
    if _es_subtema_autoria(et):
        return False
    toks = et.split()
    nexos = {"de", "del", "en", "y", "e"}
    src_n = unidecode(str(texto or "").lower())
    frase_n = unidecode(et.lower())
    if frase_n and frase_n in src_n:
        return False
    # Classic A de B leftover glue (3 tokens).
    if len(toks) == 3 and unidecode(toks[1].lower()) in nexos:
        x, y = toks[0], toks[2]
        if _es_resto_verbal(x) or _es_resto_verbal(y) or _parece_adjetivo_et(y):
            return True
        if not _es_cabeza_nominal_valida(_normaliza_token(x)):
            return True
        return False
    # Longer bags: 2+ content nouns joined ONLY by de/en/y, no event head, not a source span.
    if 4 <= len(toks) <= 8:
        content = [t for t in toks if unidecode(t.lower()) not in nexos | STOPWORDS_ES]
        heads = [_normaliza_token(t) for t in toks if _es_cabeza_nominal_valida(_normaliza_token(t))]
        only_glue = all(unidecode(t.lower()) in nexos or t[:1].islower() or True for t in toks[1:])
        glue_only = all(unidecode(t.lower()) in nexos | STOPWORDS_ES or True for t in toks)
        nexo_idx = [i for i, t in enumerate(toks) if unidecode(t.lower()) in nexos]
        if nexo_idx and not heads:
            if any(_es_resto_verbal(t) or _parece_adjetivo_et(t) for t in content[1:]):
                return True
            if frase_n not in src_n and _contiene_eslogan_subtema(et):
                return True
    return False


def _partir_oraciones(texto) -> list:
    s = re.sub(r"\s+", " ", str(texto or "")).strip()
    if not s:
        return []
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", s) if p.strip()]


def _tokens_palabras_fuente(texto) -> list:
    return re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+", str(texto or ""))


def _limpiar_objeto_evento(obj: str) -> str:
    obj = _sin_comas_etiqueta(re.sub(r"\s+", " ", str(obj or "")).strip(" .;:"))
    toks = obj.split()
    vacias = {"el", "la", "los", "las", "un", "una", "unos", "unas"}
    while toks and unidecode(toks[0].lower()) in vacias:
        toks = toks[1:]
    while toks and unidecode(toks[-1].lower().rstrip(".,;:")) in _TRAILING_INCOMPLETE:
        toks.pop()
    return " ".join(toks)


def _ocurrencia_es_nombre_propio_compuesto(texto, palabra) -> bool:
    if not palabra or not texto:
        return False
    for m in re.finditer(rf"(?i)\b{re.escape(palabra)}\b", str(texto)):
        orig = m.group(0)
        if not orig[:1].isupper():
            continue
        after = str(texto)[m.end():]
        before = str(texto)[:m.start()]
        if re.match(r"\s+[A-ZÁÉÍÓÚÑÜ]", after) or re.search(r"[A-ZÁÉÍÓÚÑÜ][\w]+\s+$", before):
            return True
    return False


def _es_nombre_de_pila_en_fuente(palabra, texto) -> bool:
    w = str(palabra or "").strip(".,;:!?")
    if len(w) < 3 or not texto:
        return False
    n = unidecode(w.lower())
    if n in _CABEZAS_SUBTEMA_VALIDAS or n in _CARGOS_SUBTEMA or n in STOPWORDS_ES:
        return False
    if re.search(rf"(?i)(?:dr|dra|sr|sra)\.?\s+{re.escape(w)}\b", str(texto)):
        return True
    return False


def _termina_en_nombre_de_pila(etiqueta, texto) -> bool:
    toks = str(etiqueta or "").strip().split()
    if not toks:
        return True
    return _es_nombre_de_pila_en_fuente(toks[-1], texto)


def _token_truncado_respecto_fuente(token, texto) -> bool:
    k = unidecode(str(token or "").lower().rstrip(".,;:"))
    if len(k) < 3 or k in _CONECTORES_ETIQUETA or k in STOPWORDS_ES:
        return False
    if k in _CABEZAS_SUBTEMA_VALIDAS:
        return False
    formas = [unidecode(t.lower()) for t in _tokens_palabras_fuente(texto)]
    if k in formas:
        return False
    return any(f.startswith(k) and len(f) > len(k) for f in formas)


def _subtema_de_baja_calidad(etiqueta, texto) -> bool:
    et = str(etiqueta or "").strip()
    if _es_subtema_autoria(et):
        return False
    if not et or _es_etiqueta_generica(et) or "," in et:
        return True
    toks = et.split()
    if len(toks) < 2 or not _frase_esta_completa(et):
        return True
    if _contiene_eslogan_subtema(et) or _de_adjetivo_huerfano(et) or _empieza_por_adj_muletilla(et):
        return True
    if _normaliza_token(toks[0]) in _CARGOS_SUBTEMA:
        return True
    if _es_pegamento_de_tokens(et, texto):
        return True
    for t in toks:
        n = _normaliza_token(t)
        if n in _VERBOS_LEAD_SUBTEMA or n in _VERBOS_NARRATIVOS_EVENTO:
            return True
        if _es_resto_verbal(t):
            return True
        if _token_truncado_respecto_fuente(t, texto):
            return True
    if _termina_en_nombre_de_pila(et, texto):
        return True
    m = re.search(r"(?i)\b(?:de|del|en|sobre|para)\s+(\S+)", et)
    if m and (
        _es_verbo_cabeza(m.group(1))
        or _es_resto_verbal(m.group(1))
        or _normaliza_token(m.group(1)) in _ADJ_MULETILLA_ETIQUETA
    ):
        return True
    return False


def _validar_estructura_subtema(etiqueta: str) -> bool:
    if not etiqueta or len(etiqueta.split()) < 2:
        return False
    if "," in etiqueta:
        return False
    if _es_etiqueta_generica(etiqueta):
        return False
    if len(etiqueta.split()) > MAX_PALABRAS_FRASE_EVENTO:
        return False
    if _PATRON_TITULAR.match(etiqueta):
        return False
    if _PATRON_ESTADO.search(etiqueta):
        return False
    if _contiene_eslogan_subtema(etiqueta) or _de_adjetivo_huerfano(etiqueta):
        return False
    palabras = etiqueta.split()
    if _es_subtema_autoria(etiqueta):
        return True
    if len(palabras) <= 2:
        nexos = {"de", "del", "para", "sobre", "en", "con", "por", "y", "e"}
        tiene_nexo = any(unidecode(p.lower().rstrip(".,;")) in nexos for p in palabras[1:])
        if not tiene_nexo:
            n0 = _normaliza_token(palabras[0])
            n1 = _normaliza_token(palabras[1]) if len(palabras) > 1 else ""
            if _es_cabeza_nominal_valida(n0) and n1 and n1 not in STOPWORDS_ES:
                return True
            return False
    return True


def _excluir_para_etiqueta(marca="", aliases=None) -> set:
    return _tokens_marca_set(marca, aliases) | STOPWORDS_ES | _VERBOS_LEAD_SUBTEMA | _CARGOS_SUBTEMA | {
        "universidad", "empresa", "compania", "noticia", "noticias", "informe",
        "nuevo", "nueva", "gran", "grande", "colombia", "pais",
    }


def _clausula_antes_de_relativo(oracion: str) -> str:
    return re.split(
        r"(?i)\s+\b(?:que|donde|quien|quienes|cuando|cual|cuales)\b\s+",
        str(oracion or ""), maxsplit=1,
    )[0].strip()


def _componer_frase_hecho(accion, objeto) -> str:
    objeto = _limpiar_objeto_evento(objeto)
    accion = str(accion or "").strip()
    if not objeto:
        return accion
    if not accion:
        return objeto
    if unidecode(accion.lower()) in unidecode(objeto.lower()):
        return objeto
    toks = objeto.split()
    cabeza_obj = _normaliza_token(toks[0]) if toks else ""
    if cabeza_obj in _CABEZAS_CONTENEDORAS_DEBILES and len(toks) >= 2:
        resto = toks[1:]
        while resto and unidecode(resto[0].lower()) in ({"de", "del", "la", "el"} | _PREP_ETIQUETA):
            resto = resto[1:]
        if resto and _parece_adjetivo_et(resto[0]):
            return f"{accion} {' '.join(resto)}"
        if resto:
            return f"{accion} de {' '.join(resto)}"
    return f"{accion} de {objeto}"


def _score_sintagma_nominal(span, oracion, excluir) -> int:
    frase = " ".join(span)
    if _contiene_eslogan_subtema(frase) or _de_adjetivo_huerfano(frase) or _empieza_por_adj_muletilla(frase):
        return -10**6
    norms = [_normaliza_token(w) for w in span]
    if not norms[0] or not norms[-1]:
        return -10**6
    if norms[0] in excluir or norms[-1] in excluir:
        return -10**6
    if norms[0] in _TRAILING_INCOMPLETE or norms[-1] in _TRAILING_INCOMPLETE:
        return -10**6
    if norms[0] in _VERBOS_LEAD_SUBTEMA or _es_verbo_cabeza(span[0]) or _es_participio_cabeza(span[0]):
        return -10**6
    if norms[0] in _CARGOS_SUBTEMA or norms[0] in _ADJ_MULETILLA_ETIQUETA:
        return -10**6
    if any(_es_verbo_cabeza(w) or _normaliza_token(w) in _VERBOS_NARRATIVOS_EVENTO for w in span):
        return -10**6
    content = [x for x in norms if x not in STOPWORDS_ES and x not in _PREP_ETIQUETA and x not in excluir]
    if len(content) < 2:
        return -10**6
    score = 0
    if _es_cabeza_nominal_valida(norms[0]) or norms[0] in _CABEZAS_CONTENEDORAS_DEBILES:
        score += 6
    if any(w in _PREP_ETIQUETA for w in norms[1:-1] if w):
        score += 2
    score += min(len(content), 4)
    if 3 <= len(span) <= 6:
        score += 2
    if 4 <= len(span) <= 6:
        score += 1
    return score


def _sintagmas_nominales_fuente(texto, excluir=None) -> list:
    excluir = excluir or set()
    ranked, vistos = [], set()
    for oracion in _partir_oraciones(texto):
        corte = _clausula_antes_de_relativo(oracion)
        tokens = re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+", corte)
        n = len(tokens)
        for i in range(n):
            for L in range(2, min(MAX_PALABRAS_FRASE_EVENTO, n - i) + 1):
                span = tokens[i:i + L]
                score = _score_sintagma_nominal(span, oracion, excluir)
                if score < 0:
                    continue
                frase = " ".join(span)
                key = unidecode(frase.lower())
                if key in vistos:
                    continue
                vistos.add(key)
                ranked.append((score, frase))
    ranked.sort(key=lambda x: (-x[0], len(x[1].split())))
    return [f for _, f in ranked]


def _nombres_completos_fuente(texto, marca="", aliases=None) -> list:
    s = str(texto or "")
    nombres = []
    for n in _variantes_marca(marca, aliases):
        n = str(n or "").strip()
        if len(n.split()) >= 2:
            nombres.append(n)
    patron = re.compile(
        r"\b([A-ZÁÉÍÓÚÑÜ][\wÁÉÍÓÚÑÜ®\.]*(?:"
        r"\s+(?:de|del|de la|de los|of|the|y|e)\s+[A-ZÁÉÍÓÚÑÜ][\wÁÉÍÓÚÑÜ®\.]*"
        r"|\s+[A-ZÁÉÍÓÚÑÜ][\wÁÉÍÓÚÑÜ®\.]*)+)\b"
    )
    for m in patron.finditer(s):
        nombres.append(m.group(1).strip())
    vistos, out = set(), []
    for n in sorted(nombres, key=len, reverse=True):
        k = unidecode(n).lower()
        if k in vistos or len(k.split()) < 2:
            continue
        vistos.add(k)
        out.append(n)
    return out


def _sigla_junto_a_nombre(nombre, texto) -> str:
    if not nombre:
        return ""
    m = re.search(re.escape(nombre) + r"\s*®?\s*\(([A-Za-zÁÉÍÓÚÑÜ]{2,8})\)", str(texto or ""), re.I)
    return m.group(1) if m else ""


def _etiqueta_trocea_nombre(frase, texto, marca="", aliases=None) -> bool:
    f = unidecode(str(frase or "").lower())
    if not f:
        return False
    nexos = {"de", "del", "la", "el", "los", "las", "of", "the", "y", "e"}
    for nom in _nombres_completos_fuente(texto, marca, aliases):
        nn = [t for t in unidecode(nom.lower()).split() if t]
        if len(nn) < 2:
            continue
        if " ".join(nn) in f:
            continue
        for i in range(1, len(nn)):
            if nn[i] in nexos:
                continue
            suf = " ".join(nn[i:])
            contenido = [t for t in nn[i:] if t not in nexos]
            if len(contenido) >= 2 and re.search(r"\b" + re.escape(suf) + r"\b", f):
                return True
    return False


def _quitar_frases_marca(texto, marca="", aliases=None) -> str:
    out = str(texto or "")
    if not out or not (marca or aliases):
        return out
    for n in sorted(_variantes_marca(marca, aliases), key=len, reverse=True):
        n = str(n or "").strip()
        if len(n) >= 4:
            out = re.sub(r"(?i)\b" + re.escape(n) + r"\b", " ", out)
    return re.sub(r"\s+", " ", out).strip()


def _accion_principal_en_texto(texto) -> str:
    s = str(texto or "")
    if not s:
        return ""
    m = re.search(
        r"(?i)\b(?:el|un|una|este|esta|su)\s+"
        r"(lanzamiento|anuncio|inauguraci[oó]n|apertura|encuentro|foro|"
        r"convenio|proyecto|programa|reconocimiento|premio|inversi[oó]n|"
        r"investigaci[oó]n|renovaci[oó]n|acreditaci[oó]n)\b",
        s,
    )
    if m:
        can = _ACCION_CANON.get(unidecode(m.group(1).lower()))
        if can:
            return can
    for patron, nombre in _ACCIONES_SUBTEMA:
        for m in re.finditer(patron, unidecode(s.lower())):
            word = m.group(1) if m.lastindex else m.group(0)
            if _ocurrencia_es_nombre_propio_compuesto(s, word):
                continue
            return nombre
    return ""


def _dominio_tras_cargo(texto) -> str:
    s = str(texto or "")
    m = re.search(
        r"(?i)(?:director(?:a)?|l[ií]der|jefe|jefa)\s+(?:de(?:l| las| los)?|en)\s+(.+?)"
        r"(?=\s*;|\s*\.|$)",
        s,
    )
    if m:
        obj = _limpiar_objeto_evento(m.group(1))
        if len(obj.split()) >= 2:
            return obj
    return ""


def _objeto_tras_evento_nominal(texto) -> str:
    s = str(texto or "")
    m = re.search(
        r"(?i)\b(?:encuentro|foro|congreso)\s+(?:anual|nacional)?\s*"
        r"(?:para|sobre|de)\s+(?:analizar|tratar)?\s*(?:las|los|la|el)?\s*(.+?)"
        r"(?=\s*,|\.|$)",
        s,
    )
    if m:
        obj = _limpiar_objeto_evento(m.group(1))
        if len([t for t in obj.split() if unidecode(t.lower()) not in STOPWORDS_ES]) >= 2:
            return obj
    return ""


def _objeto_evento_en_texto(texto: str) -> str:
    s = str(texto or "").strip()
    if not s:
        return ""
    m = re.search(
        r"(?i)(?:fue\s+)?(?:reconocid[oa]s?|premiad[oa]s?|acreditad[oa]s?|"
        r"renov[oó]|recibi[oó])\s+(?:la|el|su)?\s*(.+?)"
        r"(?=\s+del\s+Ministerio|\s+por\s+\d|\s+y\s+se\b|,|\.|$)",
        s,
    )
    if m:
        obj = _limpiar_objeto_evento(m.group(1))
        if 2 <= len(obj.split()) <= 8 and not _es_verbo_cabeza(obj.split()[0]):
            return obj
    m = re.search(
        r"(?i)(acreditaci[oó]n(?:\s+de\s+alta\s+calidad)?(?:\s+institucional)?)",
        s,
    )
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(
        r"(?i)\b(?:propone|presenta|lanza|ofrece|desarrolla)\s+"
        r"(?:un|una|el|la|este|esta)\s+(.+?)(?=\s+que\b|\s+donde\b|,|\.|$)",
        s,
    )
    if m:
        obj = _limpiar_objeto_evento(m.group(1))
        if len(obj.split()) >= 2 and not _contiene_eslogan_subtema(obj):
            return obj
    return _dominio_tras_cargo(s) or _objeto_tras_evento_nominal(s)


def _frase_evento_completa(accion, objeto, texto, max_palabras=MAX_PALABRAS_FRASE_EVENTO) -> str:
    if not objeto:
        return accion or ""
    cand = _sin_comas_etiqueta(_componer_frase_hecho(accion, objeto))
    if len(cand.split()) <= max_palabras and not _etiqueta_trocea_nombre(cand, texto):
        return cand
    if len(objeto.split()) <= max_palabras:
        return _sin_comas_etiqueta(objeto)
    return cand


def _recortar_etiqueta_sin_trocear(frase, texto, marca="", aliases=None, max_palabras=MAX_PALABRAS_FRASE_EVENTO) -> str:
    frase = _sin_comas_etiqueta(str(frase or ""))
    rec = _recortar_frase_completa(frase, max_palabras)
    if _etiqueta_trocea_nombre(rec, texto, marca, aliases) and not _etiqueta_trocea_nombre(frase, texto, marca, aliases):
        return _recortar_frase_completa(frase, max(max_palabras, min(8, len(frase.split()))))
    return rec


def _candidato_subtema_ok(frase, texto, marca="", aliases=None) -> bool:
    if _es_subtema_autoria(frase):
        return True
    if not frase or _es_etiqueta_generica(frase) or "," in str(frase):
        return False
    if _es_pegamento_de_tokens(frase, texto):
        return False
    if _etiqueta_trocea_nombre(frase, texto, marca, aliases):
        return False
    if marca and _es_nombre_o_fragmento_marca(frase, marca, aliases):
        return False
    if _subtema_de_baja_calidad(frase, texto):
        return False
    if not _validar_estructura_subtema(frase):
        return False
    return True


def _subtema_alta_calidad(frase, texto, marca="", aliases=None) -> bool:
    if not _candidato_subtema_ok(frase, texto, marca, aliases):
        return False
    n = len(str(frase).split())
    return 2 <= n <= MAX_PALABRAS_FRASE_EVENTO


def _hecho_nominal_desde_pregunta(texto: str) -> str:
    s = str(texto or "")
    qn = unidecode(re.sub(r"[¿?]", "", s).lower())
    m = re.search(r"que clima har[aá].*?\ben\s+([a-z]+)", qn)
    if m:
        return f"Pronóstico del clima en {m.group(1).title()}"
    if re.search(r"\b(clima|pronostico|temperatura)\b", qn) and re.search(r"\bhar[aá]|tiempo\b", qn):
        return "Pronóstico del clima"
    m = re.search(r"\bla\s+(\w+)\s+es\s+(redonda|plana)\b", qn)
    if m:
        return f"Forma de la {m.group(1).title()}"
    if re.search(r"\bmulta", qn) and re.search(r"\b(tengo|tiene|saber|consultar)\b", qn):
        return "Consulta de multa policial"
    m = re.search(r"donde jugar[aá]\s+(.+?)(?:\s+el\b|\s+este\b|$)", qn)
    if m:
        team = re.sub(r"\b(el|la|los|las)\s+", "", m.group(1)).strip(" .")
        if team:
            return f"Sede de {team.title()}"
    if re.search(r"\b(necesita ayuda|linea(?:s)? de (?:emergencia|atencion))\b", qn):
        return "Líneas de emergencia"
    return ""


def _extraer_subtema_especifico(texto, marca="", aliases=None) -> str:
    blob = str(texto or "").strip()
    if marca and _es_texto_solo_autoria(blob, marca, aliases):
        return _subtema_autoria_frase(blob)
    hecho_preg = _hecho_nominal_desde_pregunta(blob)
    if hecho_preg and not _subtema_de_baja_calidad(hecho_preg, blob):
        if _candidato_subtema_ok(hecho_preg, blob, marca, aliases):
            return capitalizar_etiqueta(hecho_preg)
    trabajo = _quitar_frases_marca(blob, marca, aliases) or blob
    excluir = _excluir_para_etiqueta(marca, aliases)
    accion = _accion_principal_en_texto(blob) or _accion_principal_en_texto(trabajo)
    objeto = _objeto_evento_en_texto(blob) or _objeto_evento_en_texto(trabajo)
    if objeto and (
        _subtema_de_baja_calidad(objeto, blob)
        or (marca and _es_nombre_o_fragmento_marca(objeto, marca, aliases))
    ):
        objeto = ""
    nps = _sintagmas_nominales_fuente(blob, excluir) or _sintagmas_nominales_fuente(trabajo, excluir)
    nps = [
        np for np in nps
        if np and not _subtema_de_baja_calidad(np, blob)
        and not (marca and _es_nombre_o_fragmento_marca(np, marca, aliases))
        and not _etiqueta_trocea_nombre(np, blob, marca, aliases)
    ]
    candidatos = []
    if objeto:
        candidatos.append(_frase_evento_completa(accion, objeto, blob))
        if accion:
            candidatos.append(_componer_frase_hecho(accion, objeto))
        candidatos.append(objeto)
    if accion:
        for np in nps[:6]:
            candidatos.append(np if unidecode(accion.lower()) in unidecode(np.lower())
                              else _componer_frase_hecho(accion, np))
    candidatos.extend(nps)

    def _limpiar_candidato(cand):
        frase = _recortar_etiqueta_sin_trocear(cand, blob, marca, aliases)
        palabras = frase.split()
        if palabras and (_es_verbo_cabeza(palabras[0]) or _es_participio_cabeza(palabras[0])):
            resto = " ".join(palabras[1:]).strip()
            for p in list(_PREP_ETIQUETA) + ["la", "el", "los", "las"]:
                if resto.lower().startswith(p + " "):
                    resto = resto[len(p) + 1:]
                    break
            if accion and resto:
                frase = _componer_frase_hecho(accion, resto)
            elif resto:
                frase = resto
            frase = _recortar_etiqueta_sin_trocear(frase, blob, marca, aliases)
        return _sin_comas_etiqueta(frase)

    vistos = set()
    for cand in candidatos:
        if not cand:
            continue
        frase = _limpiar_candidato(cand)
        key = unidecode(frase.lower())
        if not key or key in vistos:
            continue
        vistos.add(key)
        if _candidato_subtema_ok(frase, blob, marca, aliases):
            return capitalizar_etiqueta(frase)
    if hecho_preg:
        return capitalizar_etiqueta(hecho_preg)
    for np in nps:
        frase = _sin_comas_etiqueta(np)
        if frase and not _es_etiqueta_generica(frase) and not _es_pegamento_de_tokens(frase, blob):
            return capitalizar_etiqueta(frase)
    if accion and not _es_etiqueta_generica(accion):
        return capitalizar_etiqueta(accion)
    return capitalizar_etiqueta("Hecho institucional relevante")


def _extraer_tema_especifico(subtema, texto, marca="", aliases=None) -> str:
    if _es_subtema_autoria(subtema) or (marca and _es_texto_solo_autoria(texto, marca, aliases)):
        return _tema_autoria(texto, marca, aliases)
    blob_sub = unidecode(str(subtema or "").lower())
    for patron, nombre in _DOMINIOS_TEMA:
        if re.search(patron, blob_sub):
            if not _es_etiqueta_generica(nombre) and string_norm_label(nombre) != string_norm_label(subtema):
                return capitalizar_etiqueta(_sin_comas_etiqueta(nombre))
    tex = unidecode(str(texto or "").lower())
    for t in _tokens_marca_set(marca, aliases):
        tex = re.sub(rf"\b{re.escape(t)}\b", " ", tex)
    for patron, nombre in _DOMINIOS_TEMA:
        if re.search(patron, tex):
            if not _es_etiqueta_generica(nombre) and string_norm_label(nombre) != string_norm_label(subtema):
                return capitalizar_etiqueta(_sin_comas_etiqueta(nombre))
    sub = _sin_comas_etiqueta(str(subtema or "").strip())
    palabras = sub.split()
    if len(palabras) >= 4:
        rec = _recortar_frase_completa(sub, max_palabras=3)
        if rec and not _es_etiqueta_generica(rec):
            return capitalizar_etiqueta(rec)
    if sub and not _es_etiqueta_generica(sub):
        return capitalizar_etiqueta(sub)
    return _extraer_subtema_especifico(texto or subtema, marca, aliases)


def _asegurar_etiqueta_especifica(etiqueta, texto, marca="", aliases=None, es_subtema=True) -> str:
    et = _sin_comas_etiqueta(str(etiqueta or "")).strip()
    if _es_subtema_autoria(et):
        return _subtema_autoria_frase(texto)
    if et and not _es_etiqueta_generica(et) and "," not in et:
        if es_subtema and marca and _es_nombre_o_fragmento_marca(et, marca, aliases):
            et = ""
        elif es_subtema and _subtema_de_baja_calidad(et, texto):
            et = ""
        else:
            return capitalizar_etiqueta(et)
    if es_subtema:
        return _extraer_subtema_especifico(texto, marca, aliases)
    sub = _extraer_subtema_especifico(texto, marca, aliases)
    return _extraer_tema_especifico(sub, texto, marca, aliases)


def _sanear_etiquetas_por_item(etiquetas, textos, marca="", aliases=None, es_subtema=True):
    out = []
    for et, tx in zip(etiquetas, textos):
        if es_subtema and _es_subtema_autoria(et):
            out.append(_subtema_autoria_frase(tx))
            continue
        if (not es_subtema) and string_norm_label(et) == string_norm_label(TEMA_ESTUDIANTES_EGRESADOS):
            out.append(capitalizar_etiqueta(TEMA_ESTUDIANTES_EGRESADOS))
            continue
        if _etiqueta_pertenece_al_texto(et, tx) and not (es_subtema and _subtema_de_baja_calidad(et, tx)):
            out.append(capitalizar_etiqueta(_sin_comas_etiqueta(str(et))))
        else:
            out.append(_asegurar_etiqueta_especifica("", tx, marca, aliases, es_subtema=es_subtema))
    return out


def _texto_suficiente_analisis(texto, min_palabras=6) -> bool:
    toks = [t for t in re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü0-9]+", str(texto or "")) if len(t) > 1]
    return len(toks) >= min_palabras


def _contexto_para_excel(contexto, max_chars=1800, umbral_corto=80):
    s = str(contexto or "").strip()
    return s[:max_chars]


def _texto_clasificacion(titulo, resumen, marca, aliases=None, cuerpo=None):
    titulo = clean_text(str(titulo or "")).strip()
    resumen = clean_text(str(resumen or "")).strip()
    cuerpo = clean_text(str(cuerpo or "")).strip()
    try:
        ctx = extraer_contexto_marca(titulo, resumen, marca, aliases, cuerpo)
    except TypeError:
        ctx = extraer_contexto_marca(titulo, resumen, marca, aliases)
    if ctx and str(ctx).strip():
        return str(ctx).strip(), True
    if _texto_suficiente_analisis(resumen, 6):
        return resumen, False
    if resumen and len(resumen.split()) >= 3:
        return resumen, False
    return titulo, False


def _snippet_tono_pkl(titulo, contexto):
    ctx = str(contexto or "").strip()
    return ctx[:1800] if ctx else str(titulo or "")[:1800]


def _tono_determinista(eval_txt: str, marca: str, aliases=None):
    tex = unidecode((eval_txt or "").lower())
    if not tex or not _menciona_marca_o_alias(eval_txt, marca, aliases):
        return None
    return None


def construir_grafo_equivalencia(titulos, resumenes, contextos=None, marca="", aliases=None, embs=None):
    global _PARES_GRAFO_REVISADOS
    n = len(titulos)
    dsu = DSU(n)
    tcomp = [normalize_title_for_comparison(t) for t in titulos]
    rcomp = [_norm_cmp_texto(r) for r in (resumenes if resumenes is not None else [""] * n)]
    cn = [norm_key(str(c or "")) for c in contextos] if contextos is not None else None
    embs = list(embs) if embs is not None and len(embs) == n else [None] * n
    _PARES_GRAFO_REVISADOS = 0

    def _analisis(i):
        if contextos is not None and str(contextos[i] or "").strip():
            return str(contextos[i])
        if resumenes is not None and str(resumenes[i] or "").strip():
            return str(resumenes[i])
        return str(titulos[i] or "")

    analisis = [_analisis(i) for i in range(n)]

    def _revisar_par(i, j):
        global _PARES_GRAFO_REVISADOS
        if dsu.find(i) == dsu.find(j):
            return
        _PARES_GRAFO_REVISADOS += 1
        ai, aj = analisis[i], analisis[j]
        if _hay_conflicto_accion(ai, aj) or _hechos_nucleo_distinto(ai, aj, marca, aliases):
            return
        title_sim = _ratio_norm(tcomp[i], tcomp[j])
        res_sim = _ratio_norm(rcomp[i], rcomp[j])
        ctx_eq = bool(cn and cn[i] and cn[j] and cn[i] == cn[j])
        semantic = _cos_par(embs[i], embs[j])
        if (
            title_sim >= 0.88
            or res_sim >= 0.88
            or ctx_eq
            or semantic >= SIMILARITY_THRESHOLD_TONO
            or _historias_son_el_mismo_hecho(ai, aj, marca, aliases)
        ):
            dsu.union(i, j)

    claves = [
        _claves_bloqueo_fila(tcomp[i], analisis[i], marca, aliases, resumen_norm=rcomp[i])
        for i in range(n)
    ]
    for i, j in _pares_bloqueados(claves):
        _revisar_par(i, j)
    return dsu


def construir_grupos_consistentes(titulos, resumenes, marca="", aliases=None, embs=None, textos=None):
    dsu = construir_grafo_equivalencia(
        titulos, resumenes, contextos=textos, marca=marca, aliases=aliases, embs=embs,
    )
    return dsu.grupos(len(titulos))


def etiquetar_sin_llm(titulos, resumenes, marca, aliases=None, cuerpos=None):
    n = len(titulos)
    textos = []
    for i in range(n):
        cuerpo = cuerpos[i] if cuerpos is not None else None
        txt, _hay = _texto_clasificacion(titulos[i], resumenes[i], marca, aliases, cuerpo)
        textos.append(txt)
    dsu = construir_grafo_equivalencia(titulos, resumenes, textos, marca, aliases)
    subtemas = [_extraer_subtema_especifico(textos[i], marca, aliases) for i in range(n)]
    temas = [_extraer_tema_especifico(subtemas[i], textos[i], marca, aliases) for i in range(n)]
    temas, subtemas = _aplicar_etiquetas_autoria(titulos, textos, temas, subtemas, marca, aliases)
    for idxs in dsu.grupos(n).values():
        if len(idxs) < 2:
            continue
        miembros = [i for i in idxs if textos[i]]
        if len(miembros) < 2:
            continue
        base = miembros[0]
        if not all(_historias_son_el_mismo_hecho(textos[base], textos[i], marca, aliases) for i in miembros[1:]):
            continue
        sub_canon = Counter(subtemas[i] for i in miembros).most_common(1)[0][0]
        tema_canon = Counter(temas[i] for i in miembros).most_common(1)[0][0]
        for i in miembros:
            if _etiqueta_pertenece_al_texto(sub_canon, textos[i]) or _nucleo_evento_compartido(textos[base], textos[i]):
                subtemas[i] = sub_canon
            if _etiqueta_pertenece_al_texto(tema_canon, textos[i]) or string_norm_label(tema_canon) == string_norm_label(temas[i]):
                temas[i] = tema_canon
    subtemas = _sanear_etiquetas_por_item(subtemas, textos, marca, aliases, es_subtema=True)
    temas = _sanear_etiquetas_por_item(temas, textos, marca, aliases, es_subtema=False)
    temas, subtemas = _aplicar_etiquetas_autoria(titulos, textos, temas, subtemas, marca, aliases)
    return temas, subtemas


def _chat_json(prompt, max_tokens=800, temperature=0.0):
    try:
        resp = call_with_retries(
            openai.ChatCompletion.create,
            model=_resolver_modelo_clasificacion(),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        u = resp.get("usage", {}) if isinstance(resp, dict) else getattr(resp, "usage", {})
        if u:
            _add_tokens(
                input_n=(u.get("prompt_tokens") if isinstance(u, dict) else getattr(u, "prompt_tokens", 0)) or 0,
                output_n=(u.get("completion_tokens") if isinstance(u, dict) else getattr(u, "completion_tokens", 0)) or 0,
            )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return {}


def _pulir_subtemas_en_lotes(items, marca, aliases, pbar=None, frac0=0.70, frac1=0.86):
    out = {}
    if not items:
        return out
    size = max(25, min(40, int(TAMANO_LOTE_LLM_SUBTEMA)))
    nbat = max(1, (len(items) + size - 1) // size)
    modelo = MODELO_CLASIF_DEFAULT
    for b, start in enumerate(range(0, len(items), size)):
        chunk = items[start:start + size]
        if pbar is not None:
            frac = frac0 + (frac1 - frac0) * (b / nbat)
            pbar.progress(frac, f"Etiquetando lote {b + 1}/{nbat} · {modelo}")
        lineas = []
        for local_i, it in enumerate(chunk):
            tit = str(it.get("titulo") or "")[:140]
            txt = str(it.get("texto") or "")[:420]
            heur = str(it.get("heuristica") or "")[:80]
            lineas.append(f"{local_i}. Título: {tit}\n   Texto: {txt}\n   Heurística: {heur}")
        prompt = (
            f"Eres analista de reputación de '{marca}'. "
            "Para CADA noticia escribe UN sintagma nominal en español de Colombia "
            "(4-6 palabras, gramatical, sin comas) que describa el HECHO. "
            "JSON con claves \"0\", \"1\", ...\n"
            "PROHIBIDO: cubos genéricos, collage de keywords, verbos conjugados.\n"
            "CORRECTO: 'Proyecto residencial de lujo', 'Renovación de acreditación de alta calidad'.\n\n"
            + "\n".join(lineas)
        )
        data = _chat_json(prompt, max_tokens=MAX_TOKENS_LOTE_SUBTEMA, temperature=0.0)
        if not isinstance(data, dict):
            continue
        for local_i, it in enumerate(chunk):
            raw = data.get(str(local_i), data.get(local_i))
            if not raw:
                continue
            et = capitalizar_etiqueta(_sin_comas_etiqueta(limpiar_tema(str(raw))))
            tx = it.get("texto") or ""
            if _candidato_subtema_ok(et, tx, marca, aliases) and _etiqueta_pertenece_al_texto(et, tx):
                out[it["idx"]] = et
    return out


def _clases_de_pipeline(pipeline) -> list:
    if pipeline is None:
        return []
    objs = [pipeline]
    if hasattr(pipeline, "steps") and pipeline.steps:
        objs.append(pipeline.steps[-1][1])
    named = getattr(pipeline, "named_steps", None)
    if named:
        objs.extend(named.values())
    for obj in objs:
        if obj is not None and hasattr(obj, "classes_"):
            return [str(c).strip() for c in obj.classes_ if str(c).strip()]
    return []


def _canon_en_vocabulario_pkl(etiqueta, clases):
    if not clases:
        return None
    mapa = {}
    for c in clases:
        mapa[string_norm_label(c)] = c
        mapa[unidecode(str(c).lower()).strip()] = c
        mapa[str(c).strip()] = c
    et = str(etiqueta or "").strip()
    if et in mapa:
        return mapa[et]
    key = string_norm_label(et)
    if key in mapa:
        return mapa[key]
    return mapa.get(unidecode(et.lower()).strip())


def _score_clase_pkl(texto, clase) -> float:
    nt = string_norm_label(texto)
    nc = string_norm_label(clase)
    if not nc:
        return 0.0
    tt, tc = set(nt.split()), set(nc.split())
    overlap = len(tt & tc)
    score = overlap / max(1, len(tc))
    if overlap >= 2:
        score += 0.2
    st_t = {_stem_es(w) for w in tt if len(w) >= 4}
    st_c = {_stem_es(w) for w in tc if len(w) >= 4}
    if st_t and st_c and (st_t & st_c):
        score += 0.35
    score += 0.15 * SequenceMatcher(None, nc, nt[: max(120, len(nc) * 3)]).ratio()
    return score


def _mejor_clase_pkl(texto, clases, proba_row=None) -> str:
    if not clases:
        return ""
    scores = []
    for i, c in enumerate(clases):
        lex = _score_clase_pkl(texto, c)
        pr = float(proba_row[i]) if proba_row is not None and i < len(proba_row) else 0.0
        gen = 0.0 if _es_etiqueta_generica(c) else 0.15
        scores.append((0.55 * pr + 0.45 * lex + gen, not _es_etiqueta_generica(c), c))
    scores.sort(key=lambda x: (x[0], x[1]), reverse=True)
    no_gen = [c for _, ng, c in scores if ng]
    return no_gen[0] if no_gen else scores[0][2]


def _resolver_etiqueta_pkl(pred, texto, clases, proba_row=None) -> str:
    if not clases:
        return str(pred or "").strip()
    canon = _canon_en_vocabulario_pkl(pred, clases)
    if canon and not _es_etiqueta_generica(canon):
        return canon
    mejor = _mejor_clase_pkl(texto, clases, proba_row)
    return _canon_en_vocabulario_pkl(mejor, clases) or clases[0]


def _asignar_etiquetas_pkl(pipeline, textos, clases=None) -> list:
    clases = list(clases or _clases_de_pipeline(pipeline))
    values = [str(t or "") for t in textos]
    if not values:
        return []
    preds = [str(p).strip() for p in pipeline.predict(values)]
    probas = None
    try:
        if hasattr(pipeline, "predict_proba"):
            probas = pipeline.predict_proba(values)
    except Exception:
        probas = None
    out = []
    for i, p in enumerate(preds):
        row = probas[i] if probas is not None else None
        out.append(_resolver_etiqueta_pkl(p, values[i], clases, row))
    return out


def _forzar_vocabulario_pkl(etiquetas, clases, textos=None) -> list:
    if not clases:
        return list(etiquetas)
    out = []
    for i, et in enumerate(etiquetas):
        canon = _canon_en_vocabulario_pkl(et, clases)
        if canon:
            out.append(canon)
        else:
            tx = textos[i] if textos is not None and i < len(textos) else str(et or "")
            out.append(_mejor_clase_pkl(tx, clases))
    return out


def analizar_temas_con_pkl(textos, pkl_file):
    try:
        if hasattr(pkl_file, "seek"):
            pkl_file.seek(0)
        pipeline = joblib.load(pkl_file)
        clases = _clases_de_pipeline(pipeline)
        etiquetas = _asignar_etiquetas_pkl(pipeline, textos, clases)
        return etiquetas, clases
    except Exception as e:
        try:
            st.error(f"Error pkl temas: {e}")
        except Exception:
            pass
        return None


def _temas_nucleo_incompatible(a, b) -> bool:
    sa, sb = unidecode(str(a or "").lower()), unidecode(str(b or "").lower())
    def _hit(blob, toks):
        return any(t in blob for t in toks)
    for ga, gb in _NUCLEOS_TEMA_INCOMPATIBLES:
        if (_hit(sa, ga) and _hit(sb, gb)) or (_hit(sa, gb) and _hit(sb, ga)):
            return True
    return False


def _nombre_tema_heuristico(subtemas_grupo, textos_muestra, marca=""):
    """Encabezado editorial más general que los subtemas (dominio, no collage)."""
    subs = [str(s).strip() for s in (subtemas_grupo or []) if str(s).strip()]
    blob = " ".join(str(t) for t in (textos_muestra or [])[:4])
    votos = []
    for sub in (subs or [""]):
        if _es_subtema_autoria(sub):
            return capitalizar_etiqueta(TEMA_ESTUDIANTES_EGRESADOS)
        heur = _extraer_tema_especifico(sub, blob, marca)
        if (
            heur
            and _validar_estructura_tema(heur)
            and not _tema_es_igual_a_subtema(heur, subs or [sub])
        ):
            votos.append(capitalizar_etiqueta(_sin_comas_etiqueta(heur)))
    if votos:
        return Counter(votos).most_common(1)[0][0]
    sub0 = subs[0] if subs else ""
    palabras = sub0.split()
    for maxp in (3, 2):
        if len(palabras) > maxp:
            rec = _recortar_frase_completa(sub0, max_palabras=maxp)
            if (
                rec
                and _validar_estructura_tema(rec)
                and not _tema_es_igual_a_subtema(rec, subs)
            ):
                return capitalizar_etiqueta(rec)
    if len(palabras) >= 3:
        rec = " ".join(palabras[:2])
        if rec and string_norm_label(rec) != string_norm_label(sub0):
            return capitalizar_etiqueta(rec)
    return capitalizar_etiqueta("Hecho institucional relevante")


def consolidar_temas(subtemas, textos, pbar, marca="", embs=None):
    """Temas = headings más generales que los subtemas.

    Sin tope de 25, sin clustering n² de subtemas únicos, sin LLM por tema
    y sin un segundo pase de embeddings sobre las etiquetas. `embs` se
    acepta por compatibilidad; no se re-embebe ni se usa para recortar.
    """
    pbar = pbar or _PBarNulo()
    us = list(dict.fromkeys(subtemas))
    k_total = len(us)
    pbar.progress(0.04, f"Temas 0/{k_total}")
    if k_total <= 1:
        pbar.progress(1.0, f"Temas {max(k_total, 1)}/{max(k_total, 1)}")
        return [capitalizar_etiqueta(_sin_comas_etiqueta(s)) for s in subtemas]
    textos_por_subtema = defaultdict(list)
    for i, sub in enumerate(subtemas):
        textos_por_subtema[sub].append(textos[i] if i < len(textos) else "")
    mt = {}
    for k, sub in enumerate(us):
        pbar.progress(0.08 + 0.82 * ((k + 1) / k_total), f"Temas {k + 1}/{k_total}")
        nombre = _nombre_tema_heuristico([sub], textos_por_subtema.get(sub, []), marca)
        if _es_subtema_autoria(sub):
            nombre = TEMA_ESTUDIANTES_EGRESADOS
        mt[sub] = capitalizar_etiqueta(_sin_comas_etiqueta(nombre))
    tf = [mt.get(s, s) for s in subtemas]
    tf = _unificar_tema_por_subtema(tf, subtemas)
    tf, _ = _aplicar_etiquetas_autoria(None, textos, tf, subtemas, marca)
    # Guard: acreditación never shares tema with estudiantes/egresados
    for i, sub in enumerate(subtemas):
        blob = unidecode(str(sub).lower())
        if _es_subtema_autoria(sub) or "egresad" in blob or "estudiante" in blob:
            tf[i] = TEMA_ESTUDIANTES_EGRESADOS
        elif re.search(r"acredit|certific|alta calidad", blob):
            if string_norm_label(tf[i]) == string_norm_label(TEMA_ESTUDIANTES_EGRESADOS):
                tf[i] = "Acreditación institucional"
    pbar.progress(1.0, f"Temas listos · {len(set(tf))}")
    try:
        st.info(f"Temas: **{len(set(tf))}** (de {len(set(subtemas))} subtemas)")
    except Exception:
        pass
    return [capitalizar_etiqueta(_sin_comas_etiqueta(t)) for t in tf]


_ETIQUETA_VACIA = {"", "nan", "none", "-", "n/a"}


def _indices_validos_grupo(idxs, n):
    out = []
    for i in idxs or []:
        try:
            j = int(i)
        except (TypeError, ValueError):
            continue
        if 0 <= j < n:
            out.append(j)
    return out


def _dsu_desde_last_grupos_y_subtema(n, grupos_noticia, df, subtema_col):
    """Grupo noticia = last_grupos de procesar_lote + mismo string de Subtema.

    No SequenceMatcher, no grafo de equivalencia.
    """
    dsu = DSU(n)
    if grupos_noticia:
        for idxs in grupos_noticia.values():
            idxs = _indices_validos_grupo(idxs, n)
            if len(idxs) < 2:
                continue
            base = idxs[0]
            for j in idxs[1:]:
                dsu.union(base, j)
    if subtema_col in df.columns:
        por_sub = defaultdict(list)
        for i in range(n):
            sub = str(df.iloc[i][subtema_col]).strip()
            if sub.lower() in _ETIQUETA_VACIA:
                continue
            por_sub[sub].append(i)
        for idxs in por_sub.values():
            if len(idxs) < 2:
                continue
            base = idxs[0]
            for j in idxs[1:]:
                dsu.union(base, j)
    return dsu


def _fila_tiene_contexto(row):
    return bool(str((row or {}).get("Contexto analizado") or "").strip())


def aplicar_consistencia_grupos(df, titulo_col, resumen_col,
                                tono_col="Tono IA", tema_col="Tema", subtema_col="Subtema",
                                marca="", aliases=None,
                                vocabulario_tema=None,
                                grupos_noticia=None,
                                embs=None,
                                textos_canonicos=None,
                                pbar=None,
                                saltar_grafo=None):
    if df.empty:
        return df
    pbar = pbar or _PBarNulo()
    titulos = [str(x) for x in df[titulo_col].fillna("")]
    resumenes = [str(x) for x in df[resumen_col].fillna("")]
    n = len(df)
    textos_canonicos = (
        [str(x or "") for x in textos_canonicos]
        if textos_canonicos is not None and len(textos_canonicos) == n
        else None
    )
    df = df.copy()
    contextos = ([str(x) for x in df["Contexto analizado"].fillna("")]
                 if "Contexto analizado" in df.columns else None)
    textos_analisis = textos_canonicos or contextos or [
        f"{titulos[i]} {resumenes[i]}" for i in range(n)
    ]
    # Tras Temas listos: no reconstruir el grafo. last_grupos ya se calculó
    # en procesar_lote; filas con el mismo Subtema también son el mismo grupo.
    reusar_grupos = saltar_grafo if saltar_grafo is not None else (grupos_noticia is not None)
    if reusar_grupos:
        pbar.progress(0.08, "Agrupación 0/1")
        dsu = _dsu_desde_last_grupos_y_subtema(n, grupos_noticia, df, subtema_col)
    else:
        pbar.progress(0.08, f"Agrupación · grafo bloqueado ({n})")
        dsu = construir_grafo_equivalencia(
            titulos, resumenes,
            contextos if contextos is not None else textos_analisis,
            marca, aliases, embs=embs,
        )
        if grupos_noticia:
            for idxs in grupos_noticia.values():
                idxs = _indices_validos_grupo(idxs, n)
                if len(idxs) < 2:
                    continue
                base = idxs[0]
                for j in idxs[1:]:
                    if _hechos_nucleo_distinto(textos_analisis[base], textos_analisis[j], marca, aliases):
                        continue
                    dsu.union(base, j)
    grupos_eq = defaultdict(list)
    for i in range(n):
        grupos_eq[dsu.find(i)].append(i)
    df["Grupo noticia"] = ""
    for numero, idxs in enumerate(grupos_eq.values(), start=1):
        gid = f"G{numero:05d}"
        for i in idxs:
            df.at[df.index[i], "Grupo noticia"] = gid

    def _analisis_fila(i):
        return textos_analisis[i]

    def _indice_representante(idxs):
        def _score(i):
            tono = str(df.iloc[i][tono_col]).strip().title() if tono_col in df.columns else ""
            sub = str(df.iloc[i][subtema_col]).strip() if subtema_col in df.columns else ""
            polar = 2 if tono in ("Positivo", "Negativo") else (1 if tono == "Neutro" else 0)
            calidad = 0 if _es_etiqueta_generica(sub) else 2
            if _candidato_subtema_ok(sub, _analisis_fila(i), marca, aliases):
                calidad += 1
            return (polar, calidad, len(sub.split()), len(_analisis_fila(i)))
        return max(idxs, key=_score)

    grupos_lista = list(grupos_eq.values())
    n_eq = max(len(grupos_lista), 1)
    for gi, idxs in enumerate(grupos_lista, start=1):
        pbar.progress(0.20 + 0.70 * (gi / n_eq), f"Agrupación {gi}/{n_eq}")
        if len(idxs) < 2:
            continue
        # Post-tema (last_grupos): copiar dentro del grupo, sin n² SequenceMatcher.
        if reusar_grupos:
            subsets = [idxs]
        elif any(_hechos_nucleo_distinto(_analisis_fila(idxs[0]), _analisis_fila(j), marca, aliases) for j in idxs[1:]):
            dsu2 = DSU(len(idxs))
            for a in range(len(idxs)):
                for b in range(a + 1, len(idxs)):
                    if _historias_son_el_mismo_hecho(_analisis_fila(idxs[a]), _analisis_fila(idxs[b]), marca, aliases):
                        dsu2.union(a, b)
            subsets = [[idxs[k] for k in memb] for memb in dsu2.grupos(len(idxs)).values()]
        else:
            subsets = [idxs]
        for subidxs in subsets:
            if len(subidxs) < 2:
                continue
            ri = _indice_representante(subidxs)
            tvals = [str(df.iloc[i][tono_col]).strip().title() for i in subidxs] if tono_col in df.columns else []
            pos_neg = "Positivo" in tvals and "Negativo" in tvals
            for col in (subtema_col, tema_col):
                if col not in df.columns:
                    continue
                canon = str(df.iloc[ri][col]).strip()
                if not canon or canon.lower() in ("nan", "none", "-", "n/a"):
                    continue
                if vocabulario_tema and col == tema_col:
                    en_vocab = _canon_en_vocabulario_pkl(canon, vocabulario_tema)
                    if not en_vocab:
                        continue
                    canon = en_vocab
                elif _es_etiqueta_generica(canon):
                    continue
                else:
                    canon = capitalizar_etiqueta(canon)
                for i in subidxs:
                    df.at[df.index[i], col] = canon
            if tono_col in df.columns and not pos_neg:
                tono_rep = str(df.iloc[ri][tono_col]).strip().title()
                if tono_rep and tono_rep not in ("Duplicada", "Nan", ""):
                    for i in subidxs:
                        if str(df.iloc[i][tono_col]).strip().title() != "Duplicada":
                            df.at[df.index[i], tono_col] = tono_rep
    en_grupo = {i for idxs in grupos_eq.values() if len(idxs) >= 2 for i in idxs}

    def _sanear_selectivo(etiquetas, es_subtema):
        out = list(etiquetas)
        solos_et, solos_tx, solos_ix = [], [], []
        for i, (et, tx) in enumerate(zip(etiquetas, textos_analisis)):
            if i in en_grupo and _etiqueta_pertenece_al_texto(et, tx):
                continue
            if i in en_grupo:
                continue
            solos_et.append(et)
            solos_tx.append(tx)
            solos_ix.append(i)
        if not solos_et:
            return out
        limpios = _sanear_etiquetas_por_item(
            solos_et, solos_tx, marca, aliases, es_subtema=es_subtema
        )
        for i, et in zip(solos_ix, limpios):
            out[i] = et
        return out

    if subtema_col in df.columns:
        df[subtema_col] = _sanear_selectivo(
            [str(x) for x in df[subtema_col].tolist()], es_subtema=True
        )
    if vocabulario_tema and tema_col in df.columns:
        df[tema_col] = _forzar_vocabulario_pkl(
            [str(x) for x in df[tema_col].tolist()], vocabulario_tema, textos_analisis
        )
    elif tema_col in df.columns:
        df[tema_col] = _sanear_selectivo(
            [str(x) for x in df[tema_col].tolist()], es_subtema=False
        )
    pbar.progress(1.0, f"Agrupación {n_eq}/{n_eq}")
    return df


def columnas_salida_xlsx(existentes=None):
    order = list(COLUMNAS_XLSX_OBLIGATORIAS)
    seen = set(order)
    for c in COLUMNAS_XLSX_EXTRA:
        if c not in seen:
            order.append(c)
            seen.add(c)
    if existentes:
        for c in existentes:
            if c and c not in seen:
                order.append(c)
                seen.add(c)
    return order


def generate_output_excel(rows, km, pbar=None):
    """Escribe el xlsx de una vez. Si la fila ya trae Contexto analizado, no re-audita."""
    pbar = pbar or _PBarNulo()
    pbar.progress(0.05, "Escribiendo Excel")
    wb = Workbook()
    ws = wb.active
    ws.title = "Resultado"
    ORDER = [
        "ID Noticia", "Fecha", "Hora", "Medio", "Tipo de Medio",
        "Sección - Programa", "Región", "Título", "Autor - Conductor",
        "Nro. Pagina", "Dimensión", "Duración - Nro. Caracteres",
        "CPE", "Tier", "Audiencia", "Tono", "Tono IA", "Tema", "Subtema", "Grupo noticia",
        "Link Nota", "Resumen - Aclaracion", "Link (Streaming - Imagen)", "Menciones - Empresa",
        "ID duplicada",
        "Cuerpo Completo",
    ]
    NUM = {"ID Noticia", "Nro. Pagina", "Dimensión", "Duración - Nro. Caracteres", "CPE", "Tier", "Audiencia"}
    ORDER += ["Contexto analizado", "Coincidencia marca", "Origen coincidencia"]
    ws.append(ORDER)

    font_hyperlink = Font(color="000000", underline=None)
    align_left = Alignment(horizontal="left")
    font_header = Font(bold=True)

    for i, _col_name in enumerate(ORDER, start=1):
        ws.cell(row=1, column=i).font = font_header

    col_idx_map = {name: ORDER.index(name) + 1 for name in ORDER}
    n_rows = max(len(rows or []), 1)
    brand = ""
    aliases = []
    try:
        brand = st.session_state.get("brand_name", "")
        aliases = st.session_state.get("brand_aliases", [])
    except Exception:
        pass

    for ri, row in enumerate(rows or []):
        if ri == 0 or (ri + 1) == len(rows) or (ri + 1) % 40 == 0:
            pbar.progress(0.10 + 0.80 * ((ri + 1) / n_rows), f"Escribiendo Excel {ri + 1}/{len(rows)}")
        if _fila_tiene_contexto(row):
            ctx = str(row.get("Contexto analizado") or "")
            match = row.get("Coincidencia marca", "")
            origin = row.get("Origen coincidencia", "")
        else:
            ctx, match, origin = _brand_audit(
                row.get(km.get("titulo"), ""),
                row.get(km.get("resumen"), ""),
                brand,
                aliases,
            )
        row["Contexto analizado"], row["Coincidencia marca"], row["Origen coincidencia"] = ctx, match, origin
        tk = km.get("titulo")
        if tk and tk in row:
            row[tk] = clean_title_for_output(row.get(tk))
        rk = km.get("resumen")
        if rk and rk in row:
            row[rk] = corregir_texto(row.get(rk))

        out, links = [], {}
        for ci, h in enumerate(ORDER, start=1):
            val = row.get(h)
            cv = None
            if h == "Fecha" and pd.notna(val):
                if isinstance(val, pd.Timestamp):
                    cv = val.to_pydatetime()
                elif isinstance(val, (datetime.datetime, datetime.date)):
                    cv = val
                else:
                    cv = str(val) if val is not None else None
            elif h in NUM:
                cv = parse_numeric(val)
            elif isinstance(val, dict) and "url" in val:
                cv = val.get("value", "Link")
                if val.get("url"):
                    links[ci] = val["url"]
            elif val is not None:
                if isinstance(val, str) and val.startswith("http"):
                    cv = "Link"
                    links[ci] = val
                else:
                    cv = str(val)
            out.append(cv)
        ws.append(out)

        current_row = ws.max_row
        for ci, url in links.items():
            cell = ws.cell(row=current_row, column=ci)
            cell.hyperlink = url
            cell.font = font_hyperlink
            cell.alignment = align_left

        date_col_idx = ORDER.index("Fecha") + 1
        date_cell = ws.cell(row=current_row, column=date_col_idx)
        if isinstance(date_cell.value, (datetime.datetime, datetime.date)):
            date_cell.number_format = "DD/MM/YYYY"

        cols_millares = ["Nro. Pagina", "Dimensión", "Duración - Nro. Caracteres", "Tier", "Audiencia"]
        for col_name in cols_millares:
            cell = ws.cell(row=current_row, column=col_idx_map[col_name])
            if isinstance(cell.value, (int, float)):
                cell.number_format = "#,##0"

        cpe_cell = ws.cell(row=current_row, column=col_idx_map["CPE"])
        if isinstance(cpe_cell.value, (int, float)):
            cpe_cell.number_format = "$#,##0"

    for i, col_name in enumerate(ORDER, start=1):
        letter = ws.cell(row=1, column=i).column_letter
        if col_name in ["Título", "Resumen - Aclaracion", "Cuerpo Completo"]:
            ws.column_dimensions[letter].width = 50
        elif col_name in ["Link Nota", "Link (Streaming - Imagen)"]:
            ws.column_dimensions[letter].width = 15
        else:
            ws.column_dimensions[letter].width = 20

    buf = io.BytesIO()
    wb.save(buf)
    pbar.progress(1.0, "Escribiendo Excel")
    return buf.getvalue()


def clasificar_noticias_core(
    titulos, resumenes, marca, aliases=None, cuerpos=None,
    pkl_tono=None, pkl_tema=None, usar_llm=True, pbar=None,
):
    pbar = pbar or _PBarNulo()
    timer = _FaseTimer(pbar)
    n = len(titulos)
    titulos = [str(t or "") for t in titulos]
    resumenes = [str(r or "") for r in resumenes]
    cuerpos_l = [str(c or "") for c in cuerpos] if cuerpos is not None else [""] * n
    pbar.progress(0.05, "Contexto")
    textos, contextos, hay_marca = [], [], []
    for i in range(n):
        txt, hay = _texto_clasificacion(titulos[i], resumenes[i], marca, aliases, cuerpos_l[i])
        textos.append(txt)
        contextos.append(txt)
        hay_marca.append(hay)
    timer.mark("contexto", 0.08, f"n={n}")
    s_txt = pd.Series(textos)
    s_res = pd.Series(resumenes)
    s_tit = pd.Series(titulos)
    embs = None
    if usar_llm or pkl_tono or pkl_tema:
        pbar.progress(0.12, "Embedding")
        embs = get_embeddings_batch(textos)
    timer.mark("embeddings", 0.18, "omitido" if embs is None else "1 pase")
    pbar.progress(0.22, "Tono")
    if pkl_tono:
        tonos_raw = analizar_tono_con_pkl(
            textos, pkl_tono, titulos=titulos, resumenes=resumenes,
            marca=marca, aliases=aliases,
        ) or [{"tono": "Neutro"}] * n
        tonos = [r.get("tono", "Neutro") for r in tonos_raw]
    elif usar_llm:
        try:
            tonos_raw = asyncio.run(
                ClasificadorTono(marca, aliases).procesar_lote_async(
                    s_txt, pbar, s_res, s_tit
                )
            )
            tonos = [r.get("tono", "Neutro") for r in tonos_raw]
        except Exception:
            tonos = ["Neutro"] * n
    else:
        tonos = ["N/A"] * n
    for i, hay in enumerate(hay_marca):
        if not hay or _es_contexto_solo_autoria(titulos[i], textos[i], marca, aliases):
            tonos[i] = "Neutro"
    timer.mark("tono", 0.40)
    vocab_tema = None
    clf = None
    pbar.progress(0.45, "Subtema")
    if not usar_llm:
        temas, subtemas = etiquetar_sin_llm(titulos, resumenes, marca, aliases, cuerpos_l)
    else:
        clf = ClasificadorSubtema(marca, aliases)
        subtemas = clf.procesar_lote(s_txt, pbar, s_res, s_tit)
        pbar.progress(0.72, "Temas")
        temas = consolidar_temas(subtemas, textos, pbar, marca, embs=embs)
    if pkl_tema:
        pack = analizar_temas_con_pkl(textos, pkl_tema)
        if pack:
            temas, vocab_tema = pack
    temas = _unificar_tema_por_subtema(list(temas), list(subtemas))
    if vocab_tema:
        temas = _forzar_vocabulario_pkl(temas, vocab_tema, textos)
    temas, subtemas = _aplicar_etiquetas_autoria(
        titulos, textos, temas, subtemas, marca, aliases, vocab_tema
    )
    timer.mark("subtema_tema", 0.82)
    df = pd.DataFrame({
        "Título": titulos,
        "Resumen - Aclaracion": resumenes,
        "Contexto analizado": [_contexto_para_excel(c) for c in contextos],
        "Tono IA": tonos,
        "Tema": temas,
        "Subtema": subtemas,
    })
    grupos_noticia = getattr(clf, "last_grupos", None) if clf is not None else {}
    pbar.progress(0.88, "Agrupación")
    out = aplicar_consistencia_grupos(
        df, "Título", "Resumen - Aclaracion",
        marca=marca, aliases=aliases, vocabulario_tema=vocab_tema,
        grupos_noticia=grupos_noticia, embs=embs, textos_canonicos=textos, pbar=pbar,
        saltar_grafo=True,
    )
    timer.mark("grupos", 1.0)
    summary = _registrar_timings(timer)
    pbar.progress(1.0, summary)
    return out


def _validar_etiqueta_completa(etiqueta, titulos_grp=None, resumenes_grp=None, marca="", aliases=None,
                               fallback_fn=None, textos_grp=None, usar_llm=False):
    blob = " ".join(
        str(x) for x in list(textos_grp or [])[:3] + list(resumenes_grp or [])[:3] + list(titulos_grp or [])[:4]
        if str(x).strip()
    )
    if not etiqueta or _es_etiqueta_generica(etiqueta) or "," in str(etiqueta):
        if fallback_fn:
            return fallback_fn(titulos_grp or [])
        return _extraer_subtema_especifico(blob, marca, aliases)
    etiqueta = _sin_comas_etiqueta(etiqueta)
    if _subtema_de_baja_calidad(etiqueta, blob):
        repaired = _extraer_subtema_especifico(blob, marca, aliases)
        if _candidato_subtema_ok(repaired, blob, marca, aliases):
            return repaired
    if _frase_esta_completa(etiqueta):
        return etiqueta
    recortada = _recortar_frase_completa(etiqueta, max_palabras=MAX_PALABRAS_SUBTEMA)
    if _frase_esta_completa(recortada) and len(recortada.split()) >= 2:
        return capitalizar_etiqueta(recortada)
    if fallback_fn:
        return fallback_fn(titulos_grp or [])
    return _extraer_subtema_especifico(blob, marca, aliases)


# ── Patch ClasificadorSubtema: heuristic first, batch LLM only for BAD labels ──
def _clf_generar_etiqueta(self, textos_grp, titulos_grp, resumenes_grp, subtemas_existentes=None, evitar_etiqueta=None):
    tn = sorted(set(normalize_title_for_comparison(t) for t in titulos_grp if t))
    existentes_key = "|".join(sorted(string_norm_label(s) for s in (subtemas_existentes or []))[:20])
    evitar_key = string_norm_label(evitar_etiqueta) if evitar_etiqueta else ""
    blob_key = hashlib.md5((" ".join(str(t)[:400] for t in (textos_grp or [])[:4])).encode()).hexdigest()[:12]
    ck = hashlib.md5(("|".join(tn[:12]) + f"#{len(titulos_grp)}#{existentes_key}#{evitar_key}#{blob_key}").encode()).hexdigest()
    if ck in self._cache:
        return self._cache[ck]
    fuentes = [str(t) for t in (textos_grp or [])[:4] if t]
    fuentes += [str(r) for r in (resumenes_grp or []) if r]
    fuentes += [str(t) for t in (titulos_grp or []) if t]
    blob = " ".join(fuentes[:8])
    self._last_blob = blob
    et = _extraer_subtema_especifico(blob, self.marca, self.aliases)
    if evitar_etiqueta and string_norm_label(et) == string_norm_label(evitar_etiqueta):
        et = self._fallback(titulos_grp)
    et = _asegurar_etiqueta_especifica(et, blob, self.marca, self.aliases)
    self._llm_calls_last = 0
    self._cache[ck] = et
    return et


def _clf_fallback(self, titulos, blob=None):
    blob = " ".join(
        str(x) for x in [blob if blob is not None else getattr(self, "_last_blob", "")] + list(titulos or [])
        if str(x).strip()
    )
    et = _extraer_subtema_especifico(blob, self.marca, self.aliases)
    if et and not _es_etiqueta_generica(et) and not _es_pegamento_de_tokens(et, blob):
        return et
    return _extraer_subtema_especifico(" ".join(str(t) for t in (titulos or [])), self.marca, self.aliases)


def _clf_refinar(self, titulos, kw=None, resumenes=None, forzar_preposicion=False, prohibir_verbos=False, prohibir_nombres=False):
    return self._fallback(titulos, getattr(self, "_last_blob", ""))


def _clf_procesar_lote(self, col, pbar, res_puros, tit_puros, embs=None):
    textos = col.tolist()
    titulos = tit_puros.tolist()
    resumenes = res_puros.tolist()
    n = len(textos)
    modelo = MODELO_CLASIF_DEFAULT
    self.last_grupos = {}
    self._umbrales = _umbrales_adaptativos(n)
    u = self._umbrales
    try:
        st.caption(f"Corpus: **{n}** · umbral {u['subtema']} · `{modelo}`")
    except Exception:
        pass
    pbar.progress(0.08, "Agrupación · idénticas")
    dsu = DSU(n)
    self._paso1(titulos, resumenes, dsu)
    pbar.progress(0.14, "Agrupación · títulos")
    self._paso2(titulos, dsu)
    pbar.progress(0.20, "Embedding")
    ae = _embeddings_reusar(textos, embs)
    if u.get("usar_paso2b"):
        pbar.progress(0.24, "Agrupación · keywords")
        self._paso2b_keywords(titulos, dsu, ae)
    pbar.progress(0.30, "Agrupación · clustering")
    self._paso3(textos, ae, dsu, pbar, 0.30)
    gf = dsu.grupos(n)
    self.last_grupos = gf
    ng = len(gf)
    pbar.progress(0.55, f"Subtema · heurística ({ng} grupos)")
    mapa = {}
    sg = sorted(gf.items(), key=lambda x: -len(x[1]))

    def _etiqueta_de_item(i):
        if _es_contexto_solo_autoria(titulos[i], textos[i], self.marca, self.aliases):
            return _subtema_autoria_frase(textos[i])
        return _extraer_subtema_especifico(textos[i], self.marca, self.aliases)

    for _lid, idxs in sg:
        if _grupo_mismo_hecho(textos, idxs, self.marca, self.aliases):
            etiqueta = _extraer_subtema_especifico(
                " ".join(str(textos[i]) for i in idxs[:4]), self.marca, self.aliases
            )
            for i in idxs:
                mapa[i] = etiqueta if (
                    _etiqueta_pertenece_al_texto(etiqueta, textos[i])
                    or _nucleo_evento_compartido(etiqueta, textos[i])
                ) else _etiqueta_de_item(i)
        else:
            for i in idxs:
                mapa[i] = _etiqueta_de_item(i)
    subtemas = [mapa.get(i, "") for i in range(n)]
    pulir = _flag_env("GRILL_PULIR_SUBTEMAS", "0")
    por_pulir = []
    if pulir:
        for i, s in enumerate(subtemas):
            if not _candidato_subtema_ok(s, textos[i], self.marca, self.aliases):
                por_pulir.append({
                    "idx": i, "texto": textos[i], "titulo": titulos[i],
                    "resumen": resumenes[i], "heuristica": s,
                })
    if por_pulir:
        pulidas = _pulir_subtemas_en_lotes(por_pulir, self.marca, self.aliases, pbar=pbar)
        for i, e in pulidas.items():
            subtemas[i] = e
    else:
        pbar.progress(0.80, f"Subtema · heurística ({ng} grupos, 0 LLM)")
    pbar.progress(0.90, "Subtema · consistencia")
    subtemas = self._consistencia(subtemas, ae, pbar, u)
    for i, s in enumerate(subtemas):
        if s == "_RECLASSIFICAR" or _es_etiqueta_generica(s) or _subtema_de_baja_calidad(s, textos[i]):
            subtemas[i] = _etiqueta_de_item(i)
    for _, idxs in sg:
        if len(idxs) >= 2 and _grupo_mismo_hecho(textos, idxs, self.marca, self.aliases):
            vals = [subtemas[i] for i in idxs if not _es_etiqueta_generica(subtemas[i])]
            if vals:
                canon = Counter(vals).most_common(1)[0][0]
                for i in idxs:
                    subtemas[i] = canon
    _, subtemas = _aplicar_etiquetas_autoria(titulos, textos, ["_"] * n, subtemas, self.marca, self.aliases)
    pbar.progress(1.0, f"{len(set(subtemas))} subtemas · {modelo}")
    return [capitalizar_etiqueta(_sin_comas_etiqueta(s)) for s in subtemas]


ClasificadorSubtema._generar_etiqueta = _clf_generar_etiqueta
ClasificadorSubtema._fallback = _clf_fallback
ClasificadorSubtema._refinar = _clf_refinar
ClasificadorSubtema.procesar_lote = _clf_procesar_lote


def _umbrales_adaptativos(n: int) -> dict:
    if n <= 5:
        return dict(
            subtema=0.93, tema=0.85, dedup_label=0.90, fusion_subtemas=0.92,
            fusion_intergrupo=0.95, min_pertenencia_subtema=0.80, min_pertenencia_tema=0.75,
            coherencia_etiqueta=0.50, sim_minima_agrupacion=0.93, sim_minima_keywords=0.93,
            max_iter_fusion=1, num_temas_max=n, usar_paso2b=False, usar_fusion_iterativa=False,
            clustering_estricto=True,
        )
    if n <= 10:
        return dict(
            subtema=0.90, tema=0.84, dedup_label=0.88, fusion_subtemas=0.90,
            fusion_intergrupo=0.93, min_pertenencia_subtema=0.72, min_pertenencia_tema=0.65,
            coherencia_etiqueta=0.42, sim_minima_agrupacion=0.90, sim_minima_keywords=0.90,
            max_iter_fusion=2, num_temas_max=min(n, 5), usar_paso2b=False, usar_fusion_iterativa=False,
            clustering_estricto=True,
        )
    if n <= 20:
        return dict(
            subtema=0.86, tema=0.80, dedup_label=0.86, fusion_subtemas=0.88,
            fusion_intergrupo=0.90, min_pertenencia_subtema=0.66, min_pertenencia_tema=0.58,
            coherencia_etiqueta=0.38, sim_minima_agrupacion=0.86, sim_minima_keywords=0.86,
            max_iter_fusion=3, num_temas_max=n, usar_paso2b=True,
            usar_fusion_iterativa=True, clustering_estricto=True,
        )
    return dict(
        subtema=0.70, tema=0.70, dedup_label=UMBRAL_DEDUP_LABEL, fusion_subtemas=UMBRAL_FUSION_SUBTEMAS,
        fusion_intergrupo=0.80, min_pertenencia_subtema=UMBRAL_MIN_PERTENENCIA_SUBTEMA,
        min_pertenencia_tema=UMBRAL_MIN_PERTENENCIA_TEMA, coherencia_etiqueta=UMBRAL_COHERENCIA_ETIQUETA,
        sim_minima_agrupacion=0.74, sim_minima_keywords=0.78, max_iter_fusion=MAX_ITER_FUSION,
        num_temas_max=n, usar_paso2b=True, usar_fusion_iterativa=True,
        clustering_estricto=False,
    )


# Tono: affiliation mention is Neutro (already intended; close the leak)
_orig_mencion_solo = _mencion_solo_credito


def _mencion_solo_credito(titulo, window, marca, aliases=None):
    if _es_contexto_solo_autoria(titulo, window, marca, aliases):
        return True
    return _orig_mencion_solo(titulo, window, marca, aliases)
