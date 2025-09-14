# FastAPI for Gemini AI req
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Slow API for rate limiter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Directory issues best solution rn
try:
    from app.services.gemini_service import GeminiService
    from app.services.alpaca_service import AlpacaMarketService
    from app.db import get_ticker_connection, init_ticker_db
except ImportError:
    from services.gemini_service import GeminiService
    from services.alpaca_service import AlpacaMarketService
    from db import get_ticker_connection, init_ticker_db

# Misc
try:
    from app.models import *
except ImportError:
    from models import *

import logging
import json
import uvicorn
from typing import AsyncGenerator



# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FASTAPI app
app = FastAPI (
    version="1.0.0"
)

# Rate Limiter (# of API calls)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Cross origin resource sharing middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection of services
async def get_gemini_service() -> GeminiService:
    return GeminiService()

async def get_alpaca_service() -> AlpacaMarketService:
    return AlpacaMarketService()  

# Dependency injection of databases
    
def get_ticker_db():
    conn = get_ticker_connection()
    try:
        yield conn
    finally:
        conn.close()
 


# API startup
@app.on_event("startup")
async def startup():
    init_ticker_db()

    conn = get_ticker_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM tickers")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Populate DB
        alpaca = AlpacaMarketService()
        ticker_data = await alpaca.fetch_all_tickers() # fetch tickers with alpaca service
        tickers = ticker_data["results"]
        print(ticker_data)
        # Populate
        conn.executemany(
            "INSERT INTO tickers (ticker, company_name, exchange) VALUES (?, ?, ?)", 
                    [(t["ticker"], t["company_name"], t["exchange"]) for t in tickers]
        )
        conn.commit()
    
    # # Checking if anything
    cursor = conn.execute("SELECT ticker, company_name, exchange FROM tickers ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"Top ticker → {row['ticker']} ({row['company_name']} on {row['exchange']})")

    conn.close()




# Routes to test
@app.get("/")
async def root():
    return {"message": "Gemini FastAPI Integration API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Gemini FastAPI Integration"}






# Gemini Routes
# ---------------------------------------------------- #
@app.post("/gemini/test", response_model=ChatResponse)
@limiter.limit("3/minute")
async def simple_route(request: Request, chat_request: ChatRequest):
    return ChatResponse( response=f"Echo: {chat_request.message}", model=chat_request.model, usage=None)



@app.post("/gemini/simple", response_model=ChatResponse)
@limiter.limit("3/minute")
async def simple_chat( request: Request, chat_request: ChatRequest,  gemini_service: GeminiService = Depends(get_gemini_service) ):
    try:
        result = await gemini_service.simple_chat(
            message=chat_request.message,
            model=chat_request.model,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens
        )
        return ChatResponse( response=result["response"], usage=result["usage"], model=result["model"])
    except Exception as e:
        logger.error(f"Error in simple_chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/gemini/conversation", response_model=ChatResponse)
@limiter.limit("10/minute")
async def conversation_chat( request: Request, conversation_request: ConversationRequest, gemini_service: GeminiService = Depends(get_gemini_service)):
    try:
        result = await gemini_service.create_chat_completion(
            messages=conversation_request.messages,
            model=conversation_request.model,
            temperature=conversation_request.temperature,
            max_tokens=conversation_request.max_tokens
        )
        
        return ChatResponse( response=result["response"], usage=result["usage"], model=result["model"])
    except Exception as e:
        logger.error(f"Error in conversation_chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/gemini/stream")
@limiter.limit("10/minute")
async def stream_chat( request: Request, conversation_request: ConversationRequest, gemini_service: GeminiService = Depends(get_gemini_service)):
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            async for chunk in gemini_service.streaming_chat_completion(
                messages=conversation_request.messages,
                model=conversation_request.model,
                temperature=conversation_request.temperature,
                max_tokens=conversation_request.max_tokens
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Error in stream_chat: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache", 
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )
# ---------------------------------------------------- #







# Alpaca Routes
# ---------------------------------------------------- #
@app.get("/alpaca/fetch_tickers")
@limiter.limit("20/minute")
async def fetch_markets(request: Request, query: str, limit: int = 5, alpaca_service: AlpacaMarketService = Depends(get_alpaca_service)):
    try:
        result = await alpaca_service.get_bundle_of_tickers(query=query, limit_payload=limit)
        return result
    except Exception as e:
        logger.error(f"Error in fetch_markets Alpaca API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/alpaca/fetch_markets")
@limiter.limit("20/minute")
async def fetch_markets(request: Request, query: str, limit: int = 5, alpaca_service: AlpacaMarketService = Depends(get_alpaca_service)):
    try:
        result = await alpaca_service.get_bundle_of_tickers(query=query, limit_payload=limit)
        return result
    except Exception as e:
        logger.error(f"Error in fetch_markets Alpaca API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/alpaca/fetch_tickers")
async def fetch_tickers(request: Request):
    return {"detail": "Not added"}



@app.get("/alpaca/cache/status")
async def get_alpaca_cache_status(request: Request, alpaca_service: AlpacaMarketService = Depends(get_alpaca_service)):
    """Get the current cache status for popular stocks"""
    try:
        cache_status = alpaca_service.get_cache_status()
        return cache_status
    except Exception as e:
        logger.error(f"Error getting cache status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/alpaca/cache/refresh")
async def refresh_alpaca_cache(request: Request, alpaca_service: AlpacaMarketService = Depends(get_alpaca_service)):
    """Manually refresh the popular stocks cache"""
    try:
        refreshed_stocks = alpaca_service.refresh_popular_stocks_cache()
        return {
            "message": "Cache refreshed successfully",
            "refreshed_count": len(refreshed_stocks),
            "cache_status": alpaca_service.get_cache_status()
        }
    except Exception as e:
        logger.error(f"Error refreshing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/alpaca/fetch_company_bars")
async def fetch_company_historical_bars(request: Request):
    return {"detail": "Not added"}

# ---------------------------------------------------- #










# News Routes
# ---------------------------------------------------- #





# ---------------------------------------------------- #











# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not Found", "detail": f"Route {request.url.path} not found"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return {"error": "Internal server error", "detail": str(exc)}

