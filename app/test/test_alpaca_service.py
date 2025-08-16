import asyncio
import unittest
import os

try:
    from app.services.alpaca_service import AlpacaMarketService
except ImportError:
    from services.alpaca_service import AlpacaMarketService
    


class TestAlpacaServices(unittest.TestCase):

    def setUp(self):
        self.service = AlpacaMarketService()

    def test_historical_bars(self):
        async def async_test():
            test_symbols = ["AAPL", "LDOS", "IART", "OAKU"]

            for symbol in test_symbols:
                try:
                    bars = await self.service.get_historical_bars(symbol)
                    self.assertIsNotNone(bars)
                except Exception as e:
                    print(f"Unknown error for {symbol}: {e}")
                    self.fail(f"Test failed for {symbol}: {e}")
        
        asyncio.run(async_test())
    

    def test_ticker_search(self):
        async def async_test():
            test_queries = ["AAPL", "apple", "microsoft"]
            
            for query in test_queries:
                print(f"\nQuery: '{query}'")
                result = await self.service.get_bundle_of_tickers(query)
                print(f"Results: {len(result['results'])} matches")
                
                self.assertIn('results', result)
                self.assertIsInstance(result['results'], list)
                
                for i, company in enumerate(result['results'][:3]):
                    print(f"Company: {company['name']}, Ticker: {company['ticker']}, Exchange: {company['exchange']}")
                    self.assertIn('name', company)
                    self.assertIn('ticker', company)
                    self.assertIn('exchange', company)
                
                print(result)
                print("-------------------------------------------")
        
        asyncio.run(async_test())

    def test_get_minute_prices_for_day(self):
        async def async_test():
            test_symbols = ["AAPL", "LDOS"]
            test_time = "2025-08-01"

            for symbol in test_symbols:
                try:
                    bars = await self.service.get_minute_prices_for_day(symbol, test_time)
                    self.assertIsNotNone(bars)
                except Exception as e:
                    print(f"Unknown error for {symbol}: {e}")
                    self.fail(f"Test failed for {symbol}: {e}")
        
        asyncio.run(async_test())

if __name__ == "__main__":
    unittest.main()