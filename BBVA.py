import re
import pdfplumber
import pandas as pd

def process_pdf(uploaded_file):
    """Procesa un archivo PDF del banco Banamex y devuelve un DataFrame de Pandas."""

    def extract_pdf_text(file):
        all_text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                all_text += page.extract_text() + "\n"
        return all_text

    def preprocess_text(text):
        bloques = re.split(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
        return ''.join([bloques[i].replace('\n', ' ') + (bloques[i+1] if i+1 < len(bloques) else '') for i in range(0, len(bloques), 2)])

    def find_matches(text):
        pattern = re.compile(r'''
            (\d{2}/[A-Z]{3})\s+             # Fecha OPER
            (\d{2}/[A-Z]{3})\s+             # Fecha LIQ
            ([A-Z][0-9]{2}|BT2)?\s*         # CODIGO
            (.+?)\s+                        # DESCRIPCION
            (\d{1,3}(?:,\d{3})*\.\d{2})\s*  # CARGO/ABONO
            (\d{1,3}(?:,\d{3})*\.\d{2})?\s+ # OPERACION
            (\d{1,3}(?:,\d{3})*\.\d{2})?\s* # LIQUIDACION
        ''', re.VERBOSE)
        return pattern.findall(text)

    def create_dataframe(matches):

        data = []

        for idx, match in enumerate(matches):
            fecha_oper, fecha_liq, CODIGO, DESCRIPCION, valor1, valor2, valor3 = match.groups()
            additional_desc = get_additional_description(all_text, match, idx, matches)
            final_des = DESCRIPCION + additional_desc
            cargo, abono, operacion, liquidacion = classify_values(CODIGO, final_des, valor1, valor2, valor3)

            data.append({
                'FECHA OPERACION': fecha_oper,
                'FECHA LIQUIDACION': fecha_liq,
                'CODIGO': CODIGO,
                'DESCRIPCION': final_des.split(STOP_PHRASE)[0].strip(),
                'CARGO': cargo,
                'ABONO': abono,
                'OPERACION': operacion,
                'LIQUIDACION': liquidacion
            })

        return pd.DataFrame(data)

    def get_additional_description(all_text, match, idx, matches):
        if idx + 1 < len(matches):
            next_match_start = matches[idx + 1].start()
            return all_text[match.end():next_match_start].strip()
        else:
            return all_text[match.end():].strip()

    def classify_values(CODIGO, final_des, valor1, valor2, valor3):
        # Case with three prices
        if valor1 and valor2 and valor3:
            if CODIGO in CARGO_CODES or \
                    (CODIGO == 'N06' and any(kw in final_des for kw in CARGO_KEYWORDS)) or \
                    (CODIGO == 'N06' and any(code in final_des for code in CARGO_DESC_CODES)):
                return valor1, '0.00', valor2, valor3  # First value is CARGO
            elif CODIGO in ABONO_CODES or \
                    (CODIGO == 'N06' and any(kw in final_des for kw in ABONO_KEYWORDS)) or \
                    (CODIGO == 'N06' and any(code in final_des for code in ABONO_DESC_CODES)):
                return '0.00', valor1, valor2, valor3  # First value is ABONO

        # Case with one price
        if CODIGO in CARGO_CODES or \
                (CODIGO == 'N06' and any(kw in final_des for kw in CARGO_KEYWORDS)) or \
                (CODIGO == 'N06' and any(code in final_des for code in CARGO_DESC_CODES)):
            return valor1, '0.00', '0.00', '0.00'  # Single value is CARGO
        elif CODIGO in ABONO_CODES or \
                (CODIGO == 'N06' and any(kw in final_des for kw in ABONO_KEYWORDS)) or \
                (CODIGO == 'N06' and any(code in final_des for code in ABONO_DESC_CODES)):
            return '0.00', valor1, '0.00', '0.00'  # Single value is ABONO

        # Default case
        return '0.00', '0.00', '0.00', '0.00'

    all_text = extract_pdf_text(uploaded_file)
    all_text = preprocess_text(all_text)
    matches = find_matches(all_text)
    df = create_dataframe(matches)
    
    # Calcula los totales de retiros y depósitos
    total_retiros = df['CARGO'].replace('[\$,]', '', regex=True).astype(float).sum()
    total_depositos = df['ABONO'].replace('[\$,]', '', regex=True).astype(float).sum()

    # Devuelve el DataFrame y los totales
    return df, total_retiros, total_depositos