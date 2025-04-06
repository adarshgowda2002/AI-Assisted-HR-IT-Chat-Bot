import streamlit as st
import user_proxy
import memory
import groupchatmanager
import tools
from datetime import datetime
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
import os

# Create a directory for chat histories if it doesn't exist
CHAT_HISTORY_DIR = "chat_histories"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

def save_to_text_history(role: str, content: str):
    """Save chat messages to chat_history.txt"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("chat_history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role}: {content}\n")

def get_chat_history_handler(session_id: str) -> FileChatMessageHistory:
    """Get or create a chat history handler for the given session"""
    return FileChatMessageHistory(
        file_path=os.path.join(CHAT_HISTORY_DIR, f"chat_history_{session_id}.json")
    )

def save_to_chat_history(role: str, content: str, session_id: str):
    """Save chat messages using FileChatMessageHistory"""
    history = get_chat_history_handler(session_id)
    if role.lower() == "user":
        history.add_message(HumanMessage(content=content))
    else:
        history.add_message(AIMessage(content=content))
    save_to_text_history(role, content)

def load_chat_history(session_id: str):
    """Load existing chat history"""
    history = get_chat_history_handler(session_id)
    return history.messages

def initialize_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        messages = load_chat_history(st.session_state.session_id)
        for message in messages:
            st.session_state.messages.append({
                "role": "assistant" if isinstance(message, AIMessage) else "user",
                "content": message.content
            })

def main():
    st.title("AI Assisted HR & IT Chat Bot")
    st.markdown("Welcome to the AI Assisted HR & IT Chat Bot. Please type your message below and press 'Enter' to start the conversation.")
    initialize_session_state()

    # Add a button to clear chat history
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []
        history = get_chat_history_handler(st.session_state.session_id)
        history.clear()
        open("chat_history.txt", "w").close()
        st.rerun()

    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        if role == "user":
            st.markdown("**You:** " + content)
        else:
            st.markdown("**Assistant:** " + content)
        st.markdown("---")

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_to_chat_history("user", prompt, st.session_state.session_id)
        
        st.markdown("**You:** " + prompt)
        st.markdown("---")

        # Get AI response
        with st.spinner("Thinking..."):
            chat_response = user_proxy.user_proxy.initiate_chat(
                groupchatmanager.group_chat_manager,
                message=prompt,
            )
            
            # Extract only the direct AI response
            response_text = chat_response.summary if hasattr(chat_response, 'summary') else str(chat_response)
            
            st.markdown("**Assistant:** " + response_text)
            st.markdown("---")
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            save_to_chat_history("assistant", response_text, st.session_state.session_id)

    # Display session ID in sidebar
    st.sidebar.text(f"Session ID: {st.session_state.session_id}")

if __name__ == "__main__":
    main()






