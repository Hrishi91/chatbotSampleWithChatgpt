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
                "তুমি একজন স্বাস্থ্য সহকারী। ব্যবহারকারী যেকোনো ভাষায় লিখতে পারে, "
                "কিন্তু তুমি সবসময় বাংলা ভাষায় সহজ ও সাধারণ পরামর্শ দেবে। "
                "তুমি ডাক্তার নও, তাই ওষুধ বা নির্দিষ্ট চিকিৎসা দিও না।"
            )
        }
    ]

# Display chat history
for message in st.session_state.messages[1:]:  # skip system message
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box (accept Bengali or English)
user_input = st.chat_input("আপনার উপসর্গ লিখুন... (বাংলা বা ইংরেজিতে)")

# Function to get assistant response
def get_response(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

# When user submits input
if user_input:
    # Display user's original input
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Construct assistant prompt explicitly (to inject instruction)
    assistant_prompt = (
        f"ব্যবহারকারী লিখেছে: \"{user_input}\"। "
        "উপসর্গ বিশ্লেষণ করে বাংলায় সহজ ভাষায় সাধারণ স্বাস্থ্য পরামর্শ দাও। "
        "ডাক্তারের পরামর্শ ছাড়া কোনো চিকিৎসা বা ওষুধের নাম দিও না।"
    )

    # Append assistant prompt as if user asked it
    messages_for_response = st.session_state.messages + [{"role": "user", "content": assistant_prompt}]

    # Get assistant response
    response = get_response(messages_for_response)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
