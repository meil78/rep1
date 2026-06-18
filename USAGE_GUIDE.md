# Usage Guide - Crypto Trading Agent

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Basic Analysis

Analyze Bitcoin for trading signals:
```bash
python main.py analyze bitcoin
```

This will show you:
- Current price and market data
- Technical indicators (RSI, MACD, Moving Averages, etc.)
- Trading signal (BUY, SELL, HOLD, etc.)
- Entry price, target, and stop loss
- Confidence level

### 3. Get Trading Signals Only

```bash
python main.py signals ethereum
```

Shows signals across different timeframes quickly.

### 4. Explore Market

```bash
# Top 10 cryptocurrencies
python main.py top

# Show top 20
python main.py top --limit 20

# Show trending cryptos
python main.py trending
```

## Portfolio Management

### Add a Position

```bash
python main.py portfolio add bitcoin 0.5 45000
```

This adds:
- 0.5 BTC
- Entry price: $45,000

### View Portfolio

```bash
python main.py portfolio show
```

Shows:
- Current holdings
- Entry vs current prices
- Unrealized P&L
- Portfolio value

### Remove Position

```bash
python main.py portfolio remove bitcoin
```

## Understanding the Signals

### Signal Types

| Signal | Meaning | Action |
|--------|---------|--------|
| **STRONG BUY** | Highly bullish, multiple indicators aligned | Consider entering position |
| **BUY** | Bullish setup with good risk/reward | Good entry opportunity |
| **HOLD** | Mixed signals, unclear direction | Wait for confirmation |
| **SELL** | Bearish indicators present | Consider exiting |
| **STRONG SELL** | Highly bearish, multiple warnings | Close positions or avoid |

### Confidence Level

- **90-100%**: Very high conviction, strong alignment
- **70-89%**: Good confidence, most indicators agree
- **50-69%**: Moderate, mixed signals but direction clear
- **30-49%**: Weak, conflicting signals
- **Below 30%**: Very uncertain, avoid trading

## Understanding the Indicators

### RSI (Relative Strength Index)
- **Below 30**: Oversold (potential buy)
- **30-70**: Neutral
- **Above 70**: Overbought (potential sell)

### MACD (Moving Average Convergence Divergence)
- **Green histogram**: Bullish momentum
- **Red histogram**: Bearish momentum
- **Crossovers**: Potential trend changes

### Moving Averages
- **Price above SMA 20 & 50**: Uptrend
- **Price below SMA 20 & 50**: Downtrend
- **Golden Cross** (SMA 20 > SMA 50): Bullish signal
- **Death Cross** (SMA 20 < SMA 50): Bearish signal

## Examples

### Day Trading Setup

```bash
# Analyze top candidates
python main.py analyze bitcoin --days 1
python main.py analyze ethereum --days 1

# Get quick signals
python main.py signals cardano
```

### Swing Trading Setup

```bash
# Analyze 30-day trends
python main.py analyze bitcoin --days 30
python main.py analyze ethereum --days 30

# Add to portfolio
python main.py portfolio add ethereum 2.5 3000

# Check portfolio
python main.py portfolio show
```

## Disclaimer

⚠️ This tool provides analysis for informational purposes only. It is NOT financial advice. Always:
- Do your own research
- Consult with financial advisors
- Never risk more than you can afford to lose
- Use proper risk management
- Understand the risks of cryptocurrency trading
