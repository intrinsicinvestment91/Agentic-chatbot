from crewai import Agent, Task
from langchain.tools import tool
from llama_index.llms.together import TogetherLLM
from tools.help_desk_tools import HelpDesk
from tools.info_desk_tools import InfoDesk
from dotenv import load_dotenv
import os
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"]="gpt-3.5-turbo"



class HRdesk():





  @tool("choose the info desk agent to satisify the users query")
  def choose_info(query: str):
    """Useful if  the users query is a question(or related to a question) about anything related on the
     cryptocurrency company GNEISS, """

    info_agent = Agent(
          role='info agent',
          goal=
          """Use relevant and accurate information on the company to answer the users query 
          as well as providing insight and analysis in a efficent context by using enough text needed to give all the useful information and disregarding information that may seem trivial or useless to the user. """,
          backstory=
          "You are a info-agent for the cryptocurrency company GNEISS that is competent at answering questions and giving relevant information about the company to the user based on their query .",
        
          allow_delegation=False,
          tools = [InfoDesk.RAGsearch], #stack info related questions here if need be
          verbose = True,
          )

    task = Task(
          agent=info_agent,
          description=
          f"""Based on the given query:{query}, answer this query to the best of your ability by using the most relevant tool at your disposal. Give your answer to the query to with the most context without information that dosent seem important to the query.""",
          expected_output ="A insightful response to the users query with the necessary company information supplied, or if not possible, give possible places where the information can be found"
      )
    summary = task.execute_sync();
    print("agent response:",summary)
    return summary
    



  @tool("choose the help desk agent to satisfy the users query")
  def choose_help(query: str):
    """Useful if the users query is a task that the user wants us to execute that is related to GNEISS"""

    help_agent = Agent(
          role='Help agent',
          goal=
          'Process the task the user desires to the best of your ability based on the query',
          backstory=
          "You are a incredibly dilligent agent that is competent at completing actions provided users queries through utilizing the tools that GNEISS has that is possible to do.",
        
          allow_delegation=False,
          tools = [HelpDesk.transaction],)#stack API calls here if need be.

    task = Task(
          agent=help_agent,
          description=
          f""" Based on this query:{query}, complete the users task with as much accuracy as possible with all the information provided in the query.""",
          expected_output ="""Evidence of success from processing the users task through an API or other means, or if an error, a response of why the error occured and how it can be fixed """
      )
    summary = task.execute_sync();
    return summary;