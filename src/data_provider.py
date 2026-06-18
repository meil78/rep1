"""Data provider module for fetching cryptocurrency data."""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

class DataProvider:
    """Handles data fetching from various sources."""
    
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.coingecko_key = os.getenv("COINGECKO_API_KEY", "")
        self.timeout = 10
        self.crypto_mapping = self._load_crypto_mapping()
    
    def _load_crypto_mapping(self) -> Dict[str, str]:
        """Load cryptocurrency name to ID mapping."""
        return {
            "bitcoin": "bitcoin",
            "btc": "bitcoin",
            "ethereum": "ethereum",
            "eth": "ethereum",
            "cardano": "cardano",
            "ada": "cardano",
            "solana": "solana",
            "sol": "solana",
            "ripple": "ripple",
            "xrp": "ripple",
            "polkadot": "polkadot",
            "dot": "polkadot",
            "dogecoin": "dogecoin",
            "doge": "dogecoin",
            "litecoin": "litecoin",
            "ltc": "litecoin",
        }
    
    def get_current_price(self, crypto: str, currency: str = "usd") -> Optional[Dict]:
        """
        Get current price and market data for a cryptocurrency.
        
        Args:
            crypto: Cryptocurrency name or symbol
            currency: Currency to fetch price in (default: usd)
        
        Returns:
            Dictionary with price data or None if error
        """
        crypto_id = self._resolve_crypto_id(crypto)
        if not crypto_id:
            return None
        
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {
                "ids": crypto_id,
                "vs_currencies": currency,
                "include_market_cap": True,
                "include_24hr_vol": True,
                "include_24hr_change": True,
                "include_ath": True,
                "include_atl": True,
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            if crypto_id in data:
                return {
                    "name": crypto_id,
                    "price": data[crypto_id].get(currency),
                    "market_cap": data[crypto_id].get(f"{currency}_market_cap"),
                    "volume_24h": data[crypto_id].get(f"{currency}_24h_vol"),
                    "change_24h": data[crypto_id].get(f"{currency}_24h_change"),
                    "ath": data[crypto_id].get(f"{currency}_ath"),
                    "atl": data[crypto_id].get(f"{currency}_atl"),
                    "timestamp": datetime.now().isoformat()
                }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching price for {crypto}: {e}")
        
        return None
    
    def get_market_chart_data(self, crypto: str, days: int = 30, 
                             currency: str = "usd") -> Optional[pd.DataFrame]:
        """
        Get historical price data for a cryptocurrency.
        
        Args:
            crypto: Cryptocurrency name or symbol
            days: Number of days of history (1-365)
            currency: Currency to fetch in
        
        Returns:
            DataFrame with price history or None if error
        """
        crypto_id = self._resolve_crypto_id(crypto)
        if not crypto_id:
            return None
        
        days = max(1, min(365, days))  # Clamp between 1-365
        
        try:
            url = f"{self.coingecko_base}/coins/{crypto_id}/market_chart"
            params = {
                "vs_currency": currency,
                "days": days,
                "interval": "daily"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            prices = data.get("prices", [])
            volumes = data.get("volumes", [])
            
            df = pd.DataFrame({
                "timestamp": [datetime.fromtimestamp(p[0]/1000) for p in prices],
                "price": [p[1] for p in prices],
                "volume": [v[1] for v in volumes]
            })
            
            return df
        except requests.exceptions.RequestException as e:
            print(f"Error fetching chart data for {crypto}: {e}")
        
        return None
    
    def get_top_cryptos(self, limit: int = 10, currency: str = "usd") -> Optional[List[Dict]]:
        """
        Get top cryptocurrencies by market cap.
        
        Args:
            limit: Number of top cryptos to return
            currency: Currency to fetch in
        
        Returns:
            List of cryptocurrency data or None if error
        """
        try:
            url = f"{self.coingecko_base}/coins/markets"
            params = {
                "vs_currency": currency,
                "order": "market_cap_desc",
                "per_page": min(limit, 250),
                "sparkline": False,
                "price_change_percentage": "24h"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching top cryptos: {e}")
        
        return None
    
    def get_trending_cryptos(self) -> Optional[List[Dict]]:
        """
        Get trending cryptocurrencies.
        
        Returns:
            List of trending coins or None if error
        """
        try:
            url = f"{self.coingecko_base}/search/trending"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return data.get("coins", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trending cryptos: {e}")
        
        return None
    
    def _resolve_crypto_id(self, crypto: str) -> Optional[str]:
        """
        Resolve cryptocurrency name or symbol to CoinGecko ID.
        
        Args:
            crypto: Cryptocurrency name or symbol
        
        Returns:
            CoinGecko ID or None if not found
        """
        crypto_lower = crypto.lower()
        return self.crypto_mapping.get(crypto_lower, crypto_lower)
