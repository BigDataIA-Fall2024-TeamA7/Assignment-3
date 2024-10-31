# BD3app/pages/qa_page.py

import streamlit as st
from utils.navigation import navigate_to

def render():
    # Retrieve the document title from session state
    document_title = st.session_state.get("selected_document_title", "Document Title")

    # Page Title and Document Title
    st.markdown(
        "<h1 style='text-align: center; color: #F5F5F5; font-size: 36px;'>Q/A Interface</h1>",
        unsafe_allow_html=True
    )
    st.markdown("<hr style='border: 1px solid #4B4B4B;'>", unsafe_allow_html=True)
    st.markdown(
        f"<h2 style='color: #1E90FF; font-size: 28px;'>{document_title}</h2>",
        unsafe_allow_html=True
    )

    # Section for Question Input
    st.markdown("<h3 style='color: #F5F5F5;'>Ask a Question About the Document</h3>", unsafe_allow_html=True)
    question = st.text_input("Question:", placeholder="Type your question here...")

    # Placeholder area to display the response
    response_area = st.empty()

    # Submit button for the question
    if st.button("Ask"):
        if question:
            # Placeholder for generating a response (to be replaced with actual Q/A functionality)
            response = generate_mock_response(question)
            response_area.markdown(
                f"<div style='padding: 10px; background-color: #333; border-radius: 5px;'><strong>Answer:</strong> {response}</div>",
                unsafe_allow_html=True
            )
        else:
            response_area.warning("Please enter a question before submitting.")

    # Divider line
    st.markdown("<hr style='border: 1px solid #4B4B4B;'>", unsafe_allow_html=True)

    # Navigation back button to return to the open document page
    if st.button("⬅ Back to Document Overview"):
        navigate_to('open_document')

# Placeholder function to generate a mock response
def generate_mock_response(question):
    return f"This is a simulated answer to the question: '{question}'"
