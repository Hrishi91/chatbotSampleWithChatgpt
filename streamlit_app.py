import streamlit as st
from openai import OpenAI

# Initialize OpenAI client using Streamlit's secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# App title in Bengali
st.title("স্বাস্থ্য উপসর্গ সহকারী")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "তুমি একজন স্বাস্থ্য সহকারী, ব্যবহারকারী যে ভাষায়ই লিখুক না কেন, "
                "তুমি সবসময় বাংলা ভাষায় উত্তর দেবে। "
                "ব্যবহারকারীর উপসর্গ শুনে সাধারণ স্বাস্থ্য পরামর্শ দাও। "
                "তুমি ডাক্তার নও, তাই শুধুমাত্র সাধারণ সাবধানতা বা পরামর্শ দাও।"
            )
        }
    ]

# Display chat history
for message in st.session_state.messages[1:]:  # skip system message
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input (can be in Bengali or English)
user_input = st.chat_input("আপনার উপসর্গ লিখুন... (বাংলা বা ইংরেজিতে লিখতে পারেন)")

# Function to get a response from OpenAI in Bengali
def get_response(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

# If user input exists
if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get assistant response in Bengali
    response = get_response(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)
