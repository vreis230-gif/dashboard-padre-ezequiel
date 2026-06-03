import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Padre Ezequiel", layout="wide")

# Seu link CSV do Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSL-C_o2XTsoNlFDl0YX0521wFgzaY6mvHaf2iYGnnZ3givPhwEJzh4r6DQ5wmcrw/pub?output=csv"

def load_data(url ):
    try:
        df = pd.read_csv(url)
        # Remove espaços em branco dos nomes das colunas
        df.columns = [c.strip() for c in df.columns]
        
        # Tenta encontrar as colunas mesmo que o nome mude um pouco
        col_map = {
            'Plataforma': ['Plataforma', 'Rede Social', 'Canal'],
            'Mes': ['Mes', 'Mês', 'Periodo', 'Período'],
            'Seguidores': ['Seguidores', 'Inscritos'],
            'Visualizacoes': ['Visualizacoes', 'Visualizações', 'Views'],
            'Engajamento': ['Engajamento', 'Interações']
        }
        
        for oficial, variantes in col_map.items():
            for v in variantes:
                if v in df.columns and oficial not in df.columns:
                    df = df.rename(columns={v: oficial})
        
        # Converte números
        for col in ['Seguidores', 'Visualizacoes', 'Engajamento', 'Posts']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")
        return None

df = load_data(SHEET_URL)

if df is not None and not df.empty:
    st.title("📊 Dashboard KPIs - Padre Ezequiel")
    
    # Verifica se as colunas essenciais existem
    if 'Plataforma' in df.columns:
        st.sidebar.header("Filtros")
        plats = st.sidebar.multiselect("Plataformas", options=df['Plataforma'].unique(), default=df['Plataforma'].unique())
        df_filtered = df[df['Plataforma'].isin(plats)]
        
        # KPIs
        c1, c2, c3 = st.columns(3)
        if 'Visualizacoes' in df.columns:
            c1.metric("Total Visualizações", f"{df_filtered['Visualizacoes'].sum()/1e6:.1f}M")
        if 'Engajamento' in df.columns:
            c2.metric("Total Engajamento", f"{df_filtered['Engajamento'].sum()/1e6:.1f}M")
        
        st.divider()
        
        # Gráficos simples para evitar erros
        if 'Mes' in df.columns and 'Visualizacoes' in df.columns:
            st.plotly_chart(px.bar(df_filtered, x='Mes', y='Visualizacoes', color='Plataforma', barmode='group', title="Visualizações"), use_container_width=True)
        
        st.subheader("Visualização dos Dados")
        st.dataframe(df_filtered)
    else:
        st.warning("Não encontramos a coluna 'Plataforma'. Verifique os nomes na sua planilha.")
        st.write("Colunas encontradas:", list(df.columns))
else:
    st.error("A planilha parece estar vazia ou o link está incorreto.")
