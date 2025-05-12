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

# Cores Britvic
BRITVIC_PRIMARY = "#003057"
BRITVIC_ACCENT = "#27AE60"
BRITVIC_BG = "#F4FFF6"

# --------- Dicionário de Tradução -----------
TRANSLATIONS = (
    "Dashboard de Produção": {"pt": "Dashboard de Produção", "en": "Production Dashboard"},
    "Análise para categoria:": {"pt": "Análise para categoria:", "en": "Analysis for category:"},
    "Não há dados para esse período e categoria.": {"pt": "Não há dados para esse período e categoria.", "en": "No data for this period and category."},
    "Média diária:": {"pt": "Média diária:", "en": "Daily average:"},
    "Registros:": {"pt": "Registros:", "en": "Records:"},
    "Nenhum problema crítico encontrado.": {"pt": "Nenhum problema crítico encontrado.", "en": "No critical problems found."},
    "Coluna obrigatória ausente:": {"pt": "Coluna obrigatória ausente:", "en": "Missing required column:"},
    "Erro ao converter coluna 'data'.": {"pt": "Erro ao converter coluna 'data'.", "en": "Error converting 'data' column."},
    "Coluna '{col}' com {qtd} valores ausentes.": {"pt": "Coluna '{col}' com {qtd} valores ausentes.", "en": "Column '{col}' with {qtd} missing values."},
    "{negativos} registros negativos em 'caixas_produzidas'.": {"pt": "{negativos} registros negativos em 'caixas_produzidas'.", "en": "{negativos} negative entries in 'caixas_produzidas'."},
    "Relatório de problemas encontrados": {"pt": "Relatório de problemas encontrados", "en": "Issues detected report"},
    "🏷️ Categoria:": {"pt": "🏷️ Categoria:", "en": "🏷️ Category:"},
    "📅 Ano(s):": {"pt": "📅 Ano(s):", "en": "📅 Year(s):"},
    "📆 Mês(es):": {"pt": "📆 Mês(es):", "en": "📆 Month(s):"},
    "Tendência Diária": {"pt": "Tendência Diária", "en": "Daily Trend"},
    "Caixas Produzidas": {"pt": "Caixas Produzidas", "en": "Produced Boxes"},
    "Data": {"pt": "Data", "en": "Date"},
    "Sem dados para tendência.": {"pt": "Sem dados para tendência.", "en": "No data for trend."},

    "Produção Mensal Total": {"pt": "Produção Mensal Total", "en": "Monthly Production Total"},
    "Mês/Ano": {"pt": "Mês/Ano", "en": "Month/Year"},
    "Variação Percentual Mensal (%)": {"pt": "Variação Percentual Mensal (%)", "en": "Monthly Percentage Variation (%)"},
    "Variação (%)": {"pt": "Variação (%)", "en": "Variation (%)"},

    "Sazonalidade Mensal": {"pt": "Sazonalidade Mensal", "en": "Monthly Seasonality"},
    "Mês": {"pt": "Mês", "en": "Month"},
    "Produção": {"pt": "Produção", "en": "Production"},
    "Ano": {"pt": "Ano", "en": "Year"},
    "Sem dados para sazonalidade.": {"pt": "Sem dados para sazonalidade.", "en": "No data for seasonality."},

    "Produção Mensal": {"pt": "Produção Mensal", "en": "Monthly Production"},
    "Comparativo por Ano": {"pt": "Comparativo por Ano", "en": "Yearly Comparison"},
    "Produção Acumulada Mês a Mês": {"pt": "Produção Acumulada Mês a Mês", "en": "Cumulative Production Month by Month"},
    "Caixas Acumuladas": {"pt": "Caixas Acumuladas", "en": "Cumulative Boxes"},
    "Limite Superior": {"pt": "Limite Superior", "en": "Upper Limit"},
    "Limite Inferior": {"pt": "Limite Inferior", "en": "Lower Limit"},
    "Previsão de Produção": {"pt": "Previsão de Produção", "en": "Production Forecast"},
    "Previsão": {"pt": "Previsão", "en": "Forecast"},
    "Histórico": {"pt": "Histórico", "en": "Historical"},
    "Sem previsão disponível.": {"pt": "Sem previsão disponível.", "en": "No forecast available."},

    "Insights Automáticos": {"pt": "Insights Automáticos", "en": "Automatic Insights"},
    "Crescimento recente na produção detectado nos últimos meses.": {"pt": "Crescimento recente na produção detectado nos últimos meses.", "en": "Recent growth in production detected over the last months."},
    "Queda recente na produção detectada nos últimos meses.": {"pt": "Queda recente na produção detectada nos últimos meses.", "en": "Recent drop in production detected over the last months."},
    "Foram encontrados {qtd} dias atípicos de produção (possíveis outliers).": {"pt": "Foram encontrados {qtd} dias atípicos de produção (possíveis outliers).", "en": "Found {qtd} atypical days of production (possible outliers)."},
    "Alta variabilidade diária. Sugerido investigar causas das flutuações.": {"pt": "Alta variabilidade diária. Sugerido investigar causas das flutuações.", "en": "High daily variability. Suggested to investigate the causes for these fluctuations."},
    "Nenhum padrão preocupante encontrado para esta categoria.": {"pt": "Nenhum padrão preocupante encontrado para esta categoria.", "en": "No concerning pattern found for this category."},

    "Exportação": {"pt": "Exportação", "en": "Export"},
    "⬇️ Exportar consolidado com previsão (.xlsx)": {"pt": "⬇️ Exportar consolidado com previsão (.xlsx)", "en": "⬇️ Export consolidated with forecast (.xlsx)"},
    "Clique para exportar os dados atuais filtrados para Excel": {"pt": "Clique para exportar os dados atuais filtrados para Excel", "en": "Click to export current filtered data to Excel"},
    "Download arquivo Excel ⬇️": {"pt": "Download arquivo Excel ⬇️", "en": "Download Excel file ⬇️"},
    "Sem previsão para exportar.": {"pt": "Sem previsão para exportar.", "en": "No forecast to export."},

    "Adicione CLOUD_XLSX_URL ao seu .streamlit/secrets.toml e compartilhe a planilha para 'qualquer pessoa com o link'.": {
        "pt": "Adicione CLOUD_XLSX_URL ao seu .streamlit/secrets.toml e compartilhe a planilha para 'qualquer pessoa com o link'.",
        "en": "Add CLOUD_XLSX_URL to your .streamlit/secrets.toml and share the spreadsheet for 'anyone with the link'."
    },
    "Erro ao baixar planilha. Status code: {status}": {"pt": "Erro ao baixar planilha. Status code: {status}", "en": "Error downloading spreadsheet. Status code: {status}"},
    "Arquivo baixado não é um Excel válido. Confirme se o link é público/correto!": {"pt": "Arquivo baixado não é um Excel válido. Confirme se o link é público/correto!", "en": "Downloaded file is not a valid Excel. Confirm if the link is public/correct!"},
    "Erro ao abrir o Excel: {erro}": {"pt": "Erro ao abrir o Excel: {erro}", "en": "Error opening Excel file: {erro}"},
    "Sem dados para a seleção.": {"pt": "Sem dados para a seleção.", "en": "No data for the selection."}
    )

