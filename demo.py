#!/usr/bin/env python3
"""
Demo script for the custom supervisor implementation with tool calling.
"""

from agent.graph import graph
from agent.state import State


def demo():
    """Demo the supervisor with different types of messages."""

    print("🤖 Job Tracker Assistant Demo")
    print("=" * 50)

    # Test application tracking
    print("\n📝 Testing Application Tracking:")
    print("User: I applied to Google for a software engineer role today via LinkedIn")

    try:
        result = graph.invoke(
            State(
                messages=[
                    { "role": "user", "content": "I applied to Google for a software engineer role today via LinkedIn" }
                ],
                classification_decision=None,
                email_input=None,
            )
        )

        print(f"Classification: {result.get('classification_decision', 'None')}")
        if result.get("messages"):
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                print(f"Assistant: {last_message.content}")

    except Exception as e:
        print(f"Error: {e}")

    # Test application query
    print("\n📋 Testing Application Query:")
    print("User: Can you show me my current applications?")

    try:
        result = graph.invoke(
            State(
                messages=[
                    {
                        "role": "user",
                        "content": "Can you show me my current applications?",
                    }
                ],
                classification_decision=None,
                email_input=None,
            )
        )

        print(f"Classification: {result.get('classification_decision', 'None')}")
        if result.get("messages"):
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                print(f"Assistant: {last_message.content}")

    except Exception as e:
        print(f"Error: {e}")

    # Test non-application message
    print("\n💬 Testing Non-Application Message:")
    print("User: How do I prepare for a technical interview?")

    try:
        result = graph.invoke(
            State(
                messages=[
                    {
                        "role": "user",
                        "content": "How do I prepare for a technical interview?",
                    }
                ],
                classification_decision=None,
                email_input=None,
            )
        )

        print(f"Classification: {result.get('classification_decision', 'None')}")
        if result.get("messages"):
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                print(f"Assistant: {last_message.content}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    demo()
