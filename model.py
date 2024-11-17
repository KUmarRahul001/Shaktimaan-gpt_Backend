import requests
import os
import logging

# The API endpoint for Gemini
GEMINI_API_URL = "https://api.gemini.com/v1/model"  # Replace with the correct API endpoint
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Assuming you store the API key in an environment variable

def generate_content(user_input: str) -> str:
    """
    Generates content from Gemini API based on the user's input.
    
    :param user_input: The input message from the user.
    :return: The AI-generated response.
    """
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Construct the payload for the API request
    data = {
        "input": user_input,  # Depending on API documentation, the exact format of the data may vary
    }
    
    try:
        # Log the request for debugging
        logging.debug(f"Sending request to Gemini API: {data}")
        
        # Send a POST request to Gemini API
        response = requests.post(GEMINI_API_URL, json=data, headers=headers)
        
        # Log the response for debugging
        logging.debug(f"Response from Gemini API: {response.status_code} - {response.text}")
        
        # Check if the response was successful
        if response.status_code == 200:
            # Extract and return the generated content from the API response
            result = response.json()
            return result.get("generated_content", "Sorry, I couldn't generate a response.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        # Handle any exceptions during the API request
        logging.error(f"Error generating content: {str(e)}")
        return f"Error generating content: {str(e)}"
