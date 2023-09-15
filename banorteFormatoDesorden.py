import re
import pandas as pd
import fitz  # PyMuPDF

def process_pdf(uploaded_file):
    """Procesa un archivo PDF de Banorte y devuelve un DataFrame de Pandas."""

    def extract_pdf_text(file):
        all_text = ""
        with fitz.open(stream=file.read(), filetype="pdf") as pdf_document:
            for page_number in range(len(pdf_document)):
                page = pdf_document.load_page(page_number)
                all_text += page.get_text() + "\n"
        return all_text

    def find_matches(text):
        pattern_flexible = re.compile(
            r'(\d{2}/\d{2}/\d{4})\s+'  # Fecha de operación
            r'(\d{2}/\d{2}/\d{4})\s+'  # Fecha
            r'(\d{10})?\s*'  # Referencia (hacerlo más flexible)
            r'([\w\s\.\:\-]+?)\s+'  # Descripción (hacerlo más flexible)
            r'(\d{3})\s+'  # Código de transacción
            r'(\d{4})\s+'  # Sucursal
            r'(\$?\d{1,3}(?:,\d{3})*\.\d{2})\s+'  # Deposito / Retiro
            r'(\$?\d{1,3}(?:,\d{3})*\.\d{2})\s+'  # Saldo
            r'(\d{4})\s+'  # Movimiento
            r'(.*?)\s*'    # Descripción Detallada (opcional)
            r'(?:(-)|(\$?(?!0{1,3}\.\d{2})\d{1,3}(?:,\d{3})*\.\d{2}))\s*'  # Cheque (guion o monto no "00.00")
        )

        return pattern_flexible.findall(text)

    def create_dataframe(matches):
        data_flexible = []
        for match in matches_flexible:
            cod_transacc = match[4]
            cantidad = match[6]
            deposito = cantidad if cod_transacc == '003' else '0'
            retiro = cantidad if cod_transacc != '003' else '0'
            cheque = match[10] if match[10] != '' else match[11]

            data_flexible.append({
                'Fecha Operacion': match[0],
                'Fecha': match[1],
                'Referencia': match[2],
                'Descripción': match[3],
                'Cod. Transacc': match[4],
                'Sucursal': match[5],
                'Depositos': deposito,
                'Retiros': retiro,
                'Saldo': match[7],
                'Movimiento': match[8],
                'Descripción Detallada': match[9],
                'Cheque': cheque
            })
        return pd.DataFrame(data_flexible)

    all_text = extract_pdf_text(uploaded_file)
    matches = find_matches(all_text)
    df = create_dataframe(matches)
    return df