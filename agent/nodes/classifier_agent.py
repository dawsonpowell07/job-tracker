from langchain.chat_models import init_chat_model
from langgraph.graph import END
from langgraph.types import Command
from agent.state import State
from agent.schemas import RouterSchema
from agent.prompts.classifier_prompt import (
    CLASSIFIER_SYSTEM_PROMPT,
    CLASSIFIER_USER_PROMPT,
)
from dotenv import load_dotenv
from typing import cast

load_dotenv()

# Initialize the LLM for use with router / structured output
llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
llm_router = llm.with_structured_output(RouterSchema)


def classifier_router(state: State):
    """Analyze user message to decide which agent should handle it.

    The classifier step routes user messages to the appropriate specialized agent:
    - application_tracking: For job application logging and queries
    - interview_prep: For interview preparation questions
    - calendar: For scheduling and follow-up questions
    - resume_assistant: For resume-related questions
    - general: For general job hunting advice
    """
    # Get the last user message
    messages = state["messages"]
    if not messages:
        return Command(goto=END)

    last_message = messages[-1]
    user_message = (
        last_message.content if hasattr(last_message, "content") else str(last_message)
    )

    system_prompt = CLASSIFIER_SYSTEM_PROMPT
    user_prompt = CLASSIFIER_USER_PROMPT.format(user_message=user_message)

    # Run the router LLM
    result = llm_router.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    # Decision
    result = cast(RouterSchema, result)
    classification = result.classification

    if classification == "application_tracking":
        print(
            "🎯 Classification: APPLICATION_TRACKING - Routing to application manager"
        )
        goto = "application_agent"
        update = {
            "classification_decision": result.classification,
        }
    elif classification == "interview_prep":
        print(
            "📝 Classification: INTERVIEW_PREP - This would route to interview prep agent"
        )
        update = {
            "classification_decision": result.classification,
        }
        goto = END  # For now, end since we don't have interview prep agent
    elif classification == "calendar":
        print("📅 Classification: CALENDAR - This would route to calendar agent")
        update = {
            "classification_decision": result.classification,
        }
        goto = END  # For now, end since we don't have calendar agent
    elif classification == "resume_assistant":
        print("📄 Classification: RESUME_ASSISTANT - This would route to resume agent")
        update = {
            "classification_decision": result.classification,
        }
        goto = END  # For now, end since we don't have resume agent
    elif classification == "general":
        print("💬 Classification: GENERAL - This would route to general assistant")
        update = {
            "classification_decision": result.classification,
        }
        goto = END  # For now, end since we don't have general agent
    else:
        raise ValueError(f"Invalid classification: {result.classification}")

    return Command(goto=goto, update=update)
