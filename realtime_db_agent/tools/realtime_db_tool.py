# realtime_db_agent/db_tool.py
from langchain.tools import Tool
from dotenv import load_dotenv
import os
from realtime_db_agent.part2_generating_and_executing_sql import (
    generate_supabase_query, 
    execute_supabase_query, 
    generate_human_response,
    handle_cross_table_query  # Keep this!
)

load_dotenv()

def db_lookup(question: str) -> str:
    try:
        query_params = generate_supabase_query(question)
        # print(f"[DEBUG] Generated query params: {query_params}")  # ADD THIS
        
        if query_params.get("table_name") == "NO_QUERY":
            return "I'm sorry, that question is not related to the database."

        result = execute_supabase_query(query_params)
        # print(f"[DEBUG] Query result: {result}")  # ADD THIS
        
        if "error" in result:
            return f"The database query failed with an error. Details: {result['error']}"

        return generate_human_response(question, result)
        
    except Exception as e:
        return f"I encountered an internal processing error: {str(e)}"
    
db_tool = Tool(
    name="DatabaseLookupTool",
    func=db_lookup,
    description="Look up information in the database about products, users, and transactions. Can answer questions about product details, users, pricing, and purchase history. **It automatically handles complex queries across multiple tables (joins).**"
)

__all__ = ["db_tool"]