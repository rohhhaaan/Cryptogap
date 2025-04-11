import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go
from exchanges import get_exchange_prices
from arbitrage import calculate_arbitrage_opportunities
from ml_model.predict import get_trade_confidence
from prompts.prompt_engine import generate_analysis
from utils.fees import calculate_net_profit

# Page config
st.set_page_config(
    page_title="CryptoGap - Crypto Arbitrage Detector",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("🔄 CryptoGap")
st.markdown("Real-time crypto arbitrage opportunities between Binance and Kraken")

# Sidebar
with st.sidebar:
    st.header("Settings")
    update_interval = st.slider("Update interval (seconds)", 30, 60, 30)
    min_spread = st.slider("Minimum spread (%)", 0.1, 5.0, 0.1, 0.1)  # Default to lower value
    coins = st.multiselect(
        "Select cryptocurrencies",
        ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT", "LINK", "MATIC", "AVAX", "UNI"],
        ["BTC", "ETH", "SOL", "XRP", "ADA"]
    )
    show_debug = st.checkbox("Show Debug Info", value=True)

# Main content
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Live Prices")
    prices_placeholder = st.empty()
    debug_placeholder = st.empty()

with col2:
    st.subheader("Arbitrage Opportunities")
    opportunities_placeholder = st.empty()

# Analysis section
st.subheader("Market Analysis")
analysis_placeholder = st.empty()

# Coin-specific analysis
st.subheader("Analyze Specific Coin")
selected_coin = st.selectbox("Select a coin for detailed analysis", coins)
if st.button("Generate Analysis"):
    with st.spinner("Generating analysis..."):
        # TODO: Implement coin-specific analysis
        pass

def format_opportunity(opp):
    """Format arbitrage opportunity for display."""
    return f"""
    ### 💰 {opp['coin']} Arbitrage Opportunity
    - **Action**: Buy on {opp['buy_exchange']} at ${opp['buy_price']:.2f}, Sell on {opp['sell_exchange']} at ${opp['sell_price']:.2f}
    - **Spread**: {opp['spread_percent']:.2f}%
    - **Net Profit per Unit**: ${opp['net_profit_usd']:.4f}
    - **Opportunity Score**: {opp['opportunity_score']:.1f}/100
    - **Volume Required**: {opp['min_volume_required']:.2f} units
    - **Volatility**: {opp['volatility']:.2f}%
    - **Last Updated**: {opp['timestamp'].strftime('%H:%M:%S')}
    """

def main():
    while True:
        try:
            # Fetch current prices
            prices_df = get_exchange_prices(coins)
            
            if not prices_df.empty:
                # Format price display
                display_df = prices_df[['coin', 'binance_price', 'kraken_price', 'spread_percent', 'volatility']].copy()
                display_df.columns = ['Coin', 'Binance ($)', 'Kraken ($)', 'Spread (%)', 'Volatility (%)']
                display_df = display_df.round(2)
                prices_placeholder.dataframe(display_df, hide_index=True)

                # Show debug information
                if show_debug:
                    debug_info = "### Debug Information\n"
                    for _, row in prices_df.iterrows():
                        binance_price = float(row['binance_price'])
                        kraken_price = float(row['kraken_price'])
                        
                        # Calculate spreads in both directions
                        binance_to_kraken = ((kraken_price - binance_price) / binance_price) * 100
                        kraken_to_binance = ((binance_price - kraken_price) / kraken_price) * 100
                        
                        # Calculate net profit for both directions
                        b_to_k_profit = calculate_net_profit(
                            binance_price, 
                            kraken_price,
                            buy_exchange='Binance',
                            sell_exchange='Kraken'
                        )
                        
                        k_to_b_profit = calculate_net_profit(
                            kraken_price,
                            binance_price,
                            buy_exchange='Kraken',
                            sell_exchange='Binance'
                        )
                        
                        debug_info += f"""
                        **{row['coin']}**:
                        - Binance→Kraken Spread: {binance_to_kraken:.3f}%
                        - Kraken→Binance Spread: {kraken_to_binance:.3f}%
                        - Min Required: {min_spread:.1f}%
                        - Binance→Kraken Profit: ${b_to_k_profit:.4f}
                        - Kraken→Binance Profit: ${k_to_b_profit:.4f}
                        ---
                        """
                    debug_placeholder.markdown(debug_info)

                # Calculate arbitrage opportunities
                opportunities = calculate_arbitrage_opportunities(prices_df, min_spread)
                
                if not opportunities.empty:
                    opportunities_text = "## Found Arbitrage Opportunities!\n\n"
                    for _, opp in opportunities.iterrows():
                        opportunities_text += format_opportunity(opp) + "\n---\n"
                    opportunities_placeholder.markdown(opportunities_text)
                    
                    # Generate analysis for the best opportunity
                    best_opp = opportunities.iloc[0]
                    confidence = get_trade_confidence(
                        best_opp['spread_percent'],
                        best_opp['volatility'],
                        best_opp['volume_diff']
                    )
                    analysis = generate_analysis(best_opp, confidence)
                    analysis_placeholder.markdown(f"### AI Analysis\n{analysis}")
                else:
                    opportunities_placeholder.info("Monitoring for arbitrage opportunities... None found yet that meet the criteria.")
            else:
                st.error("Error fetching price data. Please check your internet connection.")

            time.sleep(update_interval)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main() 