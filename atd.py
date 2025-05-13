import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração inicial do Streamlit
st.set_page_config(
    page_title="Dashboard de Paradas Industriais",
    page_icon="📊",
    layout="wide"
)

# Função para carregar os dados
@st.cache_data
def load_data(file_path):
    # Leitura do arquivo
    data = pd.read_excel(file_path)
    # Processamento inicial dos dados
    data['Duracao'] = pd.to_timedelta(data['Duração']).dt.total_seconds() / 3600  # Converter duração para horas
    data['Inicio'] = pd.to_datetime(data['Início'])
    data['Fim'] = pd.to_datetime(data['Fim'])
    return data

# Carregar arquivo do Google Drive
st.sidebar.header("Subir Arquivo de Dados ��")
uploaded_file = st.sidebar.file_uploader("Selecione o arquivo do banco de dados (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Carregar os dados
    df = load_data(uploaded_file)

    # Título principal
    st.title("📊 Dashboard Corporativo de Paradas Industriais")
    st.markdown("""
    Este dashboard tem como objetivo facilitar decisões relacionadas à manutenção, monitorar paradas industriais e identificar impactos das ações realizadas. Use os filtros abaixo para personalizar a análise.
    """)

    # Filtros interativos
    st.sidebar.header("Filtros ��")
    linha_filter = st.sidebar.multiselect(
        "Selecione a(s) Linha(s):",
        options=df["Linha"].unique(),
        default=df["Linha"].unique()
    )

    ano_filter = st.sidebar.multiselect(
        "Selecione o(s) Ano(s):",
        options=df["Ano"].unique(),
        default=df["Ano"].unique()
    )

    # Aplicar filtros ao dataframe
    df_filtered = df[df["Linha"].isin(linha_filter) & df["Ano"].isin(ano_filter)]

    # KPIs
    st.header("🔑 Indicadores Principais")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_duracao = df_filtered['Duracao'].sum()
        st.metric("⏱️ Total de Horas Paradas", f"{total_duracao:,.2f} horas")

    with col2:
        total_paradas = len(df_filtered)
        st.metric("🔧 Total de Paradas", total_paradas)

    with col3:
        maior_parada = df_filtered.loc[df_filtered['Duracao'].idxmax()]
        st.metric("🔥 Maior Parada", f"{maior_parada['Duracao']:.2f} horas")

    with col4:
        linhas_mais_frequentes = df_filtered['Linha'].mode()
        st.metric("🏭 Linha Mais Parada", linhas_mais_frequentes[0])

    # Visualização: Duração Mensal Acumulada
    st.header("📅 Acumulado Mensal de Paradas")
    df_filtered['Mês_Nome'] = pd.to_datetime(df_filtered['Mês'], format='%m').dt.strftime('%B')
    df_monthly = df_filtered.groupby(["Ano", "Mês_Nome"])["Duracao"].sum().reset_index()

    fig_monthly = px.bar(
        df_monthly,
        x="Mês_Nome",
        y="Duracao",
        color="Ano",
        title="Duração Mensal Acumulada (Horas)",
        labels={'Duracao': 'Duração (H)'},
        barmode='group',
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    # Visualização: Paradas Mais Frequentes
    st.header("🚨 Paradas Mais Frequentes")
    df_frequent_stops = df_filtered['Parada'].value_counts().reset_index()
    df_frequent_stops.columns = ['Parada', 'Frequência']

    fig_frequent = px.bar(
        df_frequent_stops.head(10),
        x="Parada",
        y="Frequência",
        title="Top 10 Paradas Mais Frequentes",
        labels={'Frequência': 'Quantidade'},
        text="Frequência",
    )
    st.plotly_chart(fig_frequent, use_container_width=True)

    # Insights Automáticos
    st.header("💡 Insights Automáticos")
    total_horas_preventiva = df_filtered[df_filtered["Descrição_Parada_Nível_1"] == "MANUTENÇÃO PREVENTIVA"]["Duracao"].sum()
    total_horas_corretiva = df_filtered[df_filtered["Descrição_Parada_Nível_1"] != "MANUTENÇÃO PREVENTIVA"]["Duracao"].sum()

    st.markdown(f"""
    - **Manutenção Preventiva** foi responsável por **{total_horas_preventiva:.2f} horas** de paradas, representando **{(total_horas_preventiva / total_duracao) * 100:.2f}%** do total.
    - **Manutenção Corretiva** ou outras causas causaram **{total_horas_corretiva:.2f} horas**, representando **{(total_horas_corretiva / total_duracao) * 100:.2f}%** do total.
    - A linha com maior número de paradas foi **{linhas_mais_frequentes[0]}**, indicando uma possível necessidade de intervenção prioritária.
    """)

    # Rodapé
    st.markdown("---")
    st.markdown("**Dashboard desenvolvido por [Nome do Analista] | Gerado com Streamlit**")

else:
    st.warning("Por favor, faça o upload do arquivo de dados para continuar.")
