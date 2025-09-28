import os 
from realtime_db_agent.part2_generating_and_executing_sql import generate_supabase_query, execute_supabase_query, generate_human_response
from dotenv import load_dotenv
load_dotenv()

# Define the user query
user_input = "i want to know about the product whose product id is ZY36VAX0"

# Generate query parameters
query_params = generate_supabase_query(user_input)
# print("Generated Query Parameters:", query_params)

# Execute the query
results = execute_supabase_query(query_params)

# Generate human-friendly response
human_response = generate_human_response(user_input, results)

print("\nHuman-Friendly Response:")
print(human_response)