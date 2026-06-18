# Crypto Trading Analysis Agent

An intelligent agent that analyzes cryptocurrency markets and provides actionable trading signals and insights.

## Features

- **Real-time Price Analysis**: Fetch current prices and market data
- **Technical Indicators**: Calculate RSI, MACD, Moving Averages
- **Trading Signals**: Generate buy/sell signals with confidence levels
- **Market Sentiment**: Analyze market trends and volatility
- **Portfolio Analysis**: Evaluate your holdings and diversification
- **Risk Assessment**: Quantify risk metrics and exposure

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (CoinGecko, optional for extended data)
```

### Basic Usage

```bash
# Run interactive CLI
python main.py --help

# Analyze specific cryptocurrency
python main.py analyze bitcoin

# Get trading signals
python main.py signals ethereum

# Analyze portfolio
python main.py portfolio show
```

## Commands

### Analysis Commands

```
analyze <crypto>              - Analyze a cryptocurrency
signals <crypto>             - Get trading signals for a crypto
top [--limit N]              - Show top N cryptos by market cap
trending                     - Show trending cryptocurrencies
```

### Portfolio Commands

```
portfolio add <symbol> <amount> <price> - Add position to portfolio
portfolio remove <symbol>              - Remove position from portfolio
portfolio show                         - View portfolio analysis
```

## Signal Types

- **STRONG BUY**: Multiple indicators aligned, high confidence (>75%)
- **BUY**: Positive signals with good entry point (55-75%)
- **HOLD**: Mixed signals, wait for clarity (35-55%)
- **SELL**: Negative indicators, consider exit (15-35%)
- **STRONG SELL**: Multiple bearish signals, high conviction (<15%)

## Configuration

Edit `config.json` to customize:

```json
{
  "technical_indicators": {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "ma_short": 20,
    "ma_long": 50
  }
}
```

## Example Output

```
════════════════════════════════════════════════════════════════
  BITCOIN ANALYSIS
════════════════════════════════════════════════════════════════

Current Price: $42,500 USD
24h Change: +2.3%
Volume: $28.5B

TECHNICAL INDICATORS
├─ RSI (14): 65 (Neutral)
├─ MACD: BULLISH
├─ MA 20: $42,100 (above current price)
└─ MA 50: $41,800 (bullish alignment)

TRADING SIGNAL: BUY
Confidence: 72%
Entry: $42,300 - $42,600
Target: $44,500
Stop Loss: $41,200
════════════════════════════════════════════════════════════════
```

## Data Sources

- **Prices**: CoinGecko API (free, no key required)
- **On-chain Data**: Ready for integration

## Disclaimer

This agent provides analysis and signals for informational purposes only. It is not financial advice. Always do your own research and consult with a financial advisor before making trading decisions.

## License

MIT License - See LICENSE file
