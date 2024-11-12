import numpy as np
from datetime import datetime, timedelta
import pandas as pd

class RiskManager:
    def __init__(self, max_risk_per_trade=0.02, max_daily_risk=0.06, 
                 max_trades_per_day=3, max_drawdown=0.15, 
                 max_correlation=0.7, volatility_scaling=True):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_daily_risk = max_daily_risk
        self.max_trades_per_day = max_trades_per_day
        self.max_drawdown = max_drawdown
        self.max_correlation = max_correlation
        self.volatility_scaling = volatility_scaling
        self.daily_trades = []
        self.daily_pnl = 0
        self.trade_history = []
        self.last_volatility = None
        
    def can_trade(self, market_data=None, current_positions=None):
        """Check if new trade meets risk parameters"""
        self._cleanup_old_trades()
        
        # Basic checks
        if len(self.daily_trades) >= self.max_trades_per_day:
            return False, "Maximum daily trades reached"
            
        if abs(self.daily_pnl) >= self.max_daily_risk:
            return False, "Maximum daily risk reached"
            
        # Check drawdown
        if self._calculate_current_drawdown() > self.max_drawdown:
            return False, "Maximum drawdown exceeded"
            
        # Time-based filters
        if not self._check_trading_hours():
            return False, "Outside trading hours"
            
        # Market volatility check
        if market_data is not None and not self._check_volatility(market_data):
            return False, "Market volatility too high"
            
        # Correlation check
        if current_positions and not self._check_correlation(market_data, current_positions):
            return False, "Position correlation too high"
            
        return True, "Trade allowed"
        
    def calculate_position_size(self, account_balance, market_data=None):
        """Calculate position size based on risk parameters and market conditions"""
        if account_balance is None:
            return 1000  # Default minimum position
            
        # Base position size
        risk_amount = account_balance * self.max_risk_per_trade
        position_size = risk_amount * 100  # Standard lot calculation
        
        # Adjust for volatility if enabled
        if self.volatility_scaling and market_data is not None:
            volatility = self._calculate_volatility(market_data)
            if volatility > 0:
                # Inverse relationship with volatility
                position_size = position_size * (1 / volatility)
                self.last_volatility = volatility
        
        # Risk-adjusted position sizing
        win_rate = self._calculate_win_rate()
        if win_rate:
            position_size *= min(win_rate, 1.5)  # Cap at 150% scaling
            
        # Apply limits
        position_size = min(position_size, account_balance * 0.1)  # Max 10% of account
        position_size = max(position_size, 1000)  # Minimum position size
        
        return round(position_size, 0)
        
    def update_trade_metrics(self, trade_result):
        """Update metrics after trade completion"""
        self.daily_trades.append({
            'timestamp': datetime.now(),
            'pnl': trade_result
        })
        self.daily_pnl += trade_result
        self.trade_history.append(trade_result)
        
    def _calculate_current_drawdown(self):
        """Calculate current drawdown from trade history"""
        if not self.trade_history:
            return 0
            
        cumulative_returns = np.cumsum(self.trade_history)
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (peak - cumulative_returns) / peak
        return np.max(drawdown) if len(drawdown) > 0 else 0
        
    def _check_trading_hours(self):
        """Check if current time is within acceptable trading hours"""
        current_time = datetime.now().time()
        # Avoid trading during major news releases (typical forex market hours)
        # Returns False during typical high-impact news times
        high_impact_hours = [
            (datetime.strptime("8:30", "%H:%M").time(), datetime.strptime("9:30", "%H:%M").time()),
            (datetime.strptime("14:00", "%H:%M").time(), datetime.strptime("15:00", "%H:%M").time())
        ]
        
        for start, end in high_impact_hours:
            if start <= current_time <= end:
                return False
        return True
        
    def _check_volatility(self, market_data):
        """Check if market volatility is within acceptable range"""
        volatility = self._calculate_volatility(market_data)
        # Reject trades during extremely high volatility
        return volatility <= 2.5  # Threshold based on standard deviations
        
    def _calculate_volatility(self, market_data):
        """Calculate market volatility"""
        if 'close' in market_data:
            returns = pd.Series(market_data['close']).pct_change()
            return returns.std() * np.sqrt(252)  # Annualized volatility
        return 1.0  # Default if no data available
        
    def _check_correlation(self, market_data, current_positions):
        """Check correlation between proposed trade and existing positions"""
        if not current_positions or 'close' not in market_data:
            return True
            
        current_returns = pd.Series(market_data['close']).pct_change()
        
        for position in current_positions:
            if 'price_data' in position:
                position_returns = pd.Series(position['price_data']).pct_change()
                correlation = current_returns.corr(position_returns)
                if abs(correlation) > self.max_correlation:
                    return False
        return True
        
    def _calculate_win_rate(self):
        """Calculate historical win rate"""
        if not self.trade_history:
            return None
            
        wins = sum(1 for x in self.trade_history if x > 0)
        return wins / len(self.trade_history) if self.trade_history else None
        
    def _cleanup_old_trades(self):
        """Remove trades older than 24 hours"""
        cutoff_time = datetime.now() - timedelta(days=1)
        self.daily_trades = [trade for trade in self.daily_trades 
                           if trade['timestamp'] > cutoff_time]
        
        # Recalculate daily PnL
        self.daily_pnl = sum(trade['pnl'] for trade in self.daily_trades)
