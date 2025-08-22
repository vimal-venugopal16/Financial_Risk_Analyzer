from strands import Agent
from strands.multiagent import Swarm
import Tools as t
import toml

# -------------------------------
# Agents
# -------------------------------

with open('.streamlit\config.toml', 'r') as f:
    config = toml.load(f)



financial_agent = Agent(
    name="financial_agent",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    tools=[t.read_customer_creditdata],
    system_prompt=(config['Secrets']['finance_system_prompt'])
)

profile_agent = Agent(
    name="profile_agent",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    tools=[t.read_customer_profile],
    system_prompt=(config['Secrets']['profile_system_prompt'])
)

market_agent = Agent(
    name="market_agent",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    system_prompt=(config['Secrets']['market_system_prompt'])
)

summarizer_agent = Agent(
    name="summarizer_agent",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    system_prompt=(config['Secrets']['summarizer_system_prompt'])
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

