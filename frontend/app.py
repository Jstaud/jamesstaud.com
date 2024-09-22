import gradio as gr

# Mock function to handle user questions - Replace with your RAG model integration
def answer_question(question):
    # In a real scenario, this function will query your backend or RAG model
    # For now, it's returning a placeholder response
    return f"Thanks for asking! Currently, this is a placeholder response to: {question}"

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
