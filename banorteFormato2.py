import re
import pandas as pd
import fitz

def process_pdf(file_path):
    def read_pdf(file_path):
        with fitz.open(stream=file_path.read(), filetype="pdf") as pdf_document:
            return '\n'.join([page.get_text() for page in pdf_document])

    def combine_lines(lines):
        processed_lines = []
        current_line = ""
        for line in lines:
            if re.match(r'\d{2}-[A-Z]{3}-\d{2}', line):
                if current_line:
                    processed_lines.append(current_line.strip())
                current_line = line.strip()
            else:
                current_line += " " + line.strip()
        processed_lines.append(current_line)
        return '\n'.join(processed_lines)

    def process_matches(matches):
        retiro_keywords = ["CHEQUE", "PAGO REFERENCIADO", "TRASPASO", "COMISION", "IVA"]
        def is_retiro(concepto):
            for keyword in retiro_keywords:
                if keyword in concepto:
                    return True
            return False

        data = []
        for match in matches:
            concept_combined = " ".join([match[1], match[2]]).strip()
            deposito = match[3] if not is_retiro(concept_combined) else '0.00'
            retiro = match[3] if is_retiro(concept_combined) else '0.00'

            data.append({
                'FECHA': match[0],
                'DESCRIPCION/ESTABLECIMIENTO': concept_combined,
                'DEPOSITO': deposito,
                'RETIRO': retiro,
                'SALDO': match[4]
            })

        return pd.DataFrame(data)

    all_text = read_pdf(file_path)
    lines = all_text.split('\n')
    combined_text = combine_lines(lines)

    pattern = re.compile(
        r'(\d{2}-[A-Z]{3}-\d{2})'  # Fecha
        r'(?:([A-Z0-9]+) )?'      # Código transacción (opcional, no siempre está presente)
        r'(.+?) '                 # Concepto
        r'(\d{1,3}(?:,\d{3})*\.\d{2}) '  # Cargo/Abono
        r'(\d{1,3}(?:,\d{3})*\.\d{2})'   # Saldo
    )

    matches = pattern.findall(combined_text)
    df = process_matches(matches)

    return df
