# filepath: c:\Users\singh\Desktop\Chatbot-EC\realtime_db_agent\tools\realtime_db_tool.py
from langchain.tools import Tool
from dotenv import load_dotenv
import os
from realtime_db_agent.part2_generating_and_executing_sql import (
    generate_supabase_query, 
    execute_supabase_query, 
    generate_human_response,
    handle_cross_table_query
)

# Load environment variables
load_dotenv()

# Main function that combines everything
def db_lookup(question: str) -> str:
    """Look up information in the database and provide a human-friendly response."""
    try:
        # Check for complex cross-table queries first
        if any(keyword in question.lower() for keyword in [
            "join", "related", "between", "purchase history", "transaction", "user who", 
            "customer who", "bought", "purchased", "order"
        ]):
            return handle_cross_table_query(question)
            
        # For standard queries
        query_params = generate_supabase_query(question)
        result = execute_supabase_query(query_params)
        return generate_human_response(question, result)
        
    except Exception as e:
        return f"I encountered an error while searching the database: {str(e)}"

# Create the Tool
db_tool = Tool(
    name="DatabaseLookupTool",
    func=db_lookup,
    description="Look up information in the database about products, users, and transactions. Can answer questions about product details, users, pricing, and purchase history."
)

# Export the tool
__all__ = ["db_tool"]