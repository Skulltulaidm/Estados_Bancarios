import streamlit as st
import pandas as pd
import base64
import banregio  # Importa todo el módulo banregio.py
import banbajio

# Para descargar archivos CSV
def download_csv(df, filename="data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar archivo CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

# Cargamos el menú para seleccionar el banco
st.title("Conversor de Extractos Bancarios a CSV")
st.write("Selecciona tu banco y sube tu archivo PDF")

option = st.selectbox("Selecciona tu banco", ("Banregio", "Banbajio", "BancoY"))

uploaded_file = st.file_uploader("Sube tu archivo PDF", type=["pdf"])

if uploaded_file is not None:
    
    st.write("Archivo subido. Procesando...")
    
    if option == 'Banregio':
        # Utiliza la función de banregio.py para procesar el archivo
        df = banregio.process_pdf(uploaded_file)
        # Muestra el DataFrame en la app
    elif option == 'Banbajio':
        df = banbajio.process_pdf_banbajio(uploaded_file)    
        
    st.write(df)
    # Descargar como CSV
    download_csv(df, f"{option}_data.csv")
