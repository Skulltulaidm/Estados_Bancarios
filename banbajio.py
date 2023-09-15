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
            referencia = match[1]
            cantidad = match[3]
            if referencia and len(referencia) == 7:
                deposito = cantidad
                retiro = '0'
            else:
                deposito = '0'
                retiro = cantidad

            # Combine the Descripción and the Rest of the information
            #descripcion = match[2]
            #if match[5]:
            #    descripcion += ' ' + match[5]

            data.append({
                'Fecha': match[0],
                'Referencia': match[1],
                'Descripción': match[2],
                'Depositos': deposito,
                'Retiros': retiro,
                'Saldo': match[4],
            })

        return pd.DataFrame(data)

    fecha_pattern = r'\d{1,2} [A-Za-z]+'
    all_text = read_pdf(file_path)
    lines = all_text.split('\n')
    combined_text = combine_lines(lines, fecha_pattern)

    pattern_flexible = re.compile(
        r'(\d{1,2} (?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))\s+'  # Fecha
        r'(\d{7}|\d{3}|(?<=\s)\s)?\s+'  # Referencia (7 or 3 digits, optional)
        r'(.+?)\s+'  # Descripción larga
        #r'([\w\s\.\:\-]+?)\s+'
        r'(\$\s*\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # Deposito/Retiro
        r'(\$\s*\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # Saldo
    )

    matches_flexible = pattern_flexible.findall(combined_text)
    df_flexible = process_matches(matches_flexible)

    return df_flexible