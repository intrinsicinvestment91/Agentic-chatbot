from crewai import Agent, Task
from langchain.tools import tool
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex

import os
#from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.obsidian import ObsidianReader
from dotenv import load_dotenv
from routellm.controller import Controller
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_openai import ChatOpenAI



#need langchain and routeLLM here: (to use different LLMs within a prompt)



load_dotenv()
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")#process agent to call LLMs
os.environ["OPENAI_MODEL_NAME"]="gpt-3.5-turbo"

embeddings = OpenAIEmbeddings();#embeddings to use for vector store

#set up RouteLLM:
client = Controller(routers = ["mf"], strong_model = 'gpt-3.5-turbo' , weak_model ='gpt-3.5-turbo')#, api_base = "http://localhost:1234/v1", api_key ="lm-studio" )
#'together_ai/meta-llama/Meta-Llama-Guard-3-8B'
#openai/bartowski/stable-code-instruct-3b-GGUF



class InfoDesk():

 @tool("respond to the query using company information")
 def RAGsearch(query: str):
    """Useful if the given query requires company information to
    give a good response to the query as  as accurate as possible. """

    "do a RAG search using knowledge embedding to find using similarity search"
    #llama index RAG(can't use RouteLLM, as we cant get similar documents from llamaindex Object)

   # files= SimpleDirectoryReader(input_dir="./agents/info/")
     
    #docs = files.load_data()
    #user = "Johnathan"
   
    #base_directory_path = r"C:\Users\Ivan\OneDrive\Documents\testing"
   # user_notes = os.path.join(base_directory_path, user)
    #obsidian =  ObsidianReader(user_notes).load_data()#converts to a document object

    #print(f"Loaded {len(docs)} docs")
    #index = VectorStoreIndex.from_documents(
    #docs + obsidian
    #);
    #vector_engine = index.as_query_engine( similarity_top_k=5)#creates a query from the LLM
    #seems that 5 is the optimal choice, as it gets the most relevant to the answer, without too much context
    
    #define tools here if needed
   # response = vector_engine.query(query)
    #print(response)
    #return response  

    print('check')
    #langchain RAG + routeLLM, see testing for more info
    input_dir = "./ai-api/info/"
    loader = PyPDFDirectoryLoader(input_dir)
    docs = loader.load()
    print(len(docs))
    db = FAISS.from_documents(docs, embeddings)#load into a vector store 
    print(f"Loaded {len(docs)} docs")

    similarData = db.similarity_search(query, k = 5)
    similarArray = [doc.page_content for doc in similarData] 
    prompt = f"""Use the information given to you  that is relevant to answer this query: 
                {query} information: {similarArray}
             """
    response = client.chat.completions.create(
        model = "router-mf-0.11593",
        messages = [
            {"role": "user", "content": prompt}
        ]
    )
    print(response['model'])
    return response["choices"][0]['message']['content'];
    