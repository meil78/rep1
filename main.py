#!/usr/bin/env python3
"""Main CLI interface for Crypto Trading Analysis Agent."""

import click
import sys
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

from src.data_provider import DataProvider
from src.technical_analysis import TechnicalAnalyzer
from src.signal_generator import SignalGenerator
from src.display import Display

class CryptoAgent:
    """Main agent for crypto trading analysis."""
    
    def __init__(self):
        """Initialize the agent."""
        self.data_provider = DataProvider()
        self.technical_analyzer = TechnicalAnalyzer()
        self.signal_generator = SignalGenerator()
        self.portfolio_file = "portfolio.json"
        self.portfolio = self._load_portfolio()
    
    def _load_portfolio(self) -> dict:
        """Load portfolio from file."""
        if Path(self.portfolio_file).exists():
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_portfolio(self):
        """Save portfolio to file."""
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.portfolio, f, indent=2)
    
    def analyze_crypto(self, crypto: str, days: int = 30) -> bool:
        """Perform comprehensive analysis on a cryptocurrency."""
        Display.print_header(f"{crypto.upper()} ANALYSIS")
        
        Display.print_info("Fetching price data...")
        price_data = self.data_provider.get_current_price(crypto)
        if not price_data:
            Display.print_error(f"Could not fetch data for {crypto}")
            return False
        
        Display.print_price_info(crypto, price_data)
        
        Display.print_info("Calculating technical indicators...")
        df = self.data_provider.get_market_chart_data(crypto, days)
        if df is None or len(df) < 50:
            Display.print_error("Not enough historical data for analysis")
            return False
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        indicators = self.technical_analyzer.analyze_price_action(df)
        Display.print_technical_indicators(indicators)
        
        signal, confidence, details = self.signal_generator.generate_signal(indicators)
        Display.print_trading_signal(signal, confidence, details)
        
        print("\n" + "─" * 60)
        return True
    
    def get_trading_signals(self, crypto: str) -> bool:
        """Get trading signals for a cryptocurrency."""
        Display.print_header(f"TRADING SIGNALS - {crypto.upper()}")
        
        price_data = self.data_provider.get_current_price(crypto)
        if not price_data:
            Display.print_error(f"Could not fetch data for {crypto}")
            return False
        
        df = self.data_provider.get_market_chart_data(crypto, 30)
        if df is None or len(df) < 50:
            Display.print_error("Not enough historical data")
            return False
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        for days in [1, 7, 30]:
            print(f"\n📊 {days}-Day Analysis:")
            df_period = df.tail(days * 24)
            
            if len(df_period) < 14:
                continue
            
            indicators = self.technical_analyzer.analyze_price_action(df_period)
            signal, confidence, _ = self.signal_generator.generate_signal(indicators)
            
            print(f"  Signal: {signal.value} (Confidence: {confidence*100:.1f}%)")
        
        return True
    
    def show_top_cryptos(self, limit: int = 10) -> bool:
        """Show top cryptocurrencies by market cap."""
        Display.print_info("Fetching top cryptocurrencies...")
        cryptos = self.data_provider.get_top_cryptos(limit)
        
        if not cryptos:
            Display.print_error("Could not fetch top cryptocurrencies")
            return False
        
        Display.print_top_cryptos(cryptos, limit)
        return True
    
    def show_trending(self) -> bool:
        """Show trending cryptocurrencies."""
        Display.print_info("Fetching trending cryptocurrencies...")
        trending = self.data_provider.get_trending_cryptos()
        
        if not trending:
            Display.print_error("Could not fetch trending data")
            return False
        
        Display.print_header("TRENDING CRYPTOCURRENCIES")
        rows = []
        for i, coin in enumerate(trending[:10], 1):
            rows.append([
                i,
                coin['item']['symbol'].upper(),
                coin['item']['name'],
                f"#{coin['item']['market_cap_rank']}" if coin['item']['market_cap_rank'] else "N/A"
            ])
        
        from tabulate import tabulate
        print(tabulate(rows, headers=["#", "Symbol", "Name", "Market Cap Rank"], tablefmt="grid"))
        return True
    
    def add_portfolio_position(self, symbol: str, amount: float, entry_price: float):
        """Add a position to the portfolio."""
        symbol = symbol.lower()
        self.portfolio[symbol] = {
            "amount": amount,
            "entry_price": entry_price,
            "current_price": entry_price,
            "added_date": datetime.now().isoformat()
        }
        self._save_portfolio()
        Display.print_success(f"Added {amount} {symbol} @ ${entry_price:,.2f}")
    
    def remove_portfolio_position(self, symbol: str):
        """Remove a position from the portfolio."""
        symbol = symbol.lower()
        if symbol in self.portfolio:
            del self.portfolio[symbol]
            self._save_portfolio()
            Display.print_success(f"Removed {symbol} from portfolio")
        else:
            Display.print_error(f"{symbol} not in portfolio")
    
    def update_portfolio_prices(self):
        """Update current prices for all portfolio positions."""
        for symbol in self.portfolio:
            price_data = self.data_provider.get_current_price(symbol)
            if price_data:
                self.portfolio[symbol]['current_price'] = price_data['price']
        self._save_portfolio()
    
    def show_portfolio(self):
        """Display portfolio analysis."""
        if not self.portfolio:
            Display.print_info("Portfolio is empty. Use 'portfolio add' command to add positions.")
            return
        
        self.update_portfolio_prices()
        Display.print_header("PORTFOLIO SUMMARY")
        
        rows = []
        total_value = 0
        
        for symbol, position in self.portfolio.items():
            amount = position.get('amount', 0)
            entry_price = position.get('entry_price', 0)
            current_price = position.get('current_price', 0)
            value = amount * current_price
            pnl = (current_price - entry_price) * amount
            pnl_pct = (pnl / (amount * entry_price) * 100) if entry_price else 0
            
            total_value += value
            from colorama import Fore, Style
            color = Fore.GREEN if pnl >= 0 else Fore.RED
            
            rows.append([
                symbol.upper(),
                f"{amount:.4f}",
                f"${current_price:,.2f}",
                f"${value:,.2f}",
                f"{color}{pnl:+,.2f} ({pnl_pct:+.1f}%){Style.RESET_ALL}"
            ])
        
        if rows:
            from tabulate import tabulate
            print(tabulate(rows, headers=["Asset", "Amount", "Price", "Value", "P&L"], tablefmt="grid"))
            print(f"\nTotal Portfolio Value: ${total_value:,.2f}")

