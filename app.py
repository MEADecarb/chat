import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import fitz  # PyMuPDF

# Configure genai with the API key from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Start a chat session with the Gemini model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])


# Function to get responses from the Gemini model
def get_gemini_response(content, question):
    combined_input = f"Content: {content}\nQuestion: {question}"
    try:
        response = chat.send_message(combined_input, stream=True)
        return response
    except Exception as e:
        return f"Error: {str(e)}"


# Function to extract text from a PDF file using PyMuPDF
def extract_text_from_pdf(file):
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text


# Initialize the Streamlit app
st.set_page_config(page_title="PDF Q&A Demo")

st.header("Chat with a PDF")

# Option to remove Chat History functionality (comment the following block)
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.write("PDF successfully loaded.")

    input_text = st.text_input("Ask a question about the PDF content:", key="input")
    submit = st.button("Ask the question")

    if submit and input_text:
        response = get_gemini_response(pdf_text, input_text)

        # Store chat history (comment out if not needed)
        st.session_state['chat_history'].append(("You", input_text))

        st.subheader("The Response is")
        if isinstance(response, str) and response.startswith("Error:"):
            st.write(response)
        else:
            response_text = ""
            for chunk in response:
                response_text += chunk.text
            st.write(response_text)

# Option to remove Chat History functionality (comment the following block)
# st.subheader("The Chat History is")
# for role, text in st.session_state['chat_history']:
#     st.write(f"{role}: {text}")

else:
    st.write("Please upload a PDF file to start chatting with its content.")
