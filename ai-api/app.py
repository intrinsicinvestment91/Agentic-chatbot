import json
import uvicorn
from dotenv import load_dotenv
import os
import openai
from google.cloud import texttospeech
from typing import Union, Annotated
from fastapi.responses import FileResponse
from fastapi import FastAPI, Form, UploadFile, Header, Response, status, Request
from starlette.responses import JSONResponse
import tempfile
import logging
import httpx
from google.oauth2 import service_account
from pydantic import BaseModel
from typing import List
import pyttsx3
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from openai import OpenAI
from workflow import initiate_workflow
from io import BytesIO


limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
timeout = httpx.Timeout(timeout=5.0, read=15.0)
client = httpx.AsyncClient(limits=limits, timeout=timeout)



#text to speech engine
#documentation for it is here:https://github.com/nateshmbhat/pyttsx3?tab=readme-ov-file
engine = pyttsx3.init()
rate = engine.getProperty('rate')   # getting details of current speaking rate
print("speaking rate", rate)                        #printing current voice rate
engine.setProperty('rate', 200) 
volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
print(volume)                          #printing current volume level
engine.setProperty('volume',1.0)   
voices = engine.getProperty('voices')       #getting details of current voice
#engine.setProperty('voice', voices[0].id)  #changing index, changes voices. 0 for male
engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female


"""
DEPRECIATED
@app.on_event("shutdown")
async def shutdown_event():
    print("shutting down...")
    await client.aclose()
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic here (if needed)
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    yield  # before yield:startup, after yield: shutdown
    # Shutdown logic here
    print("shutting down...")
    await client.aclose()

app = FastAPI(lifespan = lifespan)


"""
# handle CORS preflight requests
(commented because dosent work for all requests, will fail if params cant be handled)
@app.options('/{rest_of_path:path}')
async def preflight_handler(request: Request, rest_of_path: str) -> Response:
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    return response
    """
#quick fix, but it still fails every second time, and then succeeds teh first time in a sequence.
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()



openai.api_key = os.environ.get('OPEN_AI_API_KEY')
private_chatbot_api_key = os.environ.get('CHATBOT_API_KEY')

ai_client = OpenAI(
  api_key= os.environ.get('OPEN_AI_API_KEY'),  # this is also the default, it can be omitted
)




@app.get("/")
def read_root(response: Response, chatbot_api_key: Annotated[Union[str, None], Header()] = None):
    if chatbot_api_key != private_chatbot_api_key:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return 'Unauthorized'
    print(chatbot_api_key)
    return '😺'



class Item(BaseModel):
    role: str
    content: str


class ItemList(BaseModel):
    items: List[Item]

#need this to be blocking
async def read_file(audio):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(await audio.read())
            temp_file_path = temp_file.name
            return temp_file_path

@app.post("/question")
async def create_upload_file(response: Response, audio: UploadFile, messages: str = Form(...), chatbot_api_key: Annotated[Union[str, None], Header()] = None):
    print("/question")
    print(messages)
    print(audio)
    print(response)
    if chatbot_api_key != private_chatbot_api_key:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return 'Unauthorized'
    try:
        #creates a file thats wav to input the audio file here
        make_audio_file_path = await read_file(audio)
        audio_file = open(make_audio_file_path, 'rb')#set audio file to some directory
        print("audio file", audio_file)
        audio_content = await audio.read()
        buffer = BytesIO(audio_file)
        transcript = ai_client.audio.transcriptions.create(
            model="whisper-1", file= audio_file, 
        )
        print("transcript", transcript)
        user_prompt = transcript.text #transcribe the text using whsiper-1 or something
        if user_prompt == '':#else if user didnt say anything
            return FileResponse('empty_question.mp3', media_type="audio/mpeg", filename="empty_question.mp3")

       # messages_with_prompt = parsed_messages
       # messages_with_prompt.append({"role": "user", "content": user_prompt})#what we will feed into openai.
      
        chatbot_response = initiate_workflow(user_query = user_prompt)       # completion.choices[0].message.content
       #note that: An error occurred: %s object CrewOutput can't be used in 'await' expression,
        print(chatbot_response)

    
        
        temp_file_path = 'temp.mp3'
        engine.save_to_file(chatbot_response, temp_file_path) #given a sample text, save to an mp3.
        engine.runAndWait()
        return FileResponse(temp_file_path, media_type="audio/mpeg", filename="temp.mp3", headers={"chatbot_response": chatbot_response, "user_prompt": user_prompt})
    
    except Exception as error:
        print("An error occurred: %s", str(error)) 
        raise error
        #return FileResponse('error.mp3', media_type="audio/mpeg", filename="error.mp3")
      


@app.get("/pregenerated/no_tokens")
def read_root(response: Response, chatbot_api_key: Annotated[Union[str, None], Header()] = None):
    if chatbot_api_key != private_chatbot_api_key:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return 'Unauthorized'
    return FileResponse('no_tokens.mp3', media_type="audio/mpeg", filename="no_tokens.mp3")


@app.get("/pregenerated/not_logged")
def read_root(response: Response, chatbot_api_key: Annotated[Union[str, None], Header()] = None):
    if chatbot_api_key != private_chatbot_api_key:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return 'Unauthorized'
    return FileResponse('not_logged.mp3', media_type="audio/mpeg", filename="not_logged.mp3", headers={})


@app.get("/pregenerated/empty_question")
def read_root(response: Response, chatbot_api_key: Annotated[Union[str, None], Header()] = None):
    if chatbot_api_key != private_chatbot_api_key:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return 'Unauthorized'
    return FileResponse('empty_question.mp3', media_type="audio/mpeg", filename="empty_question.mp3", headers={})


@app.get("/pregenerated/error")
def read_root(response: Response, chatbot_api_key: Annotated[Union[str, None], Header()] = None):
    if chatbot_api_key != private_chatbot_api_key:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return 'Unauthorized'
    return FileResponse('error.mp3', media_type="audio/mpeg", filename="error.mp3", headers={})


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=(5600), reload=True,)
