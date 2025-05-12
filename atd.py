import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import requests
import tempfile
import zipfile
from prophet import Prophet
import calendar

st.set_page_config(
    page_title="Dashboard de Produção - Britvic",
    layout="wide",
    page_icon="🧃"
)

# ----------- Suporte Bilíngue -----------
LANGS = {
    "pt": "Português (Brasil)",
    "en": "English"
}

st.sidebar.markdown("## 🌐 Idioma | Language")
idioma = st.sidebar.radio("Escolha o idioma / Choose language:", options=list(LANGS.keys()), format_func=lambda x: LANGS[x], key="user_lang")

def t(msg_key, **kwargs):
    TRANSLATE = {
        "pt": {
            "dashboard_title": "Dashboard de Produção - Britvic",
            "main_title": "Dashboard de Produção",
            "subtitle": "Visualização dos dados de produção Britvic",
            "category": "🏷️ Categoria:",
            "year": "📅 Ano(s):",
            "month": "📆 Mês(es):",
            "analysis_for": "Análise para categoria: <b>{cat}</b>",
            "empty_data_for_period": "Não há dados para esse período e categoria.",
            "mandatory_col_missing": "Coluna obrigatória ausente: {col}",
            "error_date_conversion": "Erro ao converter coluna 'data'.",
            "col_with_missing": "Coluna '{col}' com {num} valores ausentes.",
            "negatives": "{num} registros negativos em 'caixas_produzidas'.",
            "no_critical": "Nenhum problema crítico encontrado.",
            "data_issue_report": "Relatório de problemas encontrados",
            "no_data_selection": "Sem dados para a seleção.",
            "no_trend": "Sem dados para tendência.",
            "daily_trend": "Tendência Diária - {cat}",
            "monthly_total": "Produção Mensal Total - {cat}",
            "monthly_var": "Variação Percentual Mensal (%) - {cat}",
            "monthly_seasonal": "Sazonalidade Mensal - {cat}",
            "monthly_comp": "Produção Mensal {cat} - Comparativo por Ano",
            "monthly_accum": "Produção Acumulada Mês a Mês - {cat}",
            "no_forecast": "Sem previsão disponível.",
            "forecast": "Previsão de Produção - {cat}",
            "auto_insights": "Insights Automáticos",
            "no_pattern": "Nenhum padrão preocupante encontrado para esta categoria.",
            "recent_growth": "Crescimento recente na produção detectado nos últimos meses.",
            "recent_fall": "Queda recente na produção detectada nos últimos meses.",
            "outlier_days": "Foram encontrados {num} dias atípicos de produção (possíveis outliers).",
            "high_var": "Alta variabilidade diária. Sugerido investigar causas das flutuações.",
            "export": "Exportação",
            "export_with_fc": "⬇️ Exportar consolidado com previsão (.xlsx)",
            "download_file": "Download arquivo Excel ⬇️",
            "no_export": "Sem previsão para exportar.",
            "add_secrets": "Adicione CLOUD_XLSX_URL ao seu .streamlit/secrets.toml e compartilhe a planilha para 'qualquer pessoa com o link'.",
            "error_download_xls": "Erro ao baixar planilha. Status code: {code}",
            "not_valid_excel": "Arquivo baixado não é um Excel válido. Confirme se o link é público/correto!",
            "excel_open_error": "Erro ao abrir o Excel: {err}",
            "kpi_year": "📦 Ano {ano}",
            "kpi_sum": "{qtd:,} caixas",
            "historico": "Histórico",
            "kpi_daily_avg": "Média diária:<br><b style='color:{accent};font-size:1.15em'>{media:.0f}</b>",
            "kpi_records": "Registros: <b>{count}</b>",
            "data": "Data",
            "category_lbl": "Categoria",
            "produced_boxes": "Caixas Produzidas",
            "month_lbl": "Mês/Ano",
            "variation": "Variação (%)",
            "prod": "Produção",
            "year_lbl": "Ano",
            "accum_boxes": "Caixas Acumuladas",
            "forecast_boxes": "Previsão Caixas",
            "select_date_range": "Selecione o intervalo de datas:",
        },
        "en": {
            "dashboard_title": "Production Dashboard - Britvic",
            "main_title": "Production Dashboard",
            "subtitle": "Britvic production data visualization",
            "category": "🏷️ Category:",
            "year": "📅 Year(s):",
            "month": "📆 Month(s):",
            "analysis_for": "Analysis for category: <b>{cat}</b>",
            "empty_data_for_period": "No data for this period and category.",
            "mandatory_col_missing": "Mandatory column missing: {col}",
            "error_date_conversion": "Error converting 'data' column.",
            "col_with_missing": "Column '{col}' has {num} missing values.",
            "negatives": "{num} negative records in 'caixas_produzidas'.",
            "no_critical": "No critical issues found.",
            "data_issue_report": "Report of Identified Issues",
            "no_data_selection": "No data for selection.",
            "no_trend": "No data for trend.",
            "daily_trend": "Daily Trend - {cat}",
            "monthly_total": "Total Monthly Production - {cat}",
            "monthly_var": "Monthly Change (%) - {cat}",
            "monthly_seasonal": "Monthly Seasonality - {cat}",
            "monthly_comp": "Monthly Production {cat} - Year Comparison",
            "monthly_accum": "Accumulated Production Month by Month - {cat}",
            "no_forecast": "No available forecast.",
            "forecast": "Production Forecast - {cat}",
            "auto_insights": "Automatic Insights",
            "no_pattern": "No concerning patterns found for this category.",
            "recent_growth": "Recent growth in production detected in the last months.",
            "recent_fall": "Recent drop in production detected in the last months.",
            "outlier_days": "{num} atypical production days found (possible outliers).",
            "high_var": "High daily variability. Suggest to investigate fluctuation causes.",
            "export": "Export",
            "export_with_fc": "⬇️ Export with forecast (.xlsx)",
            "download_file": "Download Excel file ⬇️",
            "no_export": "No forecast to export.",
            "add_secrets": "Add CLOUD_XLSX_URL to your .streamlit/secrets.toml and share the sheet to 'anyone with the link'.",
            "error_download_xls": "Error downloading spreadsheet. Status code: {code}",
            "not_valid_excel": "Downloaded file is not a valid Excel. Confirm the link is public/correct!",
            "excel_open_error": "Error opening Excel: {err}",
            "kpi_year": "📦 Year {ano}",
            "kpi_sum": "{qtd:,} boxes",
            "historico": "History",
            "kpi_daily_avg": "Daily avg.:<br><b style='color:{accent};font-size:1.15em'>{media:.0f}</b>",
            "kpi_records": "Records: <b>{count}</b>",
            "data": "Date",
            "category_lbl": "Category",
            "produced_boxes": "Produced Boxes",
            "month_lbl": "Month/Year",
            "variation": "Variation (%)",
            "prod": "Production",
            "year_lbl": "Year",
            "accum_boxes": "Accum. Boxes",
            "forecast_boxes": "Forecasted Boxes",
            "select_date_range": "Select date range:",
        }
    }
    base = TRANSLATE[idioma].get(msg_key, msg_key)
    if kwargs:
        base = base.format(**kwargs)
    return base

