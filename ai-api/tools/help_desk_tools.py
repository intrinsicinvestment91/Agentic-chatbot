from crewai import Agent, Task
from langchain.tools import tool
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"]="gpt-3.5-turbo"
class HelpDesk():

 @tool("process user's cryptocurrency transaction")
 def transaction(sender_id: int, reciever_id: int):
    """ Useful to send an APi request to process a users Cryptocurrency transaction.
    User must provide the required information for the function to make a transaction, otherwise their request has failed.
  """

    "API request to make a transaction, make sure that we have an error handling and make sure the agent sends it back to the user"
    return "error, user transaction has not been processed"
