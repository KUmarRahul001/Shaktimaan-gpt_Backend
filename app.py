from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

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
    """
    Check if the message contains any common greeting word.
    
    :param message: The user's message.
    :return: True if the message is a greeting, False otherwise.
    """
    message = message.lower()
    return any(greeting in message for greeting in greetings)

def filter_google_terms(response_text: str) -> str:
    """
    Replace the word 'Google' and other restricted words in the response.
    
    :param response_text: The original response text.
    :return: The filtered response text.
    """
    restricted_terms = ["Google", "Gemini"]
    
    # Replace restricted terms with the preferred term
    for term in restricted_terms:
        response_text = response_text.replace(term, "ShaktiMaangPT")
    
    return response_text

def get_time_based_greeting() -> str:
    """
    Return a greeting based on the time of the day.
    """
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning! How can I assist you today?"
    elif current_hour < 18:
        return "Good afternoon! How may I help you today?"
    else:
        return "Good evening! How can I be of service to you today?"

@app.route('/')
def home():
    """
    Root route to confirm the server is live.
    """
    return "Welcome to the ShaktiMaangPT backend! API is live and ready to assist you."

@app.route('/favicon.ico')
def favicon():
    """
    Return a no-content response for favicon requests to avoid 404 errors.
    """
    return '', 204

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        chat_history = data.get('history', [])

        # Check if the message is a greeting
        if is_greeting(message):
            # Provide a time-based greeting for professionalism
            greeting_message = get_time_based_greeting()
            return jsonify({
                'content': f"ShaktiMaangPT: {greeting_message}",
                'role': 'assistant',
                'id': str(hash(greeting_message))
            })
        
        # Format chat history for Gemini
        formatted_history = []
        for msg in chat_history:
            role = "model" if msg['role'] == 'assistant' else "user"
            formatted_history.append({"role": role, "parts": [msg['content']]})

        # Start a new chat with Gemini
        chat = model.start_chat(history=formatted_history)
        
        # Generate response from Gemini
        response = chat.send_message(message)
        
        # Filter out restricted terms like "Google" and "Gemini"
        filtered_response = filter_google_terms(response.text)
        
        return jsonify({
            'content': filtered_response,
            'role': 'assistant',
            'id': str(hash(filtered_response))
        })
    
    except Exception as e:
        # Log the error for debugging
        logging.error(f"Error processing request: {str(e)}")

        # Return a friendly "training" message instead of showing an error
        return jsonify({
            'content': "We are currently training the system to serve you better. Please try again later.",
            'role': 'assistant',
            'id': str(hash("We are currently training the system to serve you better. Please try again later."))
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
