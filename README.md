# CryptoGap - Crypto Arbitrage Detector

CryptoGap is a real-time cryptocurrency arbitrage detection application that identifies profitable trading opportunities between Binance and Kraken exchanges. It combines live market data with machine learning predictions and AI-powered analysis to help traders make informed decisions.

## Features

- Real-time price monitoring for multiple cryptocurrencies
- Automated arbitrage opportunity detection
- Machine learning-based trade confidence scoring
- AI-powered market analysis and explanations
- Clean, intuitive Streamlit interface
- Support for multiple trading pairs

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cryptogap
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_openai_api_key
```

## Usage

1. Train the ML model (first time only):
```bash
python ml_model/train_model.py
```

2. Run the Streamlit app:
```bash
streamlit run main.py
```

3. Access the web interface at `http://localhost:8501`

## Components

- `main.py`: Streamlit web application
- `exchanges.py`: Cryptocurrency exchange integration
- `arbitrage.py`: Arbitrage opportunity detection
- `ml_model/`: Machine learning model for trade confidence prediction
- `prompts/`: LLM integration for market analysis
- `utils/`: Utility functions and helpers

## Dependencies

- Python 3.8+
- Streamlit
- ccxt
- pandas
- numpy
- scikit-learn
- xgboost
- openai
- python-dotenv

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 