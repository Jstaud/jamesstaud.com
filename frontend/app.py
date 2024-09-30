import os
import requests
import hashlib
import gradio as gr
import webbrowser
import json
import logging
from datetime import datetime, timezone
from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from dotenv import load_dotenv

def fetch_bitwarden_secrets():
    # Ensure /tmp directory exists
    os.makedirs("/tmp", exist_ok=True)

    # Create the BitwardenClient
    client = BitwardenClient(
        client_settings_from_dict(
            {
                "apiUrl": os.getenv("API_URL", "https://api.bitwarden.com"),
                "deviceType": DeviceType.SDK,
                "identityUrl": os.getenv("IDENTITY_URL", "https://identity.bitwarden.com"),
                "userAgent": "Python",
            }
        )
    )

    # Add some logging
    logging.basicConfig(level=logging.DEBUG)
    organization_id = os.getenv("ORGANIZATION_ID", "962d8882-d64b-4647-8843-b17900fc4ed7")

    # Set the state file location
    state_path = os.getenv("STATE_FILE", "/tmp/bwstate.json")

    # Authenticate with the Secrets Manager Access Token
    client.auth().login_access_token(os.getenv("BW_ACCESS_TOKEN"), state_path)

    # Sync secrets
    client.secrets().sync(organization_id, None)

    # Retrieve secrets
    secrets = client.secrets().list(organization_id).data.data

    # Set environment variables
    for secret in secrets:
        os.environ[secret.name] = secret.value

# Fetch and set Bitwarden secrets
fetch_bitwarden_secrets()

# Function to generate Gravatar URL
def get_gravatar_url(email, size=150):
    # Trim and lowercase the email
    email = email.strip().lower()
    # Generate MD5 hash of the email
    hash_email = hashlib.md5(email.encode()).hexdigest()
    # Construct the Gravatar URL
    return f"https://www.gravatar.com/avatar/{hash_email}?s={size}"

# Your Gravatar email address
gravatar_email = os.getenv("GRAVATAR_EMAIL")
gravatar_url = get_gravatar_url(gravatar_email)

# Timeout for the API request
api_timeout = 60

# Links to GitHub and Resume
github_url = os.getenv("GITHUB_URL", "https://github.com/Jstaud/jamesstaud.com")
resume_url = os.getenv("RESUME_URL", "https://github.com/Jstaud/jamesstaud.com/blob/initial-app/backend/data/James%20Staud%20Resume%202024.pdf")

# Function to open a URL in the default web browser
def open_url(url):
    return url

# Function to handle user questions by querying the backend API
def answer_question(question):
    backend_api_url = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/")
    api_key = os.getenv("API_KEY")  # Retrieve the API key from environment variables
    headers = {"X-API-Key": api_key}  # Include the API key in the headers

    if not question.strip():
        return "Please enter a question to get an answer."

    try:
        print(f"Backend API URL: {backend_api_url}")
        response = requests.post(
            backend_api_url,
            json={"question": question},
            headers=headers,
            timeout= api_timeout
        )
        response.raise_for_status()
        response_json = response.json()
        content = response_json.get("answer")
        if content is None:
            return "Sorry, I couldn't find an answer."
        answer = content.get('content', "Sorry, I couldn't find an answer.")
    except requests.exceptions.Timeout:
        answer = "The request timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        answer = f"An error occurred: {e}. Please check your question and try again. Questions should be related to my work, projects, skills, or other professional topics."
    
    return answer

# Create Gradio Interface with improved layout and Gravatar profile image
with gr.Blocks(theme='gradio/soft', css="styles.css") as demo:
    # Personal Introduction Section
    with gr.Row():
        with gr.Column():
            gr.Image(gravatar_url, elem_id="profile-image", label="James Staud")
        with gr.Column():
            gr.Markdown(
                """
                # James Staud - Ask Me Anything!
                Hi! I'm James, a passionate software developer specializing in AI and backend development.
                Feel free to ask me questions about my work, projects, skills, or anything you want to know!
                """
            )
            with gr.Row(elem_classes="center-links"):
                gr.Markdown(f'<a href="{github_url}" target="_blank" class="button-link">GitHub Repository</a>')
                gr.Markdown(f'<a href="{resume_url}" target="_blank" class="button-link">My Resume</a>')

    # Main Q&A Section
    with gr.Column():
        question = gr.Textbox(
            label="Your Question", 
            placeholder="Ask me about my projects, skills, etc.",
            lines=2,
            max_lines=4,
            elem_id="question-box"
        )
        ask_button = gr.Button("Ask")
        answer = gr.Markdown(elem_id="answer-box")

    # Loading spinner for user feedback
    ask_button.click(
        fn=answer_question, 
        inputs=question, 
        outputs=answer, 
        show_progress=True  # Show a spinner while the request is processed
    )

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080)
