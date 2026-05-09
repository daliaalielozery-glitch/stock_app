import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockVision Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

.main-header {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    background: linear-gradient(135deg, #00d4ff, #7c3aed, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
}

.sub-header {
    color: #64748b;
    font-size: 1rem;
    font-family: 'Space Mono', monospace;
    margin-top: 4px;
    margin-bottom: 2rem;
}

.metric-card {
    background: linear-gradient(135deg, #111827, #1e293b);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin: 0.4rem 0;
    box-shadow: 0 4px 24px rgba(0, 212, 255, 0.05);
}

.metric-label {
    color: #64748b;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
}

.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #e2e8f0;
}

.metric-change-pos {
    color: #10b981;
    font-size: 0.85rem;
    font-family: 'Space Mono', monospace;
}

.metric-change-neg {
    color: #f43f5e;
    font-size: 0.85rem;
    font-family: 'Space Mono', monospace;
}

.stock-name-badge {
    background: linear-gradient(135deg, #0ea5e9, #7c3aed);
    border-radius: 8px;
    padding: 0.3rem 1rem;
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: white;
    margin-bottom: 1rem;
}

.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #475569;
    margin-bottom: 1rem;
    border-left: 3px solid #0ea5e9;
    padding-left: 12px;
}

.error-box {
    background: rgba(244, 63, 94, 0.1);
    border: 1px solid #f43f5e;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    color: #fda4af;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
}

.info-box {
    background: rgba(14, 165, 233, 0.08);
    border: 1px solid #0ea5e9;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    color: #7dd3fc;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
}

div[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #1e293b;
}

.stTextInput > div > div > input {
    background: #111827 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
}

.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #7c3aed) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(14, 165, 233, 0.3) !important;
}

.stSelectbox > div > div {
    background: #111827 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Space Mono', monospace !important;
}

.stRadio > div {
    gap: 0.5rem !important;
}

hr {
    border-color: #1e293b !important;
}

.ticker-scroll {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #475569;
    background: #0d1117;
    padding: 0.5rem 0;
    border-top: 1px solid #1e293b;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 1.5rem;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="main-header" style="font-size:1.8rem;">📈 StockVision</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Pro Market Terminal</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<p class="section-title">🔎 Search Stock</p>', unsafe_allow_html=True)
    ticker_input = st.text_input("", placeholder="e.g. AAPL, TSLA, AMZN", label_visibility="collapsed")

    st.markdown('<p class="section-title" style="margin-top:1rem;">📅 Time Range</p>', unsafe_allow_html=True)
    period_map = {
        "1 Week": "7d",
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y"
    }
    period_label = st.selectbox("", list(period_map.keys()), index=1, label_visibility="collapsed")
    period = period_map[period_label]

    st.markdown('<p class="section-title" style="margin-top:1rem;">📊 Chart Type</p>', unsafe_allow_html=True)
    chart_type = st.radio("", ["Candlestick", "Line", "Area"], label_visibility="collapsed")

    analyze_btn = st.button("⚡ Analyze Stock")

    st.markdown("---")
    st.markdown('<p class="section-title">💡 Popular Symbols</p>', unsafe_allow_html=True)
    popular = ["AAPL", "TSLA", "GOOGL", "AMZN", "MSFT", "META", "NVDA", "BTC-USD"]
    cols = st.columns(2)
    for i, sym in enumerate(popular):
        with cols[i % 2]:
            if st.button(sym, key=f"pop_{sym}"):
                ticker_input = sym
                analyze_btn = True


# ─── Main Area ───────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">Stock Market Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">// Real-time market intelligence terminal</p>', unsafe_allow_html=True)

POPULAR_TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "BRK-B", "JPM", "V"]


