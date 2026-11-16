# -*- coding: utf-8 -*-
"""OCR de páginas escaneadas pendientes en el corpus."""
import csv
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image
import io

# Ubicar Tesseract en Windows
if not pytesseract.get_tesseract_version():
    raise SystemExit("Tesseract no disponible")

import os

# Ubicar Tesseract y sus datos de idioma (spa) en Windows
os.environ["TESSDATA_PREFIX"] = str(Path(__file__).resolve().parents[2] / "tessdata")

pdf_path = Path(r"FDS EVALUADAS/FDS EVALUADAS/FDS 2025/"
                "FDS 97 - MADETEC-POLIURETANO-LACA-SEMIMATE-INCOLORO-P-402- "
                "AKZONOBEL.pdf")
doc = pymupdf.open(pdf_path)

for pno, page in enumerate(doc, start=1):
    if page.get_text().strip():
        continue  # página normal, ya extraída
    print(f"OCR en página {pno}...")
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text = pytesseract.image_to_string(img, lang="spa")
    out = Path("corpus/2025/FDS 97 - MADETEC-POLIURETANO-LACA-SEMIMATE-"
               "INCOLORO-P-402- AKZONOBEL")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"page{pno}_ocr.txt").write_text(text, encoding="utf-8")
    md = Path("corpus/2025/FDS 97 - MADETEC-POLIURETANO-LACA-SEMIMATE-"
              "INCOLORO-P-402- AKZONOBEL.md")
    content = md.read_text(encoding="utf-8")
    marker = f"### Página {pno}"
    if marker in content and "OCR (Tesseract" not in content:
        ocr_block = (f"\n> ℹ️ **OCR aplicado (Tesseract 5.4, spa):** texto "
                     f"recuperado por OCR de página escaneada. Fidelidad "
                     f"sujeta a calidad del escaneo; ver "
                     f"`page{pno}_ocr.txt` en la carpeta de la ficha.\n")
        content = content.replace("> ⚠️ **PÁGINA ESCANEADA: requiere OCR.**",
                                  ocr_block + "\n> ⚠️ **PÁGINA ESCANEADA:**",
                                  1)
        md.write_text(content, encoding="utf-8")
    print(f"  -> {len(text)} caracteres, guardado en page{pno}_ocr.txt")
doc.close()
print("Listo")
