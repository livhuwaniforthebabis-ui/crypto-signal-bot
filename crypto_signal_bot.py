import requests
import time

# ===== CONFIG =====
TELEGRAM_TOKEN = 8688692681:AAFeVYJxmVzrqWRpsr5ElhZL9yANv22iF84
CHAT_ID = -1003088214813
CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Add more coins if you want
INTERVAL = 300  # seconds between checks (5 minutes)
PRICE_CHANGE_THRESHOLD = 0.01  # 1% change for BUY/SELL

# ===== FUNCTIONS =====
def get_price(symbol):
    """Fetch current price from Binance API"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url).json()
    return float(response['price'])

def generate_signal(current, previous):
    """Simple rule-based signal"""
    if previous is None:
        return "⚪ HOLD"
    change = (current - previous) / previous
    if change >= PRICE_CHANGE_THRESHOLD:
        return "📈 BUY"
    elif change <= -PRICE_CHANGE_THRESHOLD:
        return "📉 SELL"
    else:
        return "⚪ HOLD"

def send_telegram(message):
    """Send message to Telegram channel/group"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def format_message(symbol, price, signal, percent_change):
    """Format message with trend and percent change"""
    return (
        f"{symbol} Signal\n"
        f"Price: ${price:.2f}\n"
        f"Signal: {signal}\n"
        f"Change since last: {percent_change:+.2f}%"
    )

# ===== MAIN LOOP =====
previous_prices = {symbol: None for symbol in CRYPTO_SYMBOLS}
previous_signals = {symbol: None for symbol in CRYPTO_SYMBOLS}

while True:
    for symbol in CRYPTO_SYMBOLS:
        try:
            price = get_price(symbol)
            prev_price = previous_prices[symbol]
            signal = generate_signal(price, prev_price)
            
            # Calculate percent change
            percent_change = ((price - prev_price) / prev_price * 100) if prev_price else 0
            
            # Only send message if signal changed
            if signal != previous_signals[symbol]:
                message = format_message(symbol, price, signal, percent_change)
                send_telegram(message)
                print(f"✅ Sent {symbol} signal: {signal} ({percent_change:+.2f}%)")
                previous_signals[symbol] = signal
            
            previous_prices[symbol] = price
        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
    time.sleep(INTERVAL)