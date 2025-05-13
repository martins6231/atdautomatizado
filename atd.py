import streamlit as st
import pandas as pd
import requests
import tempfile
import zipfile

# Configuração inicial
st.set_page_config(
    page_title="Dashboard de Manutenção - Paradas",
    layout="wide",
    page_icon="🛠️"
)

BRITVIC_PRIMARY = "#003057"
BRITVIC_ACCENT = "#27AE60"
BRITVIC_BG = "#F4FFF6"

# CSS customizado
st.markdown(
    f"""
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
    """,
    unsafe_allow_html=True,
)

# Função para carregar dados do Google Sheets
@st.cache_data(ttl=600)
def carregar_dados(link):
    """Carrega dados de um Google Sheets público."""
    resp = requests.get(link)
    if resp.status_code != 200:
        st.error(f"Erro ao baixar planilha. Status code: {resp.status_code}")
        return None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(resp.content)
        tmp.flush()
        if not is_excel_file(tmp.name):
            st.error("Arquivo baixado não é um Excel válido.")
            return None
        df = pd.read_excel(tmp.name, engine="openpyxl")
    return df

def is_excel_file(file_path):
    try:
        with zipfile.ZipFile(file_path):
            return True
    except zipfile.BadZipFile:
        return False
    except Exception:
        return False

# Carregar link do secrets.toml
CLOUD_XLSX_URL = st.secrets["CLOUD_XLSX_URL"]

# Carregar dados
df = carregar_dados(CLOUD_XLSX_URL)

if df is not None:
    # Seguir com o processamento dos dados e visualizações...
    st.write("Dados carregados com sucesso!")
    st.dataframe(df)


def maiores_paradas_mensais(df):
    """Agrupa e seleciona as maiores paradas mensais."""
    df['Duração (horas)'] = df['Duração'].dt.total_seconds() / 3600
    maiores = (
        df.groupby(['Mês', 'Ano', 'Linha'])['Duração (horas)'].sum()
        .reset_index()
        .sort_values(by=['Ano', 'Mês', 'Duração (horas)'], ascending=[False, False, False])
    )
    return maiores


def paradas_frequentes(df):
    """Identifica as categorias de paradas mais frequentes."""
    frequentes = (
        df['Descrição_Parada_Nivel_1']
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Tipo de Parada", "Descrição_Parada_Nivel_1": "Ocorrências"})
    )
    return frequentes


# Carregar dados
df = carregar_dados()

if df is not None:
    # Filtros laterais
    st.sidebar.header("Filtros ��")
    linhas = df["Linha"].unique()
    linha_selecionada = st.sidebar.selectbox("Selecione a linha de produção:", options=linhas)

    df_filtrado = df[df["Linha"] == linha_selecionada]

    # Identidade visual e título
    st.markdown(f"""
        <div class="center">
            <img src="https://raw.githubusercontent.com/martins6231/app_atd/main/britvic_logo.png" 
                 alt="Britvic Logo" style="width: 150px; margin-bottom: 10px;">
            <h1 class="britvic-title">Dashboard de Paradas</h1>
            <p class="subtitle">Monitoramento das paradas para priorização de manutenção</p>
        </div>
    """, unsafe_allow_html=True)

    # KPIs
    st.markdown("### �� Métricas Gerais")
    total_duracao = df_filtrado['Duração'].sum().total_seconds() / 3600
    total_paradas = len(df_filtrado)
    maior_parada = df_filtrado['Duração'].max()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Duração Total (h)", f"{total_duracao:,.2f}")
    with col2:
        st.metric("Total de Paradas", total_paradas)
    with col3:
        st.metric("Maior Parada (h)", f"{maior_parada.total_seconds() / 3600:.2f}")

    # Gráfico de maiores paradas mensais
    st.markdown("### �� Maiores Paradas Mensais")
    maiores_paradas_df = maiores_paradas_mensais(df_filtrado)
    fig1 = px.bar(
        maiores_paradas_df,
        x="Mês",
        y="Duração (horas)",
        color="Linha",
        barmode="group",
        title="Maiores Paradas Mensais",
        labels={"Duração (horas)": "Horas de Parada", "Mês": "Mês"},
    )
    fig1.update_traces(marker_color=BRITVIC_ACCENT)
    fig1.update_layout(template="plotly_white", title_font_color=BRITVIC_PRIMARY)
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico de paradas mais frequentes
    st.markdown("### �� Paradas Mais Frequentes")
    paradas_frequentes_df = paradas_frequentes(df_filtrado)
    fig2 = px.pie(
        paradas_frequentes_df,
        values="Ocorrências",
        names="Tipo de Parada",
        title="Paradas por Ocorrência",
        color_discrete_sequence=px.colors.sequential.Teal,
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Insights automáticos
    st.markdown("### �� Insights Automáticos")
    ultimos_meses = df_filtrado[df_filtrado['Ano'] == df_filtrado['Ano'].max()]

    paradas_impacto = ultimos_meses.groupby('Descrição_Parada_Nivel_2')['Duração'].sum().sort_values(ascending=False).head(1)
    maior_impacto = paradas_impacto.index[0] if not paradas_impacto.empty else "Não identificado"
    st.info(f"**Maior impacto atual:** {maior_impacto}")

    if df_filtrado["Duração"].mean().total_seconds() > 3600:
        st.success("✅ Duração média de paradas acima de 1 hora. Avaliar processos críticos.")

    # Exportação de dados
    st.markdown("### �� Exportação de Dados")
    if st.button("Exportar Dados Filtrados para Excel"):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name="Paradas Filtradas")
        st.download_button(
            label="📥 Baixar Dados",
            data=buffer.getvalue(),
            file_name=f"paradas_{linha_selecionada}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
