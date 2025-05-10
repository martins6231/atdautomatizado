# streamlit_britvic_moderno.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from prophet import Prophet
import calendar
from datetime import datetime

st.set_page_config(
    page_title="Acompanhamento Britvic",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------ CSS Personalizado UI/UX ------
st.markdown("""
    <style>
    body {background-color: #FAFCFE;}
    .css-1vq4p4l {padding-top: 0rem;}
    .css-10trblm {padding: 0!important;}
    .reportview-container .main { background: #f9f9f9; }
    .sidebar-content { background: #16233A !important; color: #fff; }
    .css-184tjsw, .css-6qob1r { color: #1A233A !important; }
    .metric-label, .stCaption {font-size: 1rem!important;}
    .stMetricValue { font-weight:bold!important; font-size: 1.8rem!important;}
    .stDownloadButton button {background: #1876D1; color: #fff;}
    .stDownloadButton button:hover {background: #13518C;}
    .stButton button {background: #27AE60; color: #fff;}
    .stButton button:hover {background: #128141;}
    .stExpanderHeader {font-weight:600;}
    .egzxvld4 {margin-top: 1.2em;}
    </style>
""", unsafe_allow_html=True)

# ------ Barra de Navegação Customizada ------
st.markdown("""
<div style="display: flex;justify-content: space-between;align-items:center;padding:12px 0 24px;">
    <div style="display:flex;align-items:center;">
        <img src="https://seeklogo.com/images/B/britvic-logo-28560A1B45-seeklogo.com.png"
            style="height: 46px;margin-right:18px;">
        <span style="font-size:1.6rem;font-weight:700;color:#16233A;letter-spacing:-1px">Acompanhamento de Produção Britvic</span>
    </div>
    <div style="font-size:1.2rem;color:#557; margin-right:18px">
        <b>Powered by Streamlit • Atualizado {}</b>
    </div>
</div>""".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)

# ------ Instrução e Upload ------
st.sidebar.header("⚙️ Configurações", divider="rainbow")
st.markdown("""<div style="max-width:580px;">
Carregue sua planilha <b>.xlsx</b> de produção como referência.<br>
<span style="font-size:0.98em; color:#334; margin-top:6px;display:block">
Colunas obrigatórias: <strong>categoria, data, caixas_produzidas</strong>
</span>
</div>""", unsafe_allow_html=True)

upload = st.sidebar.file_uploader(
    "Selecione o arquivo Excel (.xlsx)...",
    type="xlsx",
    accept_multiple_files=False,
    help="Apenas arquivos .xlsx"
)

# ------ Funções Gerais ------
def nome_mes(numero):
    return calendar.month_abbr[int(numero)]

@st.cache_data
def carregar_dados(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
        return None

def tratar_dados(df):
    erros = []
    df = df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"))
    obrigatorias = ['categoria', 'data', 'caixas_produzidas']
    for col in obrigatorias:
        if col not in df.columns:
            erros.append(f"Coluna obrigatória ausente: {col}")
    try:
        df['data'] = pd.to_datetime(df['data'])
    except Exception:
        erros.append("Erro ao converter coluna 'data'.")
    na_count = df.isna().sum()
    for col, qtd in na_count.items():
        if qtd > 0:
            erros.append(f"Coluna '{col}' com {qtd} valores ausentes.")
    negativos = (df['caixas_produzidas'] < 0).sum()
    if negativos > 0:
        erros.append(f"{negativos} registros negativos em 'caixas_produzidas'.")
    df_clean = df.dropna(subset=['categoria','data','caixas_produzidas']).copy()
    df_clean['caixas_produzidas'] = pd.to_numeric(df_clean['caixas_produzidas'], errors='coerce').fillna(0).astype(int)
    df_clean = df_clean[df_clean['caixas_produzidas'] >= 0]
    df_clean = df_clean.drop_duplicates(subset=['categoria','data'], keep='first')
    return df_clean, erros

def selecionar_categoria(df):
    return sorted(df['categoria'].dropna().unique())

def dataset_ano_mes(df, categoria=None):
    df_filt = df if categoria is None else df[df['categoria'] == categoria]
    df_filt['ano'] = df_filt['data'].dt.year
    df_filt['mes'] = df_filt['data'].dt.month
    return df_filt

def filtrar_periodo(df, categoria, anos_selecionados, meses_selecionados):
    cond = (df['categoria'] == categoria)
    if anos_selecionados:
        cond &= (df['data'].dt.year.isin(anos_selecionados))
    if meses_selecionados:
        cond &= (df['data'].dt.month.isin(meses_selecionados))
    return df[cond].copy()

def gerar_dataset_modelo(df, categoria=None):
    df_cat = df[df['categoria'] == categoria] if categoria else df
    grupo = df_cat.groupby('data')['caixas_produzidas'].sum().reset_index()
    return grupo.sort_values('data')

# ------ Lógica de upload e tratamento inicial ------
if upload:
    df_raw = carregar_dados(upload)
else:
    st.info("⬆️ Faça o upload do arquivo para iniciar a visualização.", icon="ℹ️")
    st.stop()

df, erros = tratar_dados(df_raw)
with st.expander("🔍 Relatório de problemas identificados", expanded=len(erros) > 0):
    if erros:
        for e in erros: st.warning(e)
    else:
        st.success("Nenhum problema crítico encontrado.")

# ------ Seleção de parâmetros na sidebar ------
categorias = selecionar_categoria(df)
categoria_analise = st.sidebar.selectbox("Categoria:", categorias, index=0 if categorias else None)
anos_disp = sorted(df[df['categoria']==categoria_analise]['data'].dt.year.unique())
anos_selecionados = st.sidebar.multiselect(
    "Ano(s):", anos_disp, default=anos_disp,
    help="Escolha um ou múltiplos anos para análise"
)

meses_disp = sorted(df[(df['categoria']==categoria_analise) & (df['data'].dt.year.isin(anos_selecionados))]['data'].dt.month.unique())
meses_nome = [f"{m:02d} - {calendar.month_name[m]}" for m in meses_disp]
map_mes = dict(zip(meses_nome, meses_disp))
meses_selecionados_nome = st.sidebar.multiselect(
    "Mês(es):", meses_nome, default=meses_nome,
    help="Selecione um ou mais meses para análise"
)
meses_selecionados = [map_mes[n] for n in meses_selecionados_nome]

df_filtrado = filtrar_periodo(df, categoria_analise, anos_selecionados, meses_selecionados)
st.subheader(f"📊 Análise: <span style='color:#1876D1'><b>{categoria_analise}</b></span>", unsafe_allow_html=True)

if df_filtrado.empty:
    st.error("Não há dados para esse período e categoria.")
    st.stop()

# ------ KPIs ------
def exibe_kpis(df, categoria):
    df_cat = df[df['categoria'] == categoria]
    if df_cat.empty:
        st.info("Sem dados para a seleção.")
        return
    df_cat['ano'] = df_cat['data'].dt.year
    kpis = df_cat.groupby('ano')['caixas_produzidas'].agg(['sum','mean','std','count']).reset_index()
    colunas = st.columns(len(kpis))
    for i, (_, row) in enumerate(kpis.iterrows()):
        ano = int(row['ano'])
        with colunas[i]:
            st.metric(
                f"Ano {ano}",
                f"{int(row['sum']):,} caixas",
                delta=None
            )
            st.caption(f"Média diária: <b>{row['mean']:.0f}</b> &nbsp;&nbsp;|&nbsp;&nbsp; Registros: <b>{row['count']}</b>", unsafe_allow_html=True)

exibe_kpis(df_filtrado, categoria_analise)
st.markdown("---")

# ------ Visuais e módulos ------
def plot_tendencia(df, categoria):
    grupo = gerar_dataset_modelo(df, categoria)
    if grupo.empty:
        st.info("Sem dados para tendência.")
        return
    fig = px.line(
        grupo, x='data', y='caixas_produzidas',
        title='', markers=True,
        labels={"data": "Data", "caixas_produzidas": "Caixas Produzidas"}
    )
    fig.update_traces(line_color="#004DF1", line_width=2, marker=dict(size=7, color="#250E47"))
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=18, r=12, t=20, b=22),
        legend=dict(orientation='h'),
        height=350,
        xaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_variacao_mensal(df, categoria):
    agrup = dataset_ano_mes(df, categoria)
    mensal = agrup.groupby([agrup['data'].dt.to_period('M')])['caixas_produzidas'].sum().reset_index()
    mensal['mes'] = mensal['data'].dt.strftime('%b/%Y')
    mensal['var_%'] = mensal['caixas_produzidas'].pct_change() * 100
    fig1 = px.bar(
        mensal, x='mes', y='caixas_produzidas', text_auto=True,
        title='',
        labels={"mes": "Mês/Ano", "caixas_produzidas": "Caixas Produzidas"},
        height=280
    )
    fig1.update_traces(marker_color="#27AE60")
    fig1.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=22, b=18))
    fig2 = px.line(
        mensal, x='mes', y='var_%', markers=True,
        title='',
        labels={"mes": "Mês/Ano", "var_%": "Variação (%)"},
        height=250
    )
    fig2.update_traces(line_color="#F39C12", marker=dict(size=7))
    fig2.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=10, b=12))
    st.columns([1,2])[0].markdown("#### 📈 Produção Mensal")
    st.plotly_chart(fig1, use_container_width=True)
    st.columns([1,2])[0].markdown("#### 📉 Variação Percentual")
    st.plotly_chart(fig2, use_container_width=True)

