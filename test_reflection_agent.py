import sys
import os

# Add main_folder to sys.path so Python can find reflection_agent.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'main_folder')))

from reflection_agent.agent import reflection_agent  # Import your function

# Sample test cases
test_cases = [
    {
        "db_output": "Customer requested refund for order #1234. Database shows order was delivered on 2025-09-25.",
        "policy_output": "Refund policy allows returns within 7 days of delivery. Customer is eligible for a refund.",
        "expected_keywords": ["refund", "order", "eligible"]
    },
    {
        "db_output": "",
        "policy_output": "Policy states all digital products are non-refundable.",
        "expected_keywords": ["non-refundable"]
    },
]

# Run tests
for idx, case in enumerate(test_cases, start=1):
    print(f"\n=== Test Case {idx} ===")
    result = reflection_agent(case["db_output"], case["policy_output"])
    print("Merged Response:\n", result)

    # Check if expected keywords are present
    missing_keywords = [kw for kw in case["expected_keywords"] if kw.lower() not in result.lower()]
    if missing_keywords:
        print("Missing keywords:", missing_keywords)
    else:
        print("All expected keywords present")
