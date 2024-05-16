import streamlit as st
import requests

# Fetch the API key from Streamlit secrets
API_KEY = st.secrets["default"]["api_key"]
GITHUB_URL = 'https://raw.githubusercontent.com/MEADecarb/chat/main/incentives.txt'  # Replace with the actual GitHub raw URL

# Function to fetch text from a GitHub text file
def fetch_github_text_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error fetching the file from GitHub: {e}"

# Function to send a message to the Gemini API
def send_message(message, api_key):
    try:
        api_url = f'https://generativelanguage.googleapis.com/v1beta2/models/gemini-pro:generateContent?key={api_key}'
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": message
                        }
                    ]
                }
            ]
        }
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"reply": f"Error communicating with the API: {e}"}

# Fetch data from GitHub text file
github_text = fetch_github_text_file(GITHUB_URL)

# Streamlit app
st.title("Chatbot with Gemini API")

# Chatbot interaction
st.write("### Chat with the Bot")
user_input = st.text_input("You:", "")
if user_input:
    response = send_message(user_input, API_KEY)
    st.write("Bot:", response.get('contents', [{'parts': [{'text': 'No response'}]}])[0]['parts'][0]['text'])
