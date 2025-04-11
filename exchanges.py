import ccxt
import pandas as pd
from datetime import datetime
import time

def initialize_exchanges():
    """Initialize Binance and Kraken exchange objects."""
    try:
        binance = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'maker': 0.001,  # 0.1%
                'taker': 0.001,  # 0.1%
                'withdrawal': 0.0005  # 0.05%
            }
        })
        kraken = ccxt.kraken({
            'enableRateLimit': True,
            'options': {
                'maker': 0.0016,  # 0.16%
                'taker': 0.0026,  # 0.26%
                'withdrawal': 0.0005  # 0.05%
            }
        })
        return binance, kraken
    except Exception as e:
        print(f"Error initializing exchanges: {str(e)}")
        return None, None

def get_ticker_symbol(coin, exchange_id):
    """
    Convert coin symbol to exchange-specific ticker format.
    Kraken uses USD pairs while Binance uses USDT pairs.
    """
    if exchange_id == 'kraken':
        # Kraken-specific mappings
        kraken_mappings = {
            'BTC': 'XBT/USD',
            'ETH': 'ETH/USD',
            'SOL': 'SOL/USD',
            'XRP': 'XRP/USD',
            'ADA': 'ADA/USD',
            'DOT': 'DOT/USD',
            'LINK': 'LINK/USD',
            'MATIC': 'MATIC/USD',
            'AVAX': 'AVAX/USD',
            'UNI': 'UNI/USD'
        }
        return kraken_mappings.get(coin)
    else:
        # Binance uses USDT pairs
        return f"{coin}/USDT"

def fetch_price(exchange, symbol):
    """Fetch current price for a symbol from an exchange."""
    if exchange is None or symbol is None:
        return None
        
    try:
        ticker = exchange.fetch_ticker(symbol)
        if ticker and ticker.get('last') is not None:
            return {
                'price': float(ticker['last']),
                'volume': float(ticker.get('quoteVolume', 0) or ticker.get('baseVolume', 0) or 0),
                'bid': float(ticker.get('bid', 0) or 0),
                'ask': float(ticker.get('ask', 0) or 0),
                'timestamp': int(ticker['timestamp'] or time.time() * 1000)
            }
    except Exception as e:
        print(f"Error fetching {symbol} from {exchange.id}: {str(e)}")
    return None

def calculate_volatility(exchange, symbol, timeframe='1m', limit=60):
    """Calculate price volatility over the last hour."""
    if exchange is None or symbol is None:
        return 0.0
        
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if ohlcv and len(ohlcv) > 0:
            prices = [float(candle[4]) for candle in ohlcv]  # Close prices
            return pd.Series(prices).pct_change().std() * 100
    except Exception as e:
        print(f"Error calculating volatility for {symbol}: {str(e)}")
    return 0.0

def get_exchange_prices(coins):
    """Get current prices and metrics for selected coins from both exchanges."""
    binance, kraken = initialize_exchanges()
    if binance is None or kraken is None:
        print("Failed to initialize exchanges. Please check your internet connection.")
        return pd.DataFrame()
    
    data = []
    for coin in coins:
        try:
            binance_symbol = get_ticker_symbol(coin, 'binance')
            kraken_symbol = get_ticker_symbol(coin, 'kraken')
            
            if not kraken_symbol:
                print(f"Skipping {coin} - not supported on Kraken")
                continue
            
            # Fetch prices and data from both exchanges
            binance_data = fetch_price(binance, binance_symbol)
            kraken_data = fetch_price(kraken, kraken_symbol)
            
            # Skip if we couldn't get data from either exchange
            if not binance_data or not kraken_data:
                print(f"Skipping {coin} due to missing data")
                continue
            
            # Calculate volatility
            binance_vol = calculate_volatility(binance, binance_symbol) or 0.0
            kraken_vol = calculate_volatility(kraken, kraken_symbol) or 0.0
            
            # Convert Kraken USD price to USDT for comparison (assuming 1:1 ratio)
            kraken_price_usdt = kraken_data['price']
            
            # Calculate spread
            spread = abs(binance_data['price'] - kraken_price_usdt) / min(binance_data['price'], kraken_price_usdt) * 100
            
            data.append({
                'coin': coin,
                'binance_price': binance_data['price'],
                'kraken_price': kraken_price_usdt,
                'spread_percent': float(spread),
                'binance_volume': float(binance_data['volume']),
                'kraken_volume': float(kraken_data['volume']),
                'volume_diff': abs(float(binance_data['volume']) - float(kraken_data['volume'])),
                'volatility': max(binance_vol, kraken_vol),
                'timestamp': datetime.fromtimestamp(max(binance_data['timestamp'], kraken_data['timestamp']) / 1000)
            })
            
            # Add delay to respect rate limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing {coin}: {str(e)}")
            continue
    
    return pd.DataFrame(data) if data else pd.DataFrame(columns=[
        'coin', 'binance_price', 'kraken_price', 'spread_percent',
        'binance_volume', 'kraken_volume', 'volume_diff', 'volatility', 'timestamp'
    ]) 