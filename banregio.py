import re
import pandas as pd
import pdfplumber

def process_pdf(uploaded_file):
    """Procesa un archivo PDF y devuelve un DataFrame de Pandas."""

    def extract_pdf_text(file):
        all_text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                all_text += page.extract_text() + "\n"
        return all_text

    def find_matches(text):
        pattern = re.compile(
            r'(\d{2})\s+'  # Dia
            r'([A-Z]{3})\s+'  # COD. TRANSACC
            r'(.+?)\s+'  # CONCEPTO
            r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # CARGO/ABONO
            r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # SALDO
        )
        return pattern.findall(text)

    def create_dataframe(matches):
        data = []
        for match in matches:
            cod_transacc = match[1]
            cantidad = match[3]

            if "ABONO" in match[2]:
                abono = cantidad
                cargo = '0'
            else:
                cargo = cantidad if cod_transacc == 'TRA' else '0'
                abono = cantidad if cod_transacc == 'INT' else '0'

            data.append({
                'DIA': match[0],
                'COD. TRANSACC.': match[1],
                'CONCEPTO': match[2],
                'CARGO': cargo,
                'ABONO': abono,
                'SALDO': match[4]
            })
        return pd.DataFrame(data)

    all_text = extract_pdf_text(uploaded_file)
    matches = find_matches(all_text)
    df = create_dataframe(matches)
    return df
