import pandas as pd
import numpy as np
from utils.fees import calculate_net_profit, get_exchange_fees

def calculate_arbitrage_opportunities(prices_df, min_spread=0.1):
    """
    Calculate arbitrage opportunities from price data.
    
    Args:
        prices_df (pd.DataFrame): DataFrame with current prices and metrics
        min_spread (float): Minimum spread percentage to consider
        
    Returns:
        pd.DataFrame: Filtered opportunities that meet criteria
    """
    opportunities = []
    fees = get_exchange_fees()
    
    for _, row in prices_df.iterrows():
        # Skip if we don't have valid prices
        if pd.isna(row['binance_price']) or pd.isna(row['kraken_price']):
            continue
            
        # Calculate the price difference and direction
        binance_price = float(row['binance_price'])
        kraken_price = float(row['kraken_price'])
        
        # Calculate spreads in both directions
        binance_to_kraken_spread = ((kraken_price - binance_price) / binance_price) * 100
        kraken_to_binance_spread = ((binance_price - kraken_price) / kraken_price) * 100
        
        # Check both directions for opportunities
        opportunities_to_check = [
            {
                'spread': binance_to_kraken_spread,
                'buy_exchange': 'Binance',
                'sell_exchange': 'Kraken',
                'buy_price': binance_price,
                'sell_price': kraken_price
            },
            {
                'spread': kraken_to_binance_spread,
                'buy_exchange': 'Kraken',
                'sell_exchange': 'Binance',
                'buy_price': kraken_price,
                'sell_price': binance_price
            }
        ]
        
        for opp in opportunities_to_check:
            # Skip if spread is too low
            if opp['spread'] < min_spread:
                continue
                
            # Calculate net profit after fees for 1 unit
            net_profit = calculate_net_profit(
                opp['buy_price'], 
                opp['sell_price'],
                trade_amount=1.0,
                buy_exchange=opp['buy_exchange'],
                sell_exchange=opp['sell_exchange']
            )
            
            # For demo purposes, consider even tiny profits
            if net_profit > 0.00001:  # Just needs to be positive
                # Calculate minimum volume required for profitable trade
                min_volume_for_profit = abs(1.0 / net_profit) if net_profit > 0 else float('inf')
                
                # Calculate opportunity score (0-100)
                volume_score = min(100, row['volume_diff'] / 10000)  # Scale volume difference
                spread_score = min(100, opp['spread'] * 20)  # Scale spread (5% spread = 100)
                volatility_penalty = min(50, row['volatility'] * 10)  # Higher volatility = higher penalty
                
                opportunity_score = (
                    (spread_score * 0.4) +  # 40% weight on spread
                    (volume_score * 0.4) +  # 40% weight on volume
                    (100 - volatility_penalty) * 0.2  # 20% weight on inverse of volatility
                )
                
                # Include any profitable opportunity for demo purposes
                opportunities.append({
                    'coin': row['coin'],
                    'buy_exchange': opp['buy_exchange'],
                    'sell_exchange': opp['sell_exchange'],
                    'buy_price': opp['buy_price'],
                    'sell_price': opp['sell_price'],
                    'spread_percent': opp['spread'],
                    'net_profit_usd': net_profit,
                    'volume_diff': row['volume_diff'],
                    'volatility': row['volatility'],
                    'min_volume_required': min_volume_for_profit,
                    'opportunity_score': opportunity_score,
                    'timestamp': row['timestamp']
                })
    
    if not opportunities:
        return pd.DataFrame()
        
    # Convert to DataFrame and sort by opportunity score
    opportunities_df = pd.DataFrame(opportunities)
    return opportunities_df.sort_values('opportunity_score', ascending=False) 