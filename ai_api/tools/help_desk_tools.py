import os
import asyncio
from dotenv import load_dotenv
from langchain.tools import tool
from clients.llm_client import query as llm_query  # ✅ Unified LLM client

# Load environment variables
load_dotenv()

class HelpDesk:
    """
    HelpDesk Agent – handles support/transaction-related tasks using RouteLLM → DeepSeek backend.
    """

    @staticmethod
    async def transaction(sender_id: int, receiver_id: int) -> dict:
        """
        Processes a cryptocurrency transaction request.
        Routes through the unified LLM client for intelligent handling.
        """
        prompt = f"Process cryptocurrency transaction from user {sender_id} to user {receiver_id}."

        try:
            # ✅ Send prompt through the routed LLM client
            response = await llm_query(prompt)
            return {"status": "success", "agent": "HelpDesk", "response": response}

        except Exception as e:
            return {"status": "error", "agent": "HelpDesk", "details": str(e)}
