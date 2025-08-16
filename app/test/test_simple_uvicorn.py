from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx
import json

# Application 
app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple routes
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Test functions to see if FAST works
async def test_route():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/")
        print("Status code:", response.status_code)

        try:
            print("Simple chat response:", response.json())
        except Exception as e:
            print("Failed to parse JSON:", response.text)



async def test_route_2():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        print("Status code:", response.status_code)

        try:
            print("Simple chat response:", response.json())
        except Exception as e:
            print("Failed to parse JSON:", response.text)

if __name__ == "__main__":
    asyncio.run(test_route())
    asyncio.run(test_route_2())
