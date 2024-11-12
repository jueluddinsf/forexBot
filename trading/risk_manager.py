import numpy as np
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self, max_risk_per_trade=0.02, max_daily_risk=0.06, 
                 max_trades_per_day=3, max_drawdown=0.15):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_daily_risk = max_daily_risk
        self.max_trades_per_day = max_trades_per_day
        self.max_drawdown = max_drawdown
        self.daily_trades = []
        self.daily_pnl = 0
        
    def can_trade(self):
        """Check if new trade meets risk parameters"""
        self._cleanup_old_trades()
        
        # Check number of trades today
        if len(self.daily_trades) >= self.max_trades_per_day:
            return False
            
        # Check daily risk
        if abs(self.daily_pnl) >= self.max_daily_risk:
            return False
            
        return True
        
    def calculate_position_size(self, account_balance=None):
        """Calculate position size based on risk parameters"""
        if account_balance is None:
            return 1000  # Default minimum position
            
        risk_amount = account_balance * self.max_risk_per_trade
        
        # Calculate basic position size
        position_size = risk_amount * 100  # Standard lot calculation
        
        # Apply additional constraints
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
        
    def calculate_drawdown(self, equity_curve):
        """Calculate current drawdown"""
        if not equity_curve:
            return 0
            
        peak = max(equity_curve)
        current = equity_curve[-1]
        drawdown = (peak - current) / peak
        return drawdown
        
    def _cleanup_old_trades(self):
        """Remove trades older than 24 hours"""
        cutoff_time = datetime.now() - timedelta(days=1)
        self.daily_trades = [trade for trade in self.daily_trades 
                           if trade['timestamp'] > cutoff_time]
        
        # Recalculate daily PnL
        self.daily_pnl = sum(trade['pnl'] for trade in self.daily_trades)
