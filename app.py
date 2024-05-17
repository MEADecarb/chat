import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configure genai with the API key from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"]["api_key"])

## Function to load Gemini Pro model and get responses
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(content, question):
    # Combine the scraped content with the question
    combined_input = f"Content: {content}\nQuestion: {question}"
    response = chat.send_message(combined_input, stream=True)
    return response

def scrape_webpage(url):
    # Send a GET request to the webpage
    response = requests.get(url)
    # Parse the webpage content
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extract relevant content from the webpage
    content = soup.get_text(separator=' ', strip=True)
    return content

def find_internal_links(base_url):
    # Send a GET request to the base URL
    response = requests.get(base_url)
    # Parse the webpage content
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find all internal links
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Make sure the link is absolute
        full_url = urljoin(base_url, href)
        if full_url.startswith("https://energy.maryland.gov"):
            links.append(full_url)
    return list(set(links))  # Remove duplicates

## Initialize our Streamlit app
st.set_page_config(page_title="Q&A Demo")

st.header("Gemini LLM Application")

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Text input for the user question
input_text = st.text_input("Ask a question about the Maryland Energy Administration: ", key="input")

# Button to submit the question
submit = st.button("Ask the question")

if submit and input_text:
    # Scrape the content from the main webpage and all internal links
    main_url = "https://energy.maryland.gov/Pages/default.aspx"
    urls = find_internal_links(main_url)
    urls.append(main_url)  # Include the main URL itself
    all_content = ""
    for url in urls:
        all_content += scrape_webpage(url) + "\n"
    
    response = get_gemini_response(all_content, input_text)
    
    # Add user query and response to session state chat history
    st.session_state['chat_history'].append(("You", input_text))
    
    st.subheader("The Response is")
    response_text = ""
    for chunk in response:
        response_text += chunk.text
    st.write(response_text)
    st.session_state['chat_history'].append(("Bot", response_text))

# Display the chat history
st.subheader("The Chat History is")
for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")
