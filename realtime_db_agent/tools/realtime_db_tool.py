from langchain.tools import Tool
from dotenv import load_dotenv
from realtime_db_agent.part2_generating_and_executing_sql import (
    generate_supabase_query, 
    execute_supabase_query, 
    generate_human_response
)

# Load environment variables
load_dotenv()

# Main function that combines everything
def db_lookup(question: str) -> str:
    """Look up information in the database and provide a human-friendly response."""
    try:
        # Generate query parameters
        query_params = generate_supabase_query(question)
        
        # Execute the query
        results = execute_supabase_query(query_params)
        
        # Generate human response
        human_response = generate_human_response(question, results)
        return human_response
    except Exception as e:
        return f"I encountered an error while searching the database: {str(e)}"

# Create the Tool
db_tool = Tool(
    name="DatabaseLookupTool",
    func=db_lookup,
    description="Look up product information in the database and answer questions about products, inventory, prices, categories, etc."
)

# Export the tool
__all__ = ["db_tool"]