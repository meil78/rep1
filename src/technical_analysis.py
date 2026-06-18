"""Technical analysis module for calculating trading indicators."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import json

class TechnicalAnalyzer:
    """Calculates technical indicators for cryptocurrency analysis."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize analyzer with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.ti_config = self.config.get("technical_indicators", {})
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: Series of prices
            period: RSI period (default: 14)
        
        Returns:
            Series of RSI values
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, 
                      slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: Series of prices
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)
        
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_moving_averages(self, prices: pd.Series, 
                                 short: int = 20, long: int = 50) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Simple Moving Averages (SMA).
        
        Args:
            prices: Series of prices
            short: Short-term SMA period (default: 20)
            long: Long-term SMA period (default: 50)
        
        Returns:
            Tuple of (short MA, long MA)
        """
        sma_short = prices.rolling(window=short).mean()
        sma_long = prices.rolling(window=long).mean()
        
        return sma_short, sma_long
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, 
                                 std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: Series of prices
            period: Moving average period (default: 20)
            std_dev: Standard deviation multiplier (default: 2)
        
        Returns:
            Tuple of (middle band, upper band, lower band)
        """
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return sma, upper_band, lower_band
    
    def calculate_volatility(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate volatility (standard deviation of returns).
        
        Args:
            prices: Series of prices
            period: Calculation period (default: 20)
        
        Returns:
            Series of volatility values
        """
        returns = prices.pct_change()
        volatility = returns.rolling(window=period).std()
        
        return volatility
    
    def calculate_support_resistance(self, prices: pd.Series, 
                                    period: int = 20) -> Tuple[float, float]:
        """
        Calculate support and resistance levels.
        
        Args:
            prices: Series of prices
            period: Lookback period (default: 20)
        
        Returns:
            Tuple of (support, resistance)
        """
        support = prices.tail(period).min()
        resistance = prices.tail(period).max()
        
        return float(support), float(resistance)
    
    def analyze_price_action(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Perform comprehensive technical analysis on price data.
        
        Args:
            df: DataFrame with 'price' column and datetime index
        
        Returns:
            Dictionary with all technical indicators
        """
        prices = df['price']
        
        # Calculate indicators
        rsi = self.calculate_rsi(prices, self.ti_config.get("rsi_period", 14))
        macd, signal, histogram = self.calculate_macd(
            prices,
            self.ti_config.get("macd_fast", 12),
            self.ti_config.get("macd_slow", 26),
            self.ti_config.get("macd_signal", 9)
        )
        sma_short, sma_long = self.calculate_moving_averages(
            prices,
            self.ti_config.get("ma_short", 20),
            self.ti_config.get("ma_long", 50)
        )
        middle, upper, lower = self.calculate_bollinger_bands(
            prices,
            self.ti_config.get("bollinger_period", 20),
            self.ti_config.get("bollinger_std", 2)
        )
        volatility = self.calculate_volatility(prices)
        support, resistance = self.calculate_support_resistance(prices)
        
        # Get latest values
        current_price = prices.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        current_histogram = histogram.iloc[-1]
        current_sma_short = sma_short.iloc[-1]
        current_sma_long = sma_long.iloc[-1]
        current_volatility = volatility.iloc[-1]
        
        return {
            "price": float(current_price),
            "rsi": float(current_rsi) if not pd.isna(current_rsi) else None,
            "macd": float(current_macd) if not pd.isna(current_macd) else None,
            "macd_signal": float(current_signal) if not pd.isna(current_signal) else None,
            "macd_histogram": float(current_histogram) if not pd.isna(current_histogram) else None,
            "sma_short": float(current_sma_short) if not pd.isna(current_sma_short) else None,
            "sma_long": float(current_sma_long) if not pd.isna(current_sma_long) else None,
            "bb_upper": float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else None,
            "bb_middle": float(middle.iloc[-1]) if not pd.isna(middle.iloc[-1]) else None,
            "bb_lower": float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else None,
            "volatility": float(current_volatility) if not pd.isna(current_volatility) else None,
            "support": support,
            "resistance": resistance,
            "price_vs_sma_short": "above" if current_price > current_sma_short else "below",
            "price_vs_sma_long": "above" if current_price > current_sma_long else "below",
            "macd_trend": "bullish" if current_histogram > 0 else "bearish"
        }
