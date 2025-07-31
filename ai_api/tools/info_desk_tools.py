import os
import asyncio
from dotenv import load_dotenv
from clients.llm_client import query as llm_query  # ✅ Unified LLM client

# Load environment variables
load_dotenv()

class InfoDesk:
    """
    InfoDesk Agent – provides general information and answers user queries.
    Uses RouteLLM → DeepSeek backend through the unified LLM client.
    """

    @staticmethod
    async def provide_info(query_text: str) -> dict:
        """
        Responds to user informational requests.
        Sends the query through the routed LLM backend.
        """
        prompt = f"InfoDesk: Provide accurate and helpful information for the query: {query_text}"
        try:
            response = await llm_query(prompt)
            return {"status": "success", "agent": "InfoDesk", "response": response}
        except Exception as e:
            return {"status": "error", "agent": "InfoDesk", "details": str(e)}
