import streamlit as st
import time
import Agent
import Tools


def extract_message(agent_result):
    """Extract plain text message from a Strands agent result."""
    try:
        # Case 1: already plain text
        if isinstance(agent_result, str):
            return agent_result
        # Case 2: object with .result attr
        if hasattr(agent_result, "result"):
            return extract_message(agent_result.result)
        # Case 3: dict with 'messages'
        if isinstance(agent_result, dict) and "messages" in agent_result:
            return "\n".join(m.get("content", "") for m in agent_result["messages"])
        # Case 4: list of messages
        if isinstance(agent_result, list):
            return "\n".join(str(m) for m in agent_result)
    except Exception:
        return str(agent_result)
    return str(agent_result)
# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(layout="wide")
st.markdown("<h1 style='top:10;text-align: center; color: #000000; font-family: verdana; font-size: 30px;'>Customer Financial Risk Analyzer</h1>", unsafe_allow_html=True)


st.sidebar.markdown("Financial risk analyzer:Analyzes customer profile by evaluating a customer's background, behavior, and financial activities to determine the potential risk they may pose when determining any credit application.This analysis uses various attributes and data points, such as their financial details, customer profile, market trends, and demographics, to assign a risk rating with justification of why that rating was given")

st.sidebar.header("Example Prompt")
st.sidebar.write("Analyze the customer based on profile, financial, and market information and provide a risk rating.\n Ex: Profiles :\nAva Brown,\n Wood Gregory\n,Fuller Crystal\n,Mills Susan")

if prompt := st.chat_input("Enter a request for the Swarm to analyze..."):

    # Track agent execution steps
    agent_steps = ["financial_agent", "profile_agent", "market_agent", "summarizer_agent"]
    progress = st.progress(0)

    with st.status("Swarm Processing...", expanded=True) as status:
        st.write("🚀 Starting Analysis with Risk Analysis Swarm...")
        st.write("🚀 Starting with Financial Analysis Agent...")
        # Execute swarm
        result = Agent.swarm(prompt)

        # Show each agent result
        for i, agent in enumerate(agent_steps, start=1):
            if agent in result.results:
                st.write(f"🔹 {agent} completed.")
                st.write(result.results[agent].result)
            else:
                st.write(f"⚠️ {agent} did not return a result.")
            progress.progress(i / len(agent_steps))
            time.sleep(1)  # just for nicer animation

        status.update(label="✅ Swarm Completed", state="complete", expanded=False)

    # Final summary
    st.subheader("Final Swarm Summary")
    #st.write(result.results[summarizer_agent].result)
    if "summarizer_agent" in result.results:
        message = extract_message(result.results["summarizer_agent"])
        st.write(message)
        Tools.send_report(message)
    # Option 2: fallback: show all agent results
    else:
        for agent_name, agent_result in result.results.items():
            st.write(f"### {agent_name}")
            message = extract_message(agent_result)
            st.write(message)
