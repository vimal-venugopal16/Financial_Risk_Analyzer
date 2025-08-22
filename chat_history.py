import time

import streamlit as st

if "chats" not in st.session_state:
    st.session_state["chats"] = {}   # store multiple chat groups
if "active_chat" not in st.session_state:
    st.session_state["active_chat"] = "Chat 1"
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Sidebar controls ---
with st.sidebar:
    if st.button("➕ New Chat"):
        new_name = f"Chat {len(st.session_state['chats'])+1}"
        st.session_state["chats"][st.session_state["active_chat"]] = st.session_state["messages"]
        st.session_state["active_chat"] = new_name
        st.session_state["messages"] = []

with st.sidebar:
    options = list(st.session_state["chats"].keys()) + [st.session_state["active_chat"]]
    choice = st.selectbox("💬 Chat History", options, index=options.index(st.session_state["active_chat"]))
    if choice != st.session_state["active_chat"]:
        # save current before switching
        st.session_state["chats"][st.session_state["active_chat"]] = st.session_state["messages"]
        st.session_state["active_chat"] = choice
        st.session_state["messages"] = st.session_state["chats"].get(choice, [])

for role, content in st.session_state["messages"]:
    with st.chat_message(role):
        st.markdown(content)

#if prompt := st.chat_input("Type your message..."):
    # Append user message


    # Call your Swarm here
    reply = "This is a response from the swarm"
    st.session_state["messages"].append(("assistant", reply))
    with st.chat_message("assistant"):
        st.markdown(reply)

st.session_state["chats"] = {
    time.time(): [("user", "Analyze Customer Financial Risk Profile"), ("assistant", "Hi!")],
    time.time(): [("user", "Analyze customer profile"), ("assistant", "Sure...")],
}
st.session_state["active_chat"] = "Chat 2"
st.session_state["messages"] = st.session_state["chats"]["Chat 2"]
