from app import app, db, scheduler, performance_history, logger
from trading.oanda_client import OandaClient
from trading.lorentzian import LorentzianClassifier
from trading.risk_manager import RiskManager
from trading.technical_indicators import TechnicalIndicators
from flask import jsonify
from datetime import datetime
import atexit
import pytz

def check_and_execute_trades():
    """Main trading logic with multi-pair support"""
    try:
        # Update last scan time
        current_time = datetime.now(pytz.UTC)
        
        oanda_client = OandaClient()
        lorentzian = LorentzianClassifier()
        risk_manager = RiskManager()
        tech_indicators = TechnicalIndicators()
        
        # Get available pairs
        pairs = oanda_client.get_available_pairs()
        if not pairs:
            logger.warning("No trading pairs available")
            return
            
        # Initialize trading signals storage
        app.config['LAST_TRADING_SCAN'] = current_time
        app.config['TRADING_SIGNALS'] = {}
        
        # Process each pair
        for pair in pairs:
            try:
                # Get latest market data for the pair
                market_data = oanda_client.get_market_data(instrument=pair)
                if not market_data:
                    logger.warning(f"Failed to get market data for {pair}")
                    continue
                    
                # Get trading signals
                lorentzian_signal = lorentzian.get_signal(market_data)
                ema_signal = tech_indicators.check_ema_filter(market_data)
                sma_signal = tech_indicators.check_sma_filter(market_data)
                
                # Calculate technical indicators
                ema = tech_indicators.calculate_ema(market_data, tech_indicators.ema_period)
                sma = tech_indicators.calculate_sma(market_data, tech_indicators.sma_period)
                rsi = tech_indicators.calculate_rsi(market_data)
                volatility = risk_manager._calculate_volatility(market_data)
                atr_ratio = tech_indicators.calculate_atr_ratio(market_data)
                
                # Get Lorentzian prediction and trend strength
                prediction_value, trend_strength = lorentzian.get_prediction_values(market_data)
                
                # Store signals and indicators for the pair
                app.config['TRADING_SIGNALS'][pair] = {
                    'lorentzian': lorentzian_signal or 'HOLD',
                    'ema': ema_signal or 'HOLD',
                    'sma': sma_signal or 'HOLD',
                    'indicators': {
                        'Current_Price': float(market_data['close'][-1]) if market_data['close'] else None,
                        'EMA': float(ema.iloc[-1]) if not ema.empty else None,
                        'SMA': float(sma.iloc[-1]) if not sma.empty else None,
                        'Prediction': prediction_value,  # From Lorentzian classifier
                        'Trend_Strength': trend_strength,
                        'RSI': float(rsi.iloc[-1]) if not rsi.empty else None,
                        'Volatility': float(volatility) if volatility is not None else None,
                        'ATR_Ratio': float(atr_ratio) if atr_ratio is not None else None
                    }
                }
                
                # Check if signals align for a trade
                if lorentzian_signal and lorentzian_signal == ema_signal == sma_signal:
                    # Get current positions
                    current_positions = oanda_client.get_open_trades()
                    
                    # Enhanced risk management check
                    can_trade, reason = risk_manager.can_trade(
                        market_data=market_data,
                        current_positions=current_positions
                    )
                    
                    if can_trade:
                        # Get account info for position sizing
                        account_info = oanda_client.get_account_info()
                        if account_info:
                            # Calculate position size with market data consideration
                            position_size = risk_manager.calculate_position_size(
                                float(account_info['balance']),
                                market_data=market_data
                            )
                            
                            # Execute trade
                            trade_result = oanda_client.execute_trade(
                                lorentzian_signal, 
                                position_size,
                                instrument=pair
                            )
                            if trade_result:
                                logger.info(f"Trade executed for {pair}: {trade_result}")
                                if 'orderFillTransaction' in trade_result:
                                    risk_manager.update_trade_metrics(
                                        float(trade_result['orderFillTransaction']['pl'])
                                    )
                            else:
                                logger.error(f"Trade execution failed for {pair}")
                    else:
                        logger.info(f"Trade prevented for {pair} by risk management: {reason}")
                        
            except Exception as e:
                logger.error(f"Error processing pair {pair}: {str(e)}")
                continue
                        
    except Exception as e:
        logger.error(f"Error in trading logic: {str(e)}")

def update_performance_data():
    """Update performance tracking data"""
    try:
        current_time = datetime.now(pytz.UTC)
        
        oanda_client = OandaClient()
        account_info = oanda_client.get_account_info()
        if account_info:
            performance_history['dates'].append(current_time.strftime('%Y-%m-%d %H:%M:%S %Z'))
            performance_history['balances'].append(float(account_info['balance']))
            performance_history['last_update'] = current_time
            
            # Keep only last 100 data points
            if len(performance_history['dates']) > 100:
                performance_history['dates'] = performance_history['dates'][-100:]
                performance_history['balances'] = performance_history['balances'][-100:]
    except Exception as e:
        logger.error(f"Error updating performance data: {str(e)}")

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
        
        # Performance tracking job - runs every 5 minutes
        scheduler.add_job(
            func=update_performance_data,
            trigger="interval",
            minutes=5,
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
