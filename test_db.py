import os
import sys
# Add the project root to the path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from realtime_db_agent.agent import db_agent
from dotenv import load_dotenv
load_dotenv()

def test_product_by_id():
    # Test specific product ID query - using numeric ID
    query = "I want to know about the product whose product id is 36"
    print(f"\nQuery: {query}")
    response = db_agent(query)
    print("\nAgent Response:")
    print(response)

def test_cross_table_query():
    # Use a simpler cross-table query
    query = "how many transactions has garcia charlotte made?"
    print(f"\nQuery: {query}")
    response = db_agent(query)
    print("\nAgent Response:")
    print(response)

def test_transaction_query():
    # Test transaction-related query
    query = "What are the recent transactions with a total price over $200?"
    print(f"\nQuery: {query}")
    response = db_agent(query)
    print("\nAgent Response:")
    print(response)

# def test_cross_table_query():
#     # Test query that requires multiple tables
#     query = "Which users bought products with a rating of 5?"
#     print(f"\nQuery: {query}")
#     response = db_agent(query)
#     print("\nAgent Response:")
#     print(response)

if __name__ == "__main__":
    print("===== Testing Database Agent =====")
    
    # Run the tests
    # test_product_by_id()
    # test_transaction_query()
    test_cross_table_query()