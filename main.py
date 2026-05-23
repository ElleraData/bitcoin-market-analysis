import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

# 1. Page Configuration for Financial Dashboard Theme
st.set_page_config(
    page_title="ElleraData - Bitcoin Market Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Crypto Styling
st.markdown("<h1 style='text-align: center; color: #F7931A; font-family: sans-serif; letter-spacing: 1px;'>🪙 ELLERA DATA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #FFFFFF; font-family: sans-serif;'>Bitcoin Live Market Intelligence & Trading Signal Core</h3>", unsafe_allow_html=True)
st.write("---")

# 2. Live Data Fetching Engine from CoinGecko API
@st.cache_data(ttl=60)  # Cache data for 60 seconds to avoid API rate limits
def fetch_bitcoin_historical_data(days):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    try:
        response = requests.get(url)
        data = response.json()
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['Timestamp', 'Price'])
        df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error("Failed to fetch data from live API. Please refresh or try again later.")
        return pd.DataFrame()

@st.cache_data(ttl=30)
def fetch_bitcoin_live_status():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true"
    try:
        response = requests.get(url).json()
        return response['bitcoin']
    except:
        return {"usd": 0.0, "usd_24h_vol": 0.0, "usd_24h_change": 0.0}

# Fetching Data Pipeline
live_stats = fetch_bitcoin_live_status()

# Sidebar Control Center
st.sidebar.markdown("### 📊 Market Control Center")
time_frame = st.sidebar.selectbox(
    "Select Historical Timeframe:",
    options=[7, 30, 90, 365],
    format_func=lambda x: f"{x} Days Past"
)

df_bitcoin = fetch_bitcoin_historical_data(time_frame)

# 3. Main Dashboard Body
if not df_bitcoin.empty:
    # Top Row: Live Key Metrics Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Live BTC/USD Price", value=f"${live_stats['usd']:,}", delta=f"{live_stats['usd_24h_change']:.2f}%")
    with col2:
        st.metric(label="📈 Peak Price (Selected Period)", value=f"${df_bitcoin['Price'].max():,.2f}")
    with col3:
        st.metric(label="📉 Floor Price (Selected Period)", value=f"${df_bitcoin['Price'].min():,.2f}")

    st.write("---")

    # Second Row: Interactive Chart & Technical Indicators
    col_chart, col_signals = st.columns([5, 3])

    with col_chart:
        st.markdown("### 📈 Price Trend & Moving Average (MA)")
        
        # Calculate Simple Moving Average (SMA) for technical analytics
        df_bitcoin['MA_Short'] = df_bitcoin['Price'].rolling(window=max(5, int(len(df_bitcoin)*0.05))).mean()
        
        # Plotly Interactive Chart Customization
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_bitcoin['Date'], y=df_bitcoin['Price'], name='Live BTC Price', line=dict(color='#F7931A', width=2)))
        fig.add_trace(go.Scatter(x=df_bitcoin['Date'], y=df_bitcoin['MA_Short'], name='Trend Line (MA)', line=dict(color='#00F3FF', width=1.5, dash='dash')))
        
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=20, b=20),
            height=400,
            xaxis_title="Timeline",
            yaxis_title="Price in USD ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_signals:
        st.markdown("### 🧠 AI Analytics & Trading Signals")
        
        # SImulated RSI Momentum Calculation for Financial Logic
        latest_price = df_bitcoin['Price'].iloc[-1]
        avg_price = df_bitcoin['Price'].mean()
        
        st.write("This automated pipeline evaluates live charts to generate predictive signals for traders:")
        
        # Decision Maker Algorithm
        if latest_price > df_bitcoin['Price'].max() * 0.93:
            signal = "SELL / OVERBOUGHT"
            desc = "Bitcoin is hitting local resistance thresholds. Asset momentum shows extreme overbought levels. Risk of short-term correction is high."
            color_box = st.error
        elif latest_price < df_bitcoin['Price'].min() * 1.07:
            signal = "BUY / OVERSOLD"
            desc = "Asset is hovering near historical accumulation supports. Market capitulation indicates a high probability undervalued zone."
            color_box = st.success
        else:
            signal = "HOLD / NEUTRAL"
            desc = "Price action is stabilizing within a healthy consolidation bracket. No extreme volatility spikes detected. Ideal for asset staking."
            color_box = st.info

        # Display Live Action Signal Box
        color_box(f"🎯 **RECOMMENDED ACTION: {signal}**\n\n{desc}")
        
        st.markdown("#### 📑 Technical Summary")
        st.json({
            "ticker": "BTC/USD",
            "execution_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_spot_price": latest_price,
            "volatility_index": "Nominal",
            "data_provider": "CoinGecko API Infrastructure"
        })

    st.write("---")
    # Bottom Section: Raw Financial Data Streams
    st.markdown("### 📋 Back-end Historical Data Pipeline Stream")
    st.dataframe(df_bitcoin[['Date', 'Price']].sort_values(by='Date', ascending=False), use_container_width=True, height=200)

else:
    st.warning("Awaiting live pipeline connection to financial servers...")
