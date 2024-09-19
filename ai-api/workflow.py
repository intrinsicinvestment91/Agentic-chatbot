from crewai import Agent, Crew, Task
from tools.hr_desk_tools import HRdesk
import os
#from datetime import datetime
from dotenv import load_dotenv
load_dotenv()




os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"]="gpt-3.5-turbo"


#main HR agent execution through crew!:
#user_query = "What makes GNEISS special?"
#user_query = "what is your mission?"
def initiate_workflow(user_query: str):

    print(user_query)
    def HR_task(agent):
            return Task(description=f"""
                You are tasked with finding the best agent suited to satisfy the following query: 
                {user_query}
                Choose which agent is best suited to do it
                only from on your existing tools which represent choosing a agent 
                based on the description.
                You must choose an tool on this criteria if their query is relevant to the company
                otherwise answer to the best of your ability if appropiate as a HR agent.
                Dont return any thoughts about what you think is the best agent, just return their response, dont add any of your thoughts
                """,
                agent=agent, 
                expected_output="""The result from the best chosen agent"""
            )
    HRagent = Agent(role="HR manager",
                goal="""
                    Make accurate decisions on which agent to choose based on the description 
                    of each tool and to satisfy the users needs based on the relevance to your company GNEISS """,
                backstory="""
                    A competent agent hired by a cryptocurrency company: GNEISS that is great 
                    at matching agents to conduct the task they perform best at
                    in order to satisfy customer needs and queries """,
                tools=[
                        HRdesk.choose_info,
                        HRdesk.choose_help,
                ],
                verbose = True,
                
    );
    upper_management = Crew(agents = [HRagent], tasks=[HR_task(HRagent)],);


    workflow = upper_management.kickoff()
    print("final answer", workflow)#workflow is the last value from the compiled LLMs
    return str(workflow)
    #adding to memory if needed:(optional->may just add this in the info agent), perhaps redis or something to cache