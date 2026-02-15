from google.adk.agents import Agent
from google.adk.tools import google_search
from .utils import load_instruction_file
MODEL = "gemini-2.0-flash"

# ----------- Sub Agents 1: FindTrendingJargonAgent -----------
google_search_agent = Agent(
    name="FindTrendingJargonAgent",
    model=MODEL,
    description="A helpful agent that can crawl to web and get trending keywords.",
    instruction=load_instruction_file("gsearch_instruction.txt"),
    tools=[google_search],
    output_key="jargon_trends",
)


# ----------- Root Agents: CorporateJargonAgent -----------
# corporate_jargon_agent = Agent(
#     name="CorporateJargonAgent",
#     model=MODEL,
#     description="A helpful agent that converts normal text to corporate jargon blended text.",
#     instruction=load_instruction_file("root_agent_instruction.txt"),
#     sub_agents=[google_search_agent],
#     parent_agent=None,
# )

root_agent = google_search_agent

