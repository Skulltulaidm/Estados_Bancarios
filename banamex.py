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

    def process_text(all_text):
        bloques = re.split(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', all_text)
        return ''.join([bloques[i].replace('\n', ' ') + (bloques[i+1] if i+1 < len(bloques) else '') for i in range(0, len(bloques), 2)])

    def extract_data_from_text(processed_text):
        pattern_new = re.compile(
            r'(\d{2} [A-Z]{3})\s+'              # Fecha
            r'(.+?)\s+'                         # Concepto
            r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s*'  # Depósitos o Retiros
            r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # Saldo, si existe
        )
        matches_new = pattern_new.findall(processed_text)

        data_new = [{
            'FECHA': fecha,
            'CONCEPTO': concepto,
            'RETIRO': '0.00' if "PAGO RECIBIDO" in concepto or "DEPOSITO MIXTO" in concepto else valor1,
            'DEPOSITOS': valor1 if "PAGO RECIBIDO" in concepto or "DEPOSITO MIXTO" in concepto else '0.00',
            'SALDO': valor2 if valor2 else '0.00'
        } for fecha, concepto, valor1, valor2 in matches_new]

        return data_new

    all_text = extract_pdf_text(uploaded_file)
    processed_text = process_text(all_text)
    data = extract_data_from_text(processed_text)

    return pd.DataFrame(data)
