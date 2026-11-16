# -*- coding: utf-8 -*-
"""Configuración del pipeline de extracción FDS → Markdown."""
from pathlib import Path

# Raíz del proyecto (D:\PLN)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# PDFs originales (carpeta anidada tal como fue suministrada)
PDF_ROOT = PROJECT_ROOT / "FDS EVALUADAS" / "FDS EVALUADAS"

# Salida del corpus y logs
CORPUS_ROOT = PROJECT_ROOT / "corpus"
LOG_DIR = PROJECT_ROOT / "results"
EXTRACTION_LOG = LOG_DIR / "extraction_log.csv"
VERIFICATION_LOG = LOG_DIR / "verification_log.csv"

# Las 16 secciones estándar de una FDS (GHS / NTC 4435)
# Palabras clave para detectarlas en los encabezados de cualquier fabricante.
GHS_SECTIONS = {
    1: "Identificación del producto y del fabricante",
    2: "Composición / información sobre los ingredientes",
    3: "Identificación de los peligros",
    4: "Primeros auxilios",
    5: "Combate de incendios",
    6: "Liberación accidental / medidas ante derrames",
    7: "Manipulación y almacenamiento",
    8: "Controles de exposición / protección personal",
    9: "Propiedades físicas y químicas",
    10: "Estabilidad y reactividad",
    11: "Información toxicológica",
    12: "Información ecotoxicológica",
    13: "Consideraciones sobre eliminación / disposición",
    14: "Información sobre transporte",
    15: "Información sobre reglamentación",
    16: "Otra información",
}

# Patrones alternativos de encabezado (normalizados, sin acentos, mayúsculas)
SECTION_KEYWORDS = {
    1: ["IDENTIFICACION DEL FABRICANTE", "IDENTIFICACION DEL PRODUCTO",
        "IDENTIFICACION DE LA SUSTANCIA", "IDENTIFICACION QUIMICA",
        "IDENTIFICACION Y DEL PRODUCTO", "PRODUCTO Y DE LA COMPANIA",
        "IDENTIFICACION DE LA MEZCLA"],
    2: ["COMPOSICION", "INFORMACION SOBRE INGREDIENTES"],
    3: ["IDENTIFICACION DE LOS PELIGROS", "IDENTIFICACION DE RIESGOS",
        "IDENTIFICACION DE LOS RIESGOS"],
    4: ["PRIMEROS AUXILIOS"],
    5: ["COMBATE DE INCENDIOS", "MEDIDAS DE LUCHA CONTRA INCENDIOS"],
    6: ["LIBERACION ACCIDENTAL", "MEDIDAS ANTE DERRAMES", "DERRAME ACCIDENTAL",
        "FUGAS ACCIDENTALES"],
    7: ["MANIPULACION Y ALMACENAMIENTO", "MANEJO Y ALMACENAMIENTO"],
    8: ["CONTROLES DE EXPOSICION", "CONTROL DE EXPOSICION",
        "PROTECCION PERSONAL Y CONTROLES", "EXPOSICION Y PROTECCION"],
    9: ["PROPIEDADES FISICAS", "PROPIEDADES FISICOQUIMICAS",
        "PROPIEDADES FISICAS Y QUIMICAS"],
    10: ["ESTABILIDAD Y REACTIVIDAD"],
    11: ["INFORMACION TOXICOLOGICA", "TOXICOLOGIA"],
    12: ["INFORMACION ECOLOGICA", "ECOTOXICOLOGICA", "INFORMACION AMBIENTAL"],
    13: ["ELIMINACION", "DISPOSICION", "CONSIDERACIONES SOBRE LA ELIMINACION"],
    14: ["INFORMACION SOBRE TRANSPORTE", "TRANSPORTE"],
    15: ["REGLAMENTACION", "INFORMACION REGLAMENTARIA", "NORMATIVA"],
    16: ["OTRA INFORMACION", "OTRAS INFORMACIONES", "INFORMACION ADICIONAL"],
}