# CLI Commands
@click.group()
def cli():
    """Crypto Trading Analysis Agent - Your trading assistant."""
    pass

@cli.command()
@click.argument('crypto')
@click.option('--days', default=30, help='Days of history to analyze (default: 30)')
def analyze(crypto, days):
    """Analyze a cryptocurrency in detail."""
    agent = CryptoAgent()
    agent.analyze_crypto(crypto, days)

@cli.command()
@click.argument('crypto')
def signals(crypto):
    """Get trading signals for a cryptocurrency."""
    agent = CryptoAgent()
    agent.get_trading_signals(crypto)

@cli.command()
@click.option('--limit', default=10, help='Number of cryptos to show (default: 10)')
def top(limit):
    """Show top cryptocurrencies by market cap."""
    agent = CryptoAgent()
    agent.show_top_cryptos(limit)

@cli.command()
def trending():
    """Show trending cryptocurrencies."""
    agent = CryptoAgent()
    agent.show_trending()

@click.group()
def portfolio():
    """Manage your cryptocurrency portfolio."""
    pass

@portfolio.command()
@click.argument('symbol')
@click.argument('amount', type=float)
@click.argument('entry_price', type=float)
def add(symbol, amount, entry_price):
    """Add a position to your portfolio.
    
    Example: portfolio add bitcoin 0.5 45000
    """
    agent = CryptoAgent()
    agent.add_portfolio_position(symbol, amount, entry_price)

@portfolio.command()
@click.argument('symbol')
def remove(symbol):
    """Remove a position from your portfolio."""
    agent = CryptoAgent()
    agent.remove_portfolio_position(symbol)

@portfolio.command(name='show')
def show_portfolio_cmd():
    """Show your portfolio."""
    agent = CryptoAgent()
    agent.show_portfolio()

cli.add_command(portfolio)

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        Display.print_error(str(e))
        sys.exit(1)
