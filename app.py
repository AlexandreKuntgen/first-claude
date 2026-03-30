import streamlit as st
from config import STOCKS, COLORS, APP_TITLE, APP_SUBTITLE
from data_loader import fetch_stock_data, get_summary
from charts import make_price_chart, make_cumulative_chart, make_daily_returns_chart, make_volume_chart

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📈",
    layout="wide",
)

# --- Cabeçalho ---
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

# --- Busca de dados ---
with st.spinner("Buscando dados do Yahoo Finance..."):
    all_metrics = fetch_stock_data()

if not all_metrics:
    st.error("Não foi possível buscar os dados. Verifique sua conexão e tente novamente.")
    st.stop()

# --- Sidebar ---
st.sidebar.header("Ações")
TICKER_NAMES = {v: k for k, v in STOCKS.items()}

selected_tickers = []
for name, ticker in STOCKS.items():
    if ticker in all_metrics:
        checked = st.sidebar.checkbox(name, value=True, key=ticker)
        if checked:
            selected_tickers.append(ticker)

if not selected_tickers:
    st.warning("Selecione ao menos uma ação na sidebar.")
    st.stop()

metrics = {t: all_metrics[t] for t in selected_tickers}

# Resumo na sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Resumo")
summary = get_summary(metrics)
for ticker, s in summary.items():
    color = "#26a69a" if s["cum_return"] >= 0 else "#ef5350"
    st.sidebar.markdown(
        f"**{TICKER_NAMES[ticker]}**  \n"
        f"Último: `R$ {s['last_price']:.2f}`  \n"
        f"Acumulado: <span style='color:{color}'>{s['cum_return']:+.2f}%</span>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("")

# --- Linha 1: Preço | Performance Acumulada ---
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(make_price_chart(metrics), use_container_width=True)
with col2:
    st.plotly_chart(make_cumulative_chart(metrics), use_container_width=True)

# --- Linha 2: Retornos Diários ---
st.plotly_chart(make_daily_returns_chart(metrics), use_container_width=True)

# --- Linha 3: Volume ---
st.plotly_chart(make_volume_chart(metrics), use_container_width=True)

# --- Rodapé: métricas resumidas ---
st.markdown("---")
cols = st.columns(len(metrics))
for col, (ticker, s) in zip(cols, summary.items()):
    with col:
        st.metric(
            label=TICKER_NAMES[ticker],
            value=f"R$ {s['last_price']:.2f}",
            delta=f"{s['cum_return']:+.2f}% (acumulado)",
        )
        st.caption(f"Drawdown máximo: {s['max_drawdown']:.2f}%")
