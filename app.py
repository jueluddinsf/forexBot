import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime, timedelta
import pytz
import time

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

# Initialize performance tracking with timezone and default values
performance_history = {
    'dates': [],
    'balances': [],
    'last_update': None,
    'pnl_distribution': {'labels': [], 'values': []},
    'win_rate': {'wins': 0, 'losses': 0},
    'risk_metrics': {
        'market_risk': 0,
        'drawdown_risk': 0,
        'leverage_risk': 0,
        'correlation_risk': 0,
        'volatility_risk': 0
    }
}

def get_default_account_info():
    """Return default account info structure with float values"""
    return {
        'balance': 0.0,
        'unrealizedPL': 0.0,
        'marginUsed': 0.0,
        'currency': 'USD'
    }

def get_default_indicators():
    """Return default indicator values"""
    return {
        'Current_Price': None,
        'EMA': None,
        'SMA': None,
        'EMA_Period': 200,
        'SMA_Period': 200
    }

@app.route('/')
def dashboard():
    """Main dashboard route with enhanced error handling"""
    api_error = None
    trades = []
    account_info = get_default_account_info()
    trading_metrics = {'win_rate': None, 'total_trades': 0, 'profit_factor': None,
                      'sharpe_ratio': None, 'max_drawdown': None}
    
    try:
        oanda_client = OandaClient()
        if not oanda_client.verify_connection():
            api_error = "Unable to establish connection with OANDA API. Please verify your credentials."
        else:
            trades = oanda_client.get_open_trades()
            acc_info = oanda_client.get_account_info()
            
            # Validate and process account info
            if acc_info and isinstance(acc_info, dict):
                try:
                    account_info = {
                        'balance': float(acc_info.get('balance', 0)),
                        'unrealizedPL': float(acc_info.get('unrealizedPL', 0)),
                        'marginUsed': float(acc_info.get('marginUsed', 0)),
                        'currency': acc_info.get('currency', 'USD')
                    }
                except (ValueError, TypeError) as e:
                    logger.error(f"Error converting account values: {str(e)}")
                    account_info = get_default_account_info()
                
                # Calculate trading metrics
                trading_metrics = calculate_trading_metrics()
                
    except ValueError as e:
        api_error = str(e)
        logger.error(f"OANDA client initialization error: {str(e)}")
    except Exception as e:
        api_error = "An unexpected error occurred while connecting to OANDA API."
        logger.error(f"Dashboard error: {str(e)}")
    
    # Get trading signals with enhanced validation
    trading_signals = {'pairs': {}, 'timestamp': datetime.now(pytz.UTC)}
    signals_data = app.config.get('TRADING_SIGNALS', {})
    
    if isinstance(signals_data, dict):
        validated_signals = {}
        for pair, signal_info in signals_data.items():
            if isinstance(signal_info, dict):
                # Validate and convert indicator values
                indicators = signal_info.get('indicators', {})
                if isinstance(indicators, dict):
                    try:
                        validated_indicators = {
                            'Current_Price': float(indicators.get('Current_Price')) if indicators.get('Current_Price') is not None else None,
                            'EMA': float(indicators.get('EMA')) if indicators.get('EMA') is not None else None,
                            'SMA': float(indicators.get('SMA')) if indicators.get('SMA') is not None else None,
                            'EMA_Period': int(indicators.get('EMA_Period', 200)),
                            'SMA_Period': int(indicators.get('SMA_Period', 200))
                        }
                    except (ValueError, TypeError):
                        validated_indicators = get_default_indicators()
                else:
                    validated_indicators = get_default_indicators()
                
                validated_signals[pair] = {
                    'lorentzian': signal_info.get('lorentzian', 'HOLD'),
                    'ema': signal_info.get('ema', 'HOLD'),
                    'sma': signal_info.get('sma', 'HOLD'),
                    'indicators': validated_indicators
                }
        
        trading_signals['pairs'] = validated_signals
    
    return render_template('dashboard.html',
                         trades=trades or [],
                         account_info=account_info,
                         trading_metrics=trading_metrics,
                         trading_signals=trading_signals,
                         api_error=api_error,
                         timedelta=timedelta)

