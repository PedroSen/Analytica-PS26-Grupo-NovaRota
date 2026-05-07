import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title='Análise de Perigo das Linhas',
    layout='wide'
)

# ==========================================
# CARREGAMENTO DOS DADOS
# ==========================================

@st.cache_data

def carregar_dados():
    df = pd.read_csv('dataset_agregado.csv')
    return df


df = carregar_dados()

# ==========================================
# TÍTULO
# ==========================================

st.title('🚌 Sistema de Análise de Perigo das Linhas')

st.markdown(
    '''
    Esta aplicação permite visualizar:

    - Score de perigo das linhas;
    - Estatísticas de crimes;
    - Perfil de risco;
    - Informações de conforto;
    - Dados de preço;
    - Comparação entre linhas.
    '''
)

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.header('Filtros')

# Lista de linhas
linhas = sorted(df['route_short_name'].astype(str).unique())

linha_escolhida = st.sidebar.selectbox(
    'Escolha uma linha:',
    linhas
)

# ==========================================
# FILTRAR LINHA
# ==========================================

linha_df = df[df['route_short_name'].astype(str) == linha_escolhida]

if linha_df.empty:
    st.error('Linha não encontrada.')
    st.stop()

linha = linha_df.iloc[0]

# ==========================================
# DEFINIR COR DO RISCO
# ==========================================

def cor_risco(score):
    if score >= 70:
        return 'red'
    elif score >= 40:
        return 'orange'
    return 'green'

cor = cor_risco(linha['nivel_perigo_score'])

# ==========================================
# INFORMAÇÕES PRINCIPAIS
# ==========================================

st.header(f'Linha {linha_escolhida}')

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        '⚠️ Nível de Perigo',
        f"{linha['nivel_perigo_score']:.2f}"
    )

with col2:
    st.metric(
        '🚨 Crimes Totais',
        int(linha['crimes_total'])
    )

with col3:
    st.metric(
        '🛑 Número de Paradas',
        int(linha['n_paradas'])
    )

with col4:
    st.metric(
        '💰 Preço Médio',
        f"R$ {linha['price']:.2f}"
    )

# ==========================================
# PERFIL DE RISCO
# ==========================================

st.subheader('Perfil de Risco')

st.markdown(
    f'''
    <div style="
        background-color:{cor};
        padding:20px;
        border-radius:10px;
        color:white;
        font-size:24px;
        text-align:center;
        font-weight:bold;
    ">
        {linha['perfil_risco']}
    </div>
    ''',
    unsafe_allow_html=True
)

# ==========================================
# DETALHES DA LINHA
# ==========================================

st.subheader('Detalhes da Linha')

colA, colB = st.columns(2)

with colA:
    st.write('### Segurança')
    st.write(f"Crimes médios: {linha['crimes_medio']:.2f}")
    st.write(f"Crimes máximos: {linha['crimes_max']:.2f}")
    st.write(f"% sem crimes: {linha['pct_sem_crime']:.2f}%")

with colB:
    st.write('### Conforto')

    if 'indicador_ar_condicionado' in linha.index:
        st.write(
            f"Ar condicionado: {linha['indicador_ar_condicionado'] * 100:.1f}%"
        )

    if 'ano_fabricacao' in linha.index:
        st.write(
            f"Ano médio da frota: {linha['ano_fabricacao']:.0f}"
        )

    if 'duracao_viagem' in linha.index:
        st.write(
            f"Duração média da viagem: {linha['duracao_viagem']:.1f} min"
        )

# ==========================================
# GRÁFICO DE CRIMES TEMPORAIS
# ==========================================

st.subheader('Crimes por Período')

crimes_temporais = {
    'Pico Manhã': linha.get('crimes_pico_manha', 0),
    'Pico Tarde': linha.get('crimes_pico_tarde', 0),
    'Noturnos': linha.get('crimes_noturnos', 0),
    'Fim de Semana': linha.get('crimes_fim_semana', 0)
}

fig, ax = plt.subplots(figsize=(8, 4))

ax.bar(
    crimes_temporais.keys(),
    crimes_temporais.values()
)

ax.set_title('Distribuição Temporal dos Crimes')
ax.set_ylabel('Quantidade')

st.pyplot(fig)

# ==========================================
# COMPARAÇÃO COM AS LINHAS MAIS SEGURAS
# ==========================================

st.subheader('Comparação com Linhas Mais Seguras')

mais_seguras = df.sort_values(
    by='nivel_perigo_score'
).head(10)

fig2, ax2 = plt.subplots(figsize=(12, 5))

sns.barplot(
    data=mais_seguras,
    x='route_short_name',
    y='nivel_perigo_score',
    ax=ax2
)

ax2.set_title('Top 10 Linhas Mais Seguras')
ax2.set_xlabel('Linha')
ax2.set_ylabel('Score de Perigo')

st.pyplot(fig2)

# ==========================================
# COMPARAÇÃO COM AS LINHAS MAIS PERIGOSAS
# ==========================================

st.subheader('Linhas Mais Perigosas')

mais_perigosas = df.sort_values(
    by='nivel_perigo_score',
    ascending=False
).head(10)

fig3, ax3 = plt.subplots(figsize=(12, 5))

sns.barplot(
    data=mais_perigosas,
    x='route_short_name',
    y='nivel_perigo_score',
    ax=ax3
)

ax3.set_title('Top 10 Linhas Mais Perigosas')
ax3.set_xlabel('Linha')
ax3.set_ylabel('Score de Perigo')

st.pyplot(fig3)

# ==========================================
# TABELA COMPLETA
# ==========================================

st.subheader('Tabela Completa das Linhas')

st.dataframe(
    df[
        [
            'route_short_name',
            'nivel_perigo_score',
            'perfil_risco',
            'crimes_total',
            'crimes_medio',
            'n_paradas',
            'price'
        ]
    ].sort_values(
        by='nivel_perigo_score',
        ascending=False
    ),
    use_container_width=True
)

# ==========================================
# DOWNLOAD CSV
# ==========================================

st.subheader('Download dos Dados')

csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label='📥 Baixar CSV',
    data=csv,
    file_name='linhas_onibus_perigo.csv',
    mime='text/csv'
)