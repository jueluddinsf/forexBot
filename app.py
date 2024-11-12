import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import numpy as np
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "trading_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()

# Import trading components
from trading.oanda_client import OandaClient
from trading.lorentzian import LorentzianClassifier
from trading.risk_manager import RiskManager
from trading.technical_indicators import TechnicalIndicators

# Initialize performance tracking
performance_history = {
    'dates': [],
    'balances': []
}

@app.route('/')
def dashboard():
    """Main dashboard route"""
    api_error = None
    trades = []
    account_info = {'balance': 0, 'unrealizedPL': 0, 'marginUsed': 0}
    trading_metrics = {'win_rate': None, 'total_trades': 0, 'profit_factor': None,
                      'sharpe_ratio': None, 'max_drawdown': None}
    
    try:
        oanda_client = OandaClient()
        if not oanda_client.verify_connection():
            api_error = "Unable to establish connection with OANDA API. Please verify your credentials."
        else:
            trades = oanda_client.get_open_trades()
            account_info = oanda_client.get_account_info()
            
            # Calculate trading metrics
            if account_info:
                trading_metrics = calculate_trading_metrics()
                
    except ValueError as e:
        api_error = str(e)
        logger.error(f"OANDA client initialization error: {str(e)}")
    except Exception as e:
        api_error = "An unexpected error occurred while connecting to OANDA API."
        logger.error(f"Dashboard error: {str(e)}")
    
    return render_template('dashboard.html',
                         trades=trades or [],
                         account_info=account_info or {'balance': 0, 'unrealizedPL': 0, 'marginUsed': 0},
                         trading_metrics=trading_metrics,
                         api_error=api_error)

@app.route('/api/performance_analytics')
def get_performance_analytics():
    """API endpoint for performance analytics data"""
    try:
        # Get trading metrics from database
        trades_data = get_trades_data()
        risk_manager = RiskManager()
        
        # Calculate various metrics
        pnl_distribution = calculate_pnl_distribution(trades_data)
        win_rate = calculate_win_rate(trades_data)
        risk_metrics = calculate_risk_metrics(risk_manager)
        
        return jsonify({
            'performance': performance_history,
            'pnl_distribution': pnl_distribution,
            'win_rate': win_rate,
            'risk_metrics': risk_metrics
        })
    except Exception as e:
        logger.error(f"Error getting performance analytics: {str(e)}")
        return jsonify({
            'performance': {'dates': [], 'balances': []},
            'pnl_distribution': {'labels': [], 'values': []},
            'win_rate': {'wins': 0, 'losses': 0},
            'risk_metrics': {
                'market_risk': 0,
                'drawdown_risk': 0,
                'leverage_risk': 0,
                'correlation_risk': 0,
                'volatility_risk': 0
            }
        })

def calculate_trading_metrics():
    """Calculate trading performance metrics"""
    try:
        from models import Trade
        
        trades = Trade.query.all()
        if not trades:
            return {
                'win_rate': None,
                'total_trades': 0,
                'profit_factor': None,
                'sharpe_ratio': None,
                'max_drawdown': None
            }
        
        # Calculate metrics
        wins = sum(1 for trade in trades if trade.pnl and trade.pnl > 0)
        total_trades = len(trades)
        win_rate = (wins / total_trades * 100) if total_trades > 0 else None
        
        # Profit Factor
        gross_profit = sum(trade.pnl for trade in trades if trade.pnl and trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in trades if trade.pnl and trade.pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else None
        
        # Sharpe Ratio
        if total_trades > 0:
            returns = [trade.pnl for trade in trades if trade.pnl]
            if returns:
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = np.sqrt(252) * (avg_return / std_return) if std_return != 0 else None
            else:
                sharpe_ratio = None
        else:
            sharpe_ratio = None
        
        # Max Drawdown
        if trades:
            balances = np.cumsum([trade.pnl for trade in trades if trade.pnl])
            peak = np.maximum.accumulate(balances)
            drawdown = (peak - balances) / peak * 100
            max_drawdown = np.max(drawdown) if len(drawdown) > 0 else None
        else:
            max_drawdown = None
        
        return {
            'win_rate': win_rate,
            'total_trades': total_trades,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }
    except Exception as e:
        logger.error(f"Error calculating trading metrics: {str(e)}")
        return {
            'win_rate': None,
            'total_trades': 0,
            'profit_factor': None,
            'sharpe_ratio': None,
            'max_drawdown': None
        }

def get_trades_data():
    """Get historical trades data from database"""
    from models import Trade
    return Trade.query.all()

def calculate_pnl_distribution(trades):
    """Calculate P/L distribution data"""
    if not trades:
        return {'labels': [], 'values': []}
    
    pnl_values = [trade.pnl for trade in trades if trade.pnl]
    if not pnl_values:
        return {'labels': [], 'values': []}
    
    hist, bins = np.histogram(pnl_values, bins=10)
    labels = [f"{bins[i]:.2f} to {bins[i+1]:.2f}" for i in range(len(bins)-1)]
    
    return {
        'labels': labels,
        'values': hist.tolist()
    }

def calculate_win_rate(trades):
    """Calculate win/loss ratio"""
    if not trades:
        return {'wins': 0, 'losses': 0}
    
    wins = sum(1 for trade in trades if trade.pnl and trade.pnl > 0)
    losses = sum(1 for trade in trades if trade.pnl and trade.pnl < 0)
    
    return {
        'wins': wins,
        'losses': losses
    }

def calculate_risk_metrics(risk_manager):
    """Calculate current risk metrics"""
    try:
        return {
            'market_risk': risk_manager._calculate_market_risk(),
            'drawdown_risk': risk_manager._calculate_current_drawdown() * 100,
            'leverage_risk': risk_manager._calculate_leverage_risk(),
            'correlation_risk': risk_manager._calculate_correlation_risk(),
            'volatility_risk': risk_manager._calculate_volatility_risk()
        }
    except Exception as e:
        logger.error(f"Error calculating risk metrics: {str(e)}")
        return {
            'market_risk': 0,
            'drawdown_risk': 0,
            'leverage_risk': 0,
            'correlation_risk': 0,
            'volatility_risk': 0
        }

with app.app_context():
    import models
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
