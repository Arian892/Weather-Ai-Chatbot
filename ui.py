import gradio as gr
from weatherAgent import process_weather_query  # Your backend function

def chatbot_response(user_input, history):
    history = history or []
    # Append user message
    history.append({"role": "user", "content": user_input})
    # Get bot response
    response = process_weather_query(user_input)
    history.append({"role": "assistant", "content": response})
    return history, history

with gr.Blocks() as demo:
    gr.Markdown("# ⛅ Weather Chatbot")
    gr.Markdown("Ask me about current weather, forecasts, or historical weather data.")

    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox(placeholder="Ask about the weather...")
    clear = gr.Button("Clear")

    history = gr.State([])

    msg.submit(chatbot_response, inputs=[msg, history], outputs=[chatbot, history])
    clear.click(lambda: ([], []), None, [chatbot, history])

demo.launch()
