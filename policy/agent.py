import os
from policy.tools.policy_tool import policy_tool
from dotenv import load_dotenv
load_dotenv()

def policy_agent(query: str) -> str:
    """Process a policy-related query and return a response."""
    try:
        return policy_tool.run(query)
    except Exception as e:
        return f"Policy Agent Error: {str(e)}"

# Export the function
__all__ = ["policy_agent"]