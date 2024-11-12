from app import app, db, scheduler, performance_history, logger
from trading.oanda_client import OandaClient
from trading.lorentzian import LorentzianClassifier
from trading.risk_manager import RiskManager
from trading.technical_indicators import TechnicalIndicators
from flask import jsonify
from datetime import datetime
import atexit

def check_and_execute_trades():
    """Main trading logic"""
    try:
        oanda_client = OandaClient()  # Create new instance for each execution
        lorentzian = LorentzianClassifier()
        risk_manager = RiskManager()
        tech_indicators = TechnicalIndicators()

        # Get latest market data
        market_data = oanda_client.get_market_data()
        if not market_data:
            logger.warning("Failed to get market data")
            return

        # Get trading signals
        lorentzian_signal = lorentzian.get_signal(market_data)
        ema_signal = tech_indicators.check_ema_filter(market_data)
        sma_signal = tech_indicators.check_sma_filter(market_data)

        # Check if signals align for a trade
        if lorentzian_signal and lorentzian_signal == ema_signal == sma_signal:
            # Check risk parameters
            if risk_manager.can_trade():
                # Get account info for position sizing
                account_info = oanda_client.get_account_info()
                if account_info:
                    position_size = risk_manager.calculate_position_size(
                        float(account_info['balance'])
                    )
                    
                    # Execute trade
                    trade_result = oanda_client.execute_trade(lorentzian_signal, position_size)
                    if trade_result:
                        logger.info(f"Trade executed: {trade_result}")
                        # Update risk metrics
                        if 'orderFillTransaction' in trade_result:
                            risk_manager.update_trade_metrics(
                                float(trade_result['orderFillTransaction']['pl'])
                            )
                    else:
                        logger.error("Trade execution failed")
                        
    except Exception as e:
        logger.error(f"Error in trading logic: {str(e)}")

def update_performance_data():
    """Update performance tracking data"""
    try:
        oanda_client = OandaClient()  # Create new instance for each update
        account_info = oanda_client.get_account_info()
        if account_info:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            performance_history['dates'].append(current_time)
            performance_history['balances'].append(float(account_info['balance']))
            
            # Keep only last 100 data points
            if len(performance_history['dates']) > 100:
                performance_history['dates'] = performance_history['dates'][-100:]
                performance_history['balances'] = performance_history['balances'][-100:]
    except Exception as e:
        logger.error(f"Error updating performance data: {str(e)}")

@app.route('/api/performance')
def get_performance():
    """API endpoint for performance data"""
    return jsonify(performance_history)

@app.route('/api/close_trade/<trade_id>', methods=['POST'])
def close_trade(trade_id):
    """API endpoint to close a specific trade"""
    try:
        oanda_client = OandaClient()  # Create new instance for each request
        success = oanda_client.close_trade(trade_id)
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error closing trade {trade_id}: {str(e)}")
        return jsonify({'success': False})

def init_scheduler():
    """Initialize the scheduler jobs"""
    try:
        # Trading job - runs every 5 minutes
        scheduler.add_job(
            func=check_and_execute_trades,
            trigger="interval",
            minutes=5,
            id='trading_job'
        )
        
        # Performance tracking job - runs every 15 minutes
        scheduler.add_job(
            func=update_performance_data,
            trigger="interval",
            minutes=15,
            id='performance_job'
        )
        
        scheduler.start()
        logger.info("Scheduler initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing scheduler: {str(e)}")

def cleanup_scheduler():
    """Cleanup scheduler on application shutdown"""
    scheduler.shutdown()

# Register cleanup function
atexit.register(cleanup_scheduler)

if __name__ == "__main__":
    # Initialize scheduler
    init_scheduler()
    
    # Run initial performance update
    update_performance_data()
    
    # Start Flask application
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False  # Set to False in production
    )
