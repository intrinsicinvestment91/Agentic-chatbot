import os
import asyncio
from dotenv import load_dotenv
from clients.llm_client import query as llm_query  # ✅ Unified LLM client

# Load environment variables
load_dotenv()

class HRDesk:
    """
    HRDesk Agent – handles HR-related tasks using RouteLLM → DeepSeek backend.
    """

    @staticmethod
    async def handle_request(request: str) -> dict:
        """
        Processes an HR-related request (e.g., employee query, HR policy).
        Routes through the unified LLM client.
        """
        try:
            response = await llm_query(f"HRDesk: {request}")
            return {"status": "success", "agent": "HRDesk", "response": response}
        except Exception as e:
            return {"status": "error", "agent": "HRDesk", "details": str(e)}
