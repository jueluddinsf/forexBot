import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    def __init__(self):
        self.ema_period = 200
        self.sma_period = 200
        
    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average"""
        try:
            if not data or 'close' not in data:
                logger.warning("Invalid data format for EMA calculation")
                return pd.Series(dtype=float)
                
            close_prices = pd.Series(data['close'])
            if close_prices.empty:
                logger.warning("Empty price data for EMA calculation")
                return pd.Series(dtype=float)
                
            return close_prices.ewm(span=period, adjust=False).mean()
        except Exception as e:
            logger.error(f"Error calculating EMA: {str(e)}")
            return pd.Series(dtype=float)
        
    def calculate_sma(self, data, period):
        """Calculate Simple Moving Average with enhanced error handling"""
        try:
            if not data or 'close' not in data:
                logger.warning("Invalid data format for SMA calculation")
                return pd.Series(dtype=float)
            
            close_prices = pd.Series(data['close'])
            if close_prices.empty:
                logger.warning("Empty price data for SMA calculation")
                return pd.Series(dtype=float)
            
            close_prices = close_prices.fillna(method='ffill').fillna(method='bfill')
            
            if len(close_prices) < period:
                logger.warning(f"Insufficient data points for {period} period SMA")
                return pd.Series(dtype=float)
                
            sma = close_prices.rolling(window=period, min_periods=1).mean()
            return sma
            
        except Exception as e:
            logger.error(f"Error calculating SMA: {str(e)}")
            return pd.Series(dtype=float)

    def calculate_rsi(self, data, period=14):
        """Calculate Relative Strength Index"""
        try:
            if not data or 'close' not in data:
                return pd.Series(dtype=float)

            close_prices = pd.Series(data['close'])
            if close_prices.empty:
                return pd.Series(dtype=float)

            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss.replace(0, 1e-10)  # Avoid division by zero
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return pd.Series(dtype=float)

    def calculate_atr_ratio(self, data, period=14):
        """Calculate ATR Ratio"""
        try:
            if not data or not all(k in data for k in ['high', 'low', 'close']):
                return None

            high = pd.Series(data['high'])
            low = pd.Series(data['low'])
            close = pd.Series(data['close'])
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            
            if len(atr) > 0:
                current_atr = atr.iloc[-1]
                current_price = close.iloc[-1]
                return (current_atr / current_price) * 100  # Return as percentage
            return None
        except Exception as e:
            logger.error(f"Error calculating ATR ratio: {str(e)}")
            return None
            
    def check_ema_filter(self, market_data):
        """Check if price is above/below EMA for trend confirmation"""
        try:
            if not market_data or 'close' not in market_data:
                return None
                
            ema = self.calculate_ema(market_data, self.ema_period)
            if ema.empty or len(market_data['close']) == 0:
                return None
                
            current_price = market_data['close'][-1]
            current_ema = ema.iloc[-1]
            
            if pd.isna(current_price) or pd.isna(current_ema):
                return None
            
            if current_price > current_ema:
                return "LONG"
            elif current_price < current_ema:
                return "SHORT"
            return None
            
        except Exception as e:
            logger.error(f"Error in EMA filter: {str(e)}")
            return None
        
    def check_sma_filter(self, market_data):
        """Check if price is above/below SMA for trend confirmation"""
        try:
            if not market_data or 'close' not in market_data:
                return None
                
            sma = self.calculate_sma(market_data, self.sma_period)
            if sma.empty or len(market_data['close']) == 0:
                return None
                
            current_price = market_data['close'][-1]
            current_sma = sma.iloc[-1]
            
            if pd.isna(current_price) or pd.isna(current_sma):
                return None
            
            if current_price > current_sma:
                return "LONG"
            elif current_price < current_sma:
                return "SHORT"
            return None
            
        except Exception as e:
            logger.error(f"Error in SMA filter: {str(e)}")
            return None
