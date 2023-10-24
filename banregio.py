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

        date_match = re.search(r'(\d{2})\s+al\s+(\d{2})\s+de\s+([A-Z]+)\s+(\d{4})', all_text)
        if date_match:
            start_day, end_day, month, year = date_match.groups()
            date_suffix = f"{month[:3]}/{year[2:]}"
        data = []
        for match in matches:
            cod_transacc = match[1]
            cantidad = match[3]
            CARGO_KEYWORDS = ['Cobro de cheque']
            ABONO_KEYWORDS = ['DEPOSITO']

            if "ABONO" in match[2]:
                abono = cantidad
                cargo = '0'
            else:
                cargo_condition = cod_transacc == 'TRA' or (cod_transacc == 'DOC' and any(keyword in match[2] for keyword in CARGO_KEYWORDS))
                abono_condition = cod_transacc == 'INT' or (cod_transacc == 'DOC' and any(keyword in match[2] for keyword in ABONO_KEYWORDS))
                
                cargo = cantidad if cargo_condition else '0'
                abono = cantidad if abono_condition else '0'

            dia = f"{match[0]}/{month[:3]}/{year[2:]}"

            data.append({
                'DIA': dia, 
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
