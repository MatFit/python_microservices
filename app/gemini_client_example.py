# tests.py
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

HEADERS   = {
    "Content-Type": "application/json",
    "X-Forwarded-For": "127.0.0.1"
}

async def test_root(client: httpx.AsyncClient) -> None:
    resp = await client.get("/")
    print("ROOT", resp.status_code, resp.json())

async def test_chat_test(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/gemini/test",
        json={
            "message": "ping",
            "model": "gemini-1.5-flash",
            "temperature": 0.2,
            "max_tokens": 5
        },
    )
    print("GEMINI /test", resp.status_code, resp.json())

async def test_simple_chat(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/gemini/simple",
        json={
            "message": "Hello, Gemini!",
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 50
        },
    )
    print("GEMINI /simple", resp.status_code, resp.json())

# Test failed here
async def test_conversation(client: httpx.AsyncClient) -> None:
    messages = [
        {"role": "system",    "content": "You are a helpful assistant."},
        {"role": "user",      "content": "What's the weather like?"},
        {"role": "assistant", "content": "I don't have real‑time weather data."},
        {"role": "user",      "content": "That's okay, tell me about weather in general."}
    ]
    resp = await client.post(
        "/gemini/conversation",
        json={
            "messages": messages,
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 100
        },
    )
    print("GEMINI /conversation", resp.status_code, resp.json())

async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL, headers=HEADERS, timeout=30) as client:
        await test_root(client)
        await test_chat_test(client)
        await test_simple_chat(client)
        await test_conversation(client)

if __name__ == "__main__":
    asyncio.run(main())
