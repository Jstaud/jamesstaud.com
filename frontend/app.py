import os
import requests
import hashlib
import gradio as gr

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

# Function to handle user questions by querying the backend API
def answer_question(question):
    backend_api_url = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/")
    api_key = os.getenv("API_KEY")  # Retrieve the API key from environment variables
    headers = {"X-API-Key": api_key}  # Include the API key in the headers

    if not question.strip():
        return "Please enter a question to get an answer."

    try:
        response = requests.post(
            backend_api_url,
            json={"question": question},
            headers=headers,
            timeout= api_timeout
        )
        response.raise_for_status()
        response_json = response.json()
        content = response_json.get("answer")
        answer = content.get('content', "Sorry, I couldn't find an answer.")
    except requests.exceptions.Timeout:
        answer = "The request timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        answer = f"An error occurred: {e}. Please check your question and try again."
    
    return answer

# Create Gradio Interface with improved layout and Gravatar profile image
with gr.Blocks(theme=gr.themes.Monochrome()) as demo:
    # Personal Introduction Section
    with gr.Row():
        gr.Image(gravatar_url, elem_id="profile-image", label="James Staud")
        gr.Markdown(
            """
            # James Staud - Ask Me Anything!
            Hi! I'm James, a passionate software developer specializing in AI and backend development.
            Feel free to ask me questions about my work, projects, skills, or anything you want to know!
            """
        )

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
