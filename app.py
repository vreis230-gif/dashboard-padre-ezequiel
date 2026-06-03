import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração visual do Dashboard
st.set_page_config(page_title="Dashboard Padre Ezequiel", layout="wide")

# O link que você me mandou agora está fixo no código para você não precisar colar sempre!
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSL-C_o2XTsoNlFDl0YX0521wFgzaY6mvHaf2iYGnnZ3givPhwEJzh4r6DQ5wmcrw/pub?output=csv"

def load_data(url ):
    try:
        # Lê os dados diretamente da sua planilha do Google
        df = pd.read_csv(url)
        # Garante que os números sejam lidos corretamente
        cols = ['Seguidores', 'Posts', 'Visualizacoes', 'Engajamento']
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calcula as taxas automaticamente
        if 'Engajamento' in df.columns and 'Visualizacoes' in df.columns:
            df['Taxa_Engajamento'] = (df['Engajamento'] / df['Visualizacoes']) * 100
        
        # Define a ordem dos meses para os gráficos não ficarem bagunçados
        mes_order = {'Março': 1, 'Abril': 2, 'Maio': 3, 'Junho': 4, 'Julho': 5, 'Agosto': 6}
        if 'Mes' in df.columns:
            df['Mes_Num'] = df['Mes'].map(mes_order)
        return df
    except:
        return None

df = load_data(SHEET_URL)

if df is not None:
    st.title("📊 Dashboard KPIs - Padre Ezequiel")
    st.markdown("Os dados abaixo são lidos em tempo real da sua planilha do Google Sheets.")
    
    # Filtro de Plataforma na lateral
    st.sidebar.header("Filtros")
    todas_plats = df['Plataforma'].unique()
    selecionadas = st.sidebar.multiselect("Selecione as Plataformas", options=todas_plats, default=todas_plats)
    
    df_filtrado = df[df['Plataforma'].isin(selecionadas)]
    
    # Cartões de Resumo (KPIs)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Visualizações", f"{df_filtrado['Visualizacoes'].sum()/1e6:.1f}M")
    c2.metric("Total Engajamento", f"{df_filtrado['Engajamento'].sum()/1e6:.1f}M")
    c3.metric("Média Taxa Engaj.", f"{df_filtrado['Taxa_Engajamento'].mean():.2f}%")
    
    st.divider()
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(df_filtrado.sort_values('Mes_Num'), x='Mes', y='Visualizacoes', color='Plataforma', barmode='group', title="Visualizações por Mês")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.line(df_filtrado.sort_values('Mes_Num'), x='Mes', y='Seguidores', color='Plataforma', markers=True, title="Evolução de Seguidores")
        st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Dados da Planilha")
    st.dataframe(df_filtrado.drop(columns=['Mes_Num']))
else:
    st.error("Não conseguimos ler os dados da planilha. Verifique se ela está publicada corretamente como CSV.")
