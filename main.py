import fitz  # PyMuPDF for extracting text from PDFs
from rapidfuzz import process, fuzz
import pandas as pd
import re

# 📌 Función para extraer y estructurar el texto del PDF
def extraer_texto_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    texto_completo = ""

    for num_pagina in range(len(doc)):
        texto_completo += doc[num_pagina].get_text("text") + "\n\n"  # Agregar espacio entre páginas

    # Dividir en secciones basadas en títulos de artículos (Ej: "Artículo X.")
    secciones = re.split(r'\bArtículo \d+\.', texto_completo)
    secciones = [s.strip() for s in secciones if s.strip()]  # Eliminar espacios vacíos

    # Volver a agregar "Artículo X." al inicio de cada sección
    for i in range(len(secciones)):
        secciones[i] = f"Artículo {i+1}. {secciones[i]}"

    return secciones  # Retornamos secciones más completas en vez de fragmentos por página

# 📌 Función para buscar coincidencias en el texto del PDF
def buscar_texto_pdf(pregunta, respuestas, secciones):
    resultados = {}

    # Buscar coincidencias en la pregunta y en cada respuesta dentro de secciones enteras
    for i, seccion in enumerate(secciones):
        cleaned_text = seccion.replace("\n", " ")  # Eliminar saltos de línea

        score_pregunta = fuzz.partial_ratio(pregunta, cleaned_text)  # Comparar con pregunta
        if score_pregunta > 50:
            resultados[i+1] = (cleaned_text[:150] + "...", round(score_pregunta / 100, 2))  # Guardar como Artículo -> (Texto, Relevancia)

        for respuesta in respuestas:
            score_respuesta = fuzz.partial_ratio(respuesta, cleaned_text)  # Comparar con respuestas
            if score_respuesta > 50:
                # Guardar solo si es más relevante que un valor previo en el mismo artículo
                if i+1 not in resultados or round(score_respuesta / 100, 2) > resultados[i+1][1]:
                    resultados[i+1] = (cleaned_text[:150] + "...", round(score_respuesta / 100, 2))

    # Convertir los resultados en un DataFrame ordenado por relevancia (limitado a 10 resultados)
    df_resultados = pd.DataFrame([(f"Art. {art}", txt, rel) for art, (txt, rel) in resultados.items()],
                                  columns=["Artículo", "Texto", "Relevancia"]
                                 ).sort_values(by="Relevancia", ascending=False).head(10)

    return df_resultados
