import ccxt
import pandas as pd
import requests
import datetime
import pytz
import time
# 'apiKey': 'Iz8w9EmwoZOiqe7Qjm7PrUri7uu0ZDxPjS5qEQRoX5mZePHm44RBRfVVAcVyUNrF',
# 'secret': 'oEDFhfOvJgmjhEpBIfDfnHmtjnTBs4urWz5PyBdZqUpf1Y9hXTwTjmS6gdOOFmWY',
# Set up the Binance API client
exchange = ccxt.binance({
    'apiKey': 'bb43fe8bd007b775f24a30ba76a9d48df299b71b68487337c90af6d65ce2534e',
    'secret': 'e72bebb5611dcea07da10d6b9e42e19c0862a8a02859a6e8aa274bec321129d0',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'test': True,
        'adjustForTimeDifference': True
    }
})
exchange.set_sandbox_mode(True)
exchange = ccxt.binance()
# Define the trading pair and time frame
symbol = 'BTC/USDT'
timeframe = '15m'

# Define the EMA periods
ema1_period = 9
ema2_period = 21

# Define the number of candles to retrieve
limit = ema2_period + 1
# Function to convert timestamp to hour, minute, and day
def timestamp_to_hmd_vietnam(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    dt_vietnam = dt.astimezone(timezone)
    hour = dt_vietnam.hour
    minute = dt_vietnam.minute
    day = dt_vietnam.day
    month=dt_vietnam.month
    return hour, minute, day,month
# Function to calculate EMA
def calculate_ema(data, period):
    k = 2 / (period + 1)
    ema = [data['close'][0]]
    for i in range(1, len(data)):
        ema.append(data['close'][i] * k + ema[-1] * (1 - k))
    return pd.Series(ema, name='EMA_' + str(period))
def send_to_telegram(message):

    apiToken = '6266365592:AAEGRWCHLU6Jq14fCv8IpNzKCxEAncwLMww'
    chatID = '5935177714'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)
# Function to check for EMA crossovers
def check_ema_crossover(ema1, ema2):
    if ema1.iloc[-3] < ema2.iloc[-3] and ema1.iloc[-2] > ema2.iloc[-2]:
        timestamp = df.iloc[-2]['timestamp']
        hour, minute, day, month = timestamp_to_hmd_vietnam(timestamp)
        message = f"EMA(9) crossed above EMA(21) at {hour}:{minute} on day {day} on month {month}. Go long!"
        print('EMA(9) crossed above EMA(21)')
        send_to_telegram(message)
    elif ema1.iloc[-3] > ema2.iloc[-3] and ema1.iloc[-2] < ema2.iloc[-2]:
        timestamp = df.iloc[-2]['timestamp']
        hour, minute, day, month = timestamp_to_hmd_vietnam(timestamp)
        message = f"EMA(9) crossed below EMA(21) at {hour}:{minute} on day {day} on month {month}. Go long!"
        send_to_telegram(message)

# Loop to continuously monitor for EMA crossovers
while True:
    # Retrieve the latest market data from the exchange API
    data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    # Convert the market data to a pandas dataframe
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # Calculate the EMA values
    ema1 = calculate_ema(df, ema1_period)
    ema2 = calculate_ema(df, ema2_period)

    # Check for EMA crossovers
    check_ema_crossover(ema1, ema2)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Ho_Chi_Minh')
    send_to_telegram("vercel vẫn đang hoạt động")
    # Wait for 15 minutes before checking again
    time.sleep(900)
