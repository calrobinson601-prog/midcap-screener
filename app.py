



import yfinance as yf
import pandas as pd

# Define your mid-cap universe
mid_caps = ['PATH', 'LYFT', 'SHAK', 'WING', 'DY']  # You can expand this list

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def screen_stock(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2mo", interval="1d")

    if hist.shape[0] < 50:
        return None  # Not enough data

    # 1. Tight Price Consolidation
    price_range = hist['Close'].max() - hist['Close'].min()
    consolidation = price_range / hist['Close'].mean() < 0.05

    # 2. Increasing Volume on Up Days
    up_days = hist[hist['Close'] > hist['Open']]
    volume_trend = up_days['Volume'].tail(5).mean() > up_days['Volume'].head(5).mean()

    # 3. Moving Average Alignment
    ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
    ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
    price = hist['Close'].iloc[-1]
    ma_alignment = price > ma_20 and price > ma_50 and ma_20 > ma_50

    # 4. RSI Between 55–70
    rsi = calculate_rsi(hist).iloc[-1]
    rsi_ok = 55 <= rsi <= 70

    # 5. Low Beta
    beta = stock.info.get('beta', 1.5)
    beta_ok = beta <= 1.2

    # 6. Placeholder for News Drift
    news_drift = False  # Manual or API integration needed

    # 7. Breakout from Key Resistance
    resistance = hist['Close'].rolling(window=20).max().iloc[-2]
    breakout = price > resistance

    score = sum([consolidation, volume_trend, ma_alignment, rsi_ok, beta_ok, breakout])
    return {
        'Ticker': ticker,
        'Score': score,
        'RSI': round(rsi, 2),
        'Beta': beta,
        'Breakout': breakout,
        'MA Alignment': ma_alignment,
        'Volume Trend': volume_trend,
        'Consolidation': consolidation
    }

# Run the screener
results = [screen_stock(ticker) for ticker in mid_caps]
results = [r for r in results if r is not None]
df = pd.DataFrame(results).sort_values(by='Score', ascending=False)

# Display results
print("\n📊 Calvin’s Mid-Cap Breakout Rankings:")
print(df.to_string(index=False))
