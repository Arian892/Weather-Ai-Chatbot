import streamlit as st
from weatherAgent import process_weather_query

# Set up the page
st.set_page_config(page_title="Weather Chatbot", page_icon="⛅")
st.title("⛅ Weather Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your weather assistant. Ask me about current conditions, forecasts, or historical weather."}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

#checking 
# Chat input
if prompt := st.chat_input("Ask about the weather..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Checking weather..."):
            try:
                response = process_weather_query(prompt)
            except Exception as e:
                response = f"Sorry, I encountered an error: {str(e)}"
        st.write(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
