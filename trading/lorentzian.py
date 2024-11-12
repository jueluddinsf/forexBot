import numpy as np
import pandas as pd
import logging
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

class LorentzianClassifier:
    def __init__(self, neighbors_count=8, feature_count=5, volatility_lookback=20, 
                 trend_strength=0.2, max_correlation=0.7):
        self._validate_parameters(neighbors_count, feature_count, volatility_lookback,
                               trend_strength, max_correlation)
        self.neighbors_count = neighbors_count
        self.feature_count = feature_count
        self.volatility_lookback = volatility_lookback
        self.trend_strength = trend_strength
        self.max_correlation = max_correlation
        
    def _validate_parameters(self, neighbors_count: int, feature_count: int,
                           volatility_lookback: int, trend_strength: float,
                           max_correlation: float) -> None:
        """Validate initialization parameters"""
        if not 1 <= neighbors_count <= 100:
            raise ValueError("neighbors_count must be between 1 and 100")
        if not 2 <= feature_count <= 5:
            raise ValueError("feature_count must be between 2 and 5")
        if not 5 <= volatility_lookback <= 50:
            raise ValueError("volatility_lookback must be between 5 and 50")
        if not 0.0 <= trend_strength <= 1.0:
            raise ValueError("trend_strength must be between 0.0 and 1.0")
        if not 0.0 <= max_correlation <= 1.0:
            raise ValueError("max_correlation must be between 0.0 and 1.0")

    def get_lorentzian_distance(self, current_features: np.ndarray, 
                              historical_features: np.ndarray) -> Optional[float]:
        """Calculate Lorentzian distance between feature sets with validation"""
        try:
            if len(current_features) != len(historical_features):
                logger.error("Feature vectors must have same length")
                return None
                
            distance = 0
            for i in range(len(current_features)):
                if np.isnan(current_features[i]) or np.isnan(historical_features[i]):
                    continue
                distance += np.log1p(abs(current_features[i] - historical_features[i]))
            return distance
        except Exception as e:
            logger.error(f"Error calculating Lorentzian distance: {str(e)}")
            return None

    def calculate_features(self, data: Dict) -> Optional[np.ndarray]:
        """Calculate technical features for classification with enhanced validation"""
        try:
            df = pd.DataFrame(data)
            if df.empty:
                logger.warning("Empty data provided for feature calculation")
                return None
                
            features = []
            
            # Select features based on feature_count with validation
            if self.feature_count >= 1:
                rsi = self.calculate_rsi(df['close'], 14)
                features.append(rsi if not rsi.empty else pd.Series(0, index=df.index))
            if self.feature_count >= 2:
                wt = self.calculate_wt(df['high'], df['low'], df['close'])
                features.append(wt if not wt.empty else pd.Series(0, index=df.index))
            if self.feature_count >= 3:
                cci = self.calculate_cci(df['high'], df['low'], df['close'], 20)
                features.append(cci if not cci.empty else pd.Series(0, index=df.index))
            if self.feature_count >= 4:
                adx = self.calculate_adx(df['high'], df['low'], df['close'], 14)
                features.append(adx if not adx.empty else pd.Series(0, index=df.index))
            if self.feature_count >= 5:
                rsi_short = self.calculate_rsi(df['close'], 9)
                features.append(rsi_short if not rsi_short.empty else pd.Series(0, index=df.index))
            
            # Add volatility-based feature
            volatility = self.calculate_volatility(df['close'])
            features.append(volatility)
            
            # Add trend strength feature
            trend = self.calculate_trend_strength(df['close'])
            features.append(trend)
            
            # Calculate feature correlations and filter highly correlated features
            features_array = np.array(features).T
            features_array = np.nan_to_num(features_array, nan=0.0)
            
            # Filter features based on correlation
            features_array = self._filter_correlated_features(features_array)
            
            return features_array

        except Exception as e:
            logger.error(f"Error calculating features: {str(e)}")
            return None

    def get_signal(self, market_data: Dict) -> Optional[str]:
        """Get trading signal with enhanced validation and optimization"""
        try:
            features = self.calculate_features(market_data)
            if features is None or len(features) < 2:
                logger.warning("Insufficient feature data points")
                return None
                
            current_features = features[-1]
            historical_features = features[:-1]
            
            if len(historical_features) < self.neighbors_count:
                logger.warning("Insufficient historical data for KNN analysis")
                return None
            
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
            std_return = np.std(neighbor_returns)
            
            # Adaptive threshold based on volatility and trend
            volatility_factor = current_features[-2]  # Volatility feature
            trend_factor = current_features[-1]  # Trend feature
            
            base_threshold = 0.001
            adaptive_threshold = base_threshold * (1 + volatility_factor) * (1 + abs(trend_factor))
            
            # Confidence-based signal generation
            if avg_return > adaptive_threshold and avg_return > 2 * std_return:
                return "LONG"
            elif avg_return < -adaptive_threshold and abs(avg_return) > 2 * std_return:
                return "SHORT"
            return None
            
        except Exception as e:
            logger.error(f"Error in get_signal: {str(e)}")
            return None

    def _filter_correlated_features(self, features_array):
        """Filter out highly correlated features"""
        try:
            if features_array.shape[1] < 2:
                return features_array
                
            # Calculate correlation matrix
            corr_matrix = np.corrcoef(features_array.T)
            
            # Find pairs of features with correlation above threshold
            high_corr_pairs = np.where(np.abs(corr_matrix) > self.max_correlation)
            
            # Keep only unique pairs (excluding self-correlation)
            high_corr_pairs = [(i, j) for i, j in zip(*high_corr_pairs) if i < j]
            
            # Remove one feature from each highly correlated pair
            features_to_remove = set()
            for i, j in high_corr_pairs:
                # Remove the feature with higher mean correlation with others
                mean_corr_i = np.mean(np.abs(corr_matrix[i]))
                mean_corr_j = np.mean(np.abs(corr_matrix[j]))
                features_to_remove.add(i if mean_corr_i > mean_corr_j else j)
            
            # Keep features not marked for removal
            keep_features = [i for i in range(features_array.shape[1]) 
                           if i not in features_to_remove]
            
            return features_array[:, keep_features]
            
        except Exception as e:
            logger.error(f"Error filtering correlated features: {str(e)}")
            return features_array

    def calculate_volatility(self, close):
        """Calculate price volatility"""
        try:
            returns = pd.Series(close).pct_change()
            volatility = returns.rolling(window=self.volatility_lookback).std()
            return volatility
        except Exception as e:
            logger.error(f"Error calculating volatility: {str(e)}")
            return pd.Series(np.nan, index=close.index)

    def calculate_trend_strength(self, close):
        """Calculate trend strength indicator"""
        try:
            ma_fast = pd.Series(close).rolling(window=20).mean()
            ma_slow = pd.Series(close).rolling(window=50).mean()
            trend = (ma_fast - ma_slow) / ma_slow
            return trend * self.trend_strength
        except Exception as e:
            logger.error(f"Error calculating trend strength: {str(e)}")
            return pd.Series(np.nan, index=close.index)

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

    def get_prediction_values(self, market_data) -> Tuple[Optional[float], Optional[float]]:
        """Get prediction value and trend strength"""
        try:
            features = self.calculate_features(market_data)
            if features is None or len(features) < 2:
                return None, None
            
            current_features = features[-1]
            historical_features = features[:-1]
            
            if len(historical_features) < self.neighbors_count:
                return None, None
            
            distances = []
            for hist_feature in historical_features:
                distance = self.get_lorentzian_distance(current_features, hist_feature)
                if distance is not None:
                    distances.append(distance)
                
            if not distances:
                return None, None
            
            nearest_neighbors = np.argsort(distances)[:self.neighbors_count]
            neighbor_returns = self.calculate_returns(market_data, nearest_neighbors)
            
            if not neighbor_returns:
                return None, None
            
            # Calculate prediction value (normalized between 0 and 1)
            avg_return = np.mean(neighbor_returns)
            std_return = np.std(neighbor_returns)
            z_score = avg_return / (std_return + 1e-10)
            prediction = 1 / (1 + np.exp(-z_score))  # Sigmoid transformation
            
            # Calculate trend strength
            trend_direction = np.sign(avg_return)
            trend_consistency = np.mean(np.sign(neighbor_returns) == trend_direction)
            trend_strength = trend_consistency * abs(z_score) / 2
            
            return float(prediction), float(trend_strength)
            
        except Exception as e:
            logger.error(f"Error in get_prediction_values: {str(e)}")
            return None, None