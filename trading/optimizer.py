import numpy as np
import pandas as pd
from itertools import product
from .lorentzian import LorentzianClassifier
from .risk_manager import RiskManager
from .oanda_client import OandaClient
import logging
from datetime import datetime, timedelta
import time
import random
import json
import os
from sqlalchemy import create_engine, text
import pathlib
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class StrategyOptimizer:
    def __init__(self):
        self.oanda_client = OandaClient()
        self.risk_manager = RiskManager()
        self.successful_evaluations = 0
        self.total_evaluations = 0
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        self.db_engine = create_engine(database_url)
        
        # Create cached_data directory if it doesn't exist
        self.cache_dir = pathlib.Path('cached_data')
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_expiry = timedelta(hours=24)  # Cache expires after 24 hours
        
    def _get_cache_path(self):
        """Get path for cached data file"""
        return self.cache_dir / 'historical_data.csv'
        
    def _is_cache_valid(self, cache_path):
        """Check if cache exists and is not expired"""
        if not cache_path.exists():
            return False
            
        cache_modified_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - cache_modified_time < self.cache_expiry
        
    def save_historical_data(self, data):
        """Save historical data to cache"""
        try:
            cache_path = self._get_cache_path()
            df = pd.DataFrame(data)
            df.to_csv(cache_path, index=False)
            logger.info(f"Historical data cached successfully at {cache_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving historical data to cache: {str(e)}")
            return False
            
    def load_historical_data(self):
        """Load historical data from cache"""
        try:
            cache_path = self._get_cache_path()
            if not self._is_cache_valid(cache_path):
                logger.info("Cache is invalid or expired")
                return None
                
            df = pd.read_csv(cache_path)
            if len(df) > 0:
                logger.info(f"Successfully loaded {len(df)} data points from cache")
                return {
                    'open': df['open'].tolist(),
                    'high': df['high'].tolist(),
                    'low': df['low'].tolist(),
                    'close': df['close'].tolist(),
                    'volume': df['volume'].tolist()
                }
            return None
        except Exception as e:
            logger.error(f"Error loading historical data from cache: {str(e)}")
            return None

    def save_optimization_results(self, params, metrics, score):
        """Save optimization results to database with transaction support"""
        try:
            query = text("""
            INSERT INTO optimization_results 
            (parameters, metrics, score, data_points, successful_evaluations, total_evaluations, created_at, is_current)
            VALUES 
            (:parameters, :metrics, :score, :data_points, :successful_evaluations, :total_evaluations, NOW(), TRUE)
            """)
            
            with self.db_engine.begin() as conn:
                conn.execute(query, {
                    'parameters': json.dumps(params),
                    'metrics': json.dumps(metrics),
                    'score': float(score),
                    'data_points': 2000,
                    'successful_evaluations': self.successful_evaluations,
                    'total_evaluations': self.total_evaluations
                })
                logger.info(f"Optimization results saved. Success rate: {(self.successful_evaluations/self.total_evaluations)*100:.2f}%")
        except Exception as e:
            logger.error(f"Error saving optimization results: {str(e)}")
            raise

    def get_historical_data(self, total_count=2000, use_cached=True):
        """Fetch historical data for optimization with adaptive rate limiting"""
        if use_cached:
            cached_data = self.load_historical_data()
            if cached_data is not None:
                logger.info("Using cached historical data")
                return pd.DataFrame(cached_data)
            
        logger.info(f"Fetching {total_count} historical data points from API...")
        
        chunk_size = 20  # Further reduced for stability
        remaining = total_count
        all_data = {
            'open': [], 'high': [], 'low': [], 'close': [], 'volume': []
        }
        
        retry_count = 0
        max_retries = 5
        base_delay = 30  # Increased base delay
        chunks_fetched = 0
        successful_chunks = 0
        response_times = []
        total_chunks = (total_count + chunk_size - 1) // chunk_size
        
        checkpoint_path = self.cache_dir / 'optimization_checkpoint.json'
        
        # Load checkpoint if exists
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, 'r') as f:
                    checkpoint = json.load(f)
                    all_data = checkpoint['data']
                    chunks_fetched = checkpoint['chunks_fetched']
                    remaining = total_count - (chunks_fetched * chunk_size)
                    logger.info(f"Resuming from checkpoint: {chunks_fetched} chunks already fetched")
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {str(e)}")
    
        while remaining > 0 and retry_count < max_retries:
            try:
                current_chunk = min(chunk_size, remaining)
                progress = (chunks_fetched/total_chunks)*100
                logger.info(f"Fetching chunk {chunks_fetched + 1}/{total_chunks} ({progress:.1f}% complete)")
                logger.info(f"Remaining data points: {remaining}")
                
                start_time = time.time()
                chunk_data = self.oanda_client.get_market_data(count=current_chunk)
                response_time = time.time() - start_time
                
                if not chunk_data:
                    raise Exception("Failed to fetch chunk data")
                    
                # Update response times for adaptive delay
                response_times.append(response_time)
                if len(response_times) > 10:
                    response_times.pop(0)
                    
                for key in all_data.keys():
                    all_data[key].extend(chunk_data[key])
                    
                remaining -= current_chunk
                chunks_fetched += 1
                successful_chunks += 1
                retry_count = 0
                
                # Save checkpoint after each successful chunk
                try:
                    with open(checkpoint_path, 'w') as f:
                        json.dump({
                            'data': all_data,
                            'chunks_fetched': chunks_fetched
                        }, f)
                except Exception as e:
                    logger.warning(f"Failed to save checkpoint: {str(e)}")
                
                if remaining > 0:
                    # Adaptive rate limiting based on response times
                    avg_response_time = sum(response_times) / len(response_times)
                    base_wait = base_delay * (1.5 ** (chunks_fetched // 5))  # Slower growth
                    jitter = random.uniform(5, 15)
                    response_factor = min(avg_response_time * 2, 30)  # Scale delay with response time
                    
                    delay = min(base_wait + jitter + response_factor, 180)  # Cap at 3 minutes
                    logger.info(f"Rate limiting: waiting {delay:.2f} seconds (avg response time: {avg_response_time:.2f}s)")
                    time.sleep(delay)
                    
                    # Add pause after successful chunks
                    if successful_chunks % 3 == 0:
                        pause = random.uniform(45, 90)
                        logger.info(f"Adding extended pause after multiple successes: {pause:.2f} seconds")
                        time.sleep(pause)
                
            except Exception as e:
                retry_count += 1
                successful_chunks = 0  # Reset success counter on failure
                if retry_count >= max_retries:
                    logger.error(f"Failed to fetch data after {max_retries} retries")
                    return None
                delay = base_delay * (3 ** retry_count) + random.uniform(15, 30)
                logger.warning(f"Error fetching data: {str(e)}. Retrying in {delay:.2f} seconds (attempt {retry_count}/{max_retries})...")
                time.sleep(delay)
                continue
                
        df = pd.DataFrame(all_data)
        data_quality = len(df) / total_count * 100
        logger.info(f"Data collection completed. Quality: {data_quality:.1f}% ({len(df)}/{total_count} points)")
        
        # Validate data quality
        if len(df) > 0:
            if data_quality >= 90:
                logger.info("Excellent data quality achieved, caching results")
                self.save_historical_data(all_data)
            elif data_quality >= 75:
                logger.info("Good data quality achieved, caching results")
                self.save_historical_data(all_data)
            else:
                logger.warning(f"Poor data quality ({data_quality:.1f}%), results not cached")
    
        try:
            # Clean up checkpoint after successful completion
            if checkpoint_path.exists():
                checkpoint_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to clean up checkpoint: {str(e)}")
    
        return df if len(df) > 0 else None

    def evaluate_parameters(self, data, params):
        """Evaluate a set of parameters with enhanced progress tracking"""
        self.total_evaluations += 1
        logger.info(f"Evaluating parameters {self.total_evaluations}: {params}")
        
        try:
            classifier = LorentzianClassifier(
                neighbors_count=params['neighbors_count'],
                feature_count=params['feature_count'],
                volatility_lookback=params['volatility_lookback'],
                trend_strength=params['trend_strength'],
                max_correlation=params['max_correlation']
            )
            
            signals = []
            returns = []
            
            chunk_size = 150
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
                
                try:
                    signal = classifier.get_signal(chunk_data)
                    if signal:
                        signals.append(signal)
                        future_return = (data['close'].iloc[end_idx + 4] - data['close'].iloc[end_idx]) / data['close'].iloc[end_idx]
                        returns.append(future_return)
                except Exception as e:
                    logger.debug(f"Error processing chunk {chunk_idx}: {str(e)}")
                    continue
                    
                if chunk_idx % 5 == 0:
                    logger.debug(f"Parameter evaluation progress: {((chunk_idx + 1)/total_chunks)*100:.1f}%")
                    
            if len(signals) < 10:
                logger.warning(f"Insufficient signals: {len(signals)}/10 minimum required")
                return None
                
            metrics = self._calculate_metrics(signals, returns)
            if metrics:
                self.successful_evaluations += 1
                logger.info(f"Evaluation {self.total_evaluations} successful - Metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating parameters: {str(e)}")
            return None
            
    def _calculate_metrics(self, signals, returns):
        """Calculate performance metrics with validation"""
        if not signals or not returns or len(signals) != len(returns):
            logger.warning("Invalid signals or returns data")
            return None
            
        returns_array = np.array(returns)
        valid_mask = ~np.isnan(returns_array)
        returns_array = returns_array[valid_mask]
        signals = np.array(signals)[valid_mask]
        
        if len(returns_array) < 10:
            logger.warning(f"Insufficient valid returns: {len(returns_array)}/10 minimum")
            return None
            
        try:
            strategy_returns = np.where(
                signals == "LONG", 
                returns_array, 
                np.where(signals == "SHORT", -returns_array, 0)
            )
            
            win_rate = np.mean(strategy_returns > 0)
            returns_std = np.std(strategy_returns)
            sharpe_ratio = np.mean(strategy_returns) / returns_std * np.sqrt(252) if returns_std > 0 else 0
            
            gains = np.sum(strategy_returns[strategy_returns > 0])
            losses = abs(np.sum(strategy_returns[strategy_returns < 0]))
            profit_factor = gains / losses if losses != 0 else 0
            
            cumulative = np.cumsum(strategy_returns)
            rolling_max = np.maximum.accumulate(cumulative)
            drawdowns = (rolling_max - cumulative) / np.where(rolling_max != 0, rolling_max, 1)
            max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
            
            metrics = {
                'sharpe_ratio': float(sharpe_ratio),
                'win_rate': float(win_rate),
                'profit_factor': float(profit_factor),
                'max_drawdown': float(max_drawdown),
                'total_trades': len(strategy_returns)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return None
            
    def calculate_optimization_score(self, metrics: Dict) -> float:
        """Calculate comprehensive optimization score"""
        try:
            if not metrics:
                return float('-inf')
                
            # Extract metrics with validation
            sharpe_ratio = float(metrics.get('sharpe_ratio', 0))
            win_rate = float(metrics.get('win_rate', 0))
            profit_factor = float(metrics.get('profit_factor', 1))
            max_drawdown = float(metrics.get('max_drawdown', 1))
            total_trades = int(metrics.get('total_trades', 0))
            
            # Minimum requirements
            if total_trades < 30:  # Require minimum number of trades
                return float('-inf')
            if max_drawdown > 0.25:  # Maximum allowable drawdown
                return float('-inf')
            
            # Calculate weighted score
            score = (
                0.35 * sharpe_ratio +  # Emphasize risk-adjusted returns
                0.25 * win_rate +      # Consider win rate
                0.20 * profit_factor + # Consider profit factor
                0.20 * (1 - max_drawdown)  # Penalize drawdown
            )
            
            # Bonus for more trades (up to a limit)
            trade_bonus = min(total_trades / 100, 1.0) * 0.1
            score += trade_bonus
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Error calculating optimization score: {str(e)}")
            return float('-inf')
            
    def get_parameter_ranges(self):
        """Define parameter ranges for optimization"""
        return {
            'neighbors_count': range(4, 13, 2),  # [4, 6, 8, 10, 12]
            'feature_count': range(2, 6),        # [2, 3, 4, 5]
            'volatility_lookback': range(10, 31, 5), # [10, 15, 20, 25, 30]
            'trend_strength': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        }
        
    def optimize(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Find optimal parameters with comprehensive logging"""
        try:
            logger.info("Starting strategy parameter optimization...")
            self.successful_evaluations = 0
            self.total_evaluations = 0
            
            data = self.get_historical_data(total_count=2000, use_cached=True)
            if data is None:
                raise ValueError("Failed to fetch historical data")
                return None, None
            
            param_ranges = self.get_parameter_ranges()
            param_combinations = [dict(zip(param_ranges.keys(), v)) 
                                for v in product(*param_ranges.values())]
            
            best_params = None
            best_metrics = None
            best_score = float('-inf')
            
            total_combinations = len(param_combinations)
            logger.info(f"Testing {total_combinations} parameter combinations")
            
            # Track progress
            progress_file = self.cache_dir / 'optimization_progress.json'
            completed_combinations = set()
            
            # Load previous progress if exists
            if progress_file.exists():
                try:
                    with open(progress_file, 'r') as f:
                        completed_combinations = set(json.load(f)['completed'])
                    logger.info(f"Loaded {len(completed_combinations)} completed evaluations")
                except Exception as e:
                    logger.warning(f"Failed to load progress: {str(e)}")
                    completed_combinations = set()
                    
            for i, params in enumerate(param_combinations):
                param_key = json.dumps(params, sort_keys=True)
                if param_key in completed_combinations:
                    logger.debug(f"Skipping already evaluated parameters: {params}")
                    continue
                    
                logger.info(f"Evaluating combination {i+1}/{total_combinations}")
                metrics = self.evaluate_parameters(data, params)
                
                if metrics:
                    score = self.calculate_optimization_score(metrics)
                    if score > best_score:
                        best_score = score
                        best_params = params
                        best_metrics = metrics
                        logger.info(f"New best score: {score:.4f} with params: {params}")
                        
                        # Save results immediately
                        self.save_optimization_results(params, metrics, score)
                        
                        # Update is_current flag in database
                        try:
                            with self.db_engine.begin() as conn:
                                # First, set all records to is_current = False
                                conn.execute(text("UPDATE optimization_results SET is_current = FALSE"))
                                # Then set the new best result to is_current = True
                                conn.execute(
                                    text("""
                                    UPDATE optimization_results 
                                    SET is_current = TRUE 
                                    WHERE score = :score 
                                    AND parameters = :parameters::jsonb
                                    """),
                                    {
                                        'score': score,
                                        'parameters': json.dumps(params)
                                    }
                                )
                        except Exception as e:
                            logger.error(f"Error updating is_current flag: {str(e)}")
                        
                # Update progress
                completed_combinations.add(param_key)
                try:
                    with open(progress_file, 'w') as f:
                        json.dump({'completed': list(completed_combinations)}, f)
                except Exception as e:
                    logger.warning(f"Failed to save progress: {str(e)}")
                    
            logger.info("Optimization completed")
            logger.info(f"Best parameters: {best_params}")
            logger.info(f"Best metrics: {best_metrics}")
            
            return best_params, best_metrics
        except Exception as e:
            logger.error(f"Error in optimization process: {str(e)}")
            return None, None