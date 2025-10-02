from openai import OpenAI
from langchain_core.messages import HumanMessage
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from realtime_db_agent.part1_schema_retreival import get_table_schema
import json
import re
load_dotenv()

# Load table configuration from environment
AVAILABLE_TABLES = os.getenv("DB_TABLES").split(",")

# Initialize Nebius client
client = OpenAI(
    base_url="https://api.studio.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY")
)

def generate_supabase_query(user_question: str) -> dict:
    """Generate Supabase query parameters from user question using all available tables."""
    
    # Get schema for all tables
    all_schemas = ""
    for table in AVAILABLE_TABLES:
        schema = get_table_schema(table)
        all_schemas += f"\n\n{schema}"
    
    # Create the prompt
    prompt = f"""
    Given the following database schemas for all tables:
    
    {all_schemas}
    
    Based on the user question: "{user_question}"
    
    1. First determine which table(s) would be most appropriate to query.
    2. Then generate Supabase query builder parameters to answer this question.
    
    Return a JSON object with these fields:
    - table_name: the table to query
    - select: comma-separated list of columns to select, or "*" for all
    - filters: array of filter objects, each with:
      - column: the column name
      - operator: "eq", "gt", "lt", "gte", "lte", "like", etc.
      - value: the value to compare against
    - order: optional column to order by
    - order_direction: "asc" or "desc"
    - limit: optional number of rows to return
    
    Only return the JSON without any explanation.
    """
    
    # Call Nebius API
    response = client.chat.completions.create(
        model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
        messages=[
            {"role": "system", "content": "You are a database query generator that outputs only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    # Extract content from response
    content = response.choices[0].message.content
    
    # Parse the JSON response
    if "```" in content:
        match = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL)
        if match:
            content = match.group(1).strip()
    
    try:
        query_params = json.loads(content)
        return query_params
    except json.JSONDecodeError:
        # If parsing fails, return a simple default
        return {"table_name": AVAILABLE_TABLES[0], "select": "*", "filters": []}
    
def execute_supabase_query(query_params: dict):
    """Execute a query using Supabase Query Builder."""
    supabase: Client = create_client(
        os.getenv("SUPABASE_URL"), 
        os.getenv("SUPABASE_API")
    )
    
    # Get table name from query params
    table_name = query_params.get("table_name", AVAILABLE_TABLES[0])
    
    try:
        # Start building the query with the proper table
        query = supabase.table(table_name)
        
        # Add select columns
        query = query.select(query_params.get("select", "*"))
        
        # Add filters
        for filter_obj in query_params.get("filters", []):
            column = filter_obj.get("column")
            operator = filter_obj.get("operator")
            value = filter_obj.get("value")
            
            if not all([column, operator, value is not None]):
                continue
                
            # Convert value type based on column name patterns
            if "id" in column.lower() and not isinstance(value, int):
                try:
                    if value.isdigit():  # If it's all numbers, convert to int
                        value = int(value)
                except (AttributeError, ValueError):
                    pass  # Keep as is if conversion fails
            
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
        
        # Add ordering (with better error handling)
        if "order" in query_params and query_params.get("order"):
            order_col = query_params["order"]
            # Don't include table name in order clause if it has a dot
            if "." in order_col:
                order_col = order_col.split(".")[-1]
                
            direction = query_params.get("order_direction", "asc")
            if direction == "asc":
                query = query.order(order_col)
            else:
                query = query.order(order_col, desc=True)
        
        # Add limit
        limit = query_params.get("limit")
        if limit is not None and isinstance(limit, int) and limit > 0:
            query = query.limit(limit)
        
        # Execute the query
        result = query.execute()
        return {"table": table_name, "data": result.data}
        
    except Exception as e:
        # Return error info for debugging but in a structured format
        return {
            "table": table_name, 
            "data": [], 
            "error": str(e),
            "query_params": query_params
        }

def generate_human_response(user_question: str, query_result: dict) -> str:
    """Generate a human-friendly response based on query results."""
    table_name = query_result.get("table", "unknown")
    results = query_result.get("data", [])
    
    # Use Nebius client instead of llm
    response = client.chat.completions.create(
        model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant providing database query results."},
            {"role": "user", "content": f"""
The user asked: "{user_question}"

The query was executed on the '{table_name}' table and returned these results:
{json.dumps(results, indent=2)}

Please provide a clear, concise, and helpful answer to the user's question based on these results.
Format important values like prices, IDs, or product names to make them stand out.
Keep your response conversational and friendly.
"""}
        ],
        temperature=0.2
    )
    
    return response.choices[0].message.content

def handle_cross_table_query(user_question: str) -> str:
    """Handle complex queries that might involve multiple tables."""
    try:
        # Get schema for all tables
        all_schemas = ""
        for table in AVAILABLE_TABLES:
            schema = get_table_schema(table)
            all_schemas += f"\n\n{schema}"
        
        prompt = f"""
        Given these database schemas:
        
        {all_schemas}
        
        The user asked: "{user_question}"
        
        This question might require data from multiple tables. Please:
        
        1. Identify the primary table we should query first
        2. Generate a complete Supabase query for that table
        
        Return a JSON object with:
        - table_name: the primary table to query
        - select: fields to select
        - filters: array of filter objects (column, operator, value)
        - no complex joins or operations
        
        Only return the JSON without additional text.
        """
        
        # Use Nebius client instead of llm
        response = client.chat.completions.create(
            model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
            messages=[
                {"role": "system", "content": "You are a database query generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        # Parse the response to get query parameters
        content = response.choices[0].message.content
        if "```" in content:
            match = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL)
            if match:
                content = match.group(1).strip()
        
        # Execute the primary query
        query_params = json.loads(content)
        result = execute_supabase_query(query_params)
        
        # If we got results, see if we need secondary data
        if result.get("data") and not result.get("error"):
            # Now decide if we need additional data from other tables
            context_prompt = f"""
            The user asked: "{user_question}"
            
            We have data from the {query_params.get("table_name")} table:
            {json.dumps(result.get("data"), indent=2)}
            
            Should we query another table to complete this answer? If yes, which one and why?
            Answer with just "no" if sufficient, otherwise specify which table and why.
            """
            
            context_response = client.chat.completions.create(
                model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
                messages=[
                    {"role": "system", "content": "You are a database query analyzer."},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.1
            )
            
            # If the LLM suggests getting more data
            if "no" not in context_response.choices[0].message.content.lower():
                # Generate response with explanation that we need more info
                return generate_human_response(user_question, result) + "\n\nI could get more information from related tables if you'd like additional details."
            else:
                # We have all we need
                return generate_human_response(user_question, result)
        else:
            # If there was an error, explain the situation
            if result.get("error"):
                return f"I tried to find users who bought highly-rated products, but I encountered a technical issue. Could you try asking about either products with high ratings or specific user purchase history separately?"
            else:
                return "I couldn't find any matching information for your query. Could you please be more specific about what you're looking for?"
            
    except Exception as e:
        return f"I ran into a problem while trying to answer your question: {str(e)}. Could you try asking in a different way?"