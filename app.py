from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')



# List of common greeting words
greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good evening']

def is_greeting(message: str) -> bool:
    message = message.lower()
    return any(greeting in message for greeting in greetings)

def filter_google_terms(response_text: str) -> str:
    restricted_terms = ["Google", "Gemini"]
    for term in restricted_terms:
        response_text = response_text.replace(term, "ShaktiMaangPT")
    return response_text

def get_time_based_greeting() -> str:
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning! How can I assist you today?"
    elif current_hour < 18:
        return "Good afternoon! How may I help you today?"
    else:
        return "Good evening! How can I be of service to you today?"

def save_chat_to_firebase(user_message: str, assistant_response: str):
    chat_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message,
        "assistant_response": assistant_response
    }
    try:
        db.collection('chat_logs').add(chat_entry)
    except Exception as e:
        logging.error(f"Error saving chat to Firebase: {str(e)}")

@app.route('/')
def home():
    return "Welcome to the ShaktiMaangPT backend! API is live and ready to assist you."

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        chat_history = data.get('history', [])

        if not message:
            return jsonify({
                'error': 'Message is required.'
            }), 400

        if is_greeting(message):
            greeting_message = get_time_based_greeting()
            save_chat_to_firebase(message, greeting_message)
            return jsonify({
                'content': f"ShaktiMaangPT: {greeting_message}",
                'role': 'assistant',
                'id': str(hash(greeting_message))
            })

        formatted_history = []
        for msg in chat_history:
            role = "model" if msg['role'] == 'assistant' else "user"
            formatted_history.append({"role": role, "parts": [msg['content']]})

        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(message)
        filtered_response = filter_google_terms(response.text)
        save_chat_to_firebase(message, filtered_response)

        return jsonify({
            'content': filtered_response,
            'role': 'assistant',
            'id': str(hash(filtered_response))
        })

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            'content': "We are currently training the system to serve you better. Please try again later.",
            'role': 'assistant',
            'id': str(hash("We are currently training the system to serve you better. Please try again later."))
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
