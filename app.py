import streamlit as st
import google.generativeai as genai
from pathlib import Path
import docx  # For handling docx files (install using pip install docx)
import PyPDF2  # For handling PDF files (install using pip install PyPDF2)

# Configure genai with the API key from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Start a chat session with the Gemini model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])


# Function to get responses from the Gemini model with error handling
def get_gemini_response(content, question):
    combined_input = f"Content: {content}\nQuestion: {question}"
    try:
        response = chat.send_message(combined_input, stream=True)
        return response
    except Exception as e:
        # Handle potential exceptions including BlockedPromptException
        if 'BlockedPromptException' in str(e):
            return "Your prompt seems to be blocked. Please rephrase your question."
        else:
            return f"Error: {str(e)}"


# Function to process uploaded document and extract text
def process_uploaded_document(uploaded_file):
    # Check file extension and use appropriate library
    if uploaded_file.name.endswith(".docx"):
        document = docx.Document(uploaded_file)
        text = [paragraph.text for paragraph in document.paragraphs]
        return "\n".join(text)  # Join paragraphs with newline
    elif uploaded_file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    else:
        return "Unsupported file format. Please upload a docx or pdf file."


# Streamlit app logic
st.set_page_config(page_title="Document Q&A")

st.header("Chat with your Document")

uploaded_file = st.file_uploader("Upload a document (docx or pdf):", type=["docx", "pdf"])

if uploaded_file is not None:
    # Process uploaded document
    document_text = process_uploaded_document(uploaded_file)
    st.write("Document content:")
    st.write(document_text)  # Display document content for user reference

    if document_text:
        # Get user question and call Gemini model
        input_text = st.text_input("Ask a question about the document:", key="input")
        submit = st.button("Ask the question")

        if submit and input_text:
            response = get_gemini_response(document_text, input_text)

            st.session_state['chat_history'] = []  # Clear chat history for new doc

            st.subheader("The Response is")
            if isinstance(response, str) and response.startswith("Error:"):
                st.write(response)
            else:
                response_text = ""
                for chunk in response:
                    response_text += chunk.text
                st.write(response_text)


