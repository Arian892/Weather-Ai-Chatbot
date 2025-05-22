import streamlit as st
from weatherAgent import process_weather_query
from voice_input import record_and_transcribe  # ✅ Voice input function
from voice_output import speak  # ✅ Voice output function

# Set up the page
st.set_page_config(page_title="Weather Chatbot", page_icon="⛅")
st.title("⛅ Weather Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your weather assistant. Ask me about current conditions, forecasts, or historical weather."}
    ]

# Chat display
chat_container = st.container()
with chat_container:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])

            # 🔊 Add Hear button for assistant responses
            if message["role"] == "assistant":
                if st.button(f"🔊 Hear", key=f"hear_{i}"):
                    speak(message["content"])

# Input section
st.markdown("---")
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.text_input("", placeholder="Ask about the weather...", key="user_input", label_visibility="collapsed")
with col2:
    voice_button = st.button("🎤", use_container_width=True, help="Voice input")

# Input processing
if (prompt and prompt != st.session_state.get("last_prompt", "")) or voice_button:
    user_query = ""

    if prompt and prompt != st.session_state.get("last_prompt", ""):
        user_query = prompt
        st.session_state.last_prompt = prompt

    elif voice_button:
        try:
            user_query = record_and_transcribe(duration=5)
            st.success(f"Transcribed: \"{user_query}\"")
        except Exception as e:
            st.error(f"Voice input failed: {e}")
            user_query = ""

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})

        try:
            response = process_weather_query(user_query)
        except Exception as e:
            response = f"Sorry, I encountered an error: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
