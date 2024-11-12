import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.instruments as instruments
import os
import re
from datetime import datetime, timedelta
import logging
import time
from requests.exceptions import RequestException

class OandaClient:
    def __init__(self, max_retries=3, retry_delay=1):
        self.api_key = os.environ.get('OANDA_API_KEY')
        self.account_id = os.environ.get('OANDA_ACCOUNT_ID')
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.api = None
        self.instrument = "EUR_USD"  # Default instrument
        
        self._validate_credentials()
        self._initialize_api()
        
    def _validate_credentials(self):
        """Validate API credentials format"""
        if not self.api_key:
            raise ValueError("OANDA API key is not set in environment variables")
        if not self.account_id:
            raise ValueError("OANDA account ID is not set in environment variables")
            
        # Validate API key format (should be alphanumeric)
        if not re.match(r'^[a-zA-Z0-9-]+$', self.api_key):
            raise ValueError("Invalid OANDA API key format")
            
        # Validate account ID format (should match OANDA's format)
        if not re.match(r'^\d{3}-\d{3}-\d{8}-\d{3}$', self.account_id):
            raise ValueError("Invalid OANDA account ID format")
            
    def _initialize_api(self):
        """Initialize API client with retry mechanism"""
        try:
            self.api = oandapyV20.API(access_token=self.api_key,
                                    environment="practice")
            if not self.verify_connection():
                raise ValueError("Failed to establish connection with OANDA API")
        except Exception as e:
            self.logger.error(f"Failed to initialize OANDA client: {str(e)}")
            raise

    def _make_request(self, request_obj, max_retries=None):
        """Make API request with retry mechanism"""
        retries = max_retries if max_retries is not None else self.max_retries
        last_error = None
        
        for attempt in range(retries):
            try:
                response = self.api.request(request_obj)
                return response
            except RequestException as e:
                last_error = e
                self.logger.warning(f"API request failed (attempt {attempt + 1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error in API request: {str(e)}")
                raise
                
        if last_error:
            self.logger.error(f"API request failed after {retries} attempts: {str(last_error)}")
            raise last_error
            
    def verify_connection(self):
        """Verify API connection and credentials"""
        try:
            r = accounts.AccountSummary(self.account_id)
            response = self._make_request(r)
            
            if 'account' in response:
                self.logger.info("Successfully connected to OANDA API")
                return True
            else:
                self.logger.error("Invalid response format from OANDA API")
                return False
        except Exception as e:
            self.logger.error(f"Failed to connect to OANDA API: {str(e)}")
            return False
        
    def get_market_data(self, count=100):
        """Get historical market data with retry mechanism"""
        try:
            params = {
                "count": count,
                "granularity": "M5"  # 5-minute candles
            }
            
            r = instruments.InstrumentsCandles(instrument=self.instrument,
                                           params=params)
            response = self._make_request(r)
            
            if 'candles' not in response:
                self.logger.error("Invalid market data response: 'candles' field missing")
                return None
                
            candles = response['candles']
            if not candles:
                self.logger.warning("No candle data received from API")
                return None
                
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
        """Execute trade with retry mechanism"""
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
            response = self._make_request(r)
            
            if 'orderCreateTransaction' in response:
                self.logger.info(f"Trade executed successfully: {direction} {units} units")
                return response
            else:
                self.logger.error("Invalid trade execution response: missing orderCreateTransaction")
                return None
                
        except Exception as e:
            self.logger.error(f"Trade execution error: {str(e)}")
            return None

    def get_open_trades(self):
        """Get all open trades with retry mechanism"""
        if not self.verify_connection():
            self.logger.warning("Cannot get open trades: Not connected to OANDA API")
            return []
            
        try:
            r = trades.OpenTrades(self.account_id)
            response = self._make_request(r)
            
            if 'trades' not in response:
                self.logger.error("Invalid response format: 'trades' field missing")
                return []
                
            return response['trades']
        except Exception as e:
            self.logger.error(f"Error getting open trades: {str(e)}")
            return []

    def get_account_info(self):
        """Get account information with retry mechanism"""
        if not self.verify_connection():
            self.logger.warning("Cannot get account info: Not connected to OANDA API")
            return None
            
        try:
            r = accounts.AccountSummary(self.account_id)
            response = self._make_request(r)
            
            if 'account' not in response:
                self.logger.error("Invalid response format: 'account' field missing")
                return None
                
            return response['account']
        except Exception as e:
            self.logger.error(f"Error getting account info: {str(e)}")
            return None

    def close_trade(self, trade_id):
        """Close specific trade with retry mechanism"""
        if not self.verify_connection():
            self.logger.warning("Cannot close trade: Not connected to OANDA API")
            return False
            
        try:
            r = trades.TradeClose(self.account_id, trade_id)
            response = self._make_request(r)
            
            if 'orderCreateTransaction' in response:
                self.logger.info(f"Trade {trade_id} closed successfully")
                return True
            else:
                self.logger.error(f"Invalid response when closing trade {trade_id}: missing orderCreateTransaction")
                return False
                
        except Exception as e:
            self.logger.error(f"Error closing trade {trade_id}: {str(e)}")
            return False

    def get_position_data(self, instrument):
        """Get historical price data for a specific position"""
        if not self.verify_connection():
            self.logger.warning("Cannot get position data: Not connected to OANDA API")
            return None
            
        try:
            params = {
                "count": 100,  # Last 100 candles
                "granularity": "M5"  # 5-minute candles
            }
            
            r = instruments.InstrumentsCandles(instrument=instrument,
                                           params=params)
            response = self._make_request(r)
            
            if 'candles' in response:
                return [float(candle['mid']['c']) for candle in response['candles'] 
                       if candle['complete']]
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting position data: {str(e)}")
            return None