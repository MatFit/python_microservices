from typing import List, Optional, Union
from datetime import datetime, timedelta
from dotenv import load_dotenv

try:
    from app.config import settings
except ImportError:
    from config import settings
    

from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient



class AlpacaMarketService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # If there isn't an attribute '_initialized' create one to indicate that service object is created
        if not hasattr(self, '_initialized'):
            print(f"Singleton pattern in use for {self.__class__.__name__}")
            self._initialized = True
        
            self.alpaca_api_key = settings.alpaca_api_key
            self.alpaca_secret_key = settings.alpaca_secret_key
            self.historical_client = StockHistoricalDataClient(self.alpaca_api_key, self.alpaca_secret_key)
            self.trading_client = TradingClient(self.alpaca_api_key, self.alpaca_secret_key)

            # # Cache for popular stocks to avoid repeated API calls
            # self._popular_stocks_cache = None
            # self._cache_timestamp = None
            # self._cache_duration = 3600
    

    async def get_bundle_of_tickers_temp(self, query: str, limit_payload : int = 10):
            if not query:
                return {"results": []}

            query = query.upper().strip()
            
            try:
                assets = self.trading_client.get_all_assets() # BAD FIX THIS
                matches = []

                for asset in assets:
                    if (query in asset.symbol.upper() or 
                        (asset.name and query in asset.name.upper())):
                        
                        matches.append({
                            'ticker': asset.symbol,
                            'name': asset.name,
                            'exchange': asset.exchange.value if hasattr(asset.exchange, 'value') else str(asset.exchange),
                        })
                        
                        if len(matches) >= limit_payload:
                            break
                
                return {"results": matches}
                
            except Exception as e:
                print(f"Error fetching from Alpaca: {e}")
                return {"results": [], "error": str(e)}


    # TODO: Cache feature so that I can limit API usage this when users are typing in search bar
    async def get_bundle_of_tickers(self, query: str, limit_payload : int = 10):
        if not query:
            return {"results": []}

        query = query.upper().strip()
        
        try:
            assets = self.trading_client.get_all_assets() # BAD FIX THIS
            matches = []

            for asset in assets:
                if (query in asset.symbol.upper() or 
                    (asset.name and query in asset.name.upper())):
                    
                    matches.append({
                        'name': asset.name,
                        'ticker': asset.symbol,
                        'exchange': asset.exchange.value if hasattr(asset.exchange, 'value') else str(asset.exchange),
                    })
                    
                    if len(matches) >= limit_payload:
                        break
            
            return {"results": matches}
            
        except Exception as e:
            print(f"Error fetching from Alpaca: {e}")
            return {"results": [], "error": str(e)}

    

    def _get_popular_stocks(self):
        current_time = datetime.now()
        
        if (self._popular_stocks_cache and self._cache_timestamp and 
            (current_time - self._cache_timestamp).seconds < self._cache_duration):
            return self._popular_stocks_cache
        
        try:
            # Fetch only the popular stocks we care about
            popular_assets = []
            for symbol in self._top_stocks:
                try:
                    asset = self.trading_client.get_asset(symbol)
                    if asset and asset.status == 'active':
                        popular_assets.append({
                            'name': asset.name,
                            'ticker': asset.symbol,
                            'exchange': asset.exchange.value if hasattr(asset.exchange, 'value') else str(asset.exchange),
                            'status': asset.status,
                            'tradable': asset.tradable
                        })
                except Exception:
                    # Skip if asset not found or error
                    continue
            
            # Cache the results
            self._popular_stocks_cache = popular_assets
            self._cache_timestamp = current_time
            
            return popular_assets
            
        except Exception as e:
            print(f"Error fetching popular stocks: {e}")
            return []
            
    


    # def refresh_popular_stocks_cache(self):
    #     self._popular_stocks_cache = None
    #     self._cache_timestamp = None
    #     return self._get_popular_stocks()
    


    # def get_cache_status(self):
    #     if not self._cache_timestamp:
    #         return {"cached": False, "age_seconds": None, "cache_size": 0}
        
    #     age_seconds = (datetime.now() - self._cache_timestamp).seconds
    #     cache_size = len(self._popular_stocks_cache) if self._popular_stocks_cache else 0
        
    #     return {
    #         "cached": True,
    #         "age_seconds": age_seconds,
    #         "cache_duration": self._cache_duration,
    #         "cache_size": cache_size,
    #         "will_expire_in": max(0, self._cache_duration - age_seconds)
    #     }















    async def get_historical_bars(self, symbol: str,
                            timeframe: TimeFrame = TimeFrame.Day, start: Optional[datetime] = None, end: Optional[datetime] = None):
        if not start:
            start = datetime.now() - timedelta(days=30)
        if not end:
            end = datetime.now()
        
        request = StockBarsRequest(
            symbol_or_symbols=symbol, 
            timeframe=timeframe, 
            start=start, 
            end=end
        )
        
        return self.historical_client.get_stock_bars(request)


    # TODO : a method that fetches share price of some company at some particular day for every minute (60 * 24 samples per company)
    async def get_minute_prices_for_day(self, symbol: str, target_date : datetime):
        try:
            if (type(target_date) == str):
                target_date = datetime.strptime(target_date, "%Y-%m-%d")

            start_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                start=start_time,
                end=end_time
            )
            
            bars = self.historical_client.get_stock_bars(request)
            
            minute_data = []
            for bar in bars[symbol]:
                minute_data.append({
                    'timestamp': bar.timestamp,
                    'open': float(bar.open),
                    'high': float(bar.high),
                    'low': float(bar.low),
                    'close': float(bar.close),
                    'volume': int(bar.volume)
                })
            
            
            return {
                'symbol': symbol,
                'date': target_date.strftime('%Y-%m-%d'),
                'total_samples': len(minute_data),
                'data': minute_data,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"Unexpected error : {e}")
            return {
                'symbol': None,
                'date': None,
                'total_samples': 0,
                'data': [],
                'status': 'error',
                'error': str(e)
            }