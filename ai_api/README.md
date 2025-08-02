✅ AI Agent Integration – Recent Updates
🔹 Overview

This update refactors the AI agent architecture to use a unified LLM client and prepares the project for seamless integration with RouteLLM → DeepSeek.
🚀 What’s New

    Refactored Agents

        HRDesk, HelpDesk, and InfoDesk now:

            Use clients/llm_client.py for all LLM calls.

            Support RouteLLM → DeepSeek routing.

            Have simplified async methods for direct testing.

    Unified LLM Client

        Added clients/llm_client.py to handle:

            DeepSeek mock requests (local testing).

            Future RouteLLM/DeepSeek real API calls.

    Environment & Configuration

        .env_example updated with new keys for:

            LLM_PROVIDER (choose deepseek or routellm)

            DeepSeek & RouteLLM endpoints and models.

        .env should never be committed.

    Project Structure

        Renamed ai-api → ai_api for clean Python imports.

        Cleaned Git tracking for renamed/moved files.

✅ How to Test Agents Locally
HRDesk

python -c "import asyncio; from ai_api.tools.hr_desk_tools import HRDesk; print(asyncio.run(HRDesk.handle_request('Explain leave policy')))"

HelpDesk

python -c "import asyncio; from ai_api.tools.help_desk_tools import HelpDesk; print(asyncio.run(HelpDesk.transaction(1,2)))"

InfoDesk

python -c "import asyncio; from ai_api.tools.info_desk_tools import InfoDesk; print(asyncio.run(InfoDesk.provide_info('What are your support hours?')))"

🔑 Next Steps for Developers

Add real API keys to .env.

Enable live RouteLLM → DeepSeek calls in llm_client.py.

    Extend agents and workflows as needed.

💡 Repo is now clean, tested, and ready for further AI integration.

🛠️ Setup Instructions
1. Clone the Repo & Enter Project

git clone <your-fork-url>
cd Agentic-chatbot

2. Create & Activate Virtual Environment

python3.13 -m venv venv
source venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

4. Set Environment Variables

    Copy .env_example to .env:

cp .env_example .env

Fill in:

    LLM_PROVIDER=deepseek
    CHATBOT_API_KEY=your_runpod_api_key
    DEEPSEEK_API_BASE=https://api.runpod.ai/v1/deepseek
    DEEPSEEK_MODEL=deepseek-r1-1776-gguf-q3
    ROUTELLM_API_KEY=your_routellm_key
    ROUTELLM_API_BASE=https://api.routellm.com/v1
    ROUTELLM_DEFAULT_MODEL=gpt-4o

🤖 Agent Testing

Each agent can now be tested directly via the Python REPL or command line:
HRDesk

python -c "import asyncio; from ai_api.tools.hr_desk_tools import HRDesk; print(asyncio.run(HRDesk.handle_request('Explain leave policy')))"

HelpDesk

python -c "import asyncio; from ai_api.tools.help_desk_tools import HelpDesk; print(asyncio.run(HelpDesk.transaction(1,2)))"

InfoDesk

python -c "import asyncio; from ai_api.tools.info_desk_tools import InfoDesk; print(asyncio.run(InfoDesk.provide_info('What are your support hours?')))"

🌐 Running the Local API Server

Once agents work in testing:

cd ai_api
uvicorn app:app --reload --port 9000

Access at:
👉 http://127.0.0.1:9000


🔑 Next Steps for Developers

Add real API keys to .env
Enable live RouteLLM → DeepSeek integration
Extend agents & connect workflows

