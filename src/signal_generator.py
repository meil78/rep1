"""Trading signal generation module."""

from typing import Dict, Tuple
import json
from enum import Enum

class Signal(Enum):
    """Trading signal types."""
    STRONG_BUY = "STRONG BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG SELL"

class SignalGenerator:
    """Generates trading signals based on technical analysis."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize signal generator with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.signal_config = self.config.get("signal_generation", {})
        self.risk_config = self.config.get("risk_management", {})
    
    def generate_signal(self, indicators: Dict) -> Tuple[Signal, float, Dict]:
        """
        Generate trading signal from technical indicators.
        
        Args:
            indicators: Dictionary of technical indicators from TechnicalAnalyzer
        
        Returns:
            Tuple of (Signal, Confidence, Details)
        """
        scores = {
            "rsi": self._score_rsi(indicators.get("rsi")),
            "macd": self._score_macd(indicators),
            "moving_averages": self._score_moving_averages(indicators),
            "bollinger": self._score_bollinger_bands(indicators),
            "volatility": self._score_volatility(indicators.get("volatility"))
        }
        
        # Calculate weighted confidence
        weights = {
            "rsi": self.signal_config.get("confidence_weight_rsi", 0.25),
            "macd": self.signal_config.get("confidence_weight_macd", 0.35),
            "moving_averages": self.signal_config.get("confidence_weight_ma", 0.25),
            "bollinger": 0.1,
            "volatility": self.signal_config.get("confidence_weight_volatility", 0.15)
        }
        
        confidence = sum(scores[k] * weights[k] for k in scores.keys())
        confidence = max(0, min(1, confidence))  # Clamp 0-1
        
        # Determine signal
        signal = self._confidence_to_signal(confidence)
        
        # Calculate entry, target, and stop loss
        entry_price = indicators.get("price")
        target, stop_loss = self._calculate_levels(
            entry_price,
            signal,
            indicators.get("support"),
            indicators.get("resistance")
        )
        
        details = {
            "scores": scores,
            "rsi_value": indicators.get("rsi"),
            "macd_histogram": indicators.get("macd_histogram"),
            "price_vs_sma_short": indicators.get("price_vs_sma_short"),
            "price_vs_sma_long": indicators.get("price_vs_sma_long"),
            "volatility": indicators.get("volatility"),
            "entry_price": entry_price,
            "target_price": target,
            "stop_loss": stop_loss,
            "risk_reward_ratio": (target - entry_price) / (entry_price - stop_loss) if stop_loss != entry_price else 0,
            "support": indicators.get("support"),
            "resistance": indicators.get("resistance")
        }
        
        return signal, confidence, details
    
    def _score_rsi(self, rsi_value: float) -> float:
        """Score RSI indicator (0=bearish, 1=bullish)."""
        if rsi_value is None:
            return 0.5
        
        if rsi_value < 30:
            return 0.8
        elif rsi_value < 40:
            return 0.65
        elif rsi_value < 50:
            return 0.55
        elif rsi_value < 60:
            return 0.45
        elif rsi_value < 70:
            return 0.35
        else:
            return 0.2
    
    def _score_macd(self, indicators: Dict) -> float:
        """Score MACD indicator."""
        histogram = indicators.get("macd_histogram")
        macd = indicators.get("macd")
        signal = indicators.get("macd_signal")
        
        if histogram is None:
            return 0.5
        
        if macd is None or signal is None:
            return 0.75 if histogram > 0 else 0.25
        
        if macd > signal and histogram > 0:
            return 0.75
        elif macd > signal and histogram <= 0:
            return 0.55
        elif macd < signal and histogram < 0:
            return 0.25
        else:
            return 0.45
    
    def _score_moving_averages(self, indicators: Dict) -> float:
        """Score moving average crossover."""
        price = indicators.get("price")
        sma_short = indicators.get("sma_short")
        sma_long = indicators.get("sma_long")
        
        if price is None or sma_short is None or sma_long is None:
            return 0.5
        
        if price > sma_short > sma_long:
            return 0.85
        elif price > sma_short:
            return 0.65
        elif price < sma_short < sma_long:
            return 0.15
        elif price < sma_short:
            return 0.35
        
        return 0.5
    
    def _score_bollinger_bands(self, indicators: Dict) -> float:
        """Score Bollinger Bands position."""
        price = indicators.get("price")
        upper = indicators.get("bb_upper")
        lower = indicators.get("bb_lower")
        
        if price is None or upper is None or lower is None:
            return 0.5
        
        position = (price - lower) / (upper - lower) if upper != lower else 0.5
        return min(1, max(0, position))
    
    def _score_volatility(self, volatility: float) -> float:
        """Score volatility risk."""
        if volatility is None:
            return 0.5
        
        threshold = self.risk_config.get("volatility_threshold", 0.05)
        
        if volatility > threshold * 2:
            return 0.3
        elif volatility > threshold:
            return 0.5
        else:
            return 0.7
    
    def _confidence_to_signal(self, confidence: float) -> Signal:
        """Convert confidence score to trading signal."""
        strong_buy = self.signal_config.get("strong_buy_threshold", 0.75)
        buy = self.signal_config.get("buy_threshold", 0.55)
        sell = self.signal_config.get("sell_threshold", 0.35)
        strong_sell = self.signal_config.get("strong_sell_threshold", 0.15)
        
        if confidence >= strong_buy:
            return Signal.STRONG_BUY
        elif confidence >= buy:
            return Signal.BUY
        elif confidence > sell:
            return Signal.HOLD
        elif confidence >= strong_sell:
            return Signal.SELL
        else:
            return Signal.STRONG_SELL
    
    def _calculate_levels(self, entry: float, signal: Signal, 
                         support: float, resistance: float) -> Tuple[float, float]:
        """Calculate target and stop loss levels."""
        tp_percent = self.risk_config.get("take_profit_percent", 0.1)
        sl_percent = self.risk_config.get("stop_loss_percent", 0.05)
        
        if signal in [Signal.STRONG_BUY, Signal.BUY]:
            target = entry * (1 + tp_percent)
            if resistance > target:
                target = resistance * 0.95
            stop_loss = entry * (1 - sl_percent)
            if support < stop_loss:
                stop_loss = support * 1.01
        else:
            target = entry * (1 - tp_percent)
            if support < target:
                target = support * 1.05
            stop_loss = entry * (1 + sl_percent)
            if resistance > stop_loss:
                stop_loss = resistance * 0.99
        
        return target, stop_loss
