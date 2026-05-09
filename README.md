# NovaRota - Análise Inteligente de Rotas de Ônibus no Rio de Janeiro

NovaRota é um sistema inteligente de classificação e recomendação de linhas de ônibus desenvolvido durante o Processo Seletivo 2026.1 da UFRJ Analytica. O projeto integra dados de transporte público e criminalidade para informar sobre rotas mais seguras, confortáveis e eficientes no município do Rio de Janeiro.

🎯 Visão Geral
O NovaRota foi desenvolvido para resolver um problema recorrente na cidade do Rio de Janeiro: a falta de informações integradas sobre segurança e qualidade no transporte público. Nosso sistema incorpora:

- Dados de criminalidade próximos às rotas
- Conforto (presença de ar-condicionado, ano da frota)
- Eficiência (duração da viagem, número de paradas)
- Custo (tarifa da passagem)
- Duração das viagens

💡 Motivação
O Rio de Janeiro enfrenta desafios diários relacionados à violência urbana e à precariedade do transporte público. A maioria das soluções existentes prioriza apenas tempo de deslocamento e custo, negligenciando aspectos críticos como:

- Segurança durante o trajeto
- Qualidade dos veículos (ar-condicionado, conservação)
- Índices de criminalidade nas regiões atendidas
- O NovaRota preenche essa lacuna, oferecendo uma ferramenta que capacita o usuário a tomar decisões mais informadas sobre seu deslocamento.

📊 Dados Utilizados
Fontes
- SMTR / DataRio	Sistema Municipal de Transportes - rotas, paradas, viagens, tarifas	2025
- Fogo Cruzado (API)	Registros de violência armada com coordenadas geográficas	2025

Volume de Dados:
- 483 rotas de ônibus analisadas
- 27.200 viagens com dados completos
- 4.100 ocorrências criminais associadas espacialmente

Principais Variáveis
- Criminalidade	Crimes médio/máximo/mínimo por rota, % sem crime, crimes por horário (pico manhã/tarde/noite/fim de semana)
- Operacionais	Número de paradas, duração média da viagem, tarifa
- Conforto	Ano médio de fabricação da frota, presença de ar-condicionado
- Derivadas	Cluster de risco (Baixo/Médio/Alto), score de perigo
- Técnicas e Algoritmos

Pré-processamento
- Limpeza e tratamento de valores ausentes
- Remoção de duplicatas e feeds desatualizados
- Normalização e padronização de variáveis

Análise Geoespacial
- Buffers de 500m ao redor de cada parada para captura de crimes
- Buffers de 50m ao redor dos traçados LINESTRING para associação linha-parada
- Spatial joins com projeção métrica SIRGAS 2000 (EPSG:31983)

Machine Learning
- Modelo	Técnica	Resultado
- Classificação de Risco	Regressão Supervisionada	MAE, MSE, R² para validação
- Clusterização	K-Means (Elbow Method + Silhouette)	Silhouette Score: 0.37 com K=3
- Validação	Cross-Validation (KFold)	Avaliação de generalização
- Interpretabilidade	Feature Importance	Identificação dos principais preditores
- Recomendação
- Similaridade de Jaccard entre conjuntos de paradas
- Scores multicritério ponderados por perfil do usuário
- Ranking dinâmico baseado em prioridades

📈 Resultados
- Clusterização de Risco
- Cluster	Classificação	Número de Linhas
- Cluster 0	Baixo Risco	173
- Cluster 1	Médio Risco	271
- Cluster 2	Alto Risco	158
- Correlações Relevantes
- Correlação entre duração da viagem e número de paradas: 58%
- Correlação entre ar-condicionado e ano de fabricação: 88%

Insights Obtidos
- Concentração de crimes ocorre principalmente entre final da tarde e início da noite
- Regiões específicas da cidade apresentam densidade criminal significativamente maior
- Veículos mais novos (alto ano de fabricação) têm maior probabilidade de ter ar-condicionado
- Linhas com mais paradas tendem a ter maior duração de viagem (correlação 58%)

⚠️ Limitações
- Busca por linha, não por origem/destino - O sistema não realiza planejamento completo de rotas
- Subnotificação de crimes - Dados podem não representar totalidade das ocorrências
- Proximidade geográfica como proxy - Crimes próximos ≠ crimes dentro do ônibus
- Dados GTFS desatualizados - Necessidade de filtragem adicional
- Período reduzido - Projeto desenvolvido em 11 dias


🚀 Como Executar
- Pré-requisitos
- bash
- Python 3.9+
- pip install -r requirements.txt
- Instalação
- bash
- Clone o repositório
- git clone https://github.com/seu-usuario/novarota.git
- cd novarota
# Instale as dependências:
- pip install -r requirements.txt
- Executar a Aplicação Web
- bash
- streamlit run app.py
- Executar o Notebook de Análise
- bash
- jupyter notebook novarota_analysis.ipynb
# ou abra diretamente no Google Colab
