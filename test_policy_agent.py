import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from policy.tools.policy_tool import policy_tool

def test_policy():
    query = "What about warranty provided in your products?"
    result = policy_tool.run(query)
    print("\n--- Query ---")
    print(query)
    print("\n--- Result ---")
    print(result)

if __name__ == "__main__":
    test_policy()

