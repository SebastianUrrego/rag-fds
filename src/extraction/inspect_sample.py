# -*- coding: utf-8 -*-
"""Inspección rápida de una FDS de muestra para diseñar el parser."""
import pymupdf

PDF = r"FDS EVALUADAS\FDS EVALUADAS\FDS 2018\FDS 9 - OXIGEL.pdf"

doc = pymupdf.open(PDF)
print(f"Paginas: {len(doc)}")
for i, page in enumerate(doc):
    text = page.get_text()
    print(f"\n========== PAGINA {i+1} ==========")
    print(text[:1500])
doc.close()
