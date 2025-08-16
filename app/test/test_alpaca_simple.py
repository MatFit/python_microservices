#!/usr/bin/env python3
"""
Simple test script for AlpacaService that can be run from the test directory.
Usage: python3 test_alpaca_simple.py
"""

import asyncio
import sys
import os

# Add the parent directory (app) to Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

async def test_alpaca_service():
    """Test the AlpacaService"""
    try:
        print("Testing AlpacaService...")
        
        # Import the service
        from services.alpaca_service import AlpacaMarketService
        
        # Create service instance
        service = AlpacaMarketService()
        print("✓ Service created successfully")
        
        # Test ticker search
        print("\nTesting ticker search...")
        result = await service.get_bundle_of_tickers("AAPL", 5)
        print(f"✓ Ticker search result: {len(result.get('results', []))} matches")
        
        print("\n🎉 AlpacaService test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the test directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_alpaca_service())
    sys.exit(0 if success else 1)
