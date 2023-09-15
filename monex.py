import re
import pdfplumber
import pandas as pd

def process_pdf_monex(uploaded_file):
    """Procesa un archivo PDF del banco Monex y devuelve un DataFrame de Pandas."""

    def extract_pdf_text(file):
        all_text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                all_text += page.extract_text() + "\n"
        return all_text

    def find_matches_monex(text):
        pattern = re.compile(r'(\d{2}/\w{3})\s+([\w\s]+?)(?:\s+(\d{8}))?\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d+\.\d{2}|-?\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d+\.\d{2}|-?\d{1,3}(?:,\d{3})*\.\d{2})')
        return pattern.findall(text)

    def create_dataframe_monex(matches):
        data = []
        for match in matches:
            data.append({
                'Fecha': match[0],
                'Descripción': match[1],
                'Referencia': match[2],
                'Abonos': match[3],
                'Cargos': match[4],
                'Movimiento Garantía': match[5],
                'Saldo No Disponible': match[6],
                'Saldo Disponible': match[7],
                'Saldo Total': match[8]
            })
        return pd.DataFrame(data)

    all_text = extract_pdf_text(uploaded_file)
    matches = find_matches_monex(all_text)
    df = create_dataframe_monex(matches)
    return df
