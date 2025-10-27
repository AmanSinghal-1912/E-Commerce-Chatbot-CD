from openai import OpenAI
from langchain_core.messages import HumanMessage
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from realtime_db_agent.part1_schema_retreival import get_table_schema,get_all_schemas,get_table_relationships,get_relationship_map
import json
import re
import logging

load_dotenv()

# Load table configuration from environment
AVAILABLE_TABLES = os.getenv("DB_TABLES").split(",")

# Initialize Nebius client
client = OpenAI(
    base_url="https://api.studio.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY")
)

# Set up logging
logging.basicConfig(
    filename='database_queries.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
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
        model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
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
    """Execute a query using Supabase Query Builder with logging."""
    supabase: Client = create_client(
        os.getenv("SUPABASE_URL"), 
        os.getenv("SUPABASE_API")
    )
    
    # Get table name from query params
    table_name = query_params.get("table_name", AVAILABLE_TABLES[0])
    
    # Log the query being executed
    logging.info(f"QUERY: Table={table_name}, Params={json.dumps(query_params)}")
    
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
                    if isinstance(value, str) and value.isdigit():  # If it's all numbers, convert to int
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
            elif operator == "in" and isinstance(value, list):
                query = query.in_(column, value)
        
        # Add ordering
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
        
        # Log the results
        logging.info(f"RESULT: Count={len(result.data)}, First few rows={json.dumps(result.data[:3])}")
        
        return {"table": table_name, "data": result.data}
        
    except Exception as e:
        # Log the error
        logging.error(f"ERROR: {str(e)}")
        
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
        model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
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

def generate_supabase_query_for_table(user_question: str, table_name: str) -> dict:
    """Generate query params for a specific table."""
    schema = get_table_schema(table_name, sample_rows=2)
    prompt = f"""
    Schema for table '{table_name}':
    {schema}

    User question: "{user_question}"

    Return a JSON with: table_name, select, filters (array), order (optional), limit (optional).
    Only use columns from the schema above.
    """
    
    response = client.chat.completions.create(
        model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
        messages=[
            {"role": "system", "content": "Output valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    content = response.choices[0].message.content
    if "```" in content:
        content = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL).group(1).strip()
    
    try:
        return json.loads(content)
    except:
        return {"table_name": table_name, "select": "*", "filters": []}

def handle_cross_table_query(user_question: str) -> str:
    """Handle complex queries that might involve multiple tables."""
    try:
        all_schemas = get_all_schemas(sample_rows=2)
        relationships = get_table_relationships()
        relationship_map = get_relationship_map()
        
        # Step 1: Ask LLM which tables are needed
        table_selection_prompt = f"""
        Given these database schemas:
        {all_schemas}

        User question: "{user_question}"

        Which tables from the following list are needed to answer this question?
        Available tables: {AVAILABLE_TABLES}

        Return ONLY a JSON array of table names, e.g. ["users", "transactions"].
        Do not include tables not in the available list.
        """
        
        response = client.chat.completions.create(
            model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
            messages=[
                {"role": "system", "content": "You output only valid JSON arrays of table names."},
                {"role": "user", "content": table_selection_prompt}
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        if "```" in content:
            content = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL).group(1).strip()
        
        needed_tables = json.loads(content)
        needed_tables = [t for t in needed_tables if t in AVAILABLE_TABLES]

        if len(needed_tables) <= 1:
            # Fallback to single-table query
            query_params = generate_supabase_query(user_question)
            result = execute_supabase_query(query_params)
            return generate_human_response(user_question, result)

        # Step 2: Build safe query plan using REAL relationships
        primary_table = needed_tables[0]
        all_results = {}
        
        # Query primary table
        primary_params = generate_supabase_query_for_table(user_question, primary_table)
        primary_result = execute_supabase_query(primary_params)
        all_results[primary_table] = primary_result.get("data", [])
        
        # Join related tables using REAL foreign keys
        for other_table in needed_tables[1:]:
            joined = False
            for (from_t, from_c), (to_t, to_c) in relationship_map.items():
                if {from_t, to_t} == {primary_table, other_table}:
                    if from_t == primary_table:
                        join_col_primary = from_c
                        join_col_other = to_c
                    else:
                        join_col_primary = to_c
                        join_col_other = from_c

                    join_values = [
                        row.get(join_col_primary) 
                        for row in all_results[primary_table] 
                        if row.get(join_col_primary) is not None
                    ]
                    join_values = list(set(join_values))

                    if join_values:
                        other_query = {
                            "table_name": other_table,
                            "select": "*",
                            "filters": [{"column": join_col_other, "operator": "in", "value": join_values}]
                        }
                        other_result = execute_supabase_query(other_query)
                        all_results[other_table] = other_result.get("data", [])
                        joined = True
                        break
            
            if not joined:
                all_results[other_table] = []

        # Step 3: Generate response from real data
        response_prompt = f"""
        User asked: "{user_question}"
        Data from tables:
        {json.dumps(all_results, indent=2, default=str)}

        Provide a clear, factual answer using ONLY the data above.
        Do not invent relationships or data.
        If a table has no matching records, say so.
        Be concise and helpful.
        """
        
        final_resp = client.chat.completions.create(
            model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
            messages=[
                {"role": "system", "content": "Answer based strictly on provided data."},
                {"role": "user", "content": response_prompt}
            ],
            temperature=0.2
        )
        return final_resp.choices[0].message.content

    except Exception as e:
        logging.error(f"Cross-table query error: {e}")
        return f"Sorry, I couldn't process this multi-table request due to an internal error."

