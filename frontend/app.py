import os
import requests
import gradio as gr

# Function to handle user questions by querying the backend API
def answer_question(question):
    backend_api_url = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/")
    api_key = os.getenv("API_KEY")  # Retrieve the API key from environment variables
    headers = {"X-API-Key": api_key}  # Include the API key in the headers

    try:
        response = requests.post(
            backend_api_url,  # URL of the backend API
            json={"question": question},
            headers=headers  # Add the headers to the request
        )
        response.raise_for_status()
        response_json = response.json()
        content = response_json.get("answer")
        answer = content.get('content', "Sorry, I couldn't find an answer.")
    except requests.exceptions.RequestException as e:
        answer = f"An error occurred: {e}"
    return answer

# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# James Staud - Ask Me Anything!")
    gr.Markdown("Feel free to ask me questions about my work, projects, and experiences.")
    
    question = gr.Textbox(label="Your Question", placeholder="Ask me about my projects, skills, etc.")
    answer = gr.Markdown(label="Answer")
    
    # Button to trigger the question-answering
    ask_button = gr.Button("Ask")
    
    # Define what happens when the button is clicked
    ask_button.click(fn=answer_question, inputs=question, outputs=answer)

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080)