# ----------- Função de Tradução -------------
def get_lang():
    return "pt" if st.session_state.get("lang", "Português") == "Português" else "en"

def t(key, **kwargs):
    lang = get_lang()
    if key in TRANSLATIONS:
        s = TRANSLATIONS[key][lang]
        if kwargs:
            return s.format(**kwargs)
        return s
    return key

# Configuração da página
st.set_page_config(
    page_title=t("Dashboard de Produção"),
    layout="wide",
    page_icon="🧃",
)

# ----------- Seletor de Idioma -------------
with st.sidebar:
    lang = st.selectbox("🌐 Idioma / Language:", ["Português", "English"], key="lang")

# --------- CSS para estilização ---------
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

# --------- TOPO (Logo e Título) ---------
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
        <img src="https://raw.githubusercontent.com/martins6231/atdautomatizado/8a52d1f013f2cae36b078e7341ef5d3bd8ee26b3/calsberg_britvic.jpg" alt="Britvic Logo" style="width: 150px; margin-bottom: 10px;">
        <h1 style="
            font-size: 2.2rem;
            font-weight: bold;
            color: {BRITVIC_PRIMARY};
            margin: 0;"
        >
            {t('Dashboard de Produção')}
        </h1>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class='subtitle'>
    {t('Os dados deste Dashboard são atualizados automaticamente a cada <b style="color:#27AE60">10 minutos</b> a partir de uma planilha segura em nuvem (Google Drive).')}
    </div>