def plot_sazonalidade(df, categoria):
    agrup = dataset_ano_mes(df, categoria)
    if agrup.empty:
        st.info("Sem dados para sazonalidade.")
        return
    fig = px.box(
        agrup, x='mes', y='caixas_produzidas', color=agrup['ano'].astype(str),
        points='all', notched=True,
        title='', height=340,
        labels={'mes':"Mês", "caixas_produzidas":"Produção"},
        hover_data=["ano"]
    )
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1,13)),
            ticktext=[nome_mes(m) for m in range(1,13)]
        ),
        template="plotly_white",
        legend_title="Ano",
        margin=dict(l=14, r=14, t=10, b=16)
    )
    st.markdown("#### 📦 Sazonalidade Mensal")
    st.plotly_chart(fig, use_container_width=True)

def plot_comparativo_ano_mes(df, categoria):
    agrup = dataset_ano_mes(df, categoria)
    tab = agrup.groupby(['ano','mes'])['caixas_produzidas'].sum().reset_index()
    tab['mes_nome'] = tab['mes'].apply(nome_mes)
    tab = tab.sort_values(['mes'])
    fig = go.Figure()
    anos = sorted(tab['ano'].unique())
    for ano in anos:
        dados_ano = tab[tab['ano'] == ano]
        fig.add_trace(go.Bar(
            x=dados_ano['mes_nome'],
            y=dados_ano['caixas_produzidas'],
            name=str(ano),
            text=dados_ano['caixas_produzidas'],
            textposition='auto'
        ))
    fig.update_layout(
        barmode='group',
        title='',
        xaxis_title="Mês", yaxis_title="Caixas Produzidas",
        legend_title="Ano",
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=12, r=12, t=12, b=18),
        height=300
    )
    st.markdown("#### 📅 Comparativo Ano a Ano")
    st.plotly_chart(fig, use_container_width=True)

