#!/usr/bin/env python3
"""
Test script for the custom supervisor implementation with tool calling.
"""

from agent.graph import graph
from agent.state import State


def test_supervisor():
    """Test the supervisor with different types of messages."""

    test_cases = [
        "I applied to Google for a software engineer role today via LinkedIn",
        "Can you show me my current applications?",
        "Update my Google application status to interviewing",
        "How do I prepare for a technical interview?",
        "Can you help me schedule a follow-up call?",
        "I need help updating my resume",
        "What's the best way to find remote jobs?",
    ]

    for i, message in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {message}")

        try:
            # Run the graph
            result = graph.invoke(
                State(
                    messages=[{"role": "user", "content": message}],
                    classification_decision=None,
                    email_input=None,
                )
            )

            print(f"Classification: {result.get('classification_decision', 'None')}")
            print(f"Final messages: {len(result.get('messages', []))}")

            if result.get("messages"):
                last_message = result["messages"][-1]
                if hasattr(last_message, "content"):
                    print(f"Response: {last_message.content}")
                else:
                    print(f"Response: {last_message}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_supervisor()
