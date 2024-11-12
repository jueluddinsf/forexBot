import numpy as np
import pandas as pd

class LorentzianClassifier:
    def __init__(self, neighbors_count=8, feature_count=5):
        self.neighbors_count = neighbors_count
        self.feature_count = feature_count
        
    def get_lorentzian_distance(self, current_features, historical_features):
        """Calculate Lorentzian distance between feature sets"""
        distance = 0
        for i in range(len(current_features)):
            distance += np.log(1 + abs(current_features[i] - historical_features[i]))
        return distance

    def calculate_features(self, data):
        """Calculate technical features for classification"""
        df = pd.DataFrame(data)
        
        features = []
        # RSI
        features.append(self.calculate_rsi(df['close'], 14))
        # Wave Trend
        features.append(self.calculate_wt(df['high'], df['low'], df['close']))
        # CCI
        features.append(self.calculate_cci(df['high'], df['low'], df['close'], 20))
        # ADX
        features.append(self.calculate_adx(df['high'], df['low'], df['close'], 14))
        # RSI with different period
        features.append(self.calculate_rsi(df['close'], 9))
        
        return np.array(features).T

    def get_signal(self, market_data):
        """Get trading signal based on Lorentzian Classification"""
        features = self.calculate_features(market_data)
        current_features = features[-1]
        historical_features = features[:-1]
        
        distances = []
        for hist_feature in historical_features:
            distance = self.get_lorentzian_distance(current_features, hist_feature)
            distances.append(distance)
            
        nearest_neighbors = np.argsort(distances)[:self.neighbors_count]
        
        # Analyze neighbors for signal
        neighbor_returns = self.calculate_returns(market_data, nearest_neighbors)
        avg_return = np.mean(neighbor_returns)
        
        if avg_return > 0.001:  # Threshold for long signal
            return "LONG"
        elif avg_return < -0.001:  # Threshold for short signal
            return "SHORT"
        return None

    def calculate_rsi(self, close, period):
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_wt(self, high, low, close):
        hlc3 = (high + low + close) / 3
        ema_10 = hlc3.ewm(span=10).mean()
        return (ema_10 - hlc3.rolling(11).mean()) / hlc3.rolling(11).std()

    def calculate_cci(self, high, low, close, period):
        tp = (high + low + close) / 3
        sma = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: pd.Series(x).mad())
        return (tp - sma) / (0.015 * mad)

    def calculate_adx(self, high, low, close, period):
        plus_dm = high.diff()
        minus_dm = low.diff()
        tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        
        plus_di = 100 * (plus_dm.rolling(period).mean() / tr.rolling(period).mean())
        minus_di = 100 * (minus_dm.rolling(period).mean() / tr.rolling(period).mean())
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        return dx.rolling(period).mean()

    def calculate_returns(self, data, indices):
        """Calculate returns for nearest neighbors"""
        close_prices = pd.Series(data['close'])
        returns = []
        for idx in indices:
            future_return = (close_prices[idx + 4] - close_prices[idx]) / close_prices[idx]
            returns.append(future_return)
        return returns