# -------------- Layout e Cor padrão -------------
BRITVIC_PRIMARY = "#003057"
BRITVIC_ACCENT = "#27AE60"
BRITVIC_BG = "#F4FFF6"

# ---------- CSS Customizado ----------
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {BRITVIC_BG};
        }}
        .center {{
            text-align: center;
        }}
        .britvic-title {{
            font-size: 2.6rem;
            font-weight: bold;
            color: {BRITVIC_PRIMARY};
            text-align: center;
            margin-bottom: 0.3em;
        }}
        .subtitle {{
            text-align: center;
            color: {BRITVIC_PRIMARY};
            font-size: 1.0rem;
            margin-bottom: 1em;
        }}
    </style>
""", unsafe_allow_html=True)

# ----------- Topo/logomarca ------------
st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: {BRITVIC_BG};
        padding: 10px 0 20px 0;
        margin-bottom: 20px;"
    >
        <img src="https://raw.githubusercontent.com/martins6231/app_atd/main/britvic_logo.png" alt="Britvic Logo" style="width: 150px; margin-bottom: 10px;">
        <h1 style="
            font-size: 2.2rem;
            font-weight: bold;
            color: {BRITVIC_PRIMARY};
            margin: 0;"
        >
            {t("main_title")}
        </h1>
    </div>
""", unsafe_allow_html=True)

