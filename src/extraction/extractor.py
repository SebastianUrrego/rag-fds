# -*- coding: utf-8 -*-
"""
Extractor principal: PDF de FDS → estructura intermedia + Markdown.

Reglas de fidelidad (según guía del taller):
- NO se infiere información faltante: las secciones ausentes se marcan como
  "AUSENTE EN ORIGINAL" y las páginas sin texto extraíble como "REQUIERE OCR".
- Toda imagen con contenido técnico se conserva y se enlaza con ruta relativa.
- Cada elemento registra documento, página y sección.
"""
import re
import unicodedata
from pathlib import Path

import pymupdf

from .config import GHS_SECTIONS, SECTION_KEYWORDS

# ---------------------------------------------------------------------------
# Utilidades de normalización
# ---------------------------------------------------------------------------

def norm(s: str) -> str:
    """Mayúsculas sin acentos, espacios colapsados."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).upper().strip()


def sanitize(name: str) -> str:
    """Nombre de archivo/carpeta seguro y legible."""
    name = re.sub(r"[^\w\-. ]+", "", name, flags=re.UNICODE)
    return re.sub(r"\s+", " ", name).strip()


# Encabezado tipo "1. IDENTIFICACION ..." / "1 - COMPOSICION" / "11. INFORMACION..."
HEADER_RE = re.compile(r"^\s*(\d{1,2})\s*[\.\-\u2013:]\s*(.+?)\s*$")

# Encabezado tipo europeo: "SECCIÓN 1: IDENTIFICACIÓN DEL PRODUCTO"
SECCION_RE = re.compile(
    r"^\s*SECCION\s+(\d{1,2})\s*[:\.\-\u2013]?\s*(.*?)\s*$")

# Etiquetas de campo (ancladas a inicio de línea) para metadatos de la sección 1
META_LABELS = {
    "fabricante": [
        r"^\s*Empresa\s*:?",
        r"^\s*Raz[óo]n Social\s*:",
        r"^\s*Compa[ñn][íi]a\s*:",
        r"^\s*Datos (?:del|sobre) el? ?proveedor(?: o fabricante)?\s*:",
        r"^\s*Proveedor\s*:?",
        r"^\s*Fabricado por\s*:?",
        r"^\s*Elaborado por\s*:?",
        r"^\s*Fabricante\s*:?",
    ],
    "producto": [
        r"^\s*Nombre del Producto\s*:",
        r"^\s*Nombre Comercial\s*:",
        r"^\s*Identificador SGA del producto\s*:",
        r"^\s*Nombre del producto\s*:",
        r"^\s*Denominaci[óo]n\s*:",
        r"^\s*Producto\s*:",
    ],
    "version": [
        r"^\s*Emisi[oó]n\s*:",
        r"^\s*Revisi[oó]n\s*:",
        r"^\s*Fecha de (?:actualizaci[oó]n|revisi[oó]n|emisi[óo]n|elaboraci[óo]n)(?:\s*de la\s*(?:FDS|documento))?\s*:?",
        r"^\s*Versi[oó]n\s*:",
    ],
}

# Valores que indican "dato no disponible" (no son fabricante/producto reales)
BAD_VALUES = {"N/A", "N/D", "NA", "ND", "NO APLICA",
               "NO DISPONIBLE", "-", "", "VERSIÓN", "VERSION",
               "NO HAY VALIDACIÓN ANTERIOR", "NO HAY VALIDACION ANTERIOR"}

# Fragmentos que delatan que la captura es una etiqueta u otro campo,
# no el valor buscado (p. ej. el título "...Y DEL PROVEEDOR O FABRICANTE")
REJECT_FRAGMENTS = [
    "fabricante", "proveedor", "identificaci", "nombre del", "secci",
    "p[áa]gina", "hoja de", "tel[ée]fono", "direcci[óo]n", "correo",
    "c[óo]digo del producto", "fecha de", "usos", "número de", "numero de",
]


def _is_section_header(line: str):
    """Devuelve (numero, titulo) si la línea es un encabezado de sección FDS."""
    nline = norm(line)
    m = SECCION_RE.match(nline)
    if m:
        num = int(m.group(1))
        title = m.group(2)
        if 1 <= num <= 16:
            return num, title.strip() or GHS_SECTIONS[num]
    m = HEADER_RE.match(line)
    if not m:
        return None
    num = int(m.group(1))
    if not (1 <= num <= 16):
        return None
    title = m.group(2)
    # El título debe parecerse a un encabezado (mayorías mayúsculas) y no ser
    # un ítem de lista del cuerpo del texto.
    letters = [c for c in title if c.isalpha()]
    if len(letters) < 4:
        return None
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    if upper_ratio < 0.6:
        return None
    return num, title.strip()


def _match_section_by_keywords(title_norm: str):
    """Detecta la sección por palabras clave aunque el número no coincida."""
    for num, keywords in SECTION_KEYWORDS.items():
        if any(k in title_norm for k in keywords):
            return num
    return None


# ---------------------------------------------------------------------------
# Extracción
# ---------------------------------------------------------------------------

def extract_pdf(pdf_path: Path):
    """Extrae texto, tablas, imágenes y secciones de una FDS.

    Devuelve un dict con:
      pages: [{page, text, lines, tables, images, ocr_required}]
      sections: {num: {"title", "page", "status"}}
      meta: {fabricante, producto, version}
    """
    doc = pymupdf.open(pdf_path)
    pages, seen_images = [], set()
    sections = {n: None for n in GHS_SECTIONS}
    full_text_lines = []

    active_sec = None
    for pno, page in enumerate(doc, start=1):
        text = page.get_text()
        lines = [l.rstrip() for l in text.splitlines()]
        full_text_lines.extend(lines)

        ocr_required = (not text.strip()) and bool(page.get_images())
        images = extract_images(doc, page, pno, seen_images)

        # Detectar secciones presentes en esta página con sus posiciones verticales
        blocks = page.get_text("blocks")
        sec_positions = []
        for b in blocks:
            for l in b[4].splitlines():
                h = _is_section_header(l)
                if h:
                    sec_positions.append((b[1], h[0]))
                    break
        sec_positions.sort(key=lambda x: x[0])

        for img in images:
            img_sec = active_sec
            for s_y0, s_num in sec_positions:
                if img["y0"] >= s_y0:
                    img_sec = s_num
                else:
                    break
            if img_sec is None and sec_positions:
                img_sec = sec_positions[0][1]
            img["section"] = img_sec or 1

        if sec_positions:
            active_sec = sec_positions[-1][1]

        pages.append({
            "page": pno,
            "text": text,
            "lines": lines,
            "ocr_required": ocr_required,
            "images": images,
            "tables": [],  # llenadas por pdfplumber en build_markdown
        })

    # Detección de secciones sobre el texto completo (encabezados numerados)
    page_cursor = 1
    lines_per_page = [len(p["lines"]) for p in pages]
    for idx, line in enumerate(full_text_lines):
        while idx >= sum(lines_per_page[:page_cursor]):
            page_cursor += 1
        header = _is_section_header(line)
        if not header:
            continue
        num, title = header
        tnorm = norm(title)
        matched = _match_section_by_keywords(tnorm) or (
            num if tnorm else None)
        # Confirma el número por keywords, o acepta el número si el título
        # coincide parcialmente con la sección estándar
        if matched and sections[matched] is None:
            sections[matched] = {
                "title": title, "page": page_cursor, "status": "OK",
            }

    # Secciones no detectadas por encabezado: búsqueda del keyword en el texto
    flat_norm = [norm(l) for l in full_text_lines]
    for num in GHS_SECTIONS:
        if sections[num] is not None:
            continue
        for kw in SECTION_KEYWORDS[num]:
            hit = next((i for i, t in enumerate(flat_norm) if kw in t), None)
            if hit is not None:
                pg = 1
                acc = 0
                for cnt in lines_per_page:
                    acc += cnt
                    if hit < acc:
                        break
                    pg += 1
                sections[num] = {"title": GHS_SECTIONS[num], "page": pg,
                                 "status": "OK (sin encabezado numerado)"}
                break

    # Clasificación final: presente / ausente en original
    for num in GHS_SECTIONS:
        if sections[num] is None:
            sections[num] = {"title": GHS_SECTIONS[num], "page": None,
                             "status": "AUSENTE EN ORIGINAL (no inferir)"}

    doc.close()

    meta = extract_meta(pdf_path)
    return {"pages": pages, "sections": sections, "meta": meta,
            "n_pages": len(pages)}


def extract_meta(pdf_path: Path) -> dict:
    """Procedencia y version desde la seccion 1 del documento.

    Estrategia en tres niveles (documentada por trazabilidad):
    1. Captura por etiquetas de campo dentro de la seccion 1.
    2. Si no hay confianza, respaldo en el nombre del archivo suministrado
       (es procedencia documentada, no inferencia sobre el contenido).
    3. Si nada aplica, se registra N/D: no se inventa el dato.
    """
    doc = pymupdf.open(pdf_path)
    first = "\n".join(p.get_text() for p in doc[:2])
    doc.close()

    meta = {"fabricante": None, "producto": None, "version": None}
    for key, labels in META_LABELS.items():
        for label in labels:
            value = _capture(label, first, key)
            if value:
                meta[key] = value
                break

    # Respaldo por nombre de archivo: "FDS 10 - X" -> producto X;
    # "...- CORONA .pdf" -> fabricante CORONA (ultimo segmento tras " - ")
    stem = pdf_path.stem
    segments = [s.strip() for s in stem.split(" - ") if s.strip()]

    # Version declarada en el nombre del archivo: "(Version 1)" -> "Version 1"
    m_ver = re.search(r"[Vv]ersi[oó]n\s+([0-9]+(?:\.[0-9]+)?)", stem)
    if m_ver and not meta["version"]:
        meta["version"] = "Version " + m_ver.group(1)

    # Fabricante declarado en el nombre del archivo: se toma el ultimo
    # segmento que NO parezca producto (sin "PARTE/PART" ni numeros)
    if not meta["fabricante"] and len(segments) >= 2:
        for seg in reversed(segments[1:]):
            up = seg.upper().rstrip(". ")
            if re.search(r"PARTE|PART\b|\d", up):
                continue
            if len(up) <= 20 and up not in BAD_VALUES and len(up) >= 2:
                if meta["producto"] and up == meta["producto"].upper():
                    continue
                meta["fabricante"] = up
                break

    if not meta["producto"] and len(segments) >= 2:
        meta["producto"] = segments[1].strip(" ._")
    elif not meta["producto"]:
        meta["producto"] = stem
    return meta


# Tokens que delatan una razon social real (se prefieren en la ventana de
# candidatos): "PPG Industries Colombia Ltda", "Sika Colombia S.A.S.", etc.
CORP_TOKEN = re.compile(
    r"(S\.A\.S|S\.A\b|SAS\b|LTDA|LIMITADA|LLC|INC\b|CORP|C[II]A|COMPANY|"
    r"INDUSTRIES)", re.IGNORECASE)

# Lineas que parecen direccion/telefono/web: nunca son el fabricante
ADDRESS_RE = re.compile(
    r"(\d{3,}|www\.|http|@|autopista|calle|carrera|vereda|\bkm\b|"
    r"tel[eé]fono|fax|emergencia|apartado|#|e-mail|direcci|col\.|industrial|responsable|MSDS no\.)", re.IGNORECASE)


def _capture(label_re: str, raw: str, key: str = None):
    """Captura el valor de una etiqueta de campo anclada a linea.

    El valor puede quedar en la misma linea ("Empresa: X") o entre las
    primeras lineas siguientes. Ventana corta (5 lineas) para no capturar
    secciones ajenas; para fabricante se prefiere un candidato con tokens
    corporativos o un valor corto sin apariencia de direccion.
    """
    m = re.search(label_re, raw, re.IGNORECASE | re.MULTILINE)
    if not m:
        return None
    window = raw[m.end():].splitlines()[:5]
    candidates = []
    for i, line in enumerate(window):
        value = _clean(line)
        if value is None:
            continue
        if key == "fabricante" and ADDRESS_RE.search(value):
            continue
        candidates.append((i, value))
    if not candidates:
        return None
    if key == "fabricante":
        corp = [v for _, v in candidates if CORP_TOKEN.search(v)]
        if corp:
            return corp[0]
        short = [v for _, v in candidates if len(v.split()) <= 5]
        if short:
            return short[0]
        return None  # mejor N/D que un valor dudoso
    return candidates[0][1]


def _clean(value: str):
    """Valida y normaliza un metadato capturado (anti-falsos-positivos)."""
    value = re.sub(r"\s+", " ", value or "").strip(" :\t;,-")
    if value.upper() in BAD_VALUES:
        return None
    if re.fullmatch(r"[\d\.\s/]+", value):  # "1.1", "2", etc.
        return None
    if len(value) < 2 or len(value) > 120:
        return None
    low = value.lower()
    if any(f in low for f in REJECT_FRAGMENTS):
        return None
    return value


def extract_images(doc, page, pno: int, seen: set):
    """Extrae imágenes de la página (sin duplicar xrefs entre páginas)."""
    out = []
    for img in page.get_images(full=True):
        xref = img[0]
        if xref in seen:
            continue
        seen.add(xref)
        base = doc.extract_image(xref)
        # Descarta iconos/minidetalles sin contenido técnico
        if base["width"] < 40 or base["height"] < 40:
            continue
        rects = page.get_image_rects(xref)
        y0 = rects[0].y0 if rects else 0.0
        out.append({"xref": xref, "page": pno,
                    "ext": base["ext"], "data": base["image"],
                    "width": base["width"], "height": base["height"],
                    "y0": y0})
    return out
