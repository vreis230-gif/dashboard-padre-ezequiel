import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração de Estilo e Página
st.set_page_config(page_title="Dashboard Padre Ezequiel", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; }
    h1, h2, h3 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fonte de Dados (Seu novo link atualizado)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSlkfkFYoG5-wbbixuRgxLrxpMLM4y1OjejJoInmKD43a9SL-ZtmSLQqZGuQnijyQ/pub?output=csv"

@st.cache_data(ttl=600 ) # Atualiza os dados a cada 10 minutos ou ao dar F5
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns] # Remove espaços nos nomes
        
        # Mapeamento inteligente para garantir que o código encontre as colunas
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
        
        # Limpeza de números (remove pontos de milhar e converte para numérico)
        for col in ['Seguidores', 'Visualizacoes', 'Engajamento', 'Posts']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        # Cálculo de métricas extras
        if 'Engajamento' in df.columns and 'Visualizacoes' in df.columns:
            df['Taxa (%)'] = (df['Engajamento'] / df['Visualizacoes'].replace(0, 1)) * 100
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None

# 3. Construção do Dashboard
df = load_data(SHEET_URL)

if df is not None and not df.empty:
    st.title("📊 Gestão de Redes Sociais - Padre Ezequiel")
    st.markdown("Análise trimestral de performance consolidada.")
    
    # Filtros na Barra Lateral
    st.sidebar.header("Filtros de Visualização")
    if 'Plataforma' in df.columns:
        opcoes_plat = sorted(df['Plataforma'].unique())
        selecao = st.sidebar.multiselect("Selecione as Redes Sociais", options=opcoes_plat, default=opcoes_plat)
        df_final = df[df['Plataforma'].isin(selecao)]
    else:
        df_final = df

    # Linha de Destaques (KPIs)
    st.markdown("### Resumo Geral")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Visualizações Totais", f"{df_final['Visualizacoes'].sum()/1e6:.1f}M")
    with c2: st.metric("Engajamento Total", f"{df_final['Engajamento'].sum()/1e6:.1f}M")
    with c3: 
        taxa = df_final['Taxa (%)'].mean() if 'Taxa (%)' in df_final.columns else 0
        st.metric("Taxa de Engaj. Média", f"{taxa:.2f}%")
    with c4: st.metric("Volume de Posts", f"{int(df_final['Posts'].sum())}")

    st.divider()

    # Gráficos de Performance
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Mes' in df_final.columns and 'Visualizacoes' in df_final.columns:
            # Ordenação manual dos meses para o gráfico
            ordem_meses = ['Março', 'Abril', 'Maio', 'Junho', 'Julho']
            df_final['Mes'] = pd.Categorical(df_final['Mes'], categories=ordem_meses, ordered=True)
            
            fig1 = px.bar(df_final.sort_values('Mes'), x='Mes', y='Visualizacoes', color='Plataforma', 
                          barmode='group', title="<b>Visualizações por Mês</b>",
                          color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig1, use_container_width=True)
            
    with col2:
        if 'Mes' in df_final.columns and 'Seguidores' in df_final.columns:
            fig2 = px.line(df_final.sort_values('Mes'), x='Mes', y='Seguidores', color='Plataforma', 
                           markers=True, title="<b>Evolução de Seguidores</b>",
                           color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig2, use_container_width=True)

    # Tabela Detalhada
    st.markdown("### Detalhamento dos Dados")
    cols_exibir = [c for c in ['Plataforma', 'Mes', 'Seguidores', 'Posts', 'Visualizacoes', 'Engajamento', 'Taxa (%)'] if c in df_final.columns]
    st.dataframe(
        df_final[cols_exibir].style.format({
            'Taxa (%)': '{:.2f}%', 
            'Visualizacoes': '{:,.0f}', 
            'Engajamento': '{:,.0f}', 
            'Seguidores': '{:,.0f}',
            'Posts': '{:.0f}'
        }), 
        use_container_width=True,
        hide_index=True
    )

    st.markdown(f"<div style='text-align: right; color: gray; font-size: 10px;'>Última atualização: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)

else:
    st.warning("⚠️ Planilha conectada, mas nenhum dado foi encontrado. Verifique se você colou os dados corretamente na sua Planilha do Google.")
