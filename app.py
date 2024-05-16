import requests
from bs4 import BeautifulSoup

# Function to fetch text from a GitHub text file
def fetch_github_text_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Error fetching the file from GitHub."

# Function to fetch text from a webpage
def fetch_webpage_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        return text
    else:
        return "Error fetching the webpage."
import streamlit as st
import requests
from bs4 import BeautifulSoup

# Replace 'YOUR_API_KEY' with your actual Gemini API key
API_KEY = 'AIzaSyCwnAwyCBoRSe-2LaTJDqx4hQw1RbkQjAA'
GITHUB_URL = 'https://github.com/MEADecarb/chat/blob/main/incentives.txt'  # Replace with the actual GitHub raw URL
WEBPAGE_URL = 'https://energy.maryland.gov/Pages/default.aspx'

# Function to fetch text from a GitHub text file
def fetch_github_text_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Error fetching the file from GitHub."

# Function to fetch text from a webpage
def fetch_webpage_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        return text
    else:
        return "Error fetching the webpage."

# Function to send a message to the Gemini API
def send_message(message, api_key):
    api_url = 'https://api.gemini.com/v1/your-endpoint'  # Replace with actual Gemini API endpoint
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'message': message
    }
    response = requests.post(api_url, headers=headers, json=data)
    return response.json()

# Fetch data from GitHub text file and webpage
github_text = fetch_github_text_file(GITHUB_URL)
webpage_text = fetch_webpage_text(WEBPAGE_URL)

# Streamlit app
st.title("Chatbot with Gemini API")
st.write("### GitHub Text File Content")
st.write(github_text)
st.write("### Webpage Content")
st.write(webpage_text)

# Chatbot interaction
st.write("### Chat with the Bot")
user_input = st.text_input("You:", "")
if user_input:
    response = send_message(user_input, API_KEY)
    st.write("Bot:", response.get('reply', 'No response'))