@app.route('/api/test_trading', methods=['POST'])
def test_trading():
    try:
        oanda_client = OandaClient()
        test_pair = "EUR_USD"
        units = 100

        # Test buy
        buy_result = oanda_client.execute_trade("LONG", units, test_pair)
        if not buy_result:
            return jsonify({'success': False, 'error': 'Buy test failed'}), 400

        # Get the trade ID and verify trade exists
        trade_id = buy_result.get('orderFillTransaction', {}).get('id')
        if not trade_id:
            return jsonify({'success': False, 'error': 'Could not get trade ID'}), 400

        # Add delay to ensure trade is processed
        time.sleep(2)

        # Verify trade exists before closing
        open_trades = oanda_client.get_open_trades()
        trade_exists = any(trade['id'] == trade_id for trade in open_trades)
        if not trade_exists:
            return jsonify({'success': False, 'error': 'Trade verification failed'}), 400

        # Test close with verification
        close_result = oanda_client.close_trade(trade_id)
        if not close_result:
            return jsonify({'success': False, 'error': 'Close test failed'}), 400

        # Add delay before next operation
        time.sleep(2)

        # Test sell
        sell_result = oanda_client.execute_trade("SHORT", units, test_pair)
        if not sell_result:
            return jsonify({'success': False, 'error': 'Sell test failed'}), 400

        # Get and verify second trade
        trade_id = sell_result.get('orderFillTransaction', {}).get('id')
        if trade_id:
            time.sleep(2)
            open_trades = oanda_client.get_open_trades()
            trade_exists = any(trade['id'] == trade_id for trade in open_trades)
            if trade_exists:
                oanda_client.close_trade(trade_id)

        return jsonify({
            'success': True,
            'message': 'All trading operations tested successfully'
        })

    except Exception as e:
        logger.error(f"Error in test trading: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        }), 500

@app.route('/api/performance_analytics')
def get_performance_analytics():
    """API endpoint for performance analytics data with enhanced validation and error handling"""
    try:
        # Initialize response data with defaults
        response_data = {
            'performance': {
                'dates': [],
                'balances': [],
                'last_update': None
            },
            'pnl_distribution': {
                'labels': [],
                'values': []
            },
            'win_rate': {
                'wins': 0,
                'losses': 0
            },
            'risk_metrics': {
                'market_risk': 0,
                'drawdown_risk': 0,
                'leverage_risk': 0,
                'correlation_risk': 0,
                'volatility_risk': 0
            }
        }

        # Update with actual data if available
        if performance_history:
            response_data.update({
                'performance': {
                    'dates': performance_history.get('dates', []),
                    'balances': [float(b) if b is not None else 0.0 for b in performance_history.get('balances', [])],
                    'last_update': performance_history.get('last_update').isoformat() if performance_history.get('last_update') else None
                },
                'pnl_distribution': performance_history.get('pnl_distribution', {'labels': [], 'values': []}),
                'win_rate': performance_history.get('win_rate', {'wins': 0, 'losses': 0}),
                'risk_metrics': performance_history.get('risk_metrics', {
                    'market_risk': 0,
                    'drawdown_risk': 0,
                    'leverage_risk': 0,
                    'correlation_risk': 0,
                    'volatility_risk': 0
                })
            })

        # Validate data consistency
        if len(response_data['performance']['dates']) != len(response_data['performance']['balances']):
            logger.error("Data inconsistency: dates and balances arrays have different lengths")
            return jsonify({
                'error': 'Data inconsistency detected',
                'data': response_data
            }), 500

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error in performance analytics endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to fetch performance data',
            'data': response_data
        }), 500

def calculate_trading_metrics():
    """Calculate trading performance metrics with enhanced error handling"""
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
        
        # Calculate metrics with validation
        wins = sum(1 for trade in trades if trade.pnl and trade.pnl > 0)
        total_trades = len(trades)
        win_rate = (wins / total_trades * 100) if total_trades > 0 else None
        
        # Profit Factor calculation with validation
        gross_profit = sum(trade.pnl for trade in trades if trade.pnl and trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in trades if trade.pnl and trade.pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else None
        
        return {
            'win_rate': win_rate,
            'total_trades': total_trades,
            'profit_factor': profit_factor,
            'sharpe_ratio': None,
            'max_drawdown': None
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

with app.app_context():
    import models
    db.create_all()
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)