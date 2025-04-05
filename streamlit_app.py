import streamlit as st
from openai import OpenAI
from gtts import gTTS
from io import BytesIO
from streamlit_webrtc import webrtc_streamer
import tempfile

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# App title
st.title("স্বাস্থ্য উপসর্গ সহকারী (মাল্টিমোডাল)")

# Mode selector
mode = st.radio("আপনি কীভাবে কথা বলতে চান?", [
    "✍️ Text ➝ Text",
    "✍️ Text ➝ 🎧 Audio",
    "🎙️ Audio ➝ Text",
    "🎙️ Audio ➝ 🎧 Audio"
])

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "তুমি একজন স্বাস্থ্য সহকারী। ব্যবহারকারী যেকোনো ভাষায় লিখতে বা বলতে পারে, "
                "কিন্তু তুমি সবসময় বাংলা ভাষায় সহজ ও সাধারণ স্বাস্থ্য পরামর্শ দেবে। "
                "তুমি ডাক্তার নও, তাই চিকিৎসা বা ওষুধের নাম দিও না।"
            )
        }
    ]

# Show previous messages (skip system)
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Text-to-speech function
def speak_bangla(text):
    tts = gTTS(text=text, lang="bn")
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

# Get assistant response
def get_response(user_text):
    prompt = (
        f"ব্যবহারকারী লিখেছে বা বলেছে: \"{user_text}\"। "
        "উপসর্গ বিশ্লেষণ করে বাংলায় সহজ ভাষায় সাধারণ স্বাস্থ্য পরামর্শ দাও। "
        "ডাক্তারের পরামর্শ ছাড়া কোনো চিকিৎসা বা ওষুধের নাম দিও না।"
    )
    messages = st.session_state.messages + [{"role": "user", "content": user_text}, {"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

# Handle input based on mode
user_input = None

if "Text" in mode:
    text = st.chat_input("আপনার উপসর্গ লিখুন...")
    if text:
        user_input = text

if "Audio" in mode:
    st.subheader("🎙️ ভয়েস ইনপুট (mp3/wav আপলোড করুন)")
    audio = st.file_uploader("আপনার ভয়েস রেকর্ড করুন", type=["mp3", "wav"])
    if audio:
        audio_bytes = audio.read()
        audio_file = BytesIO(audio_bytes)
        with st.spinner("ভয়েস প্রসেস করা হচ্ছে..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="bn"
            )
            st.success(f"আপনার কথা: {transcript}")
            user_input = transcript

# Process if we have any user input (text or audio)
if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get assistant response
    response = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

    # Play voice if mode says so
    if "Audio" in mode:
        st.subheader("🔊 সহকারীর অডিও উত্তর")
        audio_response = speak_bangla(response)
        st.audio(audio_response, format="audio/mp3")
