from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from realtime_db_agent.part1_schema_retreival import get_table_schema
import json
load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.1
)

def generate_supabase_query(user_question: str, table_name: str = "products") -> dict:
    """Generate Supabase query parameters from user question."""
    # Dynamically get the schema from part1
    schema_text = get_table_schema(table_name)
    
    # Create a proper message object
    prompt = HumanMessage(content=f"""
    Given the following table schema:
    
    {schema_text}
    
    Generate Supabase query builder parameters to answer this question: "{user_question}"
    
    Return a JSON object with these fields:
    - select: comma-separated list of columns to select, or "*" for all
    - filters: array of filter objects, each with:
      - column: the column name
      - operator: "eq", "gt", "lt", "gte", "lte", "like", etc.
      - value: the value to compare against
    - order: optional column to order by
    - order_direction: "asc" or "desc"
    - limit: optional number of rows to return
    
    Only return the JSON without any explanation.
    """)
    
    # Use .invoke() instead of deprecated __call__
    response = llm.invoke([prompt])
    
    # Parse the JSON response
    import json
    import re
    
    # Extract JSON from the response (handles code blocks)
    content = response.content
    if "```" in content:
        match = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL)
        if match:
            content = match.group(1).strip()
    
    try:
        query_params = json.loads(content)
        return query_params
    except json.JSONDecodeError:
        # If parsing fails, return a simple default
        return {"select": "*", "filters": []}
    
def execute_supabase_query(query_params: dict):
    """Execute a query using Supabase Query Builder."""
    supabase: Client = create_client(
        os.getenv("SUPABASE_URL"), 
        os.getenv("SUPABASE_API")
    )
    
    # Start building the query
    query = supabase.table("products")
    
    # Add select columns
    query = query.select(query_params.get("select", "*"))
    
    # Add filters
    for filter_obj in query_params.get("filters", []):
        column = filter_obj.get("column")
        operator = filter_obj.get("operator")
        value = filter_obj.get("value")
        
        if not all([column, operator, value is not None]):
            continue
            
        if operator == "eq":
            query = query.eq(column, value)
        elif operator == "neq":
            query = query.neq(column, value)
        elif operator == "gt":
            query = query.gt(column, value)
        elif operator == "lt":
            query = query.lt(column, value)
        elif operator == "gte":
            query = query.gte(column, value)
        elif operator == "lte":
            query = query.lte(column, value)
        elif operator == "like":
            query = query.like(column, f"%{value}%")
        elif operator == "ilike":
            query = query.ilike(column, f"%{value}%")
        
    # Add ordering
    if "order" in query_params and query_params.get("order"):
        direction = query_params.get("order_direction", "asc")
        if direction == "asc":
            query = query.order(query_params["order"])
        else:
            query = query.order(query_params["order"], desc=True)
    
    # Add limit - FIXED HERE
    limit = query_params.get("limit")
    if limit is not None and isinstance(limit, int) and limit > 0:
        query = query.limit(limit)
    
    # Execute the query
    result = query.execute()
    return result.data

def generate_human_response(user_question: str, query_results: list) -> str:
    """Generate a human-friendly response based on query results."""
    prompt = HumanMessage(content=f"""
    The user asked: "{user_question}"
    
    The database query returned these results:
    {json.dumps(query_results, indent=2)}
    
    Please provide a clear, concise, and helpful answer to the user's question based on these results.
    Format important values like prices, IDs, or product names to make them stand out.
    """)
    
    response = llm.invoke([prompt])
    return response.content