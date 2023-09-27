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
        data_new = []

        for match in matches_new:
            fecha, concepto, valor1, valor2 = match

            if "PAGO RECIBIDO" in concepto or "DEPOSITO MIXTO" in concepto or "TRASPASO" in concepto:
                deposito = valor1
                retiro = '0.00'
            else:
                deposito = '0.00'
                retiro = valor1

            # Determinar el saldo
            if valor2:
                saldo = valor2
            else:
                saldo = '0.00'

            data_new.append({
                'FECHA': fecha,
                'CONCEPTO': concepto,
                'RETIRO': retiro,
                'DEPOSITOS': deposito,
                'SALDO': saldo
            })

        return data_new

    all_text = extract_pdf_text(uploaded_file)
    processed_text = process_text(all_text)
    data = extract_data_from_text(processed_text)

    return pd.DataFrame(data)
