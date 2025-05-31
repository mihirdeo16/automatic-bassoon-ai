from pickle import INST
from google.adk.agents import Agent
from tools import get_weather, get_current_time

NAME = "Weather and Time Agent"
MODEL = "gemini-2.0-flash"
AGENT_DESCRIPTION = (
    "A helpful agent that can answer questions about the time and weather in a city."
)
INSTRUCTOR = (
    "You are a helpful agent who can answer user questions about the time and weather in a city."
)
# Create an agent that can answer questions about the time and weather in a city.
root_agent = Agent(
    name=NAME,
    model=MODEL,
    description=AGENT_DESCRIPTION,
    instruction=INSTRUCTOR,
    tools=[get_weather, get_current_time],
)