def plot_comparativo_acumulado(df, categoria):
    agrup = dataset_ano_mes(df, categoria)
    res = agrup.groupby(['ano','mes'])['caixas_produzidas'].sum().reset_index()
    res['acumulado'] = res.groupby('ano')['caixas_produzidas'].cumsum()
    fig = px.line(
        res, x='mes', y='acumulado', color=res['ano'].astype(str),
        markers=True,
        labels={'mes':"Mês", 'acumulado':"Caixas Acumuladas", 'ano':'Ano'},
        title='',
        height=260
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(
        legend_title="Ano",
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1,13)),
            ticktext=[nome_mes(m) for m in range(1,13)]
        ),
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=10, r=10, t=14, b=12)
    )
    st.markdown("#### 🔢 Produção Acumulada")
    st.plotly_chart(fig, use_container_width=True)

def rodar_previsao_prophet(df, categoria, meses_futuro=6):
    dataset = gerar_dataset_modelo(df, categoria)
    if dataset.shape[0] < 2:
        return dataset, pd.DataFrame(), None
    dados = dataset.rename(columns={'data':'ds', 'caixas_produzidas':'y'})
    modelo = Prophet(yearly_seasonality=True, daily_seasonality=False)
    modelo.fit(dados)
    futuro = modelo.make_future_dataframe(periods=meses_futuro*30)
    previsao = modelo.predict(futuro)
    return dados, previsao, modelo

