import gradio as gr
import requests
import os

# Function to handle user questions by querying the backend API
def answer_question(question):
    backend_api_url = os.getenv("BACKEND_API_URL", "http://localhost:8000/query")
    try:
        response = requests.post(
            backend_api_url,  # URL of the backend API
            json={"question": question}
        )
        response.raise_for_status()
        answer = response.json().get("answer", "Sorry, I couldn't find an answer.")
    except requests.exceptions.RequestException as e:
        answer = f"An error occurred: {e}"
    return answer

# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# James Staud - Ask Me Anything!")
    gr.Markdown("Feel free to ask me questions about my work, projects, and experiences.")
    
    question = gr.Textbox(label="Your Question", placeholder="Ask me about my projects, skills, etc.")
    answer = gr.Textbox(label="Answer", interactive=False)
    
    # Button to trigger the question-answering
    ask_button = gr.Button("Ask")
    
    # Define what happens when the button is clicked
    ask_button.click(fn=answer_question, inputs=question, outputs=answer)

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)