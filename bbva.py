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
            ([A-Z][0-9]{2}|BT2)?\s*         # codigo
            (.+?)\s+                        # descripcion
            (\d{1,3}(?:,\d{3})*\.\d{2})\s*  # CARGO/ABONO
            (\d{1,3}(?:,\d{3})*\.\d{2})?\s+ # OPERACION
            (\d{1,3}(?:,\d{3})*\.\d{2})?\s* # LIQUIDACION
        ''', re.VERBOSE)
        return pattern.findall(text)

    cargo_codes = ['T17', 'P14', 'S39', 'S40', 'X01']
    cargo_keywords = ['mopsa', 'PAGO FACTURA', 'Mopsa']
    cargo_desc_codes = ["0164690214", "0482773643", "0116431607", "0116914225", "0105473098", "0119486771", "0476472370", "0112395312", "0100427152", "0114237803", "0115889189", "0111283014", "0450891053", "0132293021", "0119339779", "0166407420", "0115884411", "0112634511"]

    abono_codes = ['T20', 'W02', 'T09', 'C07', 'BT2', 'M97', 'Y45']
    abono_keywords = ['MOPSA', 'PAGO DE MANIOBRAS', 'Pago de maniobra', 'Pago maniobras', 'Bajar']
    abono_desc_codes = ["0101097040", "0150581933", "0185395038", "0114127706", "0169167285", "0185696151", "1153268152", "0115696585", "0164365852", "0111801791", "0143227766", "0451620290", "0110319007", "0103160033", "0114675894", "0448387516"]

    stop_phrase = "BBVA MEXICO, S.A.,"

    def create_dataframe(matches):

        data = []

        for idx, match in enumerate(matches):
            fecha_oper, fecha_liq, codigo, descripcion, valor1, valor2, valor3 = match.groups()
            additional_desc = get_additional_description(text, match, idx, matches)
            final_des = descripcion + additional_desc
            cargo, abono, operacion, liquidacion = classify_values(codigo, final_des, valor1, valor2, valor3)

            data.append({
                'FECHA OPERACION': fecha_oper,
                'FECHA LIQUIDACION': fecha_liq,
                'codigo': codigo,
                'descripcion': final_des.split(stop_phrase)[0].strip(),
                'CARGO': cargo,
                'ABONO': abono,
                'OPERACION': operacion,
                'LIQUIDACION': liquidacion
            })

        return pd.DataFrame(data)

    def get_additional_description(text, match, idx, matches):
        if idx + 1 < len(matches):
            next_match_start = matches[idx + 1].start()
            return text[match.end():next_match_start].strip()
        else:
            return text[match.end():].strip()

    def classify_values(codigo, final_des, valor1, valor2, valor3):
        # Case with three prices
        if valor1 and valor2 and valor3:
            if codigo in cargo_codes or \
                    (codigo == 'N06' and any(kw in final_des for kw in cargo_keywords)) or \
                    (codigo == 'N06' and any(code in final_des for code in cargo_desc_codes)):
                return valor1, '0.00', valor2, valor3  # First value is CARGO
            elif codigo in abono_codes or \
                    (codigo == 'N06' and any(kw in final_des for kw in abono_keywords)) or \
                    (codigo == 'N06' and any(code in final_des for code in abono_desc_codes)):
                return '0.00', valor1, valor2, valor3  # First value is ABONO

        # Case with one price
        if codigo in cargo_codes or \
                (codigo == 'N06' and any(kw in final_des for kw in cargo_keywords)) or \
                (codigo == 'N06' and any(code in final_des for code in cargo_desc_codes)):
            return valor1, '0.00', '0.00', '0.00'  # Single value is CARGO
        elif codigo in abono_codes or \
                (codigo == 'N06' and any(kw in final_des for kw in abono_keywords)) or \
                (codigo == 'N06' and any(code in final_des for code in abono_desc_codes)):
            return '0.00', valor1, '0.00', '0.00'  # Single value is ABONO

        # Default case
        return '0.00', '0.00', '0.00', '0.00'

    all_text = extract_pdf_text(uploaded_file)
    all_text = preprocess_text(all_text)
    matches = find_matches(all_text)
    df = create_dataframe(matches)
    
    # Calcula los totales de retiros y depósitos
    total_cargos = df['CARGO'].replace('[\$,]', '', regex=True).astype(float).sum()
    total_abonos = df['ABONO'].replace('[\$,]', '', regex=True).astype(float).sum()

    # Devuelve el DataFrame y los totales
    return df, total_cargos, total_abonos