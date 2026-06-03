import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração Visual (O Dashboard Lindo)
st.set_page_config(page_title="Dashboard Padre Ezequiel", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. O Link da sua Planilha Nova (COLE O SEU NOVO LINK ENTRE AS ASPAS ABAIXO)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSlkfkFYoG5-wbbixuRgxLrxpMLM4y1OjejJoInmKD43a9SL-ZtmSLQqZGuQnijyQ/pub?output=csv"

def load_data(url ):
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns] # Limpa nomes das colunas
        
        # Mapeamento inteligente de colunas (caso o nome mude um pouco)
        mapping = {
            'Plataforma': ['Plataforma', 'Rede Social', 'Canal'],
            'Mes': ['Mes', 'Mês', 'Periodo'],
            'Seguidores': ['Seguidores', 'Inscritos'],
            'Visualizacoes': ['Visualizacoes', 'Visualizações', 'Views'],
            'Engajamento': ['Engajamento', 'Interações', 'Interacoes'],
            'Posts': ['Posts', 'Postagens']
        }
        
        for oficial, variantes in mapping.items():
            for v in variantes:
                if v in df.columns and oficial not in df.columns:
                    df = df.rename(columns={v: oficial})
        
        # Converte números limpando pontos e vírgulas
        for col in ['Seguidores', 'Visualizacoes', 'Engajamento', 'Posts']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        # Cálculo de Taxa
        if 'Engajamento' in df.columns and 'Visualizacoes' in df.columns:
            df['Taxa (%)'] = (df['Engajamento'] / df['Visualizacoes'].replace(0, 1)) * 100
            
        return df
    except Exception as e:
        st.error(f"Erro na leitura: {e}")
        return None

# 3. Construção da Interface
df = load_data(SHEET_URL)

if df is not None and not df.empty:
    st.title("📊 Dashboard de Redes Sociais - Padre Ezequiel")
    st.markdown("---")
    
    # Filtros na Lateral
    st.sidebar.header("Configurações")
    if 'Plataforma' in df.columns:
        plats = st.sidebar.multiselect("Selecione as Redes Sociais", options=df['Plataforma'].unique(), default=df['Plataforma'].unique())
        df_final = df[df['Plataforma'].isin(plats)]
    else:
        df_final = df

    # KPIs (Cartões de Resumo)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Visualizações Totais", f"{df_final['Visualizacoes'].sum()/1e6:.1f}M")
    with c2: st.metric("Engajamento Total", f"{df_final['Engajamento'].sum()/1e6:.1f}M")
    with c3: 
        taxa_media = df_final['Taxa (%)'].mean() if 'Taxa (%)' in df_final.columns else 0
        st.metric("Taxa de Engaj. Média", f"{taxa_media:.2f}%")
    with c4: st.metric("Total de Posts", f"{int(df_final['Posts'].sum())}")

    st.markdown("### Análise de Desempenho")
    
    # Gráficos Lado a Lado
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Mes' in df_final.columns and 'Visualizacoes' in df_final.columns:
            fig1 = px.bar(df_final, x='Mes', y='Visualizacoes', color='Plataforma', barmode='group', 
                          title="Visualizações por Mês", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig1, use_container_width=True)
            
    with col2:
        if 'Mes' in df_final.columns and 'Seguidores' in df_final.columns:
            fig2 = px.line(df_final, x='Mes', y='Seguidores', color='Plataforma', markers=True,
                           title="Evolução de Seguidores", color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Tabela de Dados Detalhada")
    st.dataframe(df_final.style.format({'Taxa (%)': '{:.2f}%', 'Visualizacoes': '{:,.0f}', 'Engajamento': '{:,.0f}', 'Seguidores': '{:,.0f}'}), use_container_width=True)

else:
    st.warning("⚠️ Aguardando dados da planilha. Verifique se o link no código está correto e se a planilha foi publicada como CSV.")