""", unsafe_allow_html=True)
st.markdown("""<hr style="margin-bottom: 20px;">""", unsafe_allow_html=True)

def nome_mes(numero):
    lang = get_lang()
    if lang == "pt":
        meses = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    else:
        meses = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return meses[int(numero)]

# ------------------ Download seguro da planilha -----------------
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
    resp = requests.get(url)
    if resp.status_code != 200:
        st.error(t("Erro ao baixar planilha. Status code: {status}", status=resp.status_code))
        return None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(resp.content)
        tmp.flush()
        if not is_excel_file(tmp.name):
            st.error(t("Arquivo baixado não é um Excel válido. Confirme se o link é público/correto!"))
            return None
        try:
            df = pd.read_excel(tmp.name, engine="openpyxl")
        except Exception as e:
            st.error(t("Erro ao abrir o Excel: {erro}", erro=e))
            return None
    return df

if "CLOUD_XLSX_URL" not in st.secrets:
    st.error(t("Adicione CLOUD_XLSX_URL ao seu .streamlit/secrets.toml e compartilhe a planilha para 'qualquer pessoa com o link'."))
    st.stop()

xlsx_url = st.secrets["CLOUD_XLSX_URL"]
df_raw = carregar_excel_nuvem(xlsx_url)
if df_raw is None:
    st.stop()

# ---------------------------------------------------------------

def tratar_dados(df):
    erros = []
    df = df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"))
    obrigatorias = ['categoria', 'data', 'caixas_produzidas']
    for col in obrigatorias:
        if col not in df.columns:
            erros.append(t("Coluna obrigatória ausente:") + f" {col}")
    try:
        df['data'] = pd.to_datetime(df['data'])
    except Exception:
        erros.append(t("Erro ao converter coluna 'data'."))
    na_count = df.isna().sum()
    for col, qtd in na_count.items():
        if qtd > 0:
            erros.append(t("Coluna '{col}' com {qtd} valores ausentes.", col=col, qtd=qtd))
    negativos = (df['caixas_produzidas'] < 0).sum()
    if negativos > 0:
        erros.append(t("{negativos} registros negativos em 'caixas_produzidas'.", negativos=negativos))
    df_clean = df.dropna(subset=['categoria', 'data', 'caixas_produzidas']).copy()
    df_clean['caixas_produzidas'] = pd.to_numeric(df_clean['caixas_produzidas'], errors='coerce').fillna(0).astype(int)
    df_clean = df_clean[df_clean['caixas_produzidas'] >= 0]
    df_clean = df_clean.drop_duplicates(subset=['categoria', 'data'], keep='first')
    return df_clean, erros

df, erros = tratar_dados(df_raw)
with st.expander(t("Relatório de problemas encontrados"), expanded=len(erros) > 0):
    if erros:
        for e in erros:
            st.warning(e)
    else:
        st.success(t("Nenhum problema crítico encontrado."))

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

# -------- SELEÇÃO DE PARÂMETROS (Sidebar UX melhorada) --------

categorias = selecionar_categoria(df)
anos_disp = sorted(df['data'].dt.year.drop_duplicates())
meses_disp = sorted(df['data'].dt.month.drop_duplicates())
meses_nome = [f"{m:02d} - {nome_mes(m)}" for m in meses_disp]
map_mes = dict(zip(meses_nome, meses_disp))

default_categoria = categorias[0] if categorias else None
default_anos = anos_disp
default_meses_nome = meses_nome

if "filtros" not in st.session_state:
    st.session_state["filtros"] = {
        "categoria": default_categoria,
        "anos": default_anos,
        "meses_nome": default_meses_nome
    }

with st.sidebar:
    categoria_analise = st.selectbox(t("🏷️ Categoria:"), categorias, index=categorias.index(st.session_state["filtros"]["categoria"]) if categorias else 0, key="catbox")
    anos_selecionados = st.multiselect(t("📅 Ano(s):"), anos_disp, default=st.session_state["filtros"]["anos"], key="anobox")
    meses_selecionados_nome = st.multiselect(t("📆 Mês(es):"), meses_nome, default=st.session_state["filtros"]["meses_nome"], key="mesbox")

# Após interação, atualizar session_state também
st.session_state["filtros"]["categoria"] = st.session_state["catbox"]
st.session_state["filtros"]["anos"] = st.session_state["anobox"]
st.session_state["filtros"]["meses_nome"] = st.session_state["mesbox"]

meses_selecionados = [map_mes[n] for n in st.session_state["filtros"]["meses_nome"] if n in map_mes]

df_filtrado = filtrar_periodo(df, st.session_state["filtros"]["categoria"], st.session_state["filtros"]["anos"], meses_selecionados)

# --------- SUBTÍTULO PRINCIPAL ---------
st.markdown(
    f"<h3 style='color:{BRITVIC_ACCENT}; text-align:left;'>{t('Análise para categoria:')} <b>{st.session_state['filtros']['categoria']}</b></h3>",
    unsafe_allow_html=True
)
if df_filtrado.empty:
    st.error(t("Não há dados para esse período e categoria."))
    st.stop()

# --------- MÉTRICAS / KPIs ---------
def exibe_kpis(df, categoria):
    df_cat = df[df['categoria'] == categoria]
    if df_cat.empty:
        st.info(t("Sem dados para a seleção."))
        return None
    df_cat['ano'] = df_cat['data'].dt.year
    kpis = df_cat.groupby('ano')['caixas_produzidas'].agg(['sum', 'mean', 'std', 'count']).reset_index()
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 18px;">
        """, unsafe_allow_html=True
    )
    for _, row in kpis.iterrows():
        ano = int(row['ano'])
        st.markdown(
            f"""
            <div style="
                background: #e8f8ee;
                border-radius: 18px;
                box-shadow: 0 6px 28px 0 rgba(0, 48, 87, 0.13);
                padding: 28px 38px 22px 38px;
                min-width: 220px;
                margin-bottom: 13px;
                text-align: center;"
            >
                <div style="font-weight: 600; color: {BRITVIC_PRIMARY}; font-size: 1.12em; margin-bottom:5px;">
                    📦 {t("Ano") if get_lang() == "pt" else "Year"} {ano}
                </div>
                <div style="color: {BRITVIC_ACCENT}; font-size:2.1em; font-weight:bold; margin-bottom:7px;">
                    {int(row['sum']):,} {t("Caixas Produzidas")}
                </div>
                <div style="font-size: 1.08em; color: {BRITVIC_PRIMARY}; margin-bottom:2px;">
                    {t("Média diária:")}<br><b style="color:{BRITVIC_ACCENT};font-size:1.15em">{row['mean']:.0f}</b>
                </div>
                <div style="font-size: 1em; color: #666;">{t("Registros:")} <b>{row['count']}</b></div>
            </div>
            """, unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
    return kpis

exibe_kpis(df_filtrado, st.session_state["filtros"]["categoria"])

# --------- GRÁFICOS ---------
def plot_tendencia(df, categoria):
    grupo = gerar_dataset_modelo(df, categoria)
    if grupo.empty:
        st.info(t("Sem dados para tendência."))
        return
    # Barras de produção diária
    fig = px.bar(
        grupo,
        x="data",
        y="caixas_produzidas",
        title=f"{t('Tendência Diária')} - {categoria}",
        labels={"data": t("Data"), "caixas_produzidas": t("Caixas Produzidas")},
        text_auto=True
    )
    fig.update_traces(marker_color=BRITVIC_PRIMARY)
    fig.update_layout(
        template="plotly_white", 
        hovermode="x",
        title_font_color=BRITVIC_PRIMARY,
        plot_bgcolor=BRITVIC_BG,
        xaxis_tickformat="%d/%m/%Y"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_variacao_mensal(df, categoria):
    agrup = dataset_ano_mes(df, categoria)
    mensal = agrup.groupby([agrup['data'].dt.to_period('M')])['caixas_produzidas'].sum().reset_index()
    mensal['mes'] = mensal['data'].dt.strftime('%b/%Y')
    mensal['var_%'] = mensal['caixas_produzidas'].pct_change() * 100
    fig1 = px.bar(
        mensal, x='mes', y='caixas_produzidas', text_auto=True,
        title=f"{t('Produção Mensal Total')} - {categoria}",
        labels={"mes": t("Mês/Ano"), "caixas_produzidas": t("Caixas Produzidas")}
    )
    fig1.update_traces(marker_color=BRITVIC_ACCENT)
    fig1.update_layout(template="plotly_white", title_font_color=BRITVIC_PRIMARY, plot_bgcolor=BRITVIC_BG)
    fig2 = px.line(
        mensal, x='mes', y='var_%', markers=True,
        title=f"{t('Variação Percentual Mensal (%)')} - {categoria}",
        labels={"mes": t("Mês/Ano"), "var_%": t("Variação (%)")}
    )
    fig2.update_traces(line_color="#E67E22", marker=dict(size=7, color=BRITVIC_ACCENT))
    fig2.update_layout(template="plotly_white", title_font_color=BRITVIC_PRIMARY, plot_bgcolor=BRITVIC_BG)
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

def plot_sazonalidade(df, categoria):
    agrup = dataset_ano_mes(df, categoria)
    if agrup.empty:
        st.info(t("Sem dados para sazonalidade."))
        return
    fig = px.box(
        agrup, x='mes', y='caixas_produzidas', color=agrup['ano'].astype(str),
        points='all', notched=True,
        title=f"{t('Sazonalidade Mensal')} - {categoria}",
        labels={'mes': t("Mês"), "caixas_produzidas": t("Produção")},
        hover_data=["ano"], color_discrete_sequence=px.colors.sequential.Teal[::-1]
    )
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1,13)),
            ticktext=[nome_mes(m) for m in range(1,13)]
        ),
        template="plotly_white",
        legend_title=t("Ano"),
        title_font_color=BRITVIC_PRIMARY,
        plot_bgcolor=BRITVIC_BG
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_comparativo_ano_mes(df, categoria):
    agrup = dataset_ano_mes(df, categoria)
    tab = agrup.groupby(['ano','mes'])['caixas_produzidas'].sum().reset_index()
    tab['mes_nome'] = tab['mes'].apply(nome_mes)
    tab = tab.sort_values(['mes'])
    fig = go.Figure()
    anos = sorted(tab['ano'].unique())
    cores = px.colors.qualitative.Dark24
    for idx, ano in enumerate(anos):
        dados_ano = tab[tab['ano'] == ano]
        fig.add_trace(go.Bar(
            x=dados_ano['mes_nome'],
            y=dados_ano['caixas_produzidas'],
            name=str(ano),
            text=dados_ano['caixas_produzidas'],
            textposition='auto',
            marker_color=cores[idx % len(cores)]
        ))
    fig.update_layout(
        barmode='group',
        title=f"{t('Produção Mensal')} {categoria} - {t('Comparativo por Ano')}",
        xaxis_title=t("Mês"),
        yaxis_title=t("Caixas Produzidas"),
        legend_title=t("Ano"),
        hovermode="x unified",
        template="plotly_white",
        title_font_color=BRITVIC_PRIMARY,
        plot_bgcolor=BRITVIC_BG
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_comparativo_acumulado(df, categoria):
    agrup = dataset_ano_mes(df, categoria)
    res = agrup.groupby(['ano','mes'])['caixas_produzidas'].sum().reset_index()
    res['acumulado'] = res.groupby('ano')['caixas_produzidas'].cumsum()
    fig = px.line(
        res, x='mes', y='acumulado', color=res['ano'].astype(str),
        markers=True,
        labels={'mes': t("Mês"), 'acumulado': t("Caixas Acumuladas"), 'ano': t("Ano")},
        title=f"{t('Produção Acumulada Mês a Mês')} - {categoria}",
        color_discrete_sequence=px.colors.sequential.Teal[::-1]
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(
        legend_title=t("Ano"),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1,13)),
            ticktext=[nome_mes(m) for m in range(1,13)]
        ),
        hovermode="x unified",
        template="plotly_white",
        title_font_color=BRITVIC_PRIMARY,
        plot_bgcolor=BRITVIC_BG
    )
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
        st.info(t("Sem previsão disponível."))
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dados_hist['ds'], y=dados_hist['y'],
                             mode='lines+markers', name=t('Histórico'),
                             line=dict(color=BRITVIC_PRIMARY, width=2),
                             marker=dict(color=BRITVIC_ACCENT)))
    fig.add_trace(go.Scatter(x=previsao['ds'], y=previsao['yhat'],
                             mode='lines', name=t('Previsão'), line=dict(color=BRITVIC_ACCENT, width=2)))
    fig.add_trace(go.Scatter(x=previsao['ds'], y=previsao['yhat_upper'],
                             line=dict(dash='dash', color='#AED6F1'), name=t("Limite Superior"), opacity=0.3))
    fig.add_trace(go.Scatter(x=previsao['ds'], y=previsao['yhat_lower'],
                             line=dict(dash='dash', color='#AED6F1'), name=t("Limite Inferior"), opacity=0.3))
    fig.update_layout(title=f"{t('Previsão de Produção')} - {categoria}",
                     xaxis_title=t("Data"), yaxis_title=t("Caixas Produzidas"),
                     template="plotly_white", hovermode="x unified",
                     title_font_color=BRITVIC_PRIMARY,
                     plot_bgcolor=BRITVIC_BG)
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
            tendencias.append(t("Crescimento recente na produção detectado nos últimos meses."))
        elif agg
