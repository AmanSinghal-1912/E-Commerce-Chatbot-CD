import os
from realtime_db_agent.tools.realtime_db_tool import db_tool
from dotenv import load_dotenv
load_dotenv()

def db_agent(query: str) -> str:
    """Process a database-related query and return a response."""
    try:
        # Add enrichment context to help with any database queries
        enriched_query = f"""
        Query: {query}
        
        Context: The user is asking about information in our database, which contains:
        - Product information (products table)
        - User/customer details (users table)
        - Transaction/order history (transactions table)
        
        Be thorough in your search across all relevant tables.
        """
        return db_tool.run(enriched_query)
    except Exception as e:
        return f"I couldn't find the information you're looking for. Could you provide more details?"

# Export the function
__all__ = ["db_agent"]