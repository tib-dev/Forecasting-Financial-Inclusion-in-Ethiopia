# dashboard/app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# -----------------------------
# Load Data Functions
# -----------------------------
@st.cache_data
def load_enriched_data(path="../data/processed/enriched_fi_data.csv"):
    df = pd.read_csv(path, parse_dates=["observation_date"])
    df['year'] = df['observation_date'].dt.year
    return df

# -----------------------------
# Forecast Reshaping
# -----------------------------
def reshape_forecasts(forecasts):
    """
    Reshape wide forecast CSV into long format:
    indicator_code | year | scenario | forecast | lower_ci | upper_ci
    """
    rows = []
    # List of indicators in your CSV
    indicators = ["ACC_OWNERSHIP", "USG_P2P_COUNT"]
    scenarios = ["base", "optimistic", "pessimistic"]

    for _, row in forecasts.iterrows():
        year = row['year']
        for ind in indicators:
            for sc in scenarios:
                forecast_val = row.get(f"{ind}_{sc}", None)
                # Get bounds if exist
                lower = row.get(f"{ind}_lower", None)
                upper = row.get(f"{ind}_upper", None)
                rows.append({
                    "year": year,
                    "indicator_code": ind,
                    "scenario": sc.capitalize(),
                    "forecast": forecast_val,
                    "lower_ci": lower,
                    "upper_ci": upper
                })
    return pd.DataFrame(rows)

@st.cache_data
def load_forecasts(path="../models/forecast_outputs.csv"):
    # First column is the year, no header name
    df = pd.read_csv(path)
    # If first column is unnamed, rename it to 'year'
    if df.columns[0].startswith('Unnamed'):
        df = df.rename(columns={df.columns[0]: 'year'})
    df_long = reshape_forecasts(df)
    return df_long


# -----------------------------
# KPI Calculation Functions
# -----------------------------
def calculate_kpis(data):
    latest_year = data['year'].max()
    latest_data = data[data['year'] == latest_year]
    kpis = {
        "Account Ownership": round(latest_data[latest_data['indicator_code']=='ACC_OWNERSHIP']['value_numeric'].mean(),2),
        "Digital Payment Usage": round(latest_data[latest_data['indicator_code']=='USG_DIGITAL_PAYMENT']['value_numeric'].mean(),2)
    }
    # P2P/ATM ratio (example)
    if 'USG_P2P_COUNT' in latest_data.columns and 'ATM_TRANSACTIONS' in latest_data.columns:
        p2p = latest_data['USG_P2P_COUNT'].sum()
        atm = latest_data['ATM_TRANSACTIONS'].sum()
        kpis["P2P/ATM Ratio"] = round(p2p/atm if atm>0 else 0,2)
    else:
        kpis["P2P/ATM Ratio"] = "N/A"
    return kpis

# -----------------------------
# Overview Page
# -----------------------------
def show_overview(data):
    st.title("📊 Ethiopia Financial Inclusion Overview")
    kpis = calculate_kpis(data)
    col1, col2, col3 = st.columns(3)
    col1.metric("Account Ownership (%)", kpis["Account Ownership"])
    col2.metric("Digital Payment Usage (%)", kpis["Digital Payment Usage"])
    col3.metric("P2P/ATM Ratio", kpis["P2P/ATM Ratio"])

    st.markdown("### Historical Trends")
    df_trend = data.groupby(['year','indicator_code'])['value_numeric'].mean().reset_index()
    fig = px.line(df_trend, x='year', y='value_numeric', color='indicator_code',
                  markers=True, title="Financial Inclusion Trends (2011-2024)")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Trends Page
