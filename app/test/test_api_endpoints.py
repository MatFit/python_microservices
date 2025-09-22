import requests
import json

BASE_URL = "http://localhost:8000"

def test_ticker_search():
    
    tests = [
        ("AAPL", 10),
        ("apple", 5),
        ("MSFT", 3),
        ("", 10),
        ("NONEXISTENT", 10)
    ]
    
    for query, limit in tests:
        url = f"{BASE_URL}/tickers/search?query={query}&limit={limit}"
        print(f"\n🔍 Testing: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"Status: {response.status_code}")
                data = response.json()
                results = data.get("results", [])
                print(f"Found {len(results)} results")
                
                if results:
                    print(f"First result: {results[0]}")
                else:
                    print("No results returned")
                    
            else:
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_ticker_search()