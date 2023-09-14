import re
import pandas as pd
import fitz

def process_pdf_bajio(uploaded_file):
    """Procesa un archivo PDF del Banco Bajío y devuelve un DataFrame de Pandas."""

    def extract_pdf_text(file):
        all_text = ""
        pdf_document = fitz.open(file)
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            all_text += page.get_text() + "\n"
        pdf_document.close()
        return all_text

    def find_matches(text):
        pattern_new = re.compile(
            r'(\d{1,2} (?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))\s+'  # Fecha
            r'(\d{7}|\d{3}|(?<=\s)\s)?\s+'  # Referencia (7 or 3 digits, optional)
            r'(.+?)\s+'  # Descripción larga
            r'(\$\s*\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # Deposito/Retiro
            r'(\$\s*\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # Saldo
        )
        return pattern_new.findall(text)

    def create_dataframe(matches):
        data = []
        for match in matches:
            referencia = match[1]
            cantidad = match[3]
            if referencia and len(referencia) == 7:
                deposito = cantidad
                retiro = '0'
            else:
                deposito = '0'
                retiro = cantidad
            data.append({
                'Fecha': match[0],
                'Referencia': match[1],
                'Descripción': match[2],
                'Depositos': deposito,
                'Retiros': retiro,
                'Saldo': match[4],
            })
        return pd.DataFrame(data)

    all_text = extract_pdf_text(uploaded_file)
    matches = find_matches(all_text)
    df = create_dataframe(matches)
    return df
