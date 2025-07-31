import json
from flask import Flask, request, jsonify, send_file, Response 
from flask import make_response 
from dotenv import load_dotenv
import os
import wave
import openai
#from google.cloud import texttospeech
import tempfile
import logging
import pyttsx3
#from google.oauth2 import service_account
from flask_cors import CORS
from openai import OpenAI
from io import BytesIO
import io
app = Flask(__name__)
load_dotenv()
import wave
from workflow import initiate_workflow
import soundfile as sf
origins = [
    "http://localhost:3000",
]

# Configure CORS in Flask
CORS(app, origins=origins, supports_credentials=True)


openai.api_key = os.environ.get('OPENAI_API_KEY')
private_chatbot_api_key = os.environ.get('CHATBOT_API_KEY')
ai_client = OpenAI(
  api_key= os.environ.get('OPENAI_API_KEY'),  # this is also the default, it can be omitted
)
# Text-to-speech engine initialization
engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
"""
@app.before_first_request
def setup_logging():
    logger = logging.getLogger("werkzeug")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
"""
@app.route("/", methods=["GET"])
def read_root():
    chatbot_api_key = request.headers.get('chatbot_api_key')
    if chatbot_api_key != private_chatbot_api_key:
        return 'Unauthorized', 401
    return '😺'





    
    
    





app = Flask(__name__)
private_chatbot_api_key = 'your_private_key_here'

@app.route("/question", methods=["POST", "OPTIONS"])
def create_upload_file():
    if request.method == 'OPTIONS':
        return jsonify({
            'allow': 'POST, OPTIONS',
            'Access-Control-Allow-Origin': 'http://localhost:3000',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, chatbot-api-key'
        }), 200

    if 'audio' not in request.files:
        return {'error': 'No audio file found'}, 400
    
    audio_file = request.files['audio']
    messages = request.form.get('messages')
    
    if not messages:
        return {'error': 'No messages found'}, 400
    
    # Save the uploaded file to a temporary file
    temp_file_path = 'temp_received.wav'
  
    
    try:
        # Save the uploaded audio file
        audio_file.save(temp_file_path)
        
        # Convert the file to WAV format

        # Open the WAV file as a buffer
        with open(temp_file_path, 'rb') as wav_file:
            
        
        # Use the buffer with the AI client
           
            transcript = ai_client.audio.transcriptions.create(
                model="whisper-1", file=wav_file
            )
        user_prompt = transcript.text 

        if not user_prompt:
            return send_file('empty_question.mp3', mimetype='audio/mpeg', as_attachment=True, download_name="empty_question.mp3")

        chatbot_response = initiate_workflow(user_query=user_prompt)  

        # Generate response audio file
        temp_file_path_mp3 = 'temp.mp3'
        engine.save_to_file(chatbot_response, temp_file_path_mp3)
        engine.runAndWait()
        
        # Return the audio file without custom headers
        with open(temp_file_path_mp3, 'rb') as f:
            response = Response(
                f.read(),
                mimetype='audio/mpeg',
            )
            response.headers["Content-Disposition"] = "attachment; filename=temp.mp3"
            return response

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return send_file('error.mp3', mimetype='audio/mpeg', as_attachment=True, download_name="error.mp3")

    finally:
        # Clean up temporary files
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
       

def convert_to_wav(input_file, output_file):
    try:
        # Read the input file
        data, samplerate = sf.read(input_file)
        
        # Write the output file
        sf.write(output_file, data, samplerate)
        print(f"Successfully converted {input_file} to {output_file}")
    except Exception as e:
        print(f"Error during conversion: {e}")



@app.route("/pregenerated/no_tokens", methods=["GET"])
def no_tokens():
    chatbot_api_key = request.headers.get('chatbot_api_key')
    if chatbot_api_key != private_chatbot_api_key:
        return 'Unauthorized', 401
    return send_file('no_tokens.mp3', mimetype='audio/mpeg', as_attachment=True, download_name="no_tokens.mp3")

@app.route("/pregenerated/not_logged", methods=["GET"])
def not_logged():
    chatbot_api_key = request.headers.get('chatbot_api_key')
    if chatbot_api_key != private_chatbot_api_key:
        return 'Unauthorized', 401
    return send_file('not_logged.mp3', mimetype='audio/mpeg', as_attachment=True, download_name="not_logged.mp3")

@app.route("/pregenerated/empty_question", methods=["GET"])
def empty_question():
    chatbot_api_key = request.headers.get('chatbot_api_key')
    if chatbot_api_key != private_chatbot_api_key:
        return 'Unauthorized', 401
    return send_file('empty_question.mp3', mimetype='audio/mpeg', as_attachment=True, download_name="empty_question.mp3")

@app.route("/pregenerated/error", methods=["GET"])
def error():
    chatbot_api_key = request.headers.get('chatbot_api_key')
    if chatbot_api_key != private_chatbot_api_key:
        return 'Unauthorized', 401
    return send_file('error.mp3', mimetype='audio/mpeg', as_attachment=True, download_name="error.mp3")

if __name__ == "__main__":
    app.run(host="localhost", port=5600, debug=True)