import streamlit as st
import time
import boto3
from strands import Agent
from strands.tools import tool
from strands.multiagent import Swarm

# -------------------------------
# Tools deployed
# -------------------------------
@tool
def read_customer_creditdata(bucket: str, key: str) -> str:
    bucket = 'risk-analyzer-vimal'
    key = 'customer_financial_info_updated.csv'
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8")

@tool
def read_dynamodb_item(table_name: str) -> dict:
    table_name = 'risk_analyzer_profiles'
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    all_items = []
    response = None

    while True:
        if not response:
            response = table.scan()
        else:
            response = table.scan(ExclusiveStartKey=response.get('LastEvaluatedKey'))

        all_items.extend(response.get('Items', []))
        if 'LastEvaluatedKey' not in response:
            break
    return all_items

# -------------------------------
# Agents
# -------------------------------
financial_agent = Agent(
    name="financial_agent",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    tools=[read_customer_creditdata],
    system_prompt=("""You are a Customer Finance Data Analysis Agent specializing in gathering and analyzing financial information of customers from S3 bucket.
Your role in the swarm is to get information from s3 for the {prompt} and research insights on the financial data.
When giving input to other agents, evaluate if their information aligns with your research""")
)

profile_agent = Agent(
    name="profile_agent",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    tools=[read_dynamodb_item],
    system_prompt=("""You are a profile Agent specializing in generating customer profile information from dynamodb.
Your role in the swarm is to get the customer profile information from dynamoDB.
You should build upon information from other agents while adding your unique creative perspective.
Focus on novel approaches that others might not have considered.""")
)

market_agent = Agent(
    name="market_agent",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    system_prompt=("""You are a Market Analyzer Agent specializing in analyzing market inflation and employment conditions.
Your role in the swarm is to evaluate finacial info proposed by other agents and collaborate with market inforamtion.
You should carefully examine market condtions, find recent layoffs, employment rates and suggest how the customer profile performs against that.
Please analyze market trends relevant to their professions.
Be constructive in your criticism while ensuring the final solution is robust.""")
)

summarizer_agent = Agent(
    name="summarizer_agent",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    system_prompt=("""You are a Summarizer Agent specializing in synthesizing information.
Your role in the swarm is to gather insights from all agents and create a cohesive final solution.
You should combine the best ideas and address the criticisms to create a comprehensive response.
Give a risk rating to each customer based on the information you have gathered from all other agents.
The rating should be one of these 
Very High Risk
High Risk
Medium Risk
Low Risk
Focus on creating a clear, actionable summary that addresses the original query effectively.""")
)

# -------------------------------
# Swarm Setup
# -------------------------------
swarm = Swarm(
    [financial_agent, profile_agent, market_agent, summarizer_agent],
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,
    node_timeout=300.0,
    repetitive_handoff_detection_window=8,
    repetitive_handoff_min_unique_agents=3
)

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


st.title("Customer Financial Risk Analyzer - AWS Swarm")
st.sidebar.header("Example Prompt")
st.sidebar.text("Analyze the customer based on profile, financial, and market information and provide a risk rating.")

if prompt := st.chat_input("Enter a request for the Swarm to analyze..."):

    # Track agent execution steps
    agent_steps = ["financial_agent", "profile_agent", "market_agent", "summarizer_agent"]
    progress = st.progress(0)

    with st.status("Swarm Processing...", expanded=True) as status:
        st.write("🚀 Starting Swarm with 4 agents...")

        # Execute swarm
        result = swarm(prompt)

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
        st.write(extract_message(result.results["summarizer_agent"].result))

    # Option 2: fallback: show all agent results
    else:
        for agent_name, agent_result in result.results.items():
            st.write(f"### {agent_name}")
            st.write(extract_message(agent_result.result))
