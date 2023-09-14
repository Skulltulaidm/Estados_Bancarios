import streamlit as st
import pandas as pd
import base64
import banregio  # Importa todo el módulo banregio.py

# Para descargar archivos CSV
def download_csv(df, filename="data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar archivo CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

# Cargamos el menú para seleccionar el banco
st.title("Conversor de Extractos Bancarios a CSV")
st.write("Selecciona tu banco y sube tu archivo PDF")

option = st.selectbox("Selecciona tu banco", ("Banregio", "BancoX", "BancoY"))

uploaded_file = st.file_uploader("Sube tu archivo PDF", type=["pdf"])

if uploaded_file is not None:
    st.write("Archivo subido. Procesando...")
    
    if option == 'Banregio':
        # Utiliza la función de banregio.py para procesar el archivo
        df = banregio.process_pdf(uploaded_file)
        # Muestra el DataFrame en la app
        st.write(df)
        # Descargar como CSV
        download_csv(df, f"{option}_data.csv")
