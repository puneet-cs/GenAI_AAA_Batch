# Personal SIRI: Voice/Chat Assistant using LLM

import streamlit as st

# configure the app page
st.set_page_config(
    page_title = "Personal SIRI",
    layout = "wide"
)

# import other require libraries
import os
import time
import pyttsx3   # convert text  to Speech
import speech_recognition as sr  # speech to text
from groq import Groq  # help to connect with LLM online
from dotenv import load_dotenv  # load the API key from local environment

# load the key inside code from local env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Checking API key 
if not GROQ_API_KEY:
    st.error("Missing Groq API key")
    st.stop()

# initialize the LLM model
client = Groq(api_key = GROQ_API_KEY)
MODEL = "openai/gpt-oss-20b"

# Initilize Speeech to text recognizer
@st.cache_resource
def get_reconizer():
    return sr.Recognizer()

recognizer = get_reconizer()

# initialize Text to speech engine
def get_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        st.error(f"Failed to initialize the TTS engine: {e}")
        return None

# activate the microphone on laptop, record voice and convert to text
def listen_to_speech():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration = 1)
            audio = recognizer.listen(source, phrase_time_limit = 10)

        text = recognizer.recognize_google(audio)   # convert audio to text
        return text.lower()
    except sr.UnknownValueError:
        return "sorry, I didn't Catch you"
    except sr.RequestError:
        return "Speech service not available"
    except Exception as e:
        return f"Error: {e}"

def gen_ai_response(chats):
    try:
        response = client.chat.completions.create(
            model = MODEL,
            messages = chats,
            temperature = 0.7
        )
        result = response.choices[0].message.content
        return result.strip() if result else "Sorry, I could not generate the response"
    except Exception as e:
        return f"Error getting AI response: {e}"

def speak(text, voice_gender = "girl"):
    try:
        engine = get_tts_engine()
        if engine is None:
            return

        voices = engine.getProperty('voices')
        if voices:
            if voice_gender == "boy":
                for voice in voices:
                    if "male" in voices.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            else:
                for voice in voices:
                    if "female" in voice.name.lower() or "zira"  in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
        engine.setProperty('rate', 150)  # bigger value fast that will speak
        engine.setProperty('volume', 0.8)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error(f"TTS Error: {e}")

def main():
    st.title("Personal SIRI Voice Assistant")
    st.markdown("---")

# creating a list of chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role" : "system", "content" : "You are a helpful voice and chat assistant. Reply answer in just One line"}
    ]

# list of messages to show on the screen
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("CONTROLS")

    tts_enabled = st.checkbox("Enable Text to Speech", value = True)

    voice_gender = st.selectbox(
        "Voice Gender",
        options = ["girl", "boy"],
        index = 0,
        help = "This option is to decide the AI voice"
    )

    if st.button("START", type = "primary", use_container_width = True):
        with st.spinner("Listening..."):
            user_input = listen_to_speech()  # Task-1 : receieve the voice

            if user_input and user_input not in ["sorry, I didn't Catch you", "Speech service not available"]:
                st.session_state.messages.append({"role" : "user", "content" : user_input})
                st.session_state.chat_history.append({"role" : "user", "content" : user_input})

                # Get LLM reply
                with st.spinner("Thinking..."):
                    ai_response = gen_ai_response(st.session_state.chat_history)
                    st.session_state.messages.append({"role" : "assistant", "content" : ai_response})
                    st.session_state.chat_history.append({"role" : "assistant", "content" : ai_response})

                if tts_enabled:
                    speak(ai_response, voice_gender )

                st.rerun()

        st.markdown("Text Input")
        user_text = st.text_input("Type your message:", key = "text_input")




if __name__ =="__main__":
    main()