# -----------------------------
def show_trends(data):
    st.title("📈 Historical Trends")
    indicators = data['indicator_code'].unique()
    selected_indicators = st.multiselect("Select indicators to display", indicators, default=indicators[:2])

    years = st.slider("Select year range", int(data['year'].min()), int(data['year'].max()), (2011, 2024))
    filtered = data[(data['year']>=years[0]) & (data['year']<=years[1]) & (data['indicator_code'].isin(selected_indicators))]

    fig = px.line(filtered, x='year', y='value_numeric', color='indicator_code', markers=True,
                  title="Indicator Trends Over Time")

    # Optional: overlay events if available
    if 'record_type' in data.columns:
        events = data[data['record_type']=='event']
        for idx, row in events.iterrows():
            fig.add_vline(x=row['observation_date'].year, line_dash="dash", line_color="red",
                          annotation_text=row['category'], annotation_position="top left")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Forecasts Page
# -----------------------------
def show_forecasts(forecasts):
    st.title("🔮 Forecasts (2025–2027)")

    scenario = st.selectbox("Select scenario", forecasts['scenario'].unique())
    filtered = forecasts[forecasts['scenario']==scenario]

    fig = go.Figure()
    for indicator in filtered['indicator_code'].unique():
        df_ind = filtered[filtered['indicator_code']==indicator]
        fig.add_trace(go.Scatter(x=df_ind['year'], y=df_ind['forecast'],
                                 mode='lines+markers', name=f"{indicator} Forecast"))
        fig.add_trace(go.Scatter(x=df_ind['year'], y=df_ind['upper_ci'],
                                 mode='lines', line=dict(dash='dash'), name=f"{indicator} Upper CI"))
        fig.add_trace(go.Scatter(x=df_ind['year'], y=df_ind['lower_ci'],
                                 mode='lines', line=dict(dash='dash'), name=f"{indicator} Lower CI"))

    fig.update_layout(title=f"Forecasts - {scenario} Scenario",
                      xaxis_title="Year", yaxis_title="Value",
                      hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Download Forecasts Data")
    st.download_button("Download CSV", filtered.to_csv(index=False), "forecasts.csv")

# -----------------------------
# Inclusion Projections Page
# -----------------------------
# After reshape_forecasts(df) you get:
# df_long.columns = ['year', 'indicator_code', 'scenario', 'forecast', 'lower_ci', 'upper_ci']

def show_projections(forecasts_long):
    st.header("Inclusion Projections")

    # Select indicator
    indicators = forecasts_long['indicator_code'].unique()
    indicator = st.selectbox("Select indicator to plot", indicators)

    # Select scenario
    scenarios = forecasts_long['scenario'].unique()
    scenario = st.selectbox("Select scenario for projections", scenarios)

    # Filter data
    df_plot = forecasts_long[
        (forecasts_long['indicator_code'] == indicator) &
        (forecasts_long['scenario'] == scenario)
    ]

    fig = px.bar(
        df_plot,
        x='year',
        y='forecast',
        text='forecast',
        error_y=df_plot['upper_ci'] - df_plot['forecast'] if 'upper_ci' in df_plot.columns else None,
        error_y_minus=df_plot['forecast'] - df_plot['lower_ci'] if 'lower_ci' in df_plot.columns else None,
        labels={'forecast': indicator, 'year': 'Year'},
        title=f"{indicator} projections ({scenario} scenario)",
        color_discrete_sequence=['skyblue']
    )

    # Add horizontal line for target (only for ACC_OWNERSHIP)
    if indicator == "ACC_OWNERSHIP":
        fig.add_hline(
            y=60,
            line_dash="dash",
            line_color="red",
            annotation_text="60% target",
            annotation_position="top right"
        )

    # Show numbers on bars
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')

    # Update layout for legend and axes
    fig.update_layout(
        yaxis_title=indicator,
        xaxis_title="Year",
        legend_title_text="Scenario",
        template='plotly_white'
    )

    st.plotly_chart(fig, width='stretch')



# -----------------------------
# Main
# -----------------------------
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Overview", "Trends", "Forecasts", "Inclusion Projections"])

    # Load data
    data = load_enriched_data()
    forecasts = load_forecasts()

    # Page routing
    if page=="Overview":
        show_overview(data)
    elif page=="Trends":
        show_trends(data)
    elif page=="Forecasts":
        show_forecasts(forecasts)
    elif page=="Inclusion Projections":
        show_projections(forecasts)

if __name__=="__main__":
    main()
