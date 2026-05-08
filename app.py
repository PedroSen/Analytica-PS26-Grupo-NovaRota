import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

# HEAD (Configurações da página)
st.set_page_config(
    page_title="NovaRota - Avaliador de Rotas de Ônibus RJ",
    page_icon="Logo_NovaRota.png",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .st-emotion-cache-uwwqev {
      text-align: center;
    }
    .ehg91i91 img {
      width: 20% !important;
      min-width: 100px !important;
    }
</style>
""", unsafe_allow_html=True)

# DICIONÁRIO DE PERFIS
# S = Segurança, C = Conforto, E = Eficiência, P = Preço
perfis_usuario = {
    'economico': {'S': 0.1, 'C': 0.1, 'E': 0.3, 'P': 0.5},
    'seguranca': {'S': 0.6, 'C': 0.2, 'E': 0.1, 'P': 0.1},
    'conforto': {'S': 0.1, 'C': 0.6, 'E': 0.2, 'P': 0.1},
    'balanceado': {'S': 0.25, 'C': 0.25, 'E': 0.25, 'P': 0.25}
}

# FUNÇÕES
# Funções de carregamento de dados para cada um dos nossos datasets
@st.cache_data
def load_routes():
    """Carrega dados das rotas"""
    try:
        df = pd.read_csv('routes.csv')
        return df
    except FileNotFoundError:
        st.error("Arquivo routes.csv não encontrado")
        return pd.DataFrame()

@st.cache_data
def load_trips():
    """Carrega dados das viagens"""
    try:
        df = pd.read_csv('trips.csv')
        return df
    except FileNotFoundError:
        st.error("Arquivo trips.csv não encontrado")
        return pd.DataFrame()

@st.cache_data
def load_safety_data():
    """Carrega dados de segurança"""
    try:
        df = pd.read_csv('fc_api_occurrences_with_victims_detailed_2026-04-29T20_25_59.000Z.csv')
        return df
    except FileNotFoundError:
        st.warning("Arquivo de segurança não encontrado")
        return pd.DataFrame()

@st.cache_data
def load_fare_rules():
    """Carrega dados de tarifas"""
    try:
        df = pd.read_csv('fare_rules.csv')
        return df
    except FileNotFoundError:
        st.warning("Arquivo de tarifas não encontrado")
        return pd.DataFrame()

# ============================================================================
# FUNÇÕES DE CÁLCULO DE MÉTRICAS
# ============================================================================
def calcular_metrica_seguranca(route_short_name, safety_df):
    """Calcula score de segurança (0-100)"""
    if safety_df.empty:
        return 50
    
    # Procura pela coluna correta de linha/rota
    linha_col = None
    for col in safety_df.columns:
        if 'linha' in col.lower() or 'route' in col.lower() or 'line' in col.lower():
            linha_col = col
            break
    
    if linha_col is None:
        return 50
    
    # Converte para string para comparação
    safety_df[linha_col] = safety_df[linha_col].astype(str)
    route_str = str(route_short_name)
    
    ocorrencias = safety_df[safety_df[linha_col].str.contains(route_str, na=False, case=False)].shape[0]
    
    if ocorrencias == 0:
        return 95
    
    # Calcular máximo de ocorrências
    max_ocorrencias = safety_df[linha_col].value_counts().max()
    
    if max_ocorrencias == 0:
        return 100
    
    # Quanto mais ocorrências, menor o score
    score = 100 - (ocorrencias / max_ocorrencias * 100)
    return max(0, min(100, score))

def calcular_metrica_conforto(route_id, trips_df):
    """Calcula score de conforto (0-100) baseado na frequência"""
    if trips_df.empty:
        return 50
    
    freq = trips_df[trips_df['route_id'] == route_id].shape[0]
    max_freq = trips_df['route_id'].value_counts().max()
    
    if max_freq == 0:
        return 50
    
    # Mais frequência = mais conforto (mais opções de viagem)
    score = (freq / max_freq) * 100
    return max(0, min(100, score))

def calcular_metrica_eficiencia(route_id, routes_df):
    """Calcula score de eficiência (0-100) baseado em comprimento da rota"""
    if routes_df.empty:
        return 50
    
    route = routes_df[routes_df['route_id'] == route_id]
    if route.empty:
        return 50
    
    # Considera que rotas mais curtas são mais eficientes
    # Se não houver coluna de distância, usar número de trips como proxy
    if 'route_distance' in routes_df.columns:
        route_distance = route.iloc[0].get('route_distance', 0)
        if isinstance(route_distance, (int, float)) and route_distance > 0:
            max_distance = routes_df['route_distance'].max()
            if max_distance == 0:
                return 50
            score = 100 - (route_distance / max_distance * 100)
            return max(0, min(100, score))
    
    return 50

def calcular_metrica_preco(route_id, fare_rules_df):
    """Calcula score de preço (0-100)"""
    if fare_rules_df.empty:
        return 75
    
    # Assume que todas as rotas têm tarifa padrão similar
    # Score de preço é normalizado (melhor preço = score maior)
    return 75

def calcular_score_final(metrics, perfil):
    """Calcula score final baseado no perfil selecionado"""
    pesos = perfis_usuario[perfil]
    
    score = (
        metrics['S'] * pesos['S'] +
        metrics['C'] * pesos['C'] +
        metrics['E'] * pesos['E'] +
        metrics['P'] * pesos['P']
    )
    
    return score

# ============================================================================
# TÍTULO E INTRODUÇÃO
# ============================================================================
st.title("NovaRota - Avaliador de Rotas de Ônibus RJ")
st.markdown("**Sistema inteligente de análise e recomendação de linhas de ônibus**")
st.markdown("Criado por Felipe Lemos, Julio Menescal, Marina Almeida de Aguiar e Pedro Sena")

# ============================================================================
# CARREGAR DADOS
# ============================================================================
routes_df = load_routes()
trips_df = load_trips()
safety_df = load_safety_data()
fare_rules_df = load_fare_rules()

if routes_df.empty:
    st.error("⚠️ Não foi possível carregar os dados. Certifique-se de que os arquivos CSV estão no diretório correto.")
    st.stop()

# ============================================================================
# SIDEBAR - SELEÇÃO DE PERFIL
# ============================================================================
st.sidebar.header("👤 Seu Perfil")
perfil_selecionado = st.sidebar.radio(
    "Selecione seu perfil de preferência:",
    options=list(perfis_usuario.keys()),
    format_func=lambda x: {
        'economico': '💰 Econômico',
        'seguranca': '🛡️ Segurança',
        'conforto': '🪑 Conforto',
        'balanceado': '⚖️ Balanceado'
    }[x]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Pesos do Perfil Selecionado")
pesos = perfis_usuario[perfil_selecionado]
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Segurança", f"{pesos['S']:.0%}")
    st.metric("Eficiência", f"{pesos['E']:.0%}")
with col2:
    st.metric("Conforto", f"{pesos['C']:.0%}")
    st.metric("Preço", f"{pesos['P']:.0%}")

# ============================================================================
# SEÇÃO PRINCIPAL - BUSCA DE LINHA
# ============================================================================
st.header("🔍 Buscar Linha de Ônibus")

# Lista de rotas disponíveis
rotas_disponiveis = sorted(routes_df['route_short_name'].unique())
rota_selecionada = st.selectbox(
    "Selecione a linha de ônibus:",
    options=rotas_disponiveis,
    help="Escolha uma linha para analisar"
)

if rota_selecionada:
    # Filtrar dados da rota selecionada
    route_data = routes_df[routes_df['route_short_name'] == rota_selecionada].iloc[0]
    route_id = route_data['route_id']
    
    # Calcular métricas
    metrics = {
        'S': calcular_metrica_seguranca(rota_selecionada, safety_df),
        'C': calcular_metrica_conforto(route_id, trips_df),
        'E': calcular_metrica_eficiencia(route_id, routes_df),
        'P': calcular_metrica_preco(route_id, fare_rules_df)
    }
    
    score_final = calcular_score_final(metrics, perfil_selecionado)
    
    # ====================================================================
    # EXIBIR DADOS DA LINHA
    # ====================================================================
    st.subheader(f"📋 Informações da Linha {rota_selecionada}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Nome Longo:** {route_data.get('route_long_name', 'N/A')}")
    with col2:
        st.write(f"**Operadora:** {route_data.get('agency_id', 'N/A')}")
    with col3:
        st.write(f"**Tipo:** {route_data.get('route_type', 'N/A')}")
    
    st.markdown("---")
    
    # ====================================================================
    # SCORE FINAL E MÉTRICAS
    # ====================================================================
    st.subheader("📊 Análise da Linha")
    
    # Score principal
    col_score = st.columns([2, 1])[0]
    with col_score:
        # Cor baseada no score
        if score_final >= 80:
            cor_score = "🟢"
            avaliacao = "Excelente"
        elif score_final >= 60:
            cor_score = "🟡"
            avaliacao = "Bom"
        elif score_final >= 40:
            cor_score = "🟠"
            avaliacao = "Aceitável"
        else:
            cor_score = "🔴"
            avaliacao = "Baixo"
        
        st.metric(
            f"{cor_score} Score Final (Perfil: {perfil_selecionado.upper()})",
            f"{score_final:.1f}",
            delta=avaliacao,
            delta_color="off"
        )
    
    # Métricas detalhadas
    st.markdown("### Métricas Detalhadas")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🛡️ Segurança", f"{metrics['S']:.1f}", help="Score de segurança da rota")
    with col2:
        st.metric("🪑 Conforto", f"{metrics['C']:.1f}", help="Score de conforto/frequência")
    with col3:
        st.metric("⚡ Eficiência", f"{metrics['E']:.1f}", help="Score de eficiência")
    with col4:
        st.metric("💵 Preço", f"{metrics['P']:.1f}", help="Score de preço")
    
    # Gráfico Radar
    st.markdown("### Visualização Geral")
    
    fig = go.Figure(data=go.Scatterpolar(
        r=[metrics['S'], metrics['C'], metrics['E'], metrics['P']],
        theta=['Segurança', 'Conforto', 'Eficiência', 'Preço'],
        fill='toself',
        name='Linha ' + rota_selecionada,
        marker=dict(color='rgba(31, 119, 180, 0.5)'),
        line=dict(color='rgb(31, 119, 180)')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title=f'Perfil de Avaliação - Linha {rota_selecionada}',
        height=500,
        showlegend=True,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ====================================================================
    # LINHAS RECOMENDADAS
    # ====================================================================
    st.subheader("🔗 Linhas Similares Recomendadas")
    
    # Calcular métricas para todas as rotas
    todas_metricas = []
    todas_rotas = []
    
    for idx, row in routes_df.iterrows():
        rid = row['route_id']
        short_name = row['route_short_name']
        m = {
            'S': calcular_metrica_seguranca(short_name, safety_df),
            'C': calcular_metrica_conforto(rid, trips_df),
            'E': calcular_metrica_eficiencia(rid, routes_df),
            'P': calcular_metrica_preco(rid, fare_rules_df)
        }
        todas_metricas.append([m['S'], m['C'], m['E'], m['P']])
        todas_rotas.append({
            'route_id': rid,
            'route_short_name': short_name,
            'metrics': m
        })
    
    # Calcular similaridade
    if len(todas_metricas) > 0:
        metricas_array = np.array(todas_metricas)
        metricas_rota_atual = np.array([[metrics['S'], metrics['C'], metrics['E'], metrics['P']]])
        
        similaridades = cosine_similarity(metricas_rota_atual, metricas_array)[0]
        
        # Ordenar por similaridade (excluir a própria rota)
        similar_indices = np.argsort(-similaridades)
        recomendacoes = []
        
        for idx in similar_indices:
            if todas_rotas[idx]['route_short_name'] != rota_selecionada and len(recomendacoes) < 5:
                score = calcular_score_final(todas_rotas[idx]['metrics'], perfil_selecionado)
                recomendacoes.append({
                    'linha': todas_rotas[idx]['route_short_name'],
                    'score': score,
                    'similaridade': similaridades[idx],
                    'metrics': todas_rotas[idx]['metrics']
                })
        
        if recomendacoes:
            for i, rec in enumerate(recomendacoes, 1):
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.write(f"**#{i} Linha {rec['linha']}**")
                with col2:
                    st.write(f"Score: {rec['score']:.1f}")
                with col3:
                    st.write(f"Segurança: {rec['metrics']['S']:.0f}")
                with col4:
                    st.write(f"Conforto: {rec['metrics']['C']:.0f}")
                with col5:
                    st.write(f"Eficiência: {rec['metrics']['E']:.0f}")
                
                st.divider()
        else:
            st.info("Nenhuma linha similar encontrada.")

else:
    st.info("👈 Selecione uma linha na barra lateral para começar a análise.")

# RODAPÉ
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <p>Analytica - Sistema de Análise de Rotas de Ônibus do Rio de Janeiro</p>
    <p>Desenvolvido pelo Grupo N - Processo Seletivo UFRJ Analytica</p>
</div>
""", unsafe_allow_html=True)
