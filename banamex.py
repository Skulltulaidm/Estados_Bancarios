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
        return ''.join([bloques[i].replace('\n', ' ') + (bloques[i+1] if i+1 < len(bloques) else '') for i in range(0, len(bloques), 2)]).strip()

    def find_matches(text):
        pattern = re.compile(
            r'(\d{2} [A-Z]{3})\s+'              # Fecha
            r'(.+?)\s+'                         # Concepto
            r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s*'  # Depósitos o Retiros
            r'(\d{1,3}(?:,\d{3})*\.\d{2})?\s+'  # Saldo, si existe
        )
        return pattern.findall(text)

    def create_dataframe(matches):
        data = []
        for match in matches:
            fecha, concepto, valor1, valor2 = match

            if "PAGO RECIBIDO" in concepto or "DEPOSITO MIXTO" in concepto or "TRASPASO" in concepto:
                deposito = valor1
                retiro = '0.00'
            else:
                deposito = '0.00'
                retiro = valor1

            # Determinar el saldo
            if valor2:
                saldo = valor2
            else:
                saldo = '0.00'
            data.append({
                'FECHA': fecha, 
                'CONCEPTO': concepto,
                'RETIRO': retiro,
                'DEPOSITOS': deposito,
                'SALDO': saldo
            })
        return pd.DataFrame(data)

    all_text = extract_pdf_text(uploaded_file)
    all_text = preprocess_text(all_text)
    matches = find_matches(all_text)
    df = create_dataframe(matches)
    
    # Calcula y muestra el total de retiros y depósitos
    total_retiros = df['RETIRO'].replace('[\$,]', '', regex=True).astype(float).sum()
    total_depositos = df['DEPOSITOS'].replace('[\$,]', '', regex=True).astype(float).sum()
    st.write(f'Total de Retiros: ${total_retiros:.2f}')
    st.write(f'Total de Depósitos: ${total_depositos:.2f}')

    return df