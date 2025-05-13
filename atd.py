import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def inicializar_dados():
    st.title("Dashboard de Análise de Produção")

    uploaded_file = st.file_uploader("Por favor, faça o upload do arquivo Excel:", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        df['Inicio'] = pd.to_datetime(df['Inicio'], format='%d/%m/%Y %H:%M', errors='coerce')
        df['Fim'] = pd.to_datetime(df['Fim'], format='%d/%m/%Y %H:%M', errors='coerce')
        df['Duracao (h)'] = df['Duração'].apply(lambda x: float(str(x).split(':')[0]) if pd.notnull(x) and isinstance(x, str) else x)
        df['Mês'] = df['Inicio'].dt.month
        df['Ano'] = df['Inicio'].dt.year
        df['Trimestre'] = df['Inicio'].dt.quarter

        return df
    else:
        st.warning("Faça o upload de um arquivo para continuar.")
        return None

def obter_ano_e_linha(df):
    opcoes_linha = ['PET', 'TETRA 1000', 'TETRA 200', 'SIG 1000', 'SIG 200', 'TODAS']
    linha = st.selectbox("Selecione a linha:", opcoes_linha)

    ano = st.text_input("Insira o ano desejado ou 'TODOS':")
    if ano.upper() == 'TODOS':
        ano = None
    elif ano.isdigit() and len(ano) == 4:
        ano = int(ano)
    else:
        st.error("Por favor, insira um ano válido ou 'TODOS'.")
        ano = None

    mes = st.text_input("Insira o mês desejado (1-12) ou 'TODOS':")
    if mes.upper() == 'TODOS':
        mes = None
    elif mes.isdigit() and 1 <= int(mes) <= 12:
        mes = int(mes)
    else:
        st.error("Por favor, insira um mês válido (1-12) ou 'TODOS'.")
        mes = None

    return linha, ano, mes

def plotar_grafico(title, xlabel, ylabel, df, x_col, y_col):
    plt.figure(figsize=(12, 8))
    sns.barplot(x=x_col, y=y_col, data=df, orient='h')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    st.pyplot(plt.gcf())
    plt.close()

def analisar_dados(df, linha, ano, mes):
    if df is None:
        return
    
    if ano is not None:
        df = df[df['Ano'] == ano]
    if linha != 'TODAS':
        df = df[df['Linha'] == linha]
    if mes is not None:
        df = df[df['Mês'] == mes]
    
    tres_meses_antes = datetime.now() - timedelta(days=90)
    df_ultimos_meses = df[df['Inicio'] >= tres_meses_antes]
    
    # Linhas com mais problemas
    resumo = df_ultimos_meses.groupby("Linha")["Duracao (h)"].sum().nlargest(3).reset_index()
    plotar_grafico(
        'Top 3 Linhas com Mais Problemas', 
        'Duração (h)', 
        'Linha', 
        resumo, 
        'Duracao (h)', 
        'Linha'
    )
    
    # Maiores problemas na linha selecionada
    df_linha = df_ultimos_meses[df_ultimos_meses['Linha'] == linha] if linha != 'TODAS' else df_ultimos_meses
    problemas = df_linha.groupby("Parada")["Duracao (h)"].sum().nlargest(5).reset_index()
    plotar_grafico(
        f'Top 5 Problemas em {linha if linha != "TODAS" else "Todas as Linhas"}', 
        'Duração (h)', 
        'Parada', 
        problemas, 
        'Duracao (h)', 
        'Parada'
    )

    # Frequência de tipos de paradas
    freq_paradas = df_ultimos_meses['Parada'].value_counts().nlargest(5).reset_index()
    freq_paradas.columns = ['Parada', 'Quantidade']
    plotar_grafico(
        'Frequência de Tipos de Paradas (Top 5)', 
        'Quantidade', 
        'Parada', 
        freq_paradas, 
        'Quantidade', 
        'Parada'
    )

def main():
    df = inicializar_dados()
    if df is not None:
        linha, ano, mes = obter_ano_e_linha(df)
        analisar_dados(df, linha, ano, mes)

if __name__ == "__main__":
    main()
