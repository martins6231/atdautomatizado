# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64
from streamlit_option_menu import option_menu

# ----- CONFIGURAÇÃO DA PÁGINA -----
st.set_page_config(
    page_title="Análise de Eficiência de Máquinas",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----- ESTILOS CSS UNIFICADOS -----
# ----- ESTILOS CSS UNIFICADOS -----
def aplicar_estilos():
    """Aplica estilos CSS unificados para toda a aplicação."""
    st.markdown(
        """
        <style>
        /* Estilos gerais */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        /* Títulos e cabeçalhos */
        .main-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 1.5rem;
            padding: 1rem 0;
            border-bottom: 3px solid #3498db;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #3498db;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            text-align: center;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .sub-header {
            font-size: 1.8rem;
            color: #3498db;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #3498db;
        }
        
        /* Métricas e indicadores */
        .metrics-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .metric-box {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1.2rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            border-top: 4px solid #3498db;
            flex: 1;
            min-width: 200px;
            max-width: 250px;
            margin: 0 auto;
        }
        
        .metric-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 1rem;
            color: #7f8c8d;
        }
        
        /* Contêineres e caixas */
        .content-box {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .info-box {
            background-color: #e8f4f8;
            border-left: 5px solid #3498db;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.25rem;
        }
        
        /* Gráficos e tabelas */
        .chart-container {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s;
            max-width: 100%;
            min-width: 300px;
        }
        
        .chart-container:hover {
            transform: translateY(-5px);
        }
        
        .table-container {
            margin-top: 1rem;
            margin-bottom: 2rem;
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        /* Botões e interações */
        .stButton>button {
            background-color: #3498db;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: bold;
            transition: background-color 0.3s;
            margin-top: 1rem;
        }
        
        .stButton>button:hover {
            background-color: #2980b9;
        }
        
        /* Rodapé */
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #e0e0e0;
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        
        /* Ajustes responsivos */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2rem;
            }
            
            .section-title {
                font-size: 1.3rem;
            }
            
            .metric-value {
                font-size: 1.5rem;
            }
        }
        
        /* Melhorias para o menu de navegação */
        .nav-container {
            margin-bottom: 2rem;
        }
        
        /* Ajustes para os expandables */
        .streamlit-expanderHeader {
            font-weight: bold;
            color: #3498db;
        }
        
        /* Melhorias para o file uploader */
        .uploadedFile {
            border: 1px dashed #3498db;
            border-radius: 5px;
            padding: 0.5rem;
        }
        
        /* Melhorias para selectbox */
        .stSelectbox label {
            color: #2c3e50;
            font-weight: 500;
        }
        
        /* Centraliza os gráficos e ajusta margens */
        .stPlotlyChart {
            display: block;
            margin: 0 auto !important; 
            padding-bottom: 1rem;
        }
        
        /* Ajustes para o layout geral e espaçamento */
        div[data-testid="stHorizontalBlock"] {
            justify-content: center !important;
            align-items: center !important;
            gap: 1rem !important;
        }
        
        /* Ajuste para colunas */
        div[data-testid="column"] {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            width: 100%;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

# Aplica os estilos CSS
aplicar_estilos()

# ----- FUNÇÕES AUXILIARES -----
@st.cache_data
def formatar_duracao(duracao):
    """Formata uma duração (timedelta) para exibição amigável."""
    if pd.isna(duracao):
        return "00:00:00"
    
    total_segundos = int(duracao.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

@st.cache_data
def obter_nome_mes(mes_ano):
    """Converte o formato 'YYYY-MM' para um nome de mês legível."""
    if mes_ano == 'Todos':
        return 'Todos os Meses'
    
    try:
        data = datetime.strptime(mes_ano, '%Y-%m')
        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return f"{meses_pt[data.month]} {data.year}"
    except:
        return mes_ano

@st.cache_data
def processar_dados(df):
    """Processa e limpa os dados do DataFrame."""
    # Cria uma cópia para evitar SettingWithCopyWarning
    df_processado = df.copy()
    
    # Substitui os valores da coluna 'Máquina' por nomes específicos
    machine_mapping = {
        78: "PET",
        79: "TETRA 1000",
        80: "TETRA 200",
        89: "SIG 1000",
        91: "SIG 200"
    }
    
    # Verifica se a coluna 'Máquina' existe
    if 'Máquina' in df_processado.columns:
        df_processado['Máquina'] = df_processado['Máquina'].replace(machine_mapping)
    
    # Converte as colunas de tempo para o formato datetime
    for col in ['Inicio', 'Fim']:
        if col in df_processado.columns:
            df_processado[col] = pd.to_datetime(df_processado[col], errors='coerce')
    
    # Processa a coluna de duração
    if 'Duração' in df_processado.columns:
        # Tenta converter a coluna Duração para timedelta
        try:
            df_processado['Duração'] = pd.to_timedelta(df_processado['Duração'])
        except:
            # Se falhar, tenta extrair horas, minutos e segundos e criar um timedelta
            if isinstance(df_processado['Duração'].iloc[0], str):
                def parse_duration(duration_str):
                    try:
                        parts = duration_str.split(':')
                        if len(parts) == 3:
                            hours, minutes, seconds = map(int, parts)
                            return pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds)
                        else:
                            return pd.NaT
                    except:
                        return pd.NaT
                
                df_processado['Duração'] = df_processado['Duração'].apply(parse_duration)
    
    # Adiciona colunas de ano, mês e ano-mês para facilitar a filtragem
    df_processado['Ano'] = df_processado['Inicio'].dt.year
    df_processado['Mês'] = df_processado['Inicio'].dt.month
    df_processado['Mês_Nome'] = df_processado['Inicio'].dt.strftime('%B')  # Nome do mês
    df_processado['Ano-Mês'] = df_processado['Inicio'].dt.strftime('%Y-%m')
    
    # Remove registros com valores ausentes nas colunas essenciais
    df_processado = df_processado.dropna(subset=['Máquina', 'Inicio', 'Fim', 'Duração'])
    
    return df_processado

# ----- FUNÇÕES DE CÁLCULO DE INDICADORES -----
@st.cache_data
def calcular_disponibilidade(df, tempo_programado):
    """Calcula a taxa de disponibilidade."""
    tempo_total_parado = df['Duração'].sum()
    disponibilidade = (tempo_programado - tempo_total_parado) / tempo_programado * 100
    return max(0, min(100, disponibilidade))

@st.cache_data
def indice_paradas_por_area(df):
    """Calcula o índice de paradas por área responsável."""
    if 'Área Responsável' in df.columns:
        area_counts = df['Área Responsável'].value_counts(normalize=True) * 100
        return area_counts
    else:
        return pd.Series()

@st.cache_data
def pareto_causas_parada(df):
    """Identifica as principais causas de paradas (Pareto) por duração total."""
    if 'Parada' in df.columns:
        pareto = df.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
        return pareto
    else:
        return pd.Series()

@st.cache_data
def tempo_medio_paradas(df):
    """Calcula o tempo médio de parada (TMP)."""
    tmp = df['Duração'].mean()
    return tmp

@st.cache_data
def taxa_ocorrencia_paradas(df):
    """Calcula a taxa de ocorrência de paradas (número total de paradas por mês)."""
    ocorrencias_mensais = df.groupby('Ano-Mês').size()
    return ocorrencias_mensais

@st.cache_data
def tempo_total_paradas_area(df):
    """Calcula o tempo total de paradas por área."""
    if 'Área Responsável' in df.columns:
        tempo_por_area = df.groupby('Área Responsável')['Duração'].sum()
        return tempo_por_area
    else:
        return pd.Series()

@st.cache_data
def frequencia_categorias_paradas(df):
    """Calcula a frequência de paradas por categoria."""
    if 'Parada' in df.columns:
        frequencia = df['Parada'].value_counts()
        return frequencia
    else:
        return pd.Series()

@st.cache_data
def eficiencia_operacional(df, tempo_programado):
    """Calcula a eficiência operacional."""
    tempo_operacao = tempo_programado - df['Duração'].sum()
    eficiencia = tempo_operacao / tempo_programado * 100
    return max(0, min(100, eficiencia))

@st.cache_data
def indice_paradas_criticas(df, limite_horas=1):
    """Identifica paradas críticas (com duração maior que o limite especificado)."""
    limite = pd.Timedelta(hours=limite_horas)
    paradas_criticas = df[df['Duração'] > limite]
    percentual_criticas = len(paradas_criticas) / len(df) * 100 if len(df) > 0 else 0
    return paradas_criticas, percentual_criticas

# ----- FUNÇÕES DE VISUALIZAÇÃO -----
@st.cache_data
def criar_grafico_pareto(pareto):
    """Cria um gráfico de Pareto com Plotly."""
    if pareto.empty:
        return None
    
    # Converte durações para horas
    pareto_horas = pareto.apply(lambda x: x.total_seconds() / 3600)
    
    fig = px.bar(
        x=pareto_horas.index,
        y=pareto_horas.values,
        labels={'x': 'Causa de Parada', 'y': 'Duração Total (horas)'},
        title="Pareto de Causas de Paradas (Top 10 por Duração)",
        color_discrete_sequence=['#3498db'],
        text=pareto_horas.values.round(1)
    )
    
    fig.update_traces(
        texttemplate='%{text}h', 
        textposition='outside'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Duração Total (horas)",
        xaxis_title="Causa de Parada",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        # Adicionando essas configurações para melhor centralização
        width=None,  # Deixa o Streamlit definir a largura
        height=500,  # Altura fixa para melhor visualização
        template="plotly_white"  # Template limpo
    )
    
    return fig

@st.cache_data
def criar_grafico_pizza_areas(indice_paradas):
    """Cria um gráfico de pizza para áreas responsáveis com Plotly."""
    if indice_paradas.empty:
        return None
    
    fig = px.pie(
        values=indice_paradas.values,
        names=indice_paradas.index,
        title="Índice de Paradas por Área Responsável",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4  # Cria um gráfico de donut para melhor visualização
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        pull=[0.05 if i == indice_paradas.values.argmax() else 0 for i in range(len(indice_paradas))]  # Destaca o maior valor
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_ocorrencias(ocorrencias):
    """Cria um gráfico de linha para ocorrências mensais com Plotly."""
    if ocorrencias.empty or len(ocorrencias) <= 1:
        return None
    
    fig = px.line(
        x=ocorrencias.index,
        y=ocorrencias.values,
        markers=True,
        labels={'x': 'Mês', 'y': 'Número de Paradas'},
        title="Taxa de Ocorrência de Paradas por Mês",
        color_discrete_sequence=['#2ecc71']
    )
    
    # Adiciona área sob a linha para melhor visualização de tendências
    fig.add_trace(
        go.Scatter(
            x=ocorrencias.index,
            y=ocorrencias.values,
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.2)',
            line=dict(color='rgba(46, 204, 113, 0)'),
            showlegend=False
        )
    )
    
    # Adiciona valores acima dos pontos
    for i, v in enumerate(ocorrencias):
        fig.add_annotation(
            x=ocorrencias.index[i],
            y=v,
            text=str(v),
            showarrow=False,
            yshift=10,
            font=dict(color="#2c3e50")
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Número de Paradas",
        xaxis_title="Mês",
        hovermode="x unified",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_tempo_area(tempo_area):
    """Cria um gráfico de barras horizontais para tempo por área com Plotly."""
    if tempo_area.empty:
        return None
    
    # Converte durações para horas
    tempo_area_horas = tempo_area.apply(lambda x: x.total_seconds() / 3600)
    
    # Ordena os dados para melhor visualização
    tempo_area_horas = tempo_area_horas.sort_values(ascending=True)
    
    fig = px.bar(
        y=tempo_area_horas.index,
        x=tempo_area_horas.values,
        orientation='h',
        labels={'y': 'Área Responsável', 'x': 'Duração Total (horas)'},
        title="Tempo Total de Paradas por Área",
        color_discrete_sequence=['#e74c3c'],
        text=tempo_area_horas.values.round(1)
    )
    
    fig.update_traces(
        texttemplate='%{text}h', 
        textposition='outside'
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Duração Total (horas)",
        yaxis_title="Área Responsável",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_paradas_criticas(top_criticas):
    """Cria um gráfico de barras horizontais para paradas críticas com Plotly."""
    if top_criticas.empty:
        return None
    
    # Converte durações para horas
    top_criticas_horas = top_criticas.apply(lambda x: x.total_seconds() / 3600)
    
    # Ordena os dados para melhor visualização
    top_criticas_horas = top_criticas_horas.sort_values(ascending=True)
    
    fig = px.bar(
        y=top_criticas_horas.index,
        x=top_criticas_horas.values,
        orientation='h',
        labels={'y': 'Tipo de Parada', 'x': 'Duração Total (horas)'},
        title="Top 10 Paradas Críticas (>1h)",
        color_discrete_sequence=['#9b59b6'],
        text=top_criticas_horas.values.round(1)
    )
    
    fig.update_traces(
        texttemplate='%{text}h', 
        textposition='outside'
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Duração Total (horas)",
        yaxis_title="Tipo de Parada",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_pizza_areas_criticas(paradas_criticas):
    """Cria um gráfico de pizza para áreas responsáveis por paradas críticas."""
    if 'Área Responsável' not in paradas_criticas.columns or paradas_criticas.empty:
        return None
    
    areas_criticas = paradas_criticas['Área Responsável'].value_counts()
    
    fig = px.pie(
        values=areas_criticas.values,
        names=areas_criticas.index,
        title="Distribuição de Paradas Críticas por Área",
        color_discrete_sequence=px.colors.qualitative.Bold,
        hole=0.4  # Cria um gráfico de donut para melhor visualização
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        pull=[0.05 if i == areas_criticas.values.argmax() else 0 for i in range(len(areas_criticas))]  # Destaca o maior valor
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_evolucao_paradas(paradas_por_mes):
    """Cria um gráfico de linha para evolução do número de paradas por mês."""
    if paradas_por_mes.empty or len(paradas_por_mes) <= 1:
        return None
    
    fig = px.line(
        x=paradas_por_mes.index,
        y=paradas_por_mes['Número de Paradas'],
        markers=True,
        labels={'x': 'Mês', 'y': 'Número de Paradas'},
        title="Evolução do Número de Paradas por Mês",
        color_discrete_sequence=['#3498db']
    )
    
    # Adiciona área sob a linha para melhor visualização de tendências
    fig.add_trace(
        go.Scatter(
            x=paradas_por_mes.index,
            y=paradas_por_mes['Número de Paradas'],
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.2)',
            line=dict(color='rgba(52, 152, 219, 0)'),
            showlegend=False
        )
    )
    
    # Adiciona valores acima dos pontos
    for i, v in enumerate(paradas_por_mes['Número de Paradas']):
        fig.add_annotation(
            x=paradas_por_mes.index[i],
            y=v,
            text=str(v),
            showarrow=False,
            yshift=10,
            font=dict(color="#2c3e50")
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Número de Paradas",
        xaxis_title="Mês",
        hovermode="x unified",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def criar_grafico_evolucao_duracao(paradas_por_mes):
    """Cria um gráfico de linha para evolução da duração total de paradas por mês."""
    if paradas_por_mes.empty or len(paradas_por_mes) <= 1:
        return None
    
    fig = px.line(
        x=paradas_por_mes.index,
        y=paradas_por_mes['Duração (horas)'],
        markers=True,
        labels={'x': 'Mês', 'y': 'Duração Total (horas)'},
        title="Evolução da Duração Total de Paradas por Mês",
        color_discrete_sequence=['#e74c3c']
    )
    
    # Adiciona área sob a linha para melhor visualização de tendências
    fig.add_trace(
        go.Scatter(
            x=paradas_por_mes.index,
            y=paradas_por_mes['Duração (horas)'],
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.2)',
            line=dict(color='rgba(231, 76, 60, 0)'),
            showlegend=False
        )
    )
    
    # Adiciona valores acima dos pontos
    for i, v in enumerate(paradas_por_mes['Duração (horas)']):
        fig.add_annotation(
            x=paradas_por_mes.index[i],
            y=v,
            text=f"{v:.1f}h",
            showarrow=False,
            yshift=10,
            font=dict(color="#2c3e50")
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Duração Total (horas)",
        xaxis_title="Mês",
        hovermode="x unified",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

# ----- FUNÇÕES UTILITÁRIAS -----
def get_download_link(df, filename, text):
    """Gera um link para download de um DataFrame como arquivo Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Dados', index=False)
    
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="download-button">{text}</a>'
    return href

# ----- FUNÇÃO PRINCIPAL DE ANÁLISE -----
def analisar_dados(df, maquina=None, mes=None):
    """Realiza a análise dos dados com base na máquina e mês selecionados."""
    # Filtra os dados conforme seleção
    dados_filtrados = df.copy()
    
       # Filtra por máquina se especificada
    if maquina != "Todas":
        dados_filtrados = dados_filtrados[dados_filtrados['Máquina'] == maquina]
    
    # Filtra por mês se especificado e diferente de 'Todos'
    if mes != 'Todos':
        dados_filtrados = dados_filtrados[dados_filtrados['Ano-Mês'] == mes]
    
    # Verifica se há dados para a seleção atual
    if len(dados_filtrados) == 0:
        st.error("Não há dados disponíveis para os filtros selecionados.")
        return
    
    # Prepara mensagem informativa sobre os filtros aplicados
    filtro_maquina = f"máquina: **{maquina}**" if maquina != "Todas" else "todas as máquinas"
    filtro_mes = f"mês: **{obter_nome_mes(mes)}**" if mes != 'Todos' else "todos os meses"
    
    with st.container():
        st.markdown(f"""
        <div class="info-box">
            Analisando dados para {filtro_maquina}, {filtro_mes} ({len(dados_filtrados)} registros)
        </div>
        """, unsafe_allow_html=True)
    
    # Tempo programado (por exemplo, 24 horas em um dia)
    dias_unicos = dados_filtrados['Inicio'].dt.date.nunique()
    tempo_programado = pd.Timedelta(hours=24 * dias_unicos)  # Exemplo simplificado
    
    # Calcula os indicadores
    disponibilidade = calcular_disponibilidade(dados_filtrados, tempo_programado)
    indice_paradas = indice_paradas_por_area(dados_filtrados)
    pareto = pareto_causas_parada(dados_filtrados)
    tmp = tempo_medio_paradas(dados_filtrados)
    ocorrencias = taxa_ocorrencia_paradas(dados_filtrados)
    tempo_area = tempo_total_paradas_area(dados_filtrados)
    frequencia_categorias = frequencia_categorias_paradas(dados_filtrados)
    eficiencia = eficiencia_operacional(dados_filtrados, tempo_programado)
    paradas_criticas, percentual_criticas = indice_paradas_criticas(dados_filtrados)
    
    # --- EXIBIÇÃO DOS INDICADORES PRINCIPAIS ---
st.markdown('<div class="section-title">Indicadores Principais</div>', unsafe_allow_html=True)

# Layout centralizado para indicadores
with st.container():
    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
        disponibilidade = 0.0 if 'disponibilidade' not in locals() else disponibilidade
            <div class="metric-value">{disponibilidade:.1f}%</div>
            <div class="metric-label">Disponibilidade</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{eficiencia:.1f}%</div>
            <div class="metric-label">Eficiência Operacional</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{formatar_duracao(tmp)}</div>
            <div class="metric-label">Tempo Médio de Paradas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{percentual_criticas:.1f}%</div>
            <div class="metric-label">Paradas Críticas (>1h)</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- VISUALIZAÇÃO DE GRÁFICOS ---
st.markdown('<div class="section-title">Análise Gráfica</div>', unsafe_allow_html=True)

# Layout para os gráficos em grid
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico 1: Pareto de Causas de Paradas
        fig_pareto = criar_grafico_pareto(pareto)
        if fig_pareto:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_pareto, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de Pareto.")
    
    with col2:
        # Gráfico 2: Índice de Paradas por Área Responsável
        fig_areas = criar_grafico_pizza_areas(indice_paradas)
        if fig_areas:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_areas, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de áreas responsáveis.")

with st.container():
    col3, col4 = st.columns(2)
    
    with col3:
        # Gráfico 3: Taxa de Ocorrência de Paradas por Mês
        fig_ocorrencias = criar_grafico_ocorrencias(ocorrencias)
        if fig_ocorrencias and len(ocorrencias) > 1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_ocorrencias, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de ocorrências mensais (necessário mais de um mês).")
    
    with col4:
        # Gráfico 4: Tempo Total de Paradas por Área
        fig_tempo_area = criar_grafico_tempo_area(tempo_area)
        if fig_tempo_area:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_tempo_area, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de tempo por área.")
    
    # Análise de Paradas Críticas
if len(paradas_criticas) > 0:
    st.markdown('<div class="section-title">Análise de Paradas Críticas (>1h)</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-box">
        Foram identificadas <b>{len(paradas_criticas)}</b> paradas críticas (duração > 1 hora), 
        representando <b>{percentual_criticas:.1f}%</b> do total de paradas.
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        col5, col6 = st.columns(2)
        
        with col5:
            # Gráfico 5: Top 10 Paradas Críticas
            top_criticas = paradas_criticas.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
            fig_criticas = criar_grafico_paradas_criticas(top_criticas)
            if fig_criticas:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig_criticas, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Dados insuficientes para gerar o gráfico de paradas críticas.")
        
        with col6:
            # Gráfico 6: Distribuição de Paradas Críticas por Área
            fig_areas_criticas = criar_grafico_pizza_areas_criticas(paradas_criticas)
            if fig_areas_criticas:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(fig_areas_criticas, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Dados insuficientes para gerar o gráfico de distribuição de paradas críticas.")
    
    # --- TABELAS DE RESUMO ---
    st.markdown('<div class="section-title">Tabelas de Resumo</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Paradas Mais Frequentes", "⏱️ Paradas Mais Longas"])
    
    with tab1:
        # Tabela de resumo das paradas mais frequentes
        if not frequencia_categorias.empty:
            top_frequencia = frequencia_categorias.head(10).reset_index()
            top_frequencia.columns = ['Tipo de Parada', 'Frequência']
            
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.dataframe(
                top_frequencia,
                column_config={
                    "Tipo de Parada": st.column_config.TextColumn("Tipo de Parada"),
                    "Frequência": st.column_config.NumberColumn("Frequência", format="%d")
                },
                use_container_width=True,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botão para download da tabela
            st.markdown(
                get_download_link(top_frequencia, 'paradas_frequentes.xlsx', '📥 Baixar tabela de paradas frequentes'),
                unsafe_allow_html=True
            )
        else:
            st.info("Dados insuficientes para gerar a tabela de paradas frequentes.")
    
    with tab2:
        # Tabela de resumo das paradas mais longas
        if not pareto.empty:
            top_duracao = pareto.reset_index()
            top_duracao.columns = ['Tipo de Parada', 'Duração Total']
            
            # Adiciona coluna formatada para exibição
            top_duracao['Duração Formatada'] = top_duracao['Duração Total'].apply(formatar_duracao)
            top_duracao['Duração (horas)'] = top_duracao['Duração Total'].apply(lambda x: round(x.total_seconds() / 3600, 2))
            
            # Seleciona apenas as colunas para exibição
            top_duracao_display = top_duracao[['Tipo de Parada', 'Duração Formatada', 'Duração (horas)']]
            top_duracao_display.columns = ['Tipo de Parada', 'Duração (HH:MM:SS)', 'Duração (horas)']
            
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.dataframe(
                top_duracao_display,
                column_config={
                    "Tipo de Parada": st.column_config.TextColumn("Tipo de Parada"),
                    "Duração (HH:MM:SS)": st.column_config.TextColumn("Duração (HH:MM:SS)"),
                    "Duração (horas)": st.column_config.NumberColumn("Duração (horas)", format="%.2f")
                },
                use_container_width=True,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botão para download da tabela
            st.markdown(
                get_download_link(top_duracao_display, 'paradas_longas.xlsx', '📥 Baixar tabela de paradas mais longas'),
                unsafe_allow_html=True
            )
        else:
            st.info("Dados insuficientes para gerar a tabela de paradas mais longas.")
    
# --- ANÁLISE ADICIONAL POR PERÍODO ---
# Esta seção só é exibida quando analisamos mais de um mês
if mes == 'Todos' and len(dados_filtrados) > 0:
    st.markdown('<div class="section-title">Análise Temporal</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        Esta seção mostra a evolução das paradas ao longo do tempo, permitindo identificar tendências e sazonalidades.
    </div>
    """, unsafe_allow_html=True)
    
    # Agrega dados por mês
    paradas_por_mes = dados_filtrados.groupby('Ano-Mês')['Duração'].agg(['count', 'sum'])
    paradas_por_mes.columns = ['Número de Paradas', 'Duração Total']
    
    # Converte duração total para horas
    paradas_por_mes['Duração (horas)'] = paradas_por_mes['Duração Total'].apply(lambda x: x.total_seconds() / 3600)
    
    if len(paradas_por_mes) > 1:  # Só plota se houver mais de um mês
        with st.container():
            col7, col8 = st.columns(2)
            
            with col7:
                # Gráfico de linha para número de paradas por mês
                fig_evolucao_paradas = criar_grafico_evolucao_paradas(paradas_por_mes)
                if fig_evolucao_paradas:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(fig_evolucao_paradas, use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col8:
                # Gráfico de linha para duração total de paradas por mês
                fig_evolucao_duracao = criar_grafico_evolucao_duracao(paradas_por_mes)
                if fig_evolucao_duracao:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(fig_evolucao_duracao, use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Tabela de resumo por mês
        st.markdown('<div class="sub-header">Resumo Mensal de Paradas</div>', unsafe_allow_html=True)
        
        # Prepara a tabela para exibição
        tabela_mensal = paradas_por_mes.reset_index()
        tabela_mensal['Duração Média (horas)'] = tabela_mensal['Duração (horas)'] / tabela_mensal['Número de Paradas']
        tabela_mensal = tabela_mensal[['Ano-Mês', 'Número de Paradas', 'Duração (horas)', 'Duração Média (horas)']]
        
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.dataframe(
            tabela_mensal,
            column_config={
                "Ano-Mês": st.column_config.TextColumn("Mês"),
                "Número de Paradas": st.column_config.NumberColumn("Número de Paradas", format="%d"),
                "Duração (horas)": st.column_config.NumberColumn("Duração Total (horas)", format="%.2f"),
                "Duração Média (horas)": st.column_config.NumberColumn("Duração Média (horas)", format="%.2f")
            },
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botão para download da tabela
        st.markdown(
            get_download_link(tabela_mensal, 'resumo_mensal.xlsx', '📥 Baixar resumo mensal'),
            unsafe_allow_html=True
        )
    else:
        st.info("Dados insuficientes para análise temporal (necessário mais de um mês de dados).")
    
    # --- CONCLUSÕES E RECOMENDAÇÕES ---
    st.markdown('<div class="section-title">Conclusões e Recomendações</div>', unsafe_allow_html=True)
    
    # Identifica as áreas mais problemáticas
    if not tempo_area.empty:
        area_mais_problematica = tempo_area.idxmax()
        tempo_area_problematica = formatar_duracao(tempo_area.max())
        percentual_area = (tempo_area.max() / tempo_area.sum()) * 100
        
        # Identifica as causas mais frequentes
        if not frequencia_categorias.empty:
            causa_mais_frequente = frequencia_categorias.idxmax()
            frequencia_causa = frequencia_categorias.max()
            percentual_frequencia = (frequencia_causa / frequencia_categorias.sum()) * 100
            
            # Identifica a causa com maior impacto em tempo
            if not pareto.empty:
                causa_maior_impacto = pareto.idxmax()
                tempo_causa_impacto = formatar_duracao(pareto.max())
                percentual_impacto = (pareto.max() / pareto.sum()) * 100
                
                # Texto adicional para filtro de mês
                texto_periodo = ""
                if mes != 'Todos':
                    texto_periodo = f" no período de **{obter_nome_mes(mes)}**"
                
                # Texto adicional para filtro de máquina
                texto_maquina = ""
                if maquina != "Todas":
                    texto_maquina = f" para a máquina **{maquina}**"
                
                # Exibe conclusões e recomendações em cards
                col_concl, col_recom = st.columns(2)
                
                with col_concl:
                    with st.container():
                        st.markdown('<div class="content-box">', unsafe_allow_html=True)
                        st.markdown("### 📊 Principais Conclusões")
                        st.markdown(f"""
                        - A área **{area_mais_problematica}** é responsável pelo maior tempo de paradas{texto_maquina}{texto_periodo} ({tempo_area_problematica}, representando {percentual_area:.1f}% do tempo total).
                        - A causa mais frequente de paradas é **"{causa_mais_frequente}"** com {frequencia_causa} ocorrências ({percentual_frequencia:.1f}% do total).
                        - A causa com maior impacto em tempo é **"{causa_maior_impacto}"** com duração total de {tempo_causa_impacto} ({percentual_impacto:.1f}% do tempo total de paradas).
                        - A disponibilidade geral{texto_maquina}{texto_periodo} está em **{disponibilidade:.2f}%**, com eficiência operacional de **{eficiencia:.2f}%**.
                        """)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with col_recom:
                    with st.container():
                        st.markdown('<div class="content-box">', unsafe_allow_html=True)
                        st.markdown("### 💡 Recomendações")
                        st.markdown(f"""
                        1. Implementar um plano de ação focado na área **{area_mais_problematica}** para reduzir o tempo de paradas.
                        2. Investigar a causa raiz das paradas do tipo **"{causa_maior_impacto}"** para mitigar seu impacto.
                        3. Desenvolver treinamentos específicos para reduzir a frequência de paradas do tipo **"{causa_mais_frequente}"**.
                        4. Estabelecer metas de disponibilidade e eficiência, com acompanhamento periódico dos indicadores.
                        5. Implementar um programa de manutenção preventiva focado nos componentes críticos identificados na análise.
                        """)
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Dados insuficientes para gerar conclusões completas.")
        else:
            st.info("Dados insuficientes para gerar conclusões completas.")
    else:
        st.info("Dados insuficientes para gerar conclusões.")
    
    # Adiciona uma nota final com instruções para o usuário
    st.markdown("""
    <div class="info-box">
        Esta análise foi gerada automaticamente com base nos dados fornecidos. Para uma análise mais detalhada, 
        considere exportar os dados usando os botões de download disponíveis nas tabelas.
    </div>
    """, unsafe_allow_html=True)

# ----- FUNÇÃO PRINCIPAL DA APLICAÇÃO -----
def main():
    # Título principal
    st.markdown('<div class="main-title">Análise de Eficiência de Máquinas</div>', unsafe_allow_html=True)
    
    # Menu de navegação
    with st.container():
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Dados", "Sobre"],
            icons=["graph-up", "table", "info-circle"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "margin-bottom": "20px"},
                "icon": {"color": "#3498db", "font-size": "16px"},
                "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#3498db"},
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Inicializa a sessão state
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    if selected == "Dashboard":
        # Seção de upload de arquivo
        if st.session_state.df is None:
            st.markdown('<div class="section-title">Upload de Dados</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">
                Este dashboard permite analisar indicadores de eficiência de máquinas com base nos dados de paradas. 
                Comece fazendo o upload do arquivo Excel contendo os registros de paradas.
            </div>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Selecione o arquivo Excel (.xlsx)", type=["xlsx"])
                
                if uploaded_file is not None:
                    try:
                        df_original = pd.read_excel(uploaded_file)
                        st.success(f"✅ Arquivo carregado com sucesso! Foram encontrados {len(df_original)} registros de paradas.")
                        
                        # Exibe uma amostra dos dados
                        with st.expander("Visualizar amostra dos dados", expanded=False):
                            st.dataframe(df_original.head(5), use_container_width=True)
                        
                        # Processa os dados
                        with st.spinner("Processando dados..."):
                            df_processado = processar_dados(df_original)
                        
                        # Verifica se há registros válidos após processamento
                        if len(df_processado) > 0:
                            st.session_state.df = df_processado
                            st.success("✅ Dados processados com sucesso! Clique em 'Analisar' para continuar.")
                            st.rerun()
                        else:
                            st.error("❌ Não foi possível processar os dados. Verifique o formato do arquivo.")
                    except Exception as e:
                        st.error(f"❌ Erro ao carregar o arquivo: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Seção de filtros
            st.markdown('<div class="section-title">Filtros de Análise</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">
                Selecione a máquina e o período desejados para análise. 
                Você pode analisar uma máquina específica ou todas as máquinas juntas.
            </div>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    # Obtém a lista de máquinas disponíveis
                    maquinas_disponiveis = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
                    maquina_selecionada = st.selectbox("Selecione a Máquina:", maquinas_disponiveis)
                
                with col2:
                    # Obtém a lista de meses disponíveis
                    meses_disponiveis = ["Todos"] + sorted(st.session_state.df['Ano-Mês'].unique().tolist())
                    mes_selecionado = st.selectbox("Selecione o Mês:", meses_disponiveis)
                
                with col3:
                    st.write("")
                    st.write("")
                    if st.button("📊 Analisar", use_container_width=True):
                        # Realiza a análise com os filtros selecionados
                        analisar_dados(st.session_state.df, maquina_selecionada, mes_selecionado)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Botão para limpar os dados e começar novamente
            if st.button("🔄 Carregar Novos Dados", use_container_width=True):
                st.session_state.df = None
                st.rerun()
            
            # Realiza a análise com os filtros padrão na primeira carga
            if 'first_load' not in st.session_state:
                st.session_state.first_load = True
                analisar_dados(st.session_state.df, "Todas", "Todos")
    
    elif selected == "Dados":
        if st.session_state.df is not None:
            st.markdown('<div class="section-title">Visualização dos Dados</div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                # Opções de filtro para visualização
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filtro de máquina
                    maquinas_para_filtro = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
                    maquina_filtro = st.selectbox("Filtrar por Máquina:", maquinas_para_filtro)
                
                with col2:
                    # Filtro de mês
                    meses_para_filtro = ["Todos"] + sorted(st.session_state.df['Ano-Mês'].unique().tolist())
                    mes_filtro = st.selectbox("Filtrar por Mês:", meses_para_filtro)
                
                # Aplica os filtros
                dados_filtrados = st.session_state.df.copy()
                
                if maquina_filtro != "Todas":
                    dados_filtrados = dados_filtrados[dados_filtrados['Máquina'] == maquina_filtro]
                
                if mes_filtro != "Todos":
                    dados_filtrados = dados_filtrados[dados_filtrados['Ano-Mês'] == mes_filtro]
                
                # Exibe os dados filtrados
                st.markdown(f"**Mostrando {len(dados_filtrados)} registros**")
                st.dataframe(
                    dados_filtrados,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                # Botão para download dos dados
                st.markdown(
                    get_download_link(dados_filtrados, 'dados_filtrados.xlsx', '📥 Baixar dados filtrados'),
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Estatísticas básicas
            st.markdown('<div class="section-title">Estatísticas Básicas</div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                # Resumo por máquina
                resumo_maquina = dados_filtrados.groupby('Máquina').agg({
                    'Duração': ['count', 'sum', 'mean']
                })
                resumo_maquina.columns = ['Número de Paradas', 'Duração Total', 'Duração Média']
                
                # Converte para horas
                resumo_maquina['Duração Total (horas)'] = resumo_maquina['Duração Total'].apply(lambda x: x.total_seconds() / 3600)
                resumo_maquina['Duração Média (horas)'] = resumo_maquina['Duração Média'].apply(lambda x: x.total_seconds() / 3600)
                
                st.dataframe(
                                        resumo_maquina[['Número de Paradas', 'Duração Total (horas)', 'Duração Média (horas)']],
                    column_config={
                        "Número de Paradas": st.column_config.NumberColumn("Número de Paradas", format="%d"),
                        "Duração Total (horas)": st.column_config.NumberColumn("Duração Total (horas)", format="%.2f"),
                        "Duração Média (horas)": st.column_config.NumberColumn("Duração Média (horas)", format="%.2f")
                    },
                    use_container_width=True
                )
                
                # Gráfico de resumo por máquina
                if len(resumo_maquina) > 1:  # Só cria o gráfico se houver mais de uma máquina
                    fig_resumo = px.bar(
                        resumo_maquina.reset_index(),
                        x='Máquina',
                        y='Duração Total (horas)',
                        color='Máquina',
                        title="Duração Total de Paradas por Máquina",
                        labels={'Duração Total (horas)': 'Duração Total (horas)', 'Máquina': 'Máquina'},
                        text='Duração Total (horas)'
                    )
                    
                    fig_resumo.update_traces(
                        texttemplate='%{text:.1f}h', 
                        textposition='outside'
                    )
                    
                    fig_resumo.update_layout(
                        xaxis_tickangle=0,
                        autosize=True,
                        margin=dict(l=50, r=50, t=80, b=50),
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_resumo, use_container_width=True)
                
                # Botão para download do resumo
                st.markdown(
                    get_download_link(resumo_maquina.reset_index(), 'resumo_maquinas.xlsx', '📥 Baixar resumo por máquina'),
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Distribuição de paradas por dia da semana
            st.markdown('<div class="section-title">Análises Adicionais</div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                
                tab1, tab2 = st.tabs(["📅 Distribuição por Dia da Semana", "🕒 Distribuição por Hora do Dia"])
                
                with tab1:
                    # Adiciona coluna de dia da semana
                    dados_filtrados['Dia da Semana'] = dados_filtrados['Inicio'].dt.day_name()
                    
                    # Ordem dos dias da semana
                    ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    nomes_dias_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                    
                    # Mapeamento para nomes em português
                    mapeamento_dias = dict(zip(ordem_dias, nomes_dias_pt))
                    dados_filtrados['Dia da Semana PT'] = dados_filtrados['Dia da Semana'].map(mapeamento_dias)
                    
                    # Agrupa por dia da semana
                    paradas_por_dia = dados_filtrados.groupby('Dia da Semana PT').agg({
                        'Duração': ['count', 'sum']
                    })
                    paradas_por_dia.columns = ['Número de Paradas', 'Duração Total']
                    
                    # Converte para horas
                    paradas_por_dia['Duração (horas)'] = paradas_por_dia['Duração Total'].apply(lambda x: x.total_seconds() / 3600)
                    
                    # Reordena o índice de acordo com os dias da semana
                    if not paradas_por_dia.empty:
                        paradas_por_dia = paradas_por_dia.reindex(nomes_dias_pt)
                        
                        # Cria o gráfico
                        fig_dias = px.bar(
                            paradas_por_dia.reset_index(),
                            x='Dia da Semana PT',
                            y='Número de Paradas',
                            title="Distribuição de Paradas por Dia da Semana",
                            labels={'Número de Paradas': 'Número de Paradas', 'Dia da Semana PT': 'Dia da Semana'},
                            text='Número de Paradas',
                            color='Dia da Semana PT',
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        
                        fig_dias.update_traces(
                            texttemplate='%{text}', 
                            textposition='outside'
                        )
                        
                        fig_dias.update_layout(
                            xaxis_tickangle=0,
                            autosize=True,
                            margin=dict(l=50, r=50, t=80, b=50),
                            plot_bgcolor='rgba(0,0,0,0)',
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_dias, use_container_width=True)
                        
                        # Exibe a tabela
                        st.dataframe(
                            paradas_por_dia[['Número de Paradas', 'Duração (horas)']],
                            column_config={
                                "Número de Paradas": st.column_config.NumberColumn("Número de Paradas", format="%d"),
                                "Duração (horas)": st.column_config.NumberColumn("Duração (horas)", format="%.2f")
                            },
                            use_container_width=True
                        )
                    else:
                        st.info("Dados insuficientes para análise por dia da semana.")
                
                with tab2:
                    # Adiciona coluna de hora do dia
                    dados_filtrados['Hora do Dia'] = dados_filtrados['Inicio'].dt.hour
                    
                    # Agrupa por hora do dia
                    paradas_por_hora = dados_filtrados.groupby('Hora do Dia').agg({
                        'Duração': ['count', 'sum']
                    })
                    paradas_por_hora.columns = ['Número de Paradas', 'Duração Total']
                    
                    # Converte para horas
                    paradas_por_hora['Duração (horas)'] = paradas_por_hora['Duração Total'].apply(lambda x: x.total_seconds() / 3600)
                    
                    # Cria o gráfico
                    if not paradas_por_hora.empty:
                        fig_horas = px.line(
                            paradas_por_hora.reset_index(),
                            x='Hora do Dia',
                            y='Número de Paradas',
                            title="Distribuição de Paradas por Hora do Dia",
                            labels={'Número de Paradas': 'Número de Paradas', 'Hora do Dia': 'Hora do Dia'},
                            markers=True
                        )
                        
                        # Adiciona área sob a linha
                        fig_horas.add_trace(
                            go.Scatter(
                                x=paradas_por_hora.reset_index()['Hora do Dia'],
                                y=paradas_por_hora['Número de Paradas'],
                                fill='tozeroy',
                                fillcolor='rgba(52, 152, 219, 0.2)',
                                line=dict(color='rgba(52, 152, 219, 0)'),
                                showlegend=False
                            )
                        )
                        
                        fig_horas.update_layout(
                            xaxis=dict(
                                tickmode='array',
                                tickvals=list(range(0, 24)),
                                ticktext=[f"{h}:00" for h in range(0, 24)]
                            ),
                            autosize=True,
                            margin=dict(l=50, r=50, t=80, b=50),
                            plot_bgcolor='rgba(0,0,0,0)',
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_horas, use_container_width=True)
                        
                        # Exibe a tabela
                        st.dataframe(
                            paradas_por_hora[['Número de Paradas', 'Duração (horas)']],
                            column_config={
                                "Número de Paradas": st.column_config.NumberColumn("Número de Paradas", format="%d"),
                                "Duração (horas)": st.column_config.NumberColumn("Duração (horas)", format="%.2f")
                            },
                            use_container_width=True
                        )
                    else:
                        st.info("Dados insuficientes para análise por hora do dia.")
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Nenhum dado foi carregado. Por favor, vá para a página 'Dashboard' e faça o upload de um arquivo Excel.")
    
    elif selected == "Sobre":
        st.markdown('<div class="section-title">Sobre a Aplicação</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image("https://img.icons8.com/fluency/240/factory.png", width=150)
            
            with col2:
                st.markdown("""
                # Análise de Eficiência de Máquinas
                
                Esta aplicação foi desenvolvida para analisar dados de paradas de máquinas e calcular indicadores de eficiência, 
                fornecendo insights valiosos para melhorar a produtividade e reduzir o tempo de inatividade.
                """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Funcionalidades
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## ✨ Funcionalidades")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📊 Análise de Dados
                - Visualização de indicadores de disponibilidade e eficiência
                - Identificação das principais causas de paradas
                - Análise da distribuição de paradas por área responsável
                - Acompanhamento da evolução das paradas ao longo do tempo
                """)
            
            with col2:
                st.markdown("""
                ### 🔍 Recursos Adicionais
                - Filtragem por máquina e período
                - Exportação de dados para análise detalhada
                - Visualizações interativas e responsivas
                - Recomendações automáticas baseadas nos dados
                """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Como usar
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 🚀 Como Usar")
            
            st.markdown("""
            1. **Upload de Dados**: Na página "Dashboard", faça o upload de um arquivo Excel contendo os registros de paradas.
            2. **Filtros**: Selecione a máquina e o período desejados para análise.
            3. **Análise**: Visualize os gráficos, tabelas e conclusões geradas automaticamente.
            4. **Exportação**: Use os botões de download para exportar tabelas e dados para análise detalhada.
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Formato dos dados
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 📋 Formato dos Dados")
            
            st.markdown("""
            O arquivo Excel deve conter as seguintes colunas:
            
            - **Máquina**: Identificador da máquina (será convertido conforme mapeamento)
            - **Inicio**: Data e hora de início da parada
            - **Fim**: Data e hora de fim da parada
            - **Duração**: Tempo de duração da parada (HH:MM:SS)
            - **Parada**: Descrição do tipo de parada
            - **Área Responsável**: Área responsável pela parada
            """)
            
            # Exemplo de dados
            st.markdown("### Exemplo de Dados")
            
            exemplo_dados = pd.DataFrame({
                'Máquina': [78, 79, 80, 89, 91],
                'Inicio': pd.date_range(start='2023-01-01', periods=5, freq='D'),
                'Fim': pd.date_range(start='2023-01-01 02:00:00', periods=5, freq='D'),
                'Duração': ['02:00:00', '02:00:00', '02:00:00', '02:00:00', '02:00:00'],
                'Parada': ['Manutenção', 'Erro de Configuração', 'Falta de Insumos', 'Falha Elétrica', 'Troca de Produto'],
                'Área Responsável': ['Manutenção', 'Operação', 'Logística', 'Manutenção', 'Produção']
            })
            
            st.dataframe(exemplo_dados, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Tecnologias utilizadas
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("## 🛠️ Tecnologias Utilizadas")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                ### Frontend
                - **Streamlit**: Framework para criação de aplicações web
                - **Plotly**: Biblioteca para criação de gráficos interativos
                - **HTML/CSS**: Estilização e formatação da interface
                """)
            
            with col2:
                st.markdown("""
                ### Análise de Dados
                - **Pandas**: Manipulação e análise de dados
                - **NumPy**: Computação numérica
                - **Matplotlib/Seaborn**: Visualização de dados
                """)
            
            with col3:
                st.markdown("""
                ### Infraestrutura
                - **Streamlit Cloud**: Hospedagem da aplicação
                - **GitHub**: Controle de versão
                - **Python**: Linguagem de programação
                """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Requisitos do sistema
        with st.expander("📦 Requisitos do Sistema"):
            st.code("""
            # requirements.txt
            streamlit>=1.22.0
            pandas>=2.0.1
            numpy>=1.26.0
            matplotlib>=3.7.1
            seaborn>=0.12.2
            plotly>=5.14.1
            openpyxl>=3.1.2
            xlsxwriter>=3.1.0
            streamlit-option-menu>=0.3.2
            """)
    
    # Rodapé
    st.markdown("""
    <div class="footer">
        <p>© 2023-2025 Análise de Eficiência de Máquinas | Desenvolvido com ❤️ usando Streamlit</p>
        <p><small>Versão 2.0.0 | Última atualização: Maio 2025</small></p>
    </div>
    """, unsafe_allow_html=True)

# Executa a aplicação
if __name__ == "__main__":
    main()
