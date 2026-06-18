"""Display and formatting utilities for CLI output."""

from colorama import Fore, Back, Style, init
from tabulate import tabulate
from src.signal_generator import Signal
from typing import Dict
import json

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class Display:
    """Handles formatted display of analysis results."""
    
    COLORS = {
        Signal.STRONG_BUY: Fore.GREEN,
        Signal.BUY: Fore.LIGHTGREEN,
        Signal.HOLD: Fore.YELLOW,
        Signal.SELL: Fore.LIGHTRED,
        Signal.STRONG_SELL: Fore.RED
    }
    
    @staticmethod
    def print_header(title: str, width: int = 60):
        """Print a formatted header."""
        print("\n" + "═" * width)
        print(f"  {title.center(width - 4)}")
        print("═" * width)
    
    @staticmethod
    def print_subheader(title: str, width: int = 60):
        """Print a formatted subheader."""
        print(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
        print("─" * len(title))
    
    @staticmethod
    def print_price_info(crypto: str, price_data: Dict):
        """Display current price information."""
        Display.print_subheader("PRICE & MARKET DATA")
        
        rows = [
            ["Current Price", f"${price_data['price']:,.2f}"],
            ["Market Cap", f"${price_data['market_cap']:,.0f}" if price_data['market_cap'] else "N/A"],
            ["24h Volume", f"${price_data['volume_24h']:,.0f}" if price_data['volume_24h'] else "N/A"],
            ["24h Change", f"{price_data['change_24h']:+.2f}%"],
            ["All-Time High", f"${price_data['ath']:,.2f}" if price_data['ath'] else "N/A"],
            ["All-Time Low", f"${price_data['atl']:,.2f}" if price_data['atl'] else "N/A"],
        ]
        
        print(tabulate(rows, tablefmt="plain"))
    
    @staticmethod
    def print_technical_indicators(indicators: Dict):
        """Display technical indicators."""
        Display.print_subheader("TECHNICAL INDICATORS")
        
        rows = []
        
        rsi = indicators.get('rsi')
        if rsi:
            rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
            rows.append([f"RSI (14)", f"{rsi:.2f}", rsi_status])
        
        macd = indicators.get('macd')
        signal = indicators.get('macd_signal')
        if macd and signal:
            macd_trend = "Bullish" if macd > signal else "Bearish"
            rows.append([f"MACD", f"{macd:.4f}", macd_trend])
        
        sma_short = indicators.get('sma_short')
        sma_long = indicators.get('sma_long')
        if sma_short and sma_long:
            rows.append([f"SMA 20", f"${sma_short:,.2f}", f"Price vs SMA: {indicators.get('price_vs_sma_short')}"])
            rows.append([f"SMA 50", f"${sma_long:,.2f}", f"Price vs SMA: {indicators.get('price_vs_sma_long')}"])
        
        bb_upper = indicators.get('bb_upper')
        bb_lower = indicators.get('bb_lower')
        if bb_upper and bb_lower:
            rows.append([f"Support", f"${indicators.get('support'):,.2f}", "Floor"])
            rows.append([f"Resistance", f"${indicators.get('resistance'):,.2f}", "Ceiling"])
        
        volatility = indicators.get('volatility')
        if volatility:
            rows.append([f"Volatility (20d)", f"{volatility*100:.2f}%", "Risk Metric"])
        
        print(tabulate(rows, headers=["Indicator", "Value", "Status"], tablefmt="grid"))
    
    @staticmethod
    def print_trading_signal(signal, confidence: float, details: Dict):
        """Display trading signal and recommendation."""
        Display.print_subheader("TRADING SIGNAL & RECOMMENDATION")
        
        color = Display.COLORS.get(signal, Fore.WHITE)
        confidence_pct = confidence * 100
        
        print(f"\n{color}{Back.BLACK}{signal.value}{Style.RESET_ALL}")
        print(f"Confidence: {confidence_pct:.1f}%\n")
        
        rows = [
            ["Entry Price", f"${details['entry_price']:,.2f}"],
            ["Target Price", f"${details['target_price']:,.2f}"],
            ["Stop Loss", f"${details['stop_loss']:,.2f}"],
            ["Risk/Reward", f"{details['risk_reward_ratio']:.2f}x"],
        ]
        print(tabulate(rows, tablefmt="plain"))
        
        Display.print_subheader("SIGNAL COMPOSITION")
        scores = details.get('scores', {})
        score_rows = [
            ["RSI", f"{scores.get('rsi', 0)*100:.1f}%"],
            ["MACD", f"{scores.get('macd', 0)*100:.1f}%"],
            ["Moving Averages", f"{scores.get('moving_averages', 0)*100:.1f}%"],
            ["Bollinger Bands", f"{scores.get('bollinger', 0)*100:.1f}%"],
            ["Volatility", f"{scores.get('volatility', 0)*100:.1f}%"],
        ]
        print(tabulate(score_rows, tablefmt="plain"))
    
    @staticmethod
    def print_top_cryptos(cryptos: list, limit: int = 10):
        """Display top cryptocurrencies."""
        Display.print_header(f"TOP {min(limit, len(cryptos))} CRYPTOCURRENCIES")
        
        rows = []
        for i, crypto in enumerate(cryptos[:limit], 1):
            change_color = Fore.GREEN if crypto['price_change_percentage_24h_in_currency'] >= 0 else Fore.RED
            rows.append([
                i,
                crypto['symbol'].upper(),
                f"${crypto['current_price']:,.2f}",
                f"{change_color}{crypto['price_change_percentage_24h_in_currency']:+.2f}%{Style.RESET_ALL}",
                f"${crypto['market_cap']:,.0f}" if crypto['market_cap'] else "N/A",
            ])
        
        print(tabulate(rows, headers=["#", "Symbol", "Price", "24h Change", "Market Cap"], tablefmt="grid"))
    
    @staticmethod
    def print_error(message: str):
        """Print error message."""
        print(f"{Fore.RED}❌ Error: {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_success(message: str):
        """Print success message."""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_info(message: str):
        """Print info message."""
        print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
