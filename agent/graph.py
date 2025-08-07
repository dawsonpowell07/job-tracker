from langgraph.graph import START, END, StateGraph
from agent.state import State
from agent.nodes.classifier_agent import classifier_router
from agent.nodes.application_agent import application_manager_agent

# Build workflow
overall_workflow = StateGraph(State)

# Add nodes
overall_workflow.add_node("classifier_router", classifier_router)
overall_workflow.add_node("application_agent", application_manager_agent)

# Add edges to connect nodes
overall_workflow.add_edge(START, "classifier_router")
overall_workflow.add_conditional_edges(
    "classifier_router",
    lambda state: state.get("classification_decision"),
    {
        "application_tracking": "application_agent",
        "interview_prep": END,
        "calendar": END,
        "resume_assistant": END,
        "general": END,
    },
)
overall_workflow.add_edge("application_agent", END)

# Compile the workflow
graph = overall_workflow.compile()

# def stream_graph_updates(user_input: str):
#     for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
#         for value in event.values():
#             print("Assistant:", value["messages"][-1].content)


# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break
#         stream_graph_updates(user_input)
#     except:
#         # fallback if input() is not available
#         user_input = "What do you know about LangGraph?"
#         print("User: " + user_input)
#         stream_graph_updates(user_input)
#         break