# ---------- Funções auxiliares ------------

def nome_mes(numero):
    return calendar.month_abbr[int(numero)] if idioma == "pt" else calendar.month_name[int(numero)][:3]

def is_excel_file(file_path):
    try:
        with zipfile.ZipFile(file_path):
            return True
    except zipfile.BadZipFile:
        return False
    except Exception:
        return False

def convert_gsheet_link(shared_url):
    if "docs.google.com/spreadsheets" in shared_url:
        import re
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', shared_url)
        if match:
            sheet_id = match.group(1)
            return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx'
    return shared_url

@st.cache_data(ttl=600)
def carregar_excel_nuvem(link):
    url = convert_gsheet_link(link)
    with st.spinner("Carregando dados..."):
        resp = requests.get(url)
        if resp.status_code != 200:
            st.error(t("error_download_xls", code=resp.status_code))
            return None
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(resp.content)
            tmp.flush()
            if not is_excel_file(tmp.name):
                st.error(t("not_valid_excel"))
                return None
            try:
                df = pd.read_excel(tmp.name, engine="openpyxl")
            except Exception as e:
                st.error(t("excel_open_error", err=e))
                return None
        st.success("Dados carregados com sucesso!")
    return df

if "CLOUD_XLSX_URL" not in st.secrets:
    st.error(t("add_secrets"))
    st.stop()

xlsx_url = st.secrets["CLOUD_XLSX_URL"]
df_raw = carregar_excel_nuvem(xlsx_url)
if df_raw is None:
    st.stop()

def tratar_dados(df):
    erros = []
    df = df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"))
    obrigatorias = ['categoria', 'data', 'caixas_produzidas']
    for col in obrigatorias:
        if col not in df.columns:
            erros.append(t("mandatory_col_missing", col=col))
    try:
        df['data'] = pd.to_datetime(df['data'])
    except Exception:
        erros.append(t("error_date_conversion"))
    na_count = df.isna().sum()
    for col, qtd in na_count.items():
        if qtd > 0:
            erros.append(t("col_with_missing", col=col, num=qtd))
    negativos = (df['caixas_produzidas'] < 0).sum()
    if negativos > 0:
        erros.append(t("negatives", num=negativos))
    df_clean = df.dropna(subset=['categoria', 'data', 'caixas_produzidas']).copy()
    df_clean['caixas_produzidas'] = pd.to_numeric(df_clean['caixas_produzidas'], errors='coerce').fillna(0).astype(int)
    df_clean = df_clean[df_clean['caixas_produzidas'] >= 0]
    df_clean = df_clean.drop_duplicates(subset=['categoria', 'data'], keep='first')
    return df_clean, erros

df, erros = tratar_dados(df_raw)
with st.expander(t("data_issue_report"), expanded=len(erros) > 0):
    if erros:
        for e in erros:
            st.warning(e)
    else:
        st.success(t("no_critical"))

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

# ----------- Parâmetros / Filtros -----------
categorias = selecionar_categoria(df)
anos_disp = sorted(df['data'].dt.year.drop_duplicates())
meses_disp = sorted(df['data'].dt.month.drop_duplicates())
meses_nome = [f"{m:02d} - {calendar.month_name[m] if idioma == 'pt' else calendar.month_name[m][:3]}" for m in meses_disp]
map_mes = dict(zip(meses_nome, meses_disp))

