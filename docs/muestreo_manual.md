# Plantilla de muestreo manual — verificación MD vs PDF (Fase 1)

> **Objetivo:** evidencia de verificación humana exigida por la guía
> ("Verificar contra cada PDF al menos una tabla o bloque con datos").
> Cada integrante toma 2–3 fichas, compara el Markdown contra el PDF original
> y diligencia la tabla final de este documento.

## Instrucciones (15 min por ficha)

1. Abrir el PDF en `FDS EVALUADAS/FDS EVALUADAS/FDS <año>/` y el Markdown en
   `corpus/<año>/<ficha>.md` (usar el visor de Markdown de VS Code para ver
   las tablas renderizadas).
2. Verificar:
   - [ ] El **mapa de 16 secciones** coincide con lo que hay en el PDF
         (¿alguna marcada "AUSENTE EN ORIGINAL" que sí exista? = fallo nuestro).
   - [ ] La **tabla verificada** tiene los mismos valores que en el PDF
         (nombres, números CAS, unidades).
   - [ ] Los **metadatos** de la cabecera (fabricante, producto, versión/fecha)
         coinciden con la sección 1 del PDF.
   - [ ] Las **imágenes** relevantes (pictogramas, diagramas) están enlazadas.
3. Anotar el resultado en la tabla de abajo y en `results/muestreo_manual.csv`.

## Fichas asignadas (12 seleccionadas: 1 por fabricante + las de revisión)

| # | Documento | Por qué está en la muestra |
|---|---|---|
| 1 | FDS 1 -pintura-antideslizante-para-canchas (2018) | Base TECNIDECOR |
| 2 | FDS 10 - pintura-epoxi-poliamida-blanco (2018) | Formato europeo Pintuco |
| 3 | FDS 11 - Ecosphere Premium (2018) | Fabricante dudoso por revisar |
| 4 | FDS 20 - Esmalte Alquídico Serie 31 (2019) | Formato SIKA |
| 5 | FDS 29 - PINTURA PRIMERA MANO & ACABADO (2019) | Formato CORONA/CORLANC |
| 6 | FDS 23 - Tufcote 3.5 HH - Aluminum (2020) | Tabla con diferencias |
| 7 | FDS 24 - 3615SM 19LT CONVERTIDOR UNIVERSAL (2020) | Fabricante dudoso + tabla |
| 8 | FDS 39 - Pintura Tráfico Acrílica Base Agua (2020) | Formato INVESA |
| 9 | FDS 47 - DIMETCOTE 302H GREEN RESIN (2021) | Tabla con diferencias (PPG) |
| 10 | FDS 55 - ESMALTE LINEA CLASICA BLANCO (2022) | Formato QUIMICA COSMOS/PINTULAND |
| 11 | FDS 79 - PQ CORROTEC PREMIUM 507 GRIS (2024) | Tabla con diferencias (AKSONOBEL) |
| 12 | FDS 83 - epoxy-zinc-primer (2024) | Sin fabricante identificado |

## Registro de verificación (llenar)

| # | Ficha | Secciones OK | Tabla correcta | Metadatos correctos | Imágenes OK | Observaciones | Verificador |
|---|---|---|---|---|---|---|---|
| 1 | | ☐ | ☐ | ☐ | ☐ | | |
| 2 | | ☐ | ☐ | ☐ | ☐ | | |
| 3 | | ☐ | ☐ | ☐ | ☐ | | |
| 4 | | ☐ | ☐ | ☐ | ☐ | | |
| 5 | | ☐ | ☐ | ☐ | ☐ | | |
| 6 | | ☐ | ☐ | ☐ | ☐ | | |
| 7 | | ☐ | ☐ | ☐ | ☐ | | |
| 8 | | ☐ | ☐ | ☐ | ☐ | | |
| 9 | | ☐ | ☐ | ☐ | ☐ | | |
| 10 | | ☐ | ☐ | ☐ | ☐ | | |
| 11 | | ☐ | ☐ | ☐ | ☐ | | |
| 12 | | ☐ | ☐ | ☐ | ☐ | | |

## Pendientes de completar manualmente

- **11 versiones N/D** → `results/pendientes_revision.csv` (extraer la
  fecha/versión de la sección 1 o cabecera del PDF y actualizar el CSV).
- **4 fabricantes dudosos** (FDS 11, FDS 24, FDS 25, FDS 97) → confirmar en el
  PDF y corregir `results/extraction_log.csv`.
- **1 página en blanco** (FDS 97, pág. 17): ya verificada visualmente, solo
  documentada.

> **Nota:** si al revisar encuentran errores sistemáticos de extracción,
> reportarlos para ajustar el pipeline y regenerar el corpus
> (`python -m src.extraction.run`, ~3 min).
