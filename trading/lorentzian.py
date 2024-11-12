import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class LorentzianClassifier:
    def __init__(self, neighbors_count=8, feature_count=5):
        self.neighbors_count = neighbors_count
        self.feature_count = feature_count
        
    def get_lorentzian_distance(self, current_features, historical_features):
        """Calculate Lorentzian distance between feature sets"""
        try:
            distance = 0
            for i in range(len(current_features)):
                distance += np.log(1 + abs(current_features[i] - historical_features[i]))
            return distance
        except Exception as e:
            logger.error(f"Error calculating Lorentzian distance: {str(e)}")
            return None

    def calculate_features(self, data):
        """Calculate technical features for classification"""
        try:
            df = pd.DataFrame(data)
            features = []
            
            logger.debug("Calculating technical indicators...")
            
            # Select features based on feature_count
            if self.feature_count >= 1:
                features.append(self.calculate_rsi(df['close'], 14))
            if self.feature_count >= 2:
                features.append(self.calculate_wt(df['high'], df['low'], df['close']))
            if self.feature_count >= 3:
                features.append(self.calculate_cci(df['high'], df['low'], df['close'], 20))
            if self.feature_count >= 4:
                features.append(self.calculate_adx(df['high'], df['low'], df['close'], 14))
            if self.feature_count >= 5:
                features.append(self.calculate_rsi(df['close'], 9))
            
            # Convert features to numpy array and handle NaN values
            features_array = np.array(features).T
            features_array = np.nan_to_num(features_array, nan=0.0)
            return features_array

        except Exception as e:
            logger.error(f"Error calculating features: {str(e)}")
            return None

    def get_signal(self, market_data):
        """Get trading signal based on Lorentzian Classification"""
        try:
            features = self.calculate_features(market_data)
            if features is None or len(features) < self.feature_count:
                logger.warning(f"Insufficient feature data points. Required: {self.feature_count}")
                return None
                
            current_features = features[-1]
            historical_features = features[:-1]
            
            distances = []
            for hist_feature in historical_features:
                distance = self.get_lorentzian_distance(current_features, hist_feature)
                if distance is not None:
                    distances.append(distance)
                
            if not distances:
                logger.warning("No valid distances calculated")
                return None
                
            nearest_neighbors = np.argsort(distances)[:self.neighbors_count]
            
            neighbor_returns = self.calculate_returns(market_data, nearest_neighbors)
            if not neighbor_returns:
                logger.warning("No valid returns calculated")
                return None
                
            avg_return = np.mean(neighbor_returns)
            logger.debug(f"Average return calculated: {avg_return}")
            
            if avg_return > 0.001:
                return "LONG"
            elif avg_return < -0.001:
                return "SHORT"
            return None
        except Exception as e:
            logger.error(f"Error in get_signal: {str(e)}")
            return None

    def calculate_rsi(self, close, period):
        """Calculate RSI indicator"""
        try:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            loss = loss.replace(0, 0.000001)  # Avoid division by zero
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return pd.Series(np.nan, index=close.index)

    def calculate_wt(self, high, low, close):
        """Calculate Wave Trend indicator"""
        try:
            hlc3 = (high + low + close) / 3
            ema_10 = hlc3.ewm(span=10).mean()
            std = hlc3.rolling(11).std()
            std = std.replace(0, 0.000001)  # Avoid division by zero
            return (ema_10 - hlc3.rolling(11).mean()) / std
        except Exception as e:
            logger.error(f"Error calculating Wave Trend: {str(e)}")
            return pd.Series(np.nan, index=close.index)

    def calculate_cci(self, high, low, close, period):
        """Calculate CCI (Commodity Channel Index)"""
        try:
            tp = (high + low + close) / 3
            sma_tp = tp.rolling(window=period).mean()
            
            # Calculate mean absolute deviation manually
            def mad(x):
                return np.abs(x - x.mean()).mean()
            
            rolling_mad = tp.rolling(window=period).apply(mad)
            rolling_mad = rolling_mad.replace(0, 0.000001)  # Avoid division by zero
            
            cci = (tp - sma_tp) / (0.015 * rolling_mad)
            return cci
        except Exception as e:
            logger.error(f"Error calculating CCI: {str(e)}")
            return pd.Series(np.nan, index=close.index)

    def calculate_adx(self, high, low, close, period):
        """Calculate ADX indicator"""
        try:
            plus_dm = high.diff()
            minus_dm = low.diff()
            tr = pd.concat([high - low, 
                          abs(high - close.shift()), 
                          abs(low - close.shift())], axis=1).max(axis=1)
            
            tr = tr.replace(0, 0.000001)  # Avoid division by zero
            plus_di = 100 * (plus_dm.rolling(period).mean() / tr.rolling(period).mean())
            minus_di = 100 * (minus_dm.rolling(period).mean() / tr.rolling(period).mean())
            
            dx_denominator = abs(plus_di + minus_di)
            dx_denominator = dx_denominator.replace(0, 0.000001)  # Avoid division by zero
            dx = 100 * abs(plus_di - minus_di) / dx_denominator
            
            return dx.rolling(period).mean()
        except Exception as e:
            logger.error(f"Error calculating ADX: {str(e)}")
            return pd.Series(np.nan, index=close.index)

    def calculate_returns(self, data, indices):
        """Calculate returns for nearest neighbors"""
        try:
            close_prices = pd.Series(data['close'])
            returns = []
            
            for idx in indices:
                if idx + 4 >= len(close_prices):
                    continue
                try:
                    future_return = (close_prices.iloc[idx + 4] - close_prices.iloc[idx]) / close_prices.iloc[idx]
                    returns.append(future_return)
                except (IndexError, KeyError) as e:
                    logger.warning(f"Error calculating return for index {idx}: {str(e)}")
                    continue
                    
            return returns if returns else None
        except Exception as e:
            logger.error(f"Error calculating returns: {str(e)}")
            return None