default_categoria = categorias[0] if categorias else None
default_anos = anos_disp
default_meses_nome = meses_nome

# Navegação por páginas
pagina = st.sidebar.radio(
    "Navegação",
    ["Visão Geral", "Análise Detalhada", "Previsões"],
    key="pagina"
)

if pagina == "Visão Geral":
    if "filtros" not in st.session_state:
        st.session_state["filtros"] = {
            "categoria": default_categoria,
            "anos": default_anos,
            "meses_nome": default_meses_nome
        }

    with st.sidebar:
        categoria_analise = st.selectbox(t("category"), categorias, index=categorias.index(st.session_state["filtros"]["categoria"]) if categorias else 0, key="catbox")
        anos_selecionados = st.multiselect(t("year"), anos_disp, default=st.session_state["filtros"]["anos"], key="anobox")
        meses_selecionados_nome = st.multiselect(
            t("month"), 
            meses_nome, 
            default=default_meses_nome, 
            key="mesbox"
        )
        
        # Novo filtro de intervalo de datas
        data_inicial, data_final = st.date_input(
            t("select_date_range"),
            [df['data'].min().date(), df['data'].max().date()],
            min_value=df['data'].min().date(),
            max_value=df['data'].max().date()
        )
        df = df[(df['data'] >= pd.to_datetime(data_inicial)) & (df['data'] <= pd.to_datetime(data_final))]

    st.session_state["filtros"]["categoria"] = st.session_state["catbox"]
    st.session_state["filtros"]["anos"] = st.session_state["anobox"]
    st.session_state["filtros"]["meses_nome"] = st.session_state["mesbox"]

    meses_selecionados = [map_mes[n] for n in st.session_state["filtros"]["meses_nome"] if n in map_mes]

    df_filtrado = filtrar_periodo(df, st.session_state["filtros"]["categoria"], st.session_state["filtros"]["anos"], meses_selecionados)

    if df_filtrado.empty:
        st.error(t("empty_data_for_period"))
        st.stop()

    # --------- Subtítulo ---------
    st.markdown(
        f"<h3 style='color:{BRITVIC_ACCENT}; text-align:left;'>{t('analysis_for', cat=st.session_state['filtros']['categoria'])}</h3>",
        unsafe_allow_html=True
    )

    exibe_kpis(df_filtrado, st.session_state["filtros"]["categoria"])

    plot_tendencia(df_filtrado, st.session_state["filtros"]["categoria"])
    plot_variacao_mensal(df_filtrado, st.session_state["filtros"]["categoria"])
    plot_sazonalidade(df_filtrado, st.session_state["filtros"]["categoria"])

elif pagina == "Análise Detalhada":
    if len(set(df_filtrado['data'].dt.year)) > 1:
        plot_comparativo_ano_mes(df_filtrado, st.session_state["filtros"]["categoria"])
        plot_comparativo_acumulado(df_filtrado, st.session_state["filtros"]["categoria"])
    gerar_insights(df_filtrado, st.session_state["filtros"]["categoria"])

elif pagina == "Previsões":
    dados_hist, previsao, modelo_prophet = rodar_previsao_prophet(df_filtrado, st.session_state["filtros"]["categoria"], meses_futuro=6)
    plot_previsao(dados_hist, previsao, st.session_state["filtros"]["categoria"])

# --------- EXPORTAÇÃO ---------
with st.expander(t("export")):
    if st.button(t("export_with_fc"), help=t("export_with_fc")):
        base_export, nome_arq = exportar_consolidado(df_filtrado, previsao, st.session_state["filtros"]["categoria"])
        buffer = io.BytesIO()
        base_export.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        st.download_button(
            label=t("download_file"),
            data=buffer,
            file_name=nome_arq,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
