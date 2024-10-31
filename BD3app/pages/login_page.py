# BD3app/pages/login_page.py

import streamlit as st
import requests
from utils.config import load_config
from utils.navigation import navigate_to

# Load configuration settings
config = load_config()
backend_url = config["backend_url"]

def render():
    # Page Title and Subheader with Styling
    st.markdown(
        "<h1 style='text-align: center; color: #F5F5F5; font-size: 36px; margin-bottom: 0;'>🔐 Login to the Application</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align: center; color: #D3D3D3; font-size: 18px; margin-top: 0;'>Please enter your login credentials</h4>",
        unsafe_allow_html=True
    )
    st.markdown("<hr style='border: 1px solid #4B4B4B;'>", unsafe_allow_html=True)

    # Centering form content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Input fields for email and password with placeholders
        email = st.text_input("📧 Email Address", placeholder="Enter your email")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")

        # Placeholder area for displaying messages
        message_area = st.empty()

        # Mock credentials for testing
        test_email = "test@example.com"
        test_password = "password123"

        # Login Button with styling
        if st.button("🔓 Login", help="Click to access your account"):
            if email and password:
                # Check if entered credentials match the mock credentials for testing
                if email == test_email and password == test_password:
                    # Mock a successful login by simulating a JWT token
                    st.session_state['jwt_token'] = "mock_jwt_token"  # Simulated JWT token
                    st.session_state['user_email'] = email

                    # Display success message and navigate to the landing page
                    st.success(f"Welcome back, {email}!")
                    navigate_to('landing')  # Redirect to the landing page
                else:
                    # Actual backend call (uncomment if needed for real testing)
                    try:
                        # Send a POST request to the backend's /token endpoint
                        response = requests.post(
                            f"{backend_url}/token",
                            data={"username": email, "password": password}
                        )

                        if response.status_code == 200:
                            # Store the JWT token in session state
                            jwt_token = response.json().get("access_token")
                            st.session_state['jwt_token'] = jwt_token

                            # Display success message and navigate to the landing page
                            st.success(f"Welcome back, {email}!")
                            navigate_to('landing')  # Navigate to the landing page
                        elif response.status_code == 401:
                            # Unauthorized (likely incorrect username or password)
                            message_area.error("Incorrect email or password. Please try again.")
                        else:
                            # Other errors (e.g., server error)
                            message_area.error(f"Server error: {response.status_code}. Please try again later.")
                    except requests.exceptions.RequestException as e:
                        # Handle request errors (e.g., network issues)
                        message_area.error(f"An error occurred: {e}")
            else:
                # Warning if either email or password is missing
                message_area.warning("Please enter both email and password.")

    # Additional styles for the button and input fields layout
    st.markdown(
        """
        <style>
        /* Center-align and style the input fields */
        div.stTextInput > label {
            font-size: 18px;
            color: #D3D3D3;
            font-weight: bold;
        }
        /* Style login button */
        div.stButton > button:first-child {
            width: 100%;
            padding: 10px;
            font-size: 20px;
            font-weight: bold;
            color: #FFFFFF;
            background-color: #1E90FF;
            border: 1px solid #1E90FF;
            border-radius: 8px;
        }
        /* Button hover effect */
        div.stButton > button:hover {
            background-color: #FF6347;
            border: 1px solid #FF6347;
            color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Divider line
    st.markdown("<hr style='border: 1px solid #4B4B4B;'>", unsafe_allow_html=True)
