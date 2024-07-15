import streamlit as st
import replicate

def generate_arctic_response(prompt_str):
    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={"prompt": prompt_str, "prompt_template": r"{prompt}", "temperature": 0.7},
    ):
        yield event

def main():
    st.title("Arctic AI Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    def clear_chat_history():
        st.session_state.messages = []

    # Get user input
    user_input = st.text_input("You:", key="user_input")
    if st.button("Send"):
        if user_input:
            # Add user message to session state
            user_message = {"role": "user", "content": user_input}
            st.session_state.messages.append(user_message)

            # Generate and display the assistant's response
            prompt = [msg["content"] for msg in st.session_state.messages]
            prompt_str = "\n".join(prompt)

            response_stream = generate_arctic_response(prompt_str)
            response_content = ""
            for response in response_stream:
                response_content += response

            assistant_message = {"role": "assistant", "content": response_content}
            st.session_state.messages.append(assistant_message)

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.text_area("User", value=message["content"], key=hash(message["content"]))
        else:
            st.text_area("Assistant", value=message["content"], key=hash(message["content"]))

    st.button('Clear chat history', on_click=clear_chat_history, key="clear_button")

if __name__ == "__main__":
    main()
