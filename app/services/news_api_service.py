from pydantic import BaseModel
from datetime import date
from dotenv import load_dotenv
from typing import Optional, Dict, Any


try:
    from app.config import settings
except ImportError:
    from config import settings

import requests


# BaseModel - building block for defining data structures and enforcing data validation (may refactor all services to it)
class NewsAPIService:
    def __init__(self):
        load_dotenv(dotenv_path="../.env.newsapi")
        self.api_key = settings.news_api_key
        self.everything_url = settings.news_everything_url
        self.headlines_url = settings.news_headlines_url
        
    def create_params(self, keywords : Optional[str] = "news", 
                                    from_date : Optional[date] = None,
                                    sortBy : Optional[str] = "popularity",
                                    pageSize : Optional[int] = 10):
        params = {
            "apiKey" : self.api_key,
            "q" : keywords,
            "from": from_date.isoformat() if from_date else None,
            "sortBy" : sortBy,
            "language" : "en",
            "pageSize" : pageSize
        }

        # Remove 'v' if None
        params = {k : v for k, v in params.items() if v is not None}

        return params
    
    # Dict[str, Any] -> dictionary key from the parameters and Any being all other json parameters
    async def fetch_everything(self, params : Dict[str, Any]):
        response = requests.get(self.everything_url, params=params)
        response.raise_for_status() # Throw exception
        return response.json()

    async def fetch_headlines(self, params):
        response = requests.get(self.headlines_url, params=params)
        response.raise_for_status() # Throw exception
        return response.json()
        

if __name__ == "__main__":
    news = NewsAPIService()
    params = news.create_params()
    print(news.fetch_everything(params=params))
    
    
    