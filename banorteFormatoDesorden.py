import re
import pandas as pd
import fitz

def process_pdf(file_path):
    def read_pdf(file_path):
        with fitz.open(stream=file_path.read(), filetype="pdf") as pdf_document:
            return '\n'.join([page.get_text() for page in pdf_document])

    def combine_lines(lines, pattern):
        combined_lines = []
        current_line = ''

        for line in lines:
            if re.match(pattern, line):
                if current_line:
                    combined_lines.append(current_line.strip())
                current_line = line
            else:
                current_line += ' ' + line.strip()

        if current_line:
            combined_lines.append(current_line.strip())

        return '\n'.join(combined_lines)

    def process_matches(matches):
        data = []
        for match in matches:
            cod_transacc, cantidad = match[4], match[6]
            deposito = cantidad if cod_transacc == '003' else '0'
            retiro = cantidad if cod_transacc != '003' else '0'
            cheque = match[10] if match[10] else match[11]

            data.append({
                'Fecha Operacion': match[0],
                'Fecha': match[1],
                'Referencia': match[2],
                'Descripción': match[3],
                'Cod. Transacc': cod_transacc,
                'Sucursal': match[5],
                'Depositos': deposito,
                'Retiros': retiro,
                'Saldo': match[7],
                'Movimiento': match[8],
                'Descripción Detallada': match[9],
                'Cheque': cheque
            })

        return pd.DataFrame(data)

    fecha_pattern = r'\d{2}/\d{2}/\d{4}'
    all_text = read_pdf(file_path)
    lines = all_text.split('\n')
    combined_text = combine_lines(lines, fecha_pattern)

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

    matches_flexible = pattern_flexible.findall(combined_text)
    df_flexible = process_matches(matches_flexible)

    return df_flexible