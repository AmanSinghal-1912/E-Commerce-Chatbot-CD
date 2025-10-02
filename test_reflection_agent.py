import sys
import os

# Add main_folder to sys.path so Python can find reflection_agent.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'main_folder')))

from reflection_agent.agent import reflection_agent  # Import your function

# Sample test cases
test_cases = [
    {
        "db_output": "*User Information:**- **First Name:** Charlotte - **Last Name:** Garcia - **User ID:** 6 **Transactions Made by Charlotte Garcia (User ID: 6):** `1. **Transaction ID:** 6 - **Product ID:** 89- **Quantity:** 1- **Purchase Date:** 2025-10-01T15:00:00 - **Total Price:** $35.0 `2. **Transaction ID:** 26 - **Product ID:** 68 - **Quantity:** 1 - **Purchase Date:** 2025-10-02T18:00:00 - **Total Price:** $25.0 `3. **Transaction ID:** 46 - **Product ID:** 21 - **Quantity:** 1 - **Purchase Date:** 2025-10-04T09:00:00 - **Total Price:** $69.9 `4. **Transaction ID:** 66 - **Product ID:** 61 - **Quantity:** 1 - **Purchase Date:** 2025-10-05T15:00:00 - **Total Price:** $70.0 `5. **Transaction ID:** 86 - **Product ID:** 101 - **Quantity:** 1 - **Purchase Date:** 2025-10-06T19:00:00 - **Total Price:** $24.0 `6. **Transaction ID:** 106 - **Product ID:** 22 - **Quantity:** 1 - **Purchase Date:** 2025-10-07T23:00:00 - **Total Price:** $129.99 Charlotte Garcia has made a total of **6 transactions**.",
        "policy_output": "Based on our company policies, the warranty provided in our products is as follows: Our products come with a manufacturer warranty that applies to eligible products such as electronics and appliances. This warranty can be claimed by following the manufacturer's terms. Additionally, extended warranty and protection plans may be available for purchase. Please note that warranty claims must be reported within a reasonable timeframe, and some products may require specific documentation, such as DOA (Dead On Arrival) certification from the brand service center for certain items like mobile phones. If you have any further questions or concerns regarding the warranty of a specific product, please don't hesitate to reach out to us.",
    },
    # {
    #     "db_output": "",
    #     "policy_output": "Policy states all digital products are non-refundable.",
    #     "expected_keywords": ["non-refundable"]
    # },
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
