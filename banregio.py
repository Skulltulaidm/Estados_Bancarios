import re
import pdfplumber
import pandas as pd

def process_pdf(uploaded_file):
    """Procesa un archivo PDF y devuelve un DataFrame de Pandas."""
    
    PATTERN = re.compile(
        r'(\d{2})\s+'  # Dia
        r'([A-Z]{3})\s+'  # COD. TRANSACC
        r'(.+?)\s+'  # CONCEPTO
        r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # CARGO/ABONO
        r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # SALDO
    )
    CARGO_KEYWORDS = ['Cobro de cheque']
    ABONO_KEYWORDS = ['DEPOSITO']
    CARGO_CODES = ['TRA']  # Añade más códigos según necesidad
    ABONO_CODES = ['INT']  # Añade más códigos según necesidad
    
    def extract_pdf_text(file):
        all_text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                all_text += page.extract_text() + "\n"
        return all_text
    
    def preprocess_text(text):
        return text

    def extract_data(all_text):
        matches = PATTERN.findall(all_text)
        data = []
        date_match = re.search(r'(\d{2})\s+al\s+(\d{2})\s+de\s+([A-Z]+)\s+(\d{4})', all_text)
        if date_match:
            start_day, end_day, month, year = date_match.groups()

        for match in matches:
            cod_transacc = match[1]
            concepto = match[2]

            if any(keyword in concepto for keyword in ABONO_KEYWORDS):
                abono = match[3]
                cargo = '0'
            elif any(keyword in concepto for keyword in CARGO_KEYWORDS):
                cargo = match[3]
                abono = '0'
            else:
                # Si las keywords no se encontraron, busca por codigos
                cargo = match[3] if cod_transacc in CARGO_CODES else '0'
                abono = match[3] if cod_transacc in ABONO_CODES else '0'

            dia = f"{match[0]}/{month[:3]}/{year[2:]}"
            data.append({
                'DIA': dia, 
                'COD. TRANSACC.': match[1],
                'CONCEPTO': match[2],
                'CARGO': cargo,
                'ABONO': abono,
                'SALDO': match[4]
            })
        return data

    all_text = extract_pdf_text(uploaded_file)
    all_text = preprocess_text(all_text)
    
    data = extract_data(all_text)

    df = pd.DataFrame(data)

    df['CARGO'] = pd.to_numeric(df['CARGO'].str.replace(',', '').astype(float), errors='coerce')
    df['ABONO'] = pd.to_numeric(df['ABONO'].str.replace(',', '').astype(float), errors='coerce')

    total_cargo = df['CARGO'][df['CARGO'] > 0].sum()
    total_abono = df['ABONO'][df['ABONO'] > 0].sum()

    count_cargo = df['CARGO'][df['CARGO'] > 0].count()
    count_abono = df['ABONO'][df['ABONO'] > 0].count()

    return df, total_cargo, total_abono, count_cargo, count_abono
