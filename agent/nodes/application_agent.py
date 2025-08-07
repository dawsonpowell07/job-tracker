from typing import Optional
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from agent.state import State
from agent.prompts.application_manager_prompt import APPLICATION_MANAGER_PROMPT
from dotenv import load_dotenv

load_dotenv()


# Define tools
@tool
def log_application(
    company: str,
    role: str,
    date: str,
    source: str,
    resume_version: Optional[str] = None,
):
    """
    Log a new job application to the database.

    Args:
        company: The company name
        role: The job role/title
        date: The application date (YYYY-MM-DD format)
        source: How you applied (e.g., LinkedIn, referral, website)
        resume_version: Optional resume version used
    """
    return {
        "status": "success",
        "message": f"Application to {company} for {role} logged successfully",
    }


@tool
def update_application(company: str, updates: dict):
    """
    Update an existing job application.

    Args:
        company: The company name
        updates: Dictionary of fields to update (e.g., {"status": "interviewing"})
    """
    return {
        "status": "success",
        "message": f"Application to {company} updated successfully",
    }


@tool
def get_applications_by_user():
    """
    Get all applications for the current user.
    """
    return {
        "applications": [
            {
                "company": "Google",
                "role": "SWE",
                "status": "applied",
                "date": "2024-01-15",
            },
            {
                "company": "Microsoft",
                "role": "Software Engineer",
                "status": "interviewing",
                "date": "2024-01-10",
            },
        ]
    }


@tool
def Done():
    """
    Call this when you have completed the user's request and no further action is needed.
    """
    return {"status": "done", "message": "Task completed successfully"}


# Get tools
tools = [log_application, update_application, get_applications_by_user, Done]
tools_by_name = {tool.name: tool for tool in tools}

# Initialize the LLM for use with tools
llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
llm_with_tools = llm.bind_tools(tools, tool_choice="any")


# Nodes
def llm_call(state: State):
    """LLM decides whether to call a tool or not"""
    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    {"role": "system", "content": APPLICATION_MANAGER_PROMPT},
                ]
                + state["messages"]
            )
        ]
    }


def tool_node(state: State):
    """Performs the tool call"""
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(
            {"role": "tool", "content": observation, "tool_call_id": tool_call["id"]}
        )
    return {"messages": result}


# Conditional edge function
def should_continue(state: State):
    """Route to Action, or end if Done tool called"""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "Done":
                return END
            else:
                return "Action"
    return END


# Build workflow
application_manager_agent = StateGraph(State)

# Add nodes
application_manager_agent.add_node("llm_call", llm_call)
application_manager_agent.add_node("environment", tool_node)

# Add edges to connect nodes
application_manager_agent.add_edge(START, "llm_call")
application_manager_agent.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        # Name returned by should_continue : Name of next node to visit
        "Action": "environment",
        END: END,
    },
)
application_manager_agent.add_edge("environment", "llm_call")

# Compile the agent
application_manager_agent = application_manager_agent.compile()
