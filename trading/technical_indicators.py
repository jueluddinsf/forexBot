import numpy as np
import pandas as pd

class TechnicalIndicators:
    def __init__(self):
        self.ema_period = 200
        self.sma_period = 200
        
    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average"""
        close_prices = pd.Series(data['close'])
        return close_prices.ewm(span=period, adjust=False).mean()
        
    def calculate_sma(self, data, period):
        """Calculate Simple Moving Average"""
        close_prices = pd.Series(data['close'])
        return close_prices.rolling(window=period).mean()
        
    def check_ema_filter(self, market_data):
        """Check if price is above/below EMA for trend confirmation"""
        ema = self.calculate_ema(market_data, self.ema_period)
        current_price = market_data['close'][-1]
        current_ema = ema.iloc[-1]
        
        if current_price > current_ema:
            return "LONG"
        elif current_price < current_ema:
            return "SHORT"
        return None
        
    def check_sma_filter(self, market_data):
        """Check if price is above/below SMA for trend confirmation"""
        sma = self.calculate_sma(market_data, self.sma_period)
        current_price = market_data['close'][-1]
        current_sma = sma.iloc[-1]
        
        if current_price > current_sma:
            return "LONG"
        elif current_price < current_sma:
            return "SHORT"
        return None
