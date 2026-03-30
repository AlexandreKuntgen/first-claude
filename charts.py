import pandas as pd
import plotly.graph_objects as go
from config import STOCKS, COLORS

# Mapa ticker -> nome amigável
TICKER_NAMES = {v: k for k, v in STOCKS.items()}

RANGE_BUTTONS = [
    dict(count=1,  label="1M",  step="month", stepmode="backward"),
    dict(count=3,  label="3M",  step="month", stepmode="backward"),
    dict(count=6,  label="6M",  step="month", stepmode="backward"),
    dict(count=1,  label="1A",  step="year",  stepmode="backward"),
    dict(step="all", label="Tudo"),
]

LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    hovermode="x unified",
    margin=dict(l=50, r=20, t=50, b=50),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)


def _base_layout(title: str) -> dict:
    layout = dict(LAYOUT_DEFAULTS)
    layout["title"] = dict(text=title, font=dict(size=15))
    layout["xaxis"] = dict(
        rangeselector=dict(buttons=RANGE_BUTTONS),
        rangeslider=dict(visible=False),
        type="date",
    )
    return layout


def make_price_chart(metrics: dict[str, pd.DataFrame]) -> go.Figure:
    fig = go.Figure()
    for ticker, df in metrics.items():
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"].round(2),
            name=TICKER_NAMES.get(ticker, ticker),
            line=dict(color=COLORS[ticker], width=2),
            hovertemplate=f"<b>{TICKER_NAMES.get(ticker, ticker)}</b><br>R$ %{{y:.2f}}<extra></extra>",
        ))
    fig.update_layout(**_base_layout("Evolução do Preço de Fechamento (R$)"))
    fig.update_yaxes(title_text="R$", tickprefix="R$ ")
    return fig


def make_cumulative_chart(metrics: dict[str, pd.DataFrame]) -> go.Figure:
    fig = go.Figure()
    # Linha de base
    if metrics:
        first_df = next(iter(metrics.values()))
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.3)")
    for ticker, df in metrics.items():
        final_val = df["CumulativeReturn"].iloc[-1]
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["CumulativeReturn"].round(2),
            name=TICKER_NAMES.get(ticker, ticker),
            line=dict(color=COLORS[ticker], width=2),
            hovertemplate=f"<b>{TICKER_NAMES.get(ticker, ticker)}</b><br>%{{y:.2f}}%<extra></extra>",
        ))
        # Anotação no final da linha
        fig.add_annotation(
            x=df.index[-1],
            y=final_val,
            text=f" {final_val:+.1f}%",
            showarrow=False,
            font=dict(color=COLORS[ticker], size=11),
            xanchor="left",
        )
    fig.update_layout(**_base_layout("Performance Acumulada (base Jan/2025 = 0%)"))
    fig.update_yaxes(title_text="Retorno (%)", ticksuffix="%")
    return fig


def make_daily_returns_chart(metrics: dict[str, pd.DataFrame]) -> go.Figure:
    fig = go.Figure()
    for ticker, df in metrics.items():
        dr = df["DailyReturn"].dropna()
        colors = ["#26a69a" if v >= 0 else "#ef5350" for v in dr]
        fig.add_trace(go.Bar(
            x=dr.index,
            y=dr.round(2),
            name=TICKER_NAMES.get(ticker, ticker),
            marker_color=colors,
            opacity=0.7,
            hovertemplate=f"<b>{TICKER_NAMES.get(ticker, ticker)}</b><br>%{{y:.2f}}%<extra></extra>",
        ))
    layout = _base_layout("Retornos Diários (%)")
    layout["barmode"] = "overlay"
    fig.update_layout(**layout)
    fig.update_yaxes(title_text="Retorno Diário (%)", ticksuffix="%")
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.2)")
    return fig


def make_volume_chart(metrics: dict[str, pd.DataFrame]) -> go.Figure:
    fig = go.Figure()
    for ticker, df in metrics.items():
        fig.add_trace(go.Bar(
            x=df.index,
            y=df["Volume"],
            name=TICKER_NAMES.get(ticker, ticker),
            marker_color=COLORS[ticker],
            opacity=0.8,
            hovertemplate=f"<b>{TICKER_NAMES.get(ticker, ticker)}</b><br>Vol: %{{y:,.0f}}<extra></extra>",
        ))
    layout = _base_layout("Volume Negociado")
    layout["barmode"] = "group"
    fig.update_layout(**layout)
    fig.update_yaxes(title_text="Volume", tickformat=".2s")
    return fig
