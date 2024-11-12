import numpy as np
import pandas as pd
from itertools import product
from .lorentzian import LorentzianClassifier
from .risk_manager import RiskManager
from .oanda_client import OandaClient
import logging

logger = logging.getLogger(__name__)

class StrategyOptimizer:
    def __init__(self):
        self.oanda_client = OandaClient()
        self.risk_manager = RiskManager()
        self.successful_evaluations = 0
        
    def get_historical_data(self, count=5000):
        """Fetch historical data for optimization"""
        logger.info(f"Fetching {count} historical data points...")
        data = self.oanda_client.get_market_data(count=count)
        if data:
            logger.info("Successfully retrieved historical data")
            if all(key in data for key in ['open', 'high', 'low', 'close', 'volume']):
                df = pd.DataFrame(data)
                logger.info(f"Data shape: {df.shape}")
                return df
            else:
                logger.error("Missing required columns in market data")
        logger.error("Failed to retrieve valid market data")
        return None
        
    def evaluate_parameters(self, data, params):
        """Evaluate a set of parameters"""
        logger.info(f"Evaluating parameters: {params}")
        try:
            classifier = LorentzianClassifier(
                neighbors_count=params['neighbors_count'],
                feature_count=params['feature_count']
            )
            
            signals = []
            returns = []
            
            # Process data in chunks for better memory management
            chunk_size = 500
            total_chunks = (len(data) - 4) // chunk_size
            
            for chunk_idx in range(total_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min(start_idx + chunk_size, len(data) - 4)
                
                chunk_data = {
                    'close': data['close'].iloc[start_idx:end_idx].values,
                    'high': data['high'].iloc[start_idx:end_idx].values,
                    'low': data['low'].iloc[start_idx:end_idx].values,
                    'open': data['open'].iloc[start_idx:end_idx].values,
                    'volume': data['volume'].iloc[start_idx:end_idx].values
                }
                
                # Get signals for the chunk
                signal = classifier.get_signal(chunk_data)
                if signal:
                    signals.append(signal)
                    future_return = (data['close'].iloc[end_idx + 4] - data['close'].iloc[end_idx]) / data['close'].iloc[end_idx]
                    returns.append(future_return)
                
                if chunk_idx % 5 == 0:  # Log progress every 5 chunks
                    logger.info(f"Processed chunk {chunk_idx + 1}/{total_chunks}")
            
            if len(signals) < 50:  # Require minimum number of signals
                logger.warning(f"Insufficient signals generated: {len(signals)}")
                return None
                
            metrics = self._calculate_metrics(signals, returns)
            if metrics:
                self.successful_evaluations += 1
                logger.info(f"Parameters {params} achieved metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating parameters: {str(e)}")
            return None
        
    def _calculate_metrics(self, signals, returns):
        """Calculate performance metrics"""
        if not signals or not returns or len(signals) != len(returns):
            logger.warning("Invalid signals or returns data")
            return None
            
        returns_array = np.array(returns)
        valid_mask = ~np.isnan(returns_array)
        returns_array = returns_array[valid_mask]
        signals = np.array(signals)[valid_mask]
        
        if len(returns_array) < 50:
            logger.warning(f"Insufficient valid returns: {len(returns_array)}")
            return None
            
        # Calculate strategy returns
        strategy_returns = np.where(
            signals == "LONG", 
            returns_array, 
            np.where(signals == "SHORT", -returns_array, 0)
        )
        
        # Calculate metrics
        win_rate = np.mean(strategy_returns > 0)
        
        # Sharpe Ratio (annualized)
        returns_std = np.std(strategy_returns)
        if returns_std > 0:
            sharpe_ratio = np.mean(strategy_returns) / returns_std * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # Profit Factor
        gains = np.sum(strategy_returns[strategy_returns > 0])
        losses = abs(np.sum(strategy_returns[strategy_returns < 0]))
        profit_factor = gains / losses if losses != 0 else 0
        
        # Max Drawdown
        cumulative = np.cumsum(strategy_returns)
        rolling_max = np.maximum.accumulate(cumulative)
        drawdowns = (rolling_max - cumulative) / np.where(rolling_max != 0, rolling_max, 1)
        max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
        
        return {
            'sharpe_ratio': float(sharpe_ratio),
            'win_rate': float(win_rate),
            'profit_factor': float(profit_factor),
            'max_drawdown': float(max_drawdown),
            'total_trades': len(strategy_returns)
        }
        
    def optimize(self):
        """Find optimal parameters"""
        logger.info("Starting strategy optimization...")
        self.successful_evaluations = 0
        
        # Get historical data
        data = self.get_historical_data()
        if data is None:
            logger.error("Failed to fetch historical data")
            return None, None
            
        # Parameter ranges to test
        param_ranges = {
            'neighbors_count': [4, 6, 8, 10, 12],
            'feature_count': [3, 4, 5]
        }
        
        logger.info(f"Testing parameter combinations: {param_ranges}")
        
        # Generate all combinations
        param_combinations = [dict(zip(param_ranges.keys(), v)) 
                            for v in product(*param_ranges.values())]
        
        best_params = None
        best_metrics = None
        best_score = float('-inf')
        
        total_combinations = len(param_combinations)
        logger.info(f"Total parameter combinations to test: {total_combinations}")
        
        for i, params in enumerate(param_combinations, 1):
            logger.info(f"Testing combination {i}/{total_combinations}: {params}")
            metrics = self.evaluate_parameters(data, params)
            
            if metrics is None:
                logger.warning(f"Skipping invalid metrics for parameters: {params}")
                continue
            
            # Calculate combined score (adjusted weights)
            score = (
                metrics['sharpe_ratio'] * 0.35 +
                metrics['win_rate'] * 0.25 +
                metrics['profit_factor'] * 0.25 -
                metrics['max_drawdown'] * 0.15
            )
            
            if score > best_score:
                best_score = score
                best_params = params
                best_metrics = metrics
                logger.info(f"New best parameters found: {params}")
                logger.info(f"New best metrics: {metrics}")
                logger.info(f"New best score: {score}")
                
        logger.info("Optimization completed")
        logger.info(f"Total successful evaluations: {self.successful_evaluations}")
        logger.info(f"Final best parameters: {best_params}")
        logger.info(f"Final best metrics: {best_metrics}")
                
        return best_params, best_metrics
