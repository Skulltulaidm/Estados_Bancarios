import streamlit as st
import pandas as pd
import base64
import banregio  # Importa todo el módulo banregio.py
import banbajio
import monex
import banorteFormatoDesorden
import banorteFormato2
import santander
import banamex

# Para descargar archivos CSV
def download_csv(df, filename="data.csv"):
    csv = df.to_csv(index=False, encoding='utf-8-sig')  # Especifica el encoding aquí
    b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()  # Y también aquí
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar archivo CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

# Cargamos el menú para seleccionar el banco
st.title("APP EIM Consultoria para conversor de Estados de Cuenta Bancarios a CSV")
st.write("Selecciona tu banco y sube tu archivo PDF")

option = st.selectbox("Selecciona tu banco", ("Banregio", "Banbajio", "Monex", "Banorte-1", "Banorte-2", "Santander", "Banamex"))

uploaded_file = st.file_uploader("Sube tu archivo PDF", type=["pdf"])

if uploaded_file is not None:
    
    st.write("Archivo subido. Procesando...")
    
    if option == 'Banregio':
        # Utiliza la función de banregio.py para procesar el archivo
        df = banregio.process_pdf(uploaded_file)
        # Muestra el DataFrame en la app
    elif option == 'Banbajio':
        df = banbajio.process_pdf(uploaded_file)
    elif option == 'Monex':
        df = monex.process_pdf(uploaded_file)
    elif option == 'Banorte-1':
        df = banorteFormatoDesorden.process_pdf(uploaded_file) 
    elif option == 'Banorte-2':
        df = banorteFormato2.process_pdf(uploaded_file)
    elif option == 'Santander':
        df = santander.process_pdf(uploaded_file)
    elif option == 'Banamex':
        df, total_retiros, total_depositos = banamex.process_pdf(uploaded_file) 
        st.write("Es probable que la última línea de Excel arroje una Comisión que se encuentra al final del estado de cuenta, pero está fuera de los movimientos del mes.")  
        st.dataframe(df)  # Esto mostrará el DataFrame en tu aplicación Streamlit
        st.write(f'Total de Retiros: ${total_retiros:.2f}')
        st.write(f'Total de Depósitos: ${total_depositos:.2f}')    
        
    st.write(df)
    # Descargar como CSV
    download_csv(df, f"{option}_data.csv")
