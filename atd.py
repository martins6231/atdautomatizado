# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64
from streamlit_option_menu import option_menu

# Configuração da página
st.set_page_config(
    page_title="Análise de Eficiência de Máquinas",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #3498db;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    .metric-container {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
    }
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .info-box {
        background-color: #e8f4f8;
        border-left: 5px solid #3498db;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .stPlotlyChart {
        margin-bottom: 2rem;
    }
    .table-container {
        margin-top: 1rem;
        margin-bottom: 2rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
        color: #7f8c8d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Funções auxiliares
@st.cache_data
def formatar_duracao(duracao):
    """
    Formata uma duração (timedelta) para exibição amigável.
    
    Parâmetros:
    duracao (Timedelta): Duração a ser formatada
    
    Retorna:
    str: Duração formatada como "HH:MM:SS"
    """
    if pd.isna(duracao):
        return "00:00:00"
    
    total_segundos = int(duracao.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

@st.cache_data
def obter_nome_mes(mes_ano):
    """
    Converte o formato 'YYYY-MM' para um nome de mês legível.
    
    Parâmetros:
    mes_ano (str): String no formato 'YYYY-MM'
    
    Retorna:
    str: Nome do mês e ano (ex: 'Janeiro 2023')
    """
    if mes_ano == 'Todos':
        return 'Todos os Meses'
    
    try:
        data = datetime.strptime(mes_ano, '%Y-%m')
        # Ajuste para nomes de meses em português
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
    """
    Processa e limpa os dados do DataFrame.
    
    Parâmetros:
    df (DataFrame): DataFrame original
    
    Retorna:
    DataFrame: DataFrame processado
    """
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

# Funções para cálculo dos indicadores
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

# Funções para criação de gráficos com Plotly
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
        color_discrete_sequence=['#3498db']
    )
    
    # Adiciona valores acima das barras
    for i, v in enumerate(pareto_horas):
        fig.add_annotation(
            x=pareto_horas.index[i],
            y=v,
            text=f"{v:.1f}h",
            showarrow=False,
            yshift=10
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Duração Total (horas)",
        xaxis_title="Causa de Parada"
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
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2))
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
        )
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
    
    # Adiciona valores acima dos pontos
    for i, v in enumerate(ocorrencias):
        fig.add_annotation(
            x=ocorrencias.index[i],
            y=v,
            text=str(v),
            showarrow=False,
            yshift=10
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Número de Paradas",
        xaxis_title="Mês"
    )
    
    return fig

@st.cache_data
def criar_grafico_tempo_area(tempo_area):
    """Cria um gráfico de barras horizontais para tempo por área com Plotly."""
    if tempo_area.empty:
        return None
    
    # Converte durações para horas
    tempo_area_horas = tempo_area.apply(lambda x: x.total_seconds() / 3600)
    
    fig = px.bar(
        y=tempo_area_horas.index,
        x=tempo_area_horas.values,
        orientation='h',
        labels={'y': 'Área Responsável', 'x': 'Duração Total (horas)'},
        title="Tempo Total de Paradas por Área",
        color_discrete_sequence=['#e74c3c']
    )
    
    # Adiciona valores à direita das barras
    for i, v in enumerate(tempo_area_horas):
        fig.add_annotation(
            y=tempo_area_horas.index[i],
            x=v,
            text=f"{v:.1f}h",
            showarrow=False,
            xshift=10
        )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Duração Total (horas)",
        yaxis_title="Área Responsável"
    )
    
    return fig

