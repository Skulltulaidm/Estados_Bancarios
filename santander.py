import re
import pandas as pd
import fitz

def process_pdf(file_path):
    # Palabras clave
    DEPOSITO_KEYWORDS = ['ABONO', 'ABONO TRANSFERENCIA', ]
    RETIRO_KEYWORDS = ['CARGO', 'MEMBRESIA', 'CARGO TRANSFERENCIA', 'PAGO TRANSFERENCIA']

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

            deposito = cantidad if any(keyword in cod_transacc for keyword in DEPOSITO_KEYWORDS) else '0'
            retiro = cantidad if any(keyword in cod_transacc for keyword in RETIRO_KEYWORDS) else '0'

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
        r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # Retiros/Saldo
    )

    matches_flexible = pattern_flexible.findall(combined_text)
    df_flexible = process_matches(matches_flexible)

    # Adaptando las operaciones de conversión y cálculo
    df_flexible['DEPOSITOS'] = pd.to_numeric(df_flexible['DEPOSITOS'].str.replace(',', '').astype(float), errors='coerce')
    df_flexible['RETIROS'] = pd.to_numeric(df_flexible['RETIROS'].str.replace(',', '').astype(float), errors='coerce')

    total_deposito = df_flexible['DEPOSITOS'][df_flexible['DEPOSITOS'] > 0].sum()
    total_retiro = df_flexible['RETIROS'][df_flexible['RETIROS'] > 0].sum()

    count_deposito = df_flexible['DEPOSITOS'][df_flexible['DEPOSITOS'] > 0].count()
    count_retiro = df_flexible['RETIROS'][df_flexible['RETIROS'] > 0].count()

    return df_flexible, total_retiro, total_deposito, count_retiro, count_deposito
