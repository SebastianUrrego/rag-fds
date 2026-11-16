# -*- coding: utf-8 -*-
"""
Orquestador del pipeline de extracción: todas las FDS → corpus Markdown.

Uso:
    python -m src.extraction.run            # procesa todo
    python -m src.extraction.run --limit 5  # solo las primeras 5 (pruebas)

Salidas:
    corpus/<año>/<slug>.md                  # Markdown verificado
    corpus/<año>/<slug>/img/                # imágenes con rutas relativas
    results/extraction_log.csv              # registro por documento
    results/verification_log.csv            # evidencia de verificación
"""
import argparse
import csv
import time
from pathlib import Path

from .config import (CORPUS_ROOT, EXTRACTION_LOG, LOG_DIR, PDF_ROOT,
                     VERIFICATION_LOG)
from .build_markdown import build_markdown, extract_tables
from .extractor import extract_pdf, sanitize
from .verify import verify_document


def slug_year(pdf_path: Path) -> str:
    """Año del FDS a partir de la carpeta contenedora (FDS 2018 → 2018)."""
    return pdf_path.parent.name.replace("FDS", "").strip()


def process_pdf(pdf_path: Path) -> dict:
    year = slug_year(pdf_path)
    slug = sanitize(pdf_path.stem)

    out_dir = CORPUS_ROOT / year
    img_dir = out_dir / slug / "img"
    img_dir.mkdir(parents=True, exist_ok=True)

    extracted = extract_pdf(pdf_path)
    tables = extract_tables(pdf_path)

    # Guardar imágenes y registrar rutas relativas
    img_rel = f"{slug}/img"
    for page in extracted["pages"]:
        for img in page["images"]:
            fname = f"page{img['page']}_xref{img['xref']}.{img['ext']}"
            (img_dir / fname).write_bytes(img["data"])

    md = build_markdown(pdf_path, extracted, tables, img_rel)
    md_path = out_dir / f"{slug}.md"
    md_path.write_text(md, encoding="utf-8")

    verification = verify_document(pdf_path, tables)

    n_images = sum(len(p["images"]) for p in extracted["pages"])
    n_tables = sum(len(t["tables"]) for t in tables.values())
    n_scanned = verification["paginas_escaneadas"]
    missing = [str(n) for n, s in extracted["sections"].items()
               if s["status"].startswith("AUSENTE")]

    return {
        "documento": pdf_path.name,
        "año": year,
        "fabricante": extracted["meta"].get("fabricante") or "N/D",
        "producto": extracted["meta"].get("producto") or "N/D",
        "version_fecha": extracted["meta"].get("version") or "N/D",
        "paginas": extracted["n_pages"],
        "secciones_ok": 16 - len(missing),
        "secciones_ausentes": ", ".join(missing) or "ninguna",
        "tablas": n_tables,
        "imagenes": n_images,
        "paginas_escaneadas": n_scanned,
        "markdown": str(md_path.relative_to(CORPUS_ROOT.parent)),
        "estado_verificacion": verification["estado"],
        "notas": "; ".join(verification["errores"]) or "",
    }, verification


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None,
                        help="Procesa solo N fichas (para pruebas)")
    args = parser.parse_args()

    pdfs = sorted(PDF_ROOT.rglob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No se encontraron PDFs en {PDF_ROOT}")
    if args.limit:
        pdfs = pdfs[: args.limit]

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    CORPUS_ROOT.mkdir(parents=True, exist_ok=True)

    rows, verifications = [], []
    t0 = time.time()
    for i, pdf in enumerate(pdfs, start=1):
        try:
            row, verification = process_pdf(pdf)
            rows.append(row)
            verifications.append(verification)
            print(f"[{i:>3}/{len(pdfs)}] OK   {pdf.name[:70]}")
        except Exception as exc:
            rows.append({
                "documento": pdf.name, "año": slug_year(pdf),
                "fabricante": "?", "producto": "?", "version_fecha": "?",
                "paginas": "?", "secciones_ok": "?", "secciones_ausentes": "?",
                "tablas": "?", "imagenes": "?", "paginas_escaneadas": "?",
                "markdown": "", "estado_verificacion": "FALLO DE EXTRACCIÓN",
                "notas": f"{type(exc).__name__}: {exc}",
            })
            print(f"[{i:>3}/{len(pdfs)}] FAIL {pdf.name[:70]} -> {exc}")

    fields = list(rows[0].keys())
    with open(EXTRACTION_LOG, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    with open(VERIFICATION_LOG, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(verifications[0].keys()))
        writer.writeheader()
        writer.writerows(verifications)

    ok = sum(1 for r in rows if "FALLO" not in r["estado_verificacion"])
    print(f"\nTerminado en {time.time() - t0:.1f}s -> {len(rows)} fichas "
          f"({ok} verificadas)")
    print(f"  Log extracción:  {EXTRACTION_LOG}")
    print(f"  Log verificación: {VERIFICATION_LOG}")


if __name__ == "__main__":
    main()