@st.cache_data
def criar_grafico_paradas_criticas(top_criticas):
    """Cria um gráfico de barras horizontais para paradas críticas com Plotly."""
    if top_criticas.empty:
        return None
    
    # Converte durações para horas
    top_criticas_horas = top_criticas.apply(lambda x: x.total_seconds() / 3600)
    
    fig = px.bar(
        y=top_criticas_horas.index,
        x=top_criticas_horas.values,
        orientation='h',
        labels={'y': 'Tipo de Parada', 'x': 'Duração Total (horas)'},
        title="Top 10 Paradas Críticas (>1h)",
        color_discrete_sequence=['#9b59b6']
    )
    
    # Adiciona valores à direita das barras
    for i, v in enumerate(top_criticas_horas):
        fig.add_annotation(
            y=top_criticas_horas.index[i],
            x=v,
            text=f"{v:.1f}h",
            showarrow=False,
            xshift=10
        )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Duração Total (horas)",
        yaxis_title="Tipo de Parada"
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
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2))
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
        )
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
    
    # Adiciona valores acima dos pontos
    for i, v in enumerate(paradas_por_mes['Número de Paradas']):
        fig.add_annotation(
            x=paradas_por_mes.index[i],
            y=v,
            text=str(v),
            showarrow=False,
            yshift=10
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Número de Paradas",
        xaxis_title="Mês"
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
    
    # Adiciona valores acima dos pontos
    for i, v in enumerate(paradas_por_mes['Duração (horas)']):
        fig.add_annotation(
            x=paradas_por_mes.index[i],
            y=v,
            text=f"{v:.1f}h",
            showarrow=False,
            yshift=10
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Duração Total (horas)",
        xaxis_title="Mês"
    )
    
    return fig

# Função para gerar link de download
def get_download_link(df, filename, text):
    """Gera um link para download de um DataFrame como arquivo Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Dados', index=False)
    
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Função principal para análise de dados
def analisar_dados(df, maquina=None, mes=None):
    """
    Realiza a análise dos dados com base na máquina e mês selecionados.
    
    Parâmetros:
    df (DataFrame): DataFrame com os dados
    maquina (str): Nome da máquina a ser analisada, ou None para todas
    mes (str): Mês a ser analisado no formato 'YYYY-MM', ou 'Todos' para todos
    """
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
    
    st.info(f"Analisando dados para {filtro_maquina}, {filtro_mes} ({len(dados_filtrados)} registros)")
    
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
    
    # --- Exibição dos indicadores principais ---
    st.markdown('<div class="sub-header">Indicadores Principais</div>', unsafe_allow_html=True)
    
    # Layout para exibir os indicadores principais em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Disponibilidade</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{disponibilidade:.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Eficiência Operacional</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{eficiencia:.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Tempo Médio de Paradas</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{formatar_duracao(tmp)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Paradas Críticas (>1h)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{percentual_criticas:.2f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Visualização de gráficos ---
    st.markdown('<div class="sub-header">Análise Gráfica</div>', unsafe_allow_html=True)
    
    # Layout para os gráficos em grid
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico 1: Pareto de Causas de Paradas
        fig_pareto = criar_grafico_pareto(pareto)
        if fig_pareto:
            st.plotly_chart(fig_pareto, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de Pareto.")
    
    with col2:
        # Gráfico 2: Índice de Paradas por Área Responsável
        fig_areas = criar_grafico_pizza_areas(indice_paradas)
        if fig_areas:
            st.plotly_chart(fig_areas, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de áreas responsáveis.")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Gráfico 3: Taxa de Ocorrência de Paradas por Mês
        fig_ocorrencias = criar_grafico_ocorrencias(ocorrencias)
        if fig_ocorrencias and len(ocorrencias) > 1:
            st.plotly_chart(fig_ocorrencias, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de ocorrências mensais (necessário mais de um mês).")
    
    with col4:
        # Gráfico 4: Tempo Total de Paradas por Área
        fig_tempo_area = criar_grafico_tempo_area(tempo_area)
        if fig_tempo_area:
            st.plotly_chart(fig_tempo_area, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de tempo por área.")
    
    # Análise de Paradas Críticas
    if len(paradas_criticas) > 0:
        st.markdown('<div class="sub-header">Análise de Paradas Críticas (>1h)</div>', unsafe_allow_html=True)
        st.info(f"Foram identificadas **{len(paradas_criticas)}** paradas críticas (duração > 1 hora), representando **{percentual_criticas:.2f}%** do total de paradas.")
        
        col5, col6 = st.columns(2)
        
        with col5:
                        # Gráfico 5: Top 10 Paradas Críticas
            top_criticas = paradas_criticas.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
            fig_criticas = criar_grafico_paradas_criticas(top_criticas)
            if fig_criticas:
                st.plotly_chart(fig_criticas, use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar o gráfico de paradas críticas.")
        
        with col6:
            # Gráfico 6: Distribuição de Paradas Críticas por Área
            fig_areas_criticas = criar_grafico_pizza_areas_criticas(paradas_criticas)
            if fig_areas_criticas:
                st.plotly_chart(fig_areas_criticas, use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar o gráfico de distribuição de paradas críticas.")
    
    # --- Tabelas de resumo ---
    st.markdown('<div class="sub-header">Tabelas de Resumo</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Paradas Mais Frequentes", "Paradas Mais Longas"])
    
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
                get_download_link(top_frequencia, 'paradas_frequentes.xlsx', 'Baixar tabela de paradas frequentes'),
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
                get_download_link(top_duracao_display, 'paradas_longas.xlsx', 'Baixar tabela de paradas mais longas'),
                unsafe_allow_html=True
            )
        else:
            st.info("Dados insuficientes para gerar a tabela de paradas mais longas.")
    
    # --- Análise adicional por período ---
    # Esta seção só é exibida quando analisamos mais de um mês
    if mes == 'Todos' and len(dados_filtrados) > 0:
        st.markdown('<div class="sub-header">Análise Temporal</div>', unsafe_allow_html=True)
        st.info("Esta seção mostra a evolução das paradas ao longo do tempo, permitindo identificar tendências e sazonalidades.")
        
        # Agrega dados por mês
        paradas_por_mes = dados_filtrados.groupby('Ano-Mês')['Duração'].agg(['count', 'sum'])
        paradas_por_mes.columns = ['Número de Paradas', 'Duração Total']
        
        # Converte duração total para horas
        paradas_por_mes['Duração (horas)'] = paradas_por_mes['Duração Total'].apply(lambda x: x.total_seconds() / 3600)
        
        if len(paradas_por_mes) > 1:  # Só plota se houver mais de um mês
            col7, col8 = st.columns(2)
            
            with col7:
                # Gráfico de linha para número de paradas por mês
                fig_evolucao_paradas = criar_grafico_evolucao_paradas(paradas_por_mes)
                if fig_evolucao_paradas:
                    st.plotly_chart(fig_evolucao_paradas, use_container_width=True)
            
            with col8:
                # Gráfico de linha para duração total de paradas por mês
                fig_evolucao_duracao = criar_grafico_evolucao_duracao(paradas_por_mes)
                if fig_evolucao_duracao:
                    st.plotly_chart(fig_evolucao_duracao, use_container_width=True)
            
            # Tabela de resumo por mês
            st.subheader("Resumo Mensal de Paradas")
            
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
                get_download_link(tabela_mensal, 'resumo_mensal.xlsx', 'Baixar resumo mensal'),
                unsafe_allow_html=True
            )
        else:
            st.info("Dados insuficientes para análise temporal (necessário mais de um mês de dados).")
    
    # --- Conclusões e Recomendações ---
    st.markdown('<div class="sub-header">Conclusões e Recomendações</div>', unsafe_allow_html=True)
    
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
                
                # Exibe conclusões
                with st.expander("Ver Conclusões", expanded=True):
                    st.markdown(f"""
                    ### Principais Conclusões:
                    
                    - A área **{area_mais_problematica}** é responsável pelo maior tempo de paradas{texto_maquina}{texto_periodo} ({tempo_area_problematica}, representando {percentual_area:.1f}% do tempo total).
                    - A causa mais frequente de paradas é **"{causa_mais_frequente}"** com {frequencia_causa} ocorrências ({percentual_frequencia:.1f}% do total).
                    - A causa com maior impacto em tempo é **"{causa_maior_impacto}"** com duração total de {tempo_causa_impacto} ({percentual_impacto:.1f}% do tempo total de paradas).
                    - A disponibilidade geral{texto_maquina}{texto_periodo} está em **{disponibilidade:.2f}%**, com eficiência operacional de **{eficiencia:.2f}%**.
                    """)
                
                # Exibe recomendações
                with st.expander("Ver Recomendações", expanded=True):
                    st.markdown(f"""
                    ### Recomendações:
                    
                    1. Implementar um plano de ação focado na área **{area_mais_problematica}** para reduzir o tempo de paradas.
                    2. Investigar a causa raiz das paradas do tipo **"{causa_maior_impacto}"** para mitigar seu impacto.
                    3. Desenvolver treinamentos específicos para reduzir a frequência de paradas do tipo **"{causa_mais_frequente}"**.
                    4. Estabelecer metas de disponibilidade e eficiência, com acompanhamento periódico dos indicadores.
                    5. Implementar um programa de manutenção preventiva focado nos componentes críticos identificados na análise.
                    """)
            else:
                st.info("Dados insuficientes para gerar conclusões completas.")
        else:
            st.info("Dados insuficientes para gerar conclusões completas.")
    else:
        st.info("Dados insuficientes para gerar conclusões.")
    
    # Adiciona uma nota final com instruções para o usuário
    st.info("Esta análise foi gerada automaticamente com base nos dados fornecidos. Para uma análise mais detalhada, considere exportar os dados usando os botões de download disponíveis nas tabelas.")

# Função principal da aplicação
def main():
    # Título principal
    st.markdown('<div class="main-header">Análise de Eficiência de Máquinas</div>', unsafe_allow_html=True)
    
    # Menu de navegação
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
    
    # Inicializa a sessão state
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    if selected == "Dashboard":
        # Seção de upload de arquivo
        if st.session_state.df is None:
            st.markdown('<div class="sub-header">Upload de Dados</div>', unsafe_allow_html=True)
            st.info("Este dashboard permite analisar indicadores de eficiência de máquinas com base nos dados de paradas. Comece fazendo o upload do arquivo Excel contendo os registros de paradas.")
            
            uploaded_file = st.file_uploader("Selecione o arquivo Excel (.xlsx)", type=["xlsx"])
            
            if uploaded_file is not None:
                try:
                    df_original = pd.read_excel(uploaded_file)
                    st.success(f"Arquivo carregado com sucesso! Foram encontrados {len(df_original)} registros de paradas.")
                    
                    # Processa os dados
                    df_processado = processar_dados(df_original)
                    
                    # Verifica se há registros válidos após processamento
                    if len(df_processado) > 0:
                        st.session_state.df = df_processado
                        st.experimental_rerun()
                    else:
                        st.error("Não foi possível processar os dados. Verifique o formato do arquivo.")
                except Exception as e:
                    st.error(f"Erro ao carregar o arquivo: {str(e)}")
        else:
            # Seção de filtros
            st.markdown('<div class="sub-header">Filtros de Análise</div>', unsafe_allow_html=True)
            st.info("Selecione a máquina e o período desejados para análise. Você pode analisar uma máquina específica ou todas as máquinas juntas.")
            
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
                if st.button("Analisar", use_container_width=True):
                    # Realiza a análise com os filtros selecionados
                    analisar_dados(st.session_state.df, maquina_selecionada, mes_selecionado)
            
            # Botão para limpar os dados e começar novamente
            if st.button("Carregar Novos Dados", use_container_width=True):
                st.session_state.df = None
                st.experimental_rerun()
    
    elif selected == "Dados":
        if st.session_state.df is not None:
            st.markdown('<div class="sub-header">Visualização dos Dados</div>', unsafe_allow_html=True)
            
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
            st.dataframe(
                dados_filtrados,
                use_container_width=True,
                hide_index=True
            )
            
            # Estatísticas básicas
            st.markdown('<div class="sub-header">Estatísticas Básicas</div>', unsafe_allow_html=True)
            
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
            
            # Botão para download dos dados
            st.markdown(
                get_download_link(dados_filtrados, 'dados_filtrados.xlsx', 'Baixar dados filtrados'),
                unsafe_allow_html=True
            )
        else:
            st.info("Nenhum dado foi carregado. Por favor, vá para a página 'Dashboard' e faça o upload de um arquivo Excel.")
    
    elif selected == "Sobre":
        st.markdown('<div class="sub-header">Sobre a Aplicação</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### Análise de Eficiência de Máquinas
        
        Esta aplicação foi desenvolvida para analisar dados de paradas de máquinas e calcular indicadores de eficiência. Ela permite:
        
        - Visualizar indicadores de disponibilidade e eficiência
        - Identificar as principais causas de paradas
        - Analisar a distribuição de paradas por área responsável
        - Acompanhar a evolução das paradas ao longo do tempo
        - Gerar relatórios e exportar dados para análise detalhada
        
        ### Como Usar
        
        1. **Upload de Dados**: Na página "Dashboard", faça o upload de um arquivo Excel contendo os registros de paradas.
        2. **Filtros**: Selecione a máquina e o período desejados para análise.
        3. **Análise**: Visualize os gráficos, tabelas e conclusões geradas automaticamente.
        4. **Exportação**: Use os botões de download para exportar tabelas e dados para análise detalhada.
        
        ### Formato dos Dados
        
        O arquivo Excel deve conter as seguintes colunas:
        
        - **Máquina**: Identificador da máquina (será convertido conforme mapeamento)
        - **Inicio**: Data e hora de início da parada
        - **Fim**: Data e hora de fim da parada
        - **Duração**: Tempo de duração da parada (HH:MM:SS)
        - **Parada**: Descrição do tipo de parada
        - **Área Responsável**: Área responsável pela parada
        
        ### Tecnologias Utilizadas
        
        - **Streamlit**: Framework para criação de aplicações web
        - **Pandas**: Biblioteca para manipulação e análise de dados
        - **Plotly**: Biblioteca para criação de gráficos interativos
        - **Matplotlib/Seaborn**: Bibliotecas para visualização de dados
        
        ### Hospedagem
        
        Esta aplicação pode ser hospedada no Streamlit Cloud, seguindo estes passos:
        
        1. Crie uma conta no [Streamlit Cloud](https://streamlit.io/cloud)
        2. Faça upload do código para um repositório GitHub
        3. Conecte o repositório ao Streamlit Cloud
        4. Configure as dependências no arquivo `requirements.txt`
        
        ### Manutenção e Atualização
        
        Para manter a aplicação atualizada:
        
        1. Atualize regularmente as bibliotecas no arquivo `requirements.txt`
        2. Monitore o uso e desempenho da aplicação
        3. Implemente novos recursos conforme necessário
        4. Realize backups periódicos dos dados importantes
        """)
        
        st.markdown('<div class="sub-header">Requisitos do Sistema</div>', unsafe_allow_html=True)
        
        st.code("""
        # requirements.txt
        streamlit==1.22.0
        pandas==2.0.1
        numpy==1.24.3
        matplotlib==3.7.1
        seaborn==0.12.2
        plotly==5.14.1
        openpyxl==3.1.2
        xlsxwriter==3.1.0
        streamlit-option-menu==0.3.2
        """)
    
    # Rodapé
    st.markdown('<div class="footer">Análise de Eficiência de Máquinas © 2023</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
