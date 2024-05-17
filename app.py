import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configure OpenAI with the API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

def get_gpt_response(content, question):
    combined_input = f"Content: {content}\nQuestion: {question}"
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=combined_input,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except openai.error.InvalidRequestError as e:
        return f"Error: {str(e)}"

def scrape_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.get_text(separator=' ', strip=True)
    return content

def find_internal_links(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if full_url.startswith("https://energy.maryland.gov"):
            links.append(full_url)
    return list(set(links))  # Remove duplicates

## Initialize our Streamlit app
st.set_page_config(page_title="Q&A Demo")

st.header("Maryland Energy Administration Q&A")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

input_text = st.text_input("Ask a question about the Maryland Energy Administration: ", key="input")
submit = st.button("Ask the question")

if submit and input_text:
    main_url = "https://energy.maryland.gov/Pages/default.aspx"
    urls = find_internal_links(main_url)
    urls.append(main_url)  # Include the main URL itself
    all_content = ""
    for url in urls:
        all_content += scrape_webpage(url) + "\n"
    
    response = get_gpt_response(all_content, input_text)
    
    st.session_state['chat_history'].append(("You", input_text))
    
    st.subheader("The Response is")
    st.write(response)
    st.session_state['chat_history'].append(("Bot", response))

st.subheader("The Chat History is")
for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")