def fetch_stock_data(symbol: str, period: str):
    """Fetch stock data with validation."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            return None, None, "❌ Invalid symbol or no data available. Please check the ticker."
        hist = ticker.history(period=period)
        if hist.empty:
            return None, None, "❌ No historical data found for this period."
        return ticker, hist, None
    except Exception as e:
        return None, None, f"❌ Error fetching data: {str(e)}"


def get_price_color(change):
    return "#10b981" if change >= 0 else "#f43f5e"


def build_candlestick(hist, symbol):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05, row_heights=[0.75, 0.25])
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist['Open'], high=hist['High'],
        low=hist['Low'], close=hist['Close'], name='Price',
        increasing_line_color='#10b981', decreasing_line_color='#f43f5e',
        increasing_fillcolor='rgba(16,185,129,0.15)',
        decreasing_fillcolor='rgba(244,63,94,0.15)'
    ), row=1, col=1)
    colors = ['#10b981' if c >= o else '#f43f5e'
              for c, o in zip(hist['Close'], hist['Open'])]
    fig.add_trace(go.Bar(
        x=hist.index, y=hist['Volume'], name='Volume',
        marker_color=colors, opacity=0.7
    ), row=2, col=1)
    _style_fig(fig, f"{symbol} — Candlestick")
    return fig


def build_line(hist, symbol):
    ma20 = hist['Close'].rolling(20).mean()
    ma7 = hist['Close'].rolling(7).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Close Price',
                             line=dict(color='#0ea5e9', width=2.5)))
    fig.add_trace(go.Scatter(x=hist.index, y=ma7, name='MA 7',
                             line=dict(color='#f59e0b', width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(x=hist.index, y=ma20, name='MA 20',
                             line=dict(color='#7c3aed', width=1.5, dash='dash')))
    _style_fig(fig, f"{symbol} — Price + Moving Averages")
    return fig


def build_area(hist, symbol):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['Close'], name='Close',
        fill='tozeroy',
        line=dict(color='#0ea5e9', width=2),
        fillcolor='rgba(14,165,233,0.1)'
    ))
    _style_fig(fig, f"{symbol} — Area Chart")
    return fig


def _style_fig(fig, title):
    fig.update_layout(
        title=dict(text=title, font=dict(family='Space Mono', color='#64748b', size=13)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Space Mono', color='#94a3b8', size=11),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='#1e293b', borderwidth=1),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(gridcolor='#1e293b', showgrid=True, zeroline=False, rangeslider=dict(visible=False)),
        yaxis=dict(gridcolor='#1e293b', showgrid=True, zeroline=False),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#111827', bordercolor='#1e293b',
                        font=dict(family='Space Mono', color='#e2e8f0', size=12))
    )


# ─── Live Market Snapshot ────────────────────────────────────────────────────
st.markdown('<p class="section-title">⚡ Live Market Snapshot</p>', unsafe_allow_html=True)

snap_cols = st.columns(len(POPULAR_TICKERS))
for i, sym in enumerate(POPULAR_TICKERS):
    with snap_cols[i]:
        try:
            t = yf.Ticker(sym)
            info = t.fast_info
            price = info.last_price
            prev_close = info.previous_close
            change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0
            color = get_price_color(change_pct)
            arrow = "▲" if change_pct >= 0 else "▼"
            st.markdown(f"""
            <div class="metric-card" style="padding:0.8rem 1rem; text-align:center;">
                <div style="font-family:'Space Mono',monospace; font-size:0.7rem; color:#475569;">{sym}</div>
                <div style="font-family:'Space Mono',monospace; font-size:1rem; font-weight:700; color:#e2e8f0;">${price:,.2f}</div>
                <div style="font-family:'Space Mono',monospace; font-size:0.72rem; color:{color};">{arrow} {abs(change_pct):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.markdown(f"""
            <div class="metric-card" style="padding:0.8rem 1rem; text-align:center;">
                <div style="font-family:'Space Mono',monospace; font-size:0.7rem; color:#475569;">{sym}</div>
                <div style="font-family:'Space Mono',monospace; font-size:0.85rem; color:#1e3a5f;">— N/A —</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─── Analysis Section ────────────────────────────────────────────────────────
if analyze_btn and ticker_input:
    symbol = ticker_input.strip().upper()
    st.markdown(f'<div class="stock-name-badge">📡 Analyzing: {symbol}</div>', unsafe_allow_html=True)

    with st.spinner("Fetching market data..."):
        ticker_obj, hist, error = fetch_stock_data(symbol, period)

    if error:
        st.markdown(f'<div class="error-box">{error}</div>', unsafe_allow_html=True)
    else:
        info = ticker_obj.info

        # ── Key Metrics Row ──────────────────────────────────────────────────
        current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev_close = info.get("previousClose", current_price)
        price_change = current_price - prev_close
        change_pct = (price_change / prev_close * 100) if prev_close else 0
        day_high = info.get("dayHigh", 0)
        day_low = info.get("dayLow", 0)
        mkt_cap = info.get("marketCap", 0)
        volume = info.get("volume", 0)
        pe_ratio = info.get("trailingPE", None)
        fifty_two_high = info.get("fiftyTwoWeekHigh", 0)
        fifty_two_low = info.get("fiftyTwoWeekLow", 0)
        company_name = info.get("longName", symbol)

        color = get_price_color(change_pct)
        arrow = "▲" if change_pct >= 0 else "▼"

        st.markdown(f'<p class="section-title">📊 {company_name} — Key Metrics</p>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Current Price</div>
                <div class="metric-value">${current_price:,.2f}</div>
                <div class="{'metric-change-pos' if change_pct >= 0 else 'metric-change-neg'}">{arrow} ${abs(price_change):.2f} ({abs(change_pct):.2f}%)</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Day Range</div>
                <div class="metric-value" style="font-size:1.1rem;">${day_low:,.2f} – ${day_high:,.2f}</div>
                <div class="metric-change-pos">Today's trading range</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            cap_str = f"${mkt_cap/1e12:.2f}T" if mkt_cap >= 1e12 else f"${mkt_cap/1e9:.2f}B" if mkt_cap >= 1e9 else f"${mkt_cap/1e6:.2f}M"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Market Cap</div>
                <div class="metric-value">{cap_str}</div>
                <div class="metric-change-pos">P/E: {pe_ratio:.2f}x</div>
            </div>""" if pe_ratio else f"""
            <div class="metric-card">
                <div class="metric-label">Market Cap</div>
                <div class="metric-value">{cap_str}</div>
                <div class="metric-change-pos">P/E: N/A</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            vol_str = f"{volume/1e6:.2f}M" if volume >= 1e6 else f"{volume:,}"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Volume</div>
                <div class="metric-value">{vol_str}</div>
                <div class="metric-change-pos">52W: ${fifty_two_low:.2f}–${fifty_two_high:.2f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Chart ────────────────────────────────────────────────────────────
        st.markdown(f'<p class="section-title">📈 Price Chart — {period_label}</p>', unsafe_allow_html=True)

        if chart_type == "Candlestick":
            fig = build_candlestick(hist, symbol)
        elif chart_type == "Line":
            fig = build_line(hist, symbol)
        else:
            fig = build_area(hist, symbol)

        st.plotly_chart(fig, use_container_width=True)

        # ── OHLCV Table ───────────────────────────────────────────────────────
        st.markdown('<p class="section-title">📋 Historical OHLCV Data</p>', unsafe_allow_html=True)

        display_hist = hist[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        display_hist.index = display_hist.index.strftime('%Y-%m-%d')
        display_hist = display_hist.round(2)
        display_hist['Volume'] = display_hist['Volume'].apply(lambda x: f"{int(x):,}")
        display_hist.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        st.dataframe(
            display_hist.tail(30).sort_index(ascending=False),
            use_container_width=True,
            height=300
        )

        # ── Statistics ────────────────────────────────────────────────────────
        st.markdown('<p class="section-title">📉 Price Statistics</p>', unsafe_allow_html=True)

        close_prices = hist['Close']
        daily_returns = close_prices.pct_change().dropna()

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Period High</div>
                <div class="metric-value">${close_prices.max():,.2f}</div>
                <div class="metric-label" style="margin-top:8px;">Period Low</div>
                <div class="metric-value">${close_prices.min():,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with s2:
            total_return = ((close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0]) * 100
            tr_color = "#10b981" if total_return >= 0 else "#f43f5e"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Return</div>
                <div class="metric-value" style="color:{tr_color};">{total_return:+.2f}%</div>
                <div class="metric-label" style="margin-top:8px;">Daily Avg Return</div>
                <div class="metric-value" style="font-size:1.1rem;">{daily_returns.mean()*100:+.3f}%</div>
            </div>""", unsafe_allow_html=True)
        with s3:
            volatility = daily_returns.std() * 100
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Volatility (Daily Std)</div>
                <div class="metric-value">{volatility:.3f}%</div>
                <div class="metric-label" style="margin-top:8px;">Data Points</div>
                <div class="metric-value">{len(hist)} days</div>
            </div>""", unsafe_allow_html=True)

        # ── Returns Chart ─────────────────────────────────────────────────────
        st.markdown('<p class="section-title">📊 Daily Returns Distribution</p>', unsafe_allow_html=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=daily_returns * 100,
            nbinsx=40,
            name='Daily Returns',
            marker_color='#0ea5e9',
            opacity=0.75
        ))
        fig2.add_vline(x=0, line_width=1.5, line_dash="dash", line_color="#f43f5e")
        _style_fig(fig2, "Daily Returns Distribution (%)")
        st.plotly_chart(fig2, use_container_width=True)

elif analyze_btn and not ticker_input:
    st.markdown('<div class="error-box">⚠️ Please enter a stock symbol in the sidebar before analyzing.</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="info-box">
        👈 Enter a stock symbol in the sidebar (e.g., <strong>AAPL</strong>, <strong>TSLA</strong>, <strong>NVDA</strong>) and click <strong>Analyze Stock</strong> to begin.<br><br>
        The live snapshot above updates automatically with the latest prices for popular tickers.
    </div>
    """, unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style="text-align:center; font-family:'Space Mono',monospace; font-size:0.7rem; color:#334155;">
    StockVision Pro &nbsp;|&nbsp; Built with Streamlit + yFinance &nbsp;|&nbsp; 
    Data sourced from Yahoo Finance &nbsp;|&nbsp; For educational purposes only
</p>
""", unsafe_allow_html=True)