def plot_previsao(dados_hist, previsao, categoria):
    if previsao.empty:
        st.info("Sem previsão disponível.")
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dados_hist['ds'], y=dados_hist['y'],
                             mode='lines+markers', name='Histórico',
                             line=dict(color='#2980B9', width=2),
                             marker=dict(color='#154360')))
    fig.add_trace(go.Scatter(x=previsao['ds'], y=previsao['yhat'],
                             mode='lines', name='Previsão', line=dict(color='#27AE60', width=2)))
    fig.add_trace(go.Scatter(x=previsao['ds'], y=previsao['yhat_upper'],
                             line=dict(dash='dash', color='#AED6F1'), name='Limite Superior', opacity=0.3))
    fig.add_trace(go.Scatter(x=previsao['ds'], y=previsao['yhat_lower'],
                             line=dict(dash='dash', color='#AED6F1'), name='Limite Inferior', opacity=0.3))
    fig.update_layout(
        title='',
        xaxis_title="Data", yaxis_title="Caixas Produzidas",
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=18, r=18, t=10, b=18),
        height=320
    )
    st.markdown("#### 🤖 Previsão de Produção (6 meses)")
    st.plotly_chart(fig, use_container_width=True)

def gerar_insights(df, categoria):
    grupo = gerar_dataset_modelo(df, categoria)
    tendencias = []
    mensal = grupo.copy()
    mensal['mes'] = mensal['data'].dt.to_period('M')
    agg = mensal.groupby('mes')['caixas_produzidas'].sum()
    if len(agg) > 6:
        ultimos = min(3, len(agg))
        if agg[-ultimos:].mean() > agg[:-ultimos].mean():
            tendencias.append("Crescimento recente na produção detectado nos últimos meses.")
        elif agg[-ultimos:].mean() < agg[:-ultimos].mean():
            tendencias.append("Queda recente na produção detectada nos últimos meses.")
    q1 = grupo['caixas_produzidas'].quantile(0.25)
    q3 = grupo['caixas_produzidas'].quantile(0.75)
    outliers = grupo[(grupo['caixas_produzidas'] < q1 - 1.5*(q3-q1)) | (grupo['caixas_produzidas'] > q3 + 1.5*(q3-q1))]
    if not outliers.empty:
        tendencias.append(f"Foram encontrados {outliers.shape[0]} dias atípicos de produção (possíveis outliers).")
    std = grupo['caixas_produzidas'].std()
    mean = grupo['caixas_produzidas'].mean()
    if mean > 0 and std/mean > 0.5:
        tendencias.append("Alta variabilidade diária. Sugerido investigar causas das flutuações.")
    with st.expander("💡 Insights Automáticos", expanded=True):
        for t in tendencias:
            st.info(t)
        if not tendencias:
            st.success("Nenhum padrão preocupante encontrado para esta categoria.")

def exportar_consolidado(df, previsao, categoria):
    if previsao.empty:
        st.warning("Sem previsão para exportar.")
        return
    dados = gerar_dataset_modelo(df, categoria)
    previsao_col = previsao[['ds', 'yhat']].rename(columns={'ds':'data', 'yhat':'previsao_caixas'})
    base_export = dados.merge(previsao_col, left_on='data', right_on='data', how='outer').sort_values("data")
    base_export['categoria'] = categoria
    nome_arq = f'consolidado_{categoria.lower()}.xlsx'
    return base_export, nome_arq

# ------ Dashboards ------
with st.container():
    plot_tendencia(df_filtrado, categoria_analise)
    st.markdown("<br>", unsafe_allow_html=True)
    plot_variacao_mensal(df_filtrado, categoria_analise)
    st.markdown("<br>", unsafe_allow_html=True)
    plot_sazonalidade(df_filtrado, categoria_analise)

with st.container():
    if len(set(df_filtrado['data'].dt.year)) > 1:
        with st.columns(2)[0]:
            plot_comparativo_ano_mes(df_filtrado, categoria_analise)
        with st.columns(2)[1]:
            plot_comparativo_acumulado(df_filtrado, categoria_analise)

dados_hist, previsao, modelo_prophet = rodar_previsao_prophet(df_filtrado, categoria_analise, meses_futuro=6)
plot_previsao(dados_hist, previsao, categoria_analise)
gerar_insights(df_filtrado, categoria_analise)

# ------ Exportação ------
with st.expander("🗂️ Exportação de Consolidado"):
    if st.button("Exportar consolidado com previsão (.xlsx)"):
        base_export, nome_arq = exportar_consolidado(df_filtrado, previsao, categoria_analise)
        buffer = io.BytesIO()
        base_export.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        st.download_button(
            label="Download arquivo Excel",
            data=buffer,
            file_name=nome_arq,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
