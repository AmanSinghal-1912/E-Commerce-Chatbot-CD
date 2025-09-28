import os
from realtime_db_agent.tools.realtime_db_tool import db_tool
from dotenv import load_dotenv
load_dotenv()

def db_agent(query: str) -> str:
    """Process a database-related query and return a response."""
    try:
        # Add enrichment context to help with product-specific queries
        enriched_query = f"""
        Query: {query}
        
        Context: The user is asking about our product information. 
        If they mention a specific product, provide detailed information.
        If they mention a product ID, search by that ID.
        If you can't find the exact product, suggest similar options.
        """
        return db_tool.run(enriched_query)
    except Exception as e:
        return f"I couldn't find that specific product information. Could you provide more details?"
# Export the function
__all__ = ["db_agent"]