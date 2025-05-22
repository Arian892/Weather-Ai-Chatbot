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

# Create a container for messages with fixed height
chat_container = st.container()
with chat_container:
    # Display chat messages in a scrollable area
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Add some spacing
st.write("")

# Fixed input at bottom using columns
st.markdown("---")
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.text_input("", placeholder="Ask about the weather...", key="user_input", label_visibility="collapsed", on_change=None)
with col2:
    voice_button = st.button("🎤", use_container_width=True, help="Voice input")

# Process input (works for both Enter key and button click)
if (prompt and prompt != st.session_state.get("last_prompt", "")) or voice_button:
    if prompt and prompt != st.session_state.get("last_prompt", ""):
        # Store the current prompt to avoid reprocessing
        st.session_state.last_prompt = prompt
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get assistant response
        try:
            response = process_weather_query(prompt)
        except Exception as e:
            response = f"Sorry, I encountered an error: {str(e)}"
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to show new messages
        st.rerun()
    
    elif voice_button:
        st.info("Voice input feature coming soon!")