import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu

# Set page configuration
st.set_page_config(
    page_title="Machine Efficiency Analysis",
    page_icon="🏭",
    layout="wide"
)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'pt-BR'

# Translations
translations = {
    'pt-BR': {
        'title': 'Análise de Eficiência de Máquinas',
        'date_range': 'Período de Análise',
        'start_date': 'Data Inicial',
        'end_date': 'Data Final',
        'quick_periods': 'Períodos Rápidos',
        'today': 'Hoje',
        'yesterday': 'Ontem',
        'last_week': 'Última Semana',
        'last_month': 'Último Mês',
        'downtime_filter': 'Filtro de Paradas',
        'efficiency_metrics': 'Métricas de Eficiência',
        'comparison': 'Comparação de Períodos',
        'select_period': 'Selecione o Período de Comparação'
    },
    'en': {
        'title': 'Machine Efficiency Analysis',
        'date_range': 'Analysis Period',
        'start_date': 'Start Date',
        'end_date': 'End Date',
        'quick_periods': 'Quick Periods',
        'today': 'Today',
        'yesterday': 'Yesterday',
        'last_week': 'Last Week',
        'last_month': 'Last Month',
        'downtime_filter': 'Downtime Filter',
        'efficiency_metrics': 'Efficiency Metrics',
        'comparison': 'Period Comparison',
        'select_period': 'Select Comparison Period'
    }
}

def get_text(key):
    return translations[st.session_state.language][key]

# Language selector
col_lang = st.sidebar.columns([8, 2])
with col_lang[1]:
    if st.button('🌐'):
        st.session_state.language = 'en' if st.session_state.language == 'pt-BR' else 'pt-BR'
        st.rerun()

# Main title
st.title(get_text('title'))

# Date range selection
st.subheader(get_text('date_range'))
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(get_text('start_date'), datetime.now().date() - timedelta(days=30))
with col2:
    end_date = st.date_input(get_text('end_date'), datetime.now().date())

# Quick period selection
st.subheader(get_text('quick_periods'))
quick_periods = st.columns(4)

with quick_periods[0]:
    if st.button(get_text('today')):
        start_date = datetime.now().date()
        end_date = start_date
        st.rerun()

with quick_periods[1]:
    if st.button(get_text('yesterday')):
        end_date = datetime.now().date() - timedelta(days=1)
        start_date = end_date
        st.rerun()

with quick_periods[2]:
    if st.button(get_text('last_week')):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        st.rerun()

with quick_periods[3]:
    if st.button(get_text('last_month')):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        st.rerun()

# Validate date range
if start_date > end_date:
    st.error('Start date must be before or equal to end date')
    st.stop()

# Downtime filter
st.subheader(get_text('downtime_filter'))
downtime_types = ['Mechanical', 'Electrical', 'Operational', 'Quality']
selected_downtimes = st.multiselect('', downtime_types, default=downtime_types)

# Sample data generation (replace with your actual data loading)
@st.cache_data
def generate_sample_data(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq='H')
    data = {
        'timestamp': date_range,
        'efficiency': np.random.uniform(60, 100, len(date_range)),
        'downtime_type': np.random.choice(downtime_types, len(date_range)),
        'downtime_duration': np.random.uniform(0, 60, len(date_range))
    }
    return pd.DataFrame(data)

# Load and filter data
df = generate_sample_data(start_date, end_date)
df = df[df['downtime_type'].isin(selected_downtimes)]

# Metrics calculation
col_metrics = st.columns(4)
with col_metrics[0]:
    avg_efficiency = df['efficiency'].mean()
    st.metric("Average Efficiency", f"{avg_efficiency:.1f}%")

with col_metrics[1]:
    total_downtime = df['downtime_duration'].sum()
    st.metric("Total Downtime", f"{total_downtime:.1f} min")

with col_metrics[2]:
    availability = 100 - (total_downtime / (len(df) * 60) * 100)
    st.metric("Availability", f"{availability:.1f}%")

with col_metrics[3]:
    mtbf = len(df) / (df['downtime_duration'] > 0).sum() if (df['downtime_duration'] > 0).sum() > 0 else 0
    st.metric("MTBF (hours)", f"{mtbf:.1f}")

# Visualization
st.subheader(get_text('efficiency_metrics'))
tab1, tab2, tab3 = st.tabs(["Efficiency Trend", "Downtime Analysis", "Pareto Chart"])

with tab1:
    fig_efficiency = px.line(df, x='timestamp', y='efficiency', 
                           title='Efficiency Over Time')
    st.plotly_chart(fig_efficiency, use_container_width=True)

with tab2:
    downtime_by_type = df.groupby('downtime_type')['downtime_duration'].sum().reset_index()
    fig_downtime = px.bar(downtime_by_type, x='downtime_type', y='downtime_duration',
                         title='Total Downtime by Type')
    st.plotly_chart(fig_downtime, use_container_width=True)

with tab3:
    # Pareto chart
    downtime_pareto = downtime_by_type.sort_values('downtime_duration', ascending=False)
    downtime_pareto['cumulative_percentage'] = downtime_pareto['downtime_duration'].cumsum() / downtime_pareto['downtime_duration'].sum() * 100
    
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(x=downtime_pareto['downtime_type'], 
                               y=downtime_pareto['downtime_duration'],
                               name='Downtime'))
    fig_pareto.add_trace(go.Scatter(x=downtime_pareto['downtime_type'],
                                   y=downtime_pareto['cumulative_percentage'],
                                   name='Cumulative %',
                                   yaxis='y2'))
    
    fig_pareto.update_layout(
        title='Downtime Pareto Analysis',
        yaxis=dict(title='Downtime Duration (min)'),
        yaxis2=dict(title='Cumulative %', overlaying='y', side='right')
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

# Period comparison
st.subheader(get_text('comparison'))
comparison_start = st.date_input(get_text('select_period'), 
                               value=start_date - timedelta(days=(end_date - start_date).days))
comparison_end = comparison_start + (end_date - start_date)

if comparison_start and comparison_end:
    comparison_df = generate_sample_data(comparison_start, comparison_end)
    comparison_df = comparison_df[comparison_df['downtime_type'].isin(selected_downtimes)]
    
    # Compare metrics
    col_compare = st.columns(4)
    with col_compare[0]:
        comparison_efficiency = comparison_df['efficiency'].mean()
        efficiency_diff = avg_efficiency - comparison_efficiency
        st.metric("Efficiency Comparison", 
                 f"{comparison_efficiency:.1f}%",
                 f"{efficiency_diff:+.1f}%")
    
    with col_compare[1]:
        comparison_downtime = comparison_df['downtime_duration'].sum()
        downtime_diff = total_downtime - comparison_downtime
        st.metric("Downtime Comparison",
                 f"{comparison_downtime:.1f} min",
                 f"{downtime_diff:+.1f} min")
    
    with col_compare[2]:
        comparison_availability = 100 - (comparison_downtime / (len(comparison_df) * 60) * 100)
        availability_diff = availability - comparison_availability
        st.metric("Availability Comparison",
                 f"{comparison_availability:.1f}%",
                 f"{availability_diff:+.1f}%")
    
    with col_compare[3]:
        comparison_mtbf = len(comparison_df) / (comparison_df['downtime_duration'] > 0).sum() if (comparison_df['downtime_duration'] > 0).sum() > 0 else 0
        mtbf_diff = mtbf - comparison_mtbf
        st.metric("MTBF Comparison",
                 f"{comparison_mtbf:.1f} hours",
                 f"{mtbf_diff:+.1f} hours")