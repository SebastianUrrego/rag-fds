# -*- coding: utf-8 -*-
"""Generación del Markdown del corpus a partir de la extracción."""
import re

import pdfplumber

from .extractor import _is_section_header, norm


def extract_tables(pdf_path):
    """Extrae tablas con pdfplumber, indexadas por página."""
    tables = {}
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            try:
                raw = page.extract_tables()
            except Exception as exc:  # tabla corrupta: se registra y sigue
                tables[pno] = {"error": str(exc), "tables": []}
                continue
            clean = []
            for t in raw or []:
                rows = [[(c or "").strip() for c in row] for row in t]
                rows = [r for r in rows if any(r)]
                if len(rows) >= 2 and max(len(r) for r in rows) >= 2:
                    clean.append(rows)
            tables[pno] = {"error": None, "tables": clean}
    return tables


def rows_to_markdown(rows):
    """Convierte filas de una tabla a formato Markdown (celdas con <br>)."""
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]
    md = ["| " + " | ".join(c.replace("|", "\\|").replace("\n", "<br>")
                             for c in r) + "|" for r in rows]
    md.insert(1, "|" + "---|" * ncols)
    return "\n".join(md)


def build_markdown(pdf_path, extracted, tables, img_dir_rel):
    """Arma el Markdown final de una FDS."""
    meta = extracted["meta"]
    md = [f"# {meta.get('producto') or pdf_path.stem}", ""]
    md += ["> **Documento fuente:** " + pdf_path.name]
    md += ["> **Fabricante:** " + (meta.get("fabricante") or "N/D (no inferir)")]
    md += ["> **Versión / fecha:** " + (meta.get("version") or "N/D (no inferir)")]
    md += ["> **Páginas:** " + str(extracted["n_pages"]), ""]

    # Resumen de las 16 secciones
    md += ["## Mapa de secciones FDS", "",
           "| # | Sección | Página | Estado |", "|---|---|---|---|"]
    for num, info in extracted["sections"].items():
        page = info["page"] if info["page"] is not None else "—"
        md.append(f"| {num} | {info['title']} | {page} | {info['status']} |")
    md += ["", "---", ""]

    # Contenido por página, con encabezados de sección inline y tablas/imágenes
    for pinfo in extracted["pages"]:
        pno = pinfo["page"]
        md.append(f"### Página {pno}")
        md.append("")
        if pinfo["ocr_required"]:
            md.append("> **PÁGINA ESCANEADA: requiere OCR.** El texto no es "
                      "extraíble con la biblioteca vectorial; revisar imagen "
                      "asociada. Limitación registrada en el log.")
            md.append("")
        elif not pinfo["text"].strip():
            md.append("> ℹ️ **PÁGINA EN BLANCO EN EL ORIGINAL** (sin texto ni "
                      "imágenes). No es un fallo de extracción.")
            md.append("")

        current_section = None
        for line in pinfo["lines"]:
            header = _is_section_header(line)
            if header:
                num, title = header
                current_section = num
                md.append(f"## {num}. {title}")
                md.append("")
            elif line.strip():
                md.append(line)
        md.append("")

        # Tablas de la página (pdfplumber)
        page_tables = tables.get(pno, {"tables": [], "error": None})
        if page_tables["error"]:
            md.append(f"> **FALLO DE EXTRACCIÓN de tabla (página {pno}):** "
                      f"`{page_tables['error']}`")
            md.append("")
        for ti, rows in enumerate(page_tables["tables"], start=1):
            sec = (f"sección {current_section}" if current_section
                   else "sección indeterminada")
            md.append(f"#### Tabla {ti} (página {pno}, {sec})")
            md.append("")
            md.append(rows_to_markdown(rows))
            md.append("")

        # Imágenes con ruta relativa y trazabilidad
        for img in pinfo["images"]:
            fname = f"page{pno}_xref{img['xref']}.{img['ext']}"
            rel = f"{img_dir_rel}/{fname}"
            md.append(f"![imagen página {pno}]({rel})")
            md.append(f"")
            md.append(f"*Imagen técnica — documento: {pdf_path.name}.pdf, "
                      f"página {pno}, sección: "
                      f"{current_section or 'indeterminada'}.*")
            md.append("")

    return "\n".join(md)
