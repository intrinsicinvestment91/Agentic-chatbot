import os
import aiohttp
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").lower()

# DeepSeek config
DEEPSEEK_API_KEY = os.getenv("CHATBOT_API_KEY", "dummy_key")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "mock-model")

# RouteLLM config
ROUTELLM_API_KEY = os.getenv("ROUTELLM_API_KEY", "dummy_key")
ROUTELLM_API_BASE = os.getenv("ROUTELLM_API_BASE", "")
ROUTELLM_DEFAULT_MODEL = os.getenv("ROUTELLM_DEFAULT_MODEL", "gpt-4o")

headers_common = {"Content-Type": "application/json"}


def _is_mock_mode():
    """Detects if we are running without real keys or endpoints."""
    return (
        DEEPSEEK_API_KEY == "dummy_key"
        or not DEEPSEEK_API_BASE
        or (LLM_PROVIDER == "routellm" and ROUTELLM_API_KEY == "dummy_key")
    )


async def _call_deepseek(prompt: str) -> str:
    """Send query to DeepSeek via Runpod API."""
    if _is_mock_mode():
        return f"[Mock Response] (DeepSeek) You said: {prompt}"

    url = f"{DEEPSEEK_API_BASE}/chat/completions"
    headers = {**headers_common, "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    payload = {"model": DEEPSEEK_MODEL, "messages": [{"role": "user", "content": prompt}]}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "Error: no response")


async def _call_routellm(prompt: str) -> str:
    """Send query to RouteLLM API."""
    if _is_mock_mode():
        return f"[Mock Response] (RouteLLM) You said: {prompt}"

    url = f"{ROUTELLM_API_BASE}/chat/completions"
    headers = {**headers_common, "Authorization": f"Bearer {ROUTELLM_API_KEY}"}
    payload = {"model": ROUTELLM_DEFAULT_MODEL, "messages": [{"role": "user", "content": prompt}]}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "Error: no response")


async def query(prompt: str) -> str:
    """Unified LLM interface for agents with mock fallback."""
    if LLM_PROVIDER == "deepseek":
        return await _call_deepseek(prompt)
    elif LLM_PROVIDER == "routellm":
        return await _call_routellm(prompt)
    else:
        return f"[Mock Response] Unknown LLM_PROVIDER '{LLM_PROVIDER}'"


# Test from command line
if __name__ == "__main__":
    async def _test():
        result = await query("Hello, test from llm_client!")
        print("LLM Response:", result)

    asyncio.run(_test())
