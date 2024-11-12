import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.instruments as instruments
import os
from datetime import datetime, timedelta
import logging

class OandaClient:
    def __init__(self):
        self.api_key = os.environ.get('OANDA_API_KEY')
        self.account_id = os.environ.get('OANDA_ACCOUNT_ID')
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("OANDA_API_KEY environment variable is not set")
        if not self.account_id:
            raise ValueError("OANDA_ACCOUNT_ID environment variable is not set")
            
        try:
            self.api = oandapyV20.API(access_token=self.api_key,
                                  environment="practice")
            self.instrument = "EUR_USD"  # Default instrument
            
            # Verify connection on initialization
            if not self.verify_connection():
                raise ValueError("Failed to establish connection with OANDA API")
        except Exception as e:
            self.logger.error(f"Failed to initialize OANDA client: {str(e)}")
            raise
        
    def verify_connection(self):
        """Verify API connection and credentials"""
        try:
            r = accounts.AccountSummary(self.account_id)
            response = self.api.request(r)
            if 'account' in response:
                self.logger.info("Successfully connected to OANDA API")
                return True
            else:
                self.logger.error("Invalid response from OANDA API")
                return False
        except Exception as e:
            self.logger.error(f"Failed to connect to OANDA API: {str(e)}")
            return False
        
    def get_market_data(self, count=100):
        """Get historical market data"""
        try:
            params = {
                "count": count,
                "granularity": "M5"  # 5-minute candles
            }
            
            r = instruments.InstrumentsCandles(instrument=self.instrument,
                                           params=params)
            response = self.api.request(r)
            
            if 'candles' not in response:
                self.logger.error("Invalid market data response")
                return None
                
            candles = response['candles']
            data = {
                'open': [],
                'high': [],
                'low': [],
                'close': [],
                'volume': []
            }
            
            for candle in candles:
                if candle['complete']:  # Only use completed candles
                    data['open'].append(float(candle['mid']['o']))
                    data['high'].append(float(candle['mid']['h']))
                    data['low'].append(float(candle['mid']['l']))
                    data['close'].append(float(candle['mid']['c']))
                    data['volume'].append(float(candle['volume']))
                    
            return data if any(data.values()) else None
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {str(e)}")
            return None

    def execute_trade(self, direction, units):
        """Execute trade with OANDA"""
        if not self.verify_connection():
            self.logger.error("Cannot execute trade: Not connected to OANDA API")
            return None
            
        try:
            data = {
                "order": {
                    "type": "MARKET",
                    "instrument": self.instrument,
                    "units": units if direction == "LONG" else -units,
                    "timeInForce": "FOK",
                    "positionFill": "DEFAULT"
                }
            }
            
            r = orders.OrderCreate(self.account_id, data=data)
            response = self.api.request(r)
            
            if 'orderCreateTransaction' in response:
                self.logger.info(f"Trade executed successfully: {direction} {units} units")
                return response
            else:
                self.logger.error("Invalid trade execution response")
                return None
                
        except Exception as e:
            self.logger.error(f"Trade execution error: {str(e)}")
            return None

    def get_open_trades(self):
        """Get all open trades"""
        if not self.verify_connection():
            return []
            
        try:
            r = trades.OpenTrades(self.account_id)
            response = self.api.request(r)
            return response.get('trades', [])
        except Exception as e:
            self.logger.error(f"Error getting open trades: {str(e)}")
            return []

    def get_account_info(self):
        """Get account information"""
        if not self.verify_connection():
            return None
            
        try:
            r = accounts.AccountSummary(self.account_id)
            response = self.api.request(r)
            return response.get('account')
        except Exception as e:
            self.logger.error(f"Error getting account info: {str(e)}")
            return None

    def close_trade(self, trade_id):
        """Close specific trade"""
        if not self.verify_connection():
            return False
            
        try:
            r = trades.TradeClose(self.account_id, trade_id)
            response = self.api.request(r)
            
            if 'orderCreateTransaction' in response:
                self.logger.info(f"Trade {trade_id} closed successfully")
                return True
            else:
                self.logger.error(f"Invalid response when closing trade {trade_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error closing trade: {str(e)}")
            return False
