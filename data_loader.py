import pandas as pd
import yfinance as yf
import streamlit as st
from config import START_DATE, END_DATE, STOCKS


@st.cache_data(ttl=3600)
def fetch_stock_data() -> dict[str, pd.DataFrame]:
    """Busca dados históricos das 3 ações e retorna dict {ticker: DataFrame}."""
    tickers = list(STOCKS.values())
    raw = yf.download(tickers, start=START_DATE, end=END_DATE, auto_adjust=True, progress=False)

    result = {}
    for ticker in tickers:
        # yfinance retorna MultiIndex (field, ticker) quando múltiplos tickers
        try:
            close  = raw["Close"][ticker].dropna()
            volume = raw["Volume"][ticker].dropna()
        except KeyError:
            close  = raw["Close"].dropna()
            volume = raw["Volume"].dropna()

        if close.empty:
            continue

        df = pd.DataFrame({"Close": close, "Volume": volume})
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        df["DailyReturn"]      = df["Close"].pct_change() * 100
        df["CumulativeReturn"] = (df["Close"] / df["Close"].iloc[0] - 1) * 100

        result[ticker] = df

    return result


def get_summary(metrics: dict[str, pd.DataFrame]) -> dict:
    """Retorna resumo por ticker: preço atual, retorno acumulado, drawdown máximo."""
    summary = {}
    for ticker, df in metrics.items():
        last_price     = df["Close"].iloc[-1]
        cum_return     = df["CumulativeReturn"].iloc[-1]
        rolling_max    = df["Close"].cummax()
        drawdown       = ((df["Close"] - rolling_max) / rolling_max * 100).min()
        summary[ticker] = {
            "last_price":  last_price,
            "cum_return":  cum_return,
            "max_drawdown": drawdown,
        }
    return summary
