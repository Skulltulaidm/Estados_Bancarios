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
            cod_transacc = match[2]
            cantidad = match[3]
            deposito = cantidad if 'ABONO' in cod_transacc else '0'
            retiro = cantidad if 'CARGO' in cod_transacc or 'MEMBRESIA' in cod_transacc else '0'

            data.append({
                'FECHA': match[0],
                'FOLIO': match[1],
                'DESCRIPCION': match[2],
                'DEPOSITOS': deposito,
                'RETIROS': retiro,
                'SALDO': match[4]
            })
        return pd.DataFrame(data)

    fecha_pattern = r'\d{2}-\w{3}-\d{4}'
    all_text = read_pdf(file_path)
    lines = all_text.split('\n')
    combined_text = combine_lines(lines, fecha_pattern)

    pattern_flexible = re.compile(
        r'(\d{2}-\w{3}-\d{4})\s+'           # Fecha
        r'(\d{7})\s+'                       # Folio
        r'(.+?)\s+'                         # Descripción
        r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # Depositos
        r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  #Retiros/Saldo
    )

    matches_flexible = pattern_flexible.findall(combined_text)
    df_flexible = process_matches(matches_flexible)

    return df_flexible