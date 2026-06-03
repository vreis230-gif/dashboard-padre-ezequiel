import streamlit as st
import pandas as pd

st.set_page_config(page_title="Diagnóstico de Dados", layout="wide")

# Link da sua planilha (Certifique-se de que este é o link CSV novo)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSL-C_o2XTsoNlFDl0YX0521wFgzaY6mvHaf2iYGnnZ3givPhwEJzh4r6DQ5wmcrw/pub?output=csv"

st.title("🔍 Diagnóstico de Conexão" )

try:
    df = pd.read_csv(SHEET_URL)
    st.success("✅ Planilha conectada com sucesso!")
    
    st.subheader("1. Como o Dashboard está vendo suas colunas:")
    st.write(list(df.columns))
    
    st.subheader("2. Primeiras linhas dos seus dados:")
    st.dataframe(df.head())
    
    st.info("💡 Se você não vir os nomes 'Plataforma', 'Visualizacoes', etc., acima, significa que a planilha no Google Sheets precisa ser ajustada.")

except Exception as e:
    st.error(f"❌ Erro ao conectar: {e}")
    st.markdown("""
    ### Possíveis causas:
    1. O link acima não é o da planilha **nova**.
    2. A planilha não foi **Publicada na Web** como **CSV**.
    """)
