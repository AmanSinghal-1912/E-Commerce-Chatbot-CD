from openai import OpenAI
from langchain_core.messages import HumanMessage
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from realtime_db_agent.part1_schema_retreival import get_table_schema
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

def handle_cross_table_query(user_question: str) -> str:
    """Handle complex queries that might involve multiple tables."""
    try:
        # Get schema for all tables
        all_schemas = ""
        for table in AVAILABLE_TABLES:
            schema = get_table_schema(table)
            all_schemas += f"\n\n{schema}"
        
        # First, identify relevant tables and plan the query approach
        planning_prompt = f"""
        Given these database schemas:
        
        {all_schemas}
        
        The user asked: "{user_question}"
        
        This question requires data from multiple tables.
        
        1. Determine which tables are needed to fully answer this query
        2. Explain how these tables should be linked (which columns)
        
        Return a JSON object with:
        {{
          "primary_table": "name of main table to query first",
          "secondary_tables": ["other table names needed"],
          "join_conditions": [
            {{
              "table1": "name of first table", 
              "column1": "column in first table", 
              "table2": "name of second table", 
              "column2": "column in second table"
            }}
          ]
        }}
        
        Only return the JSON without additional text.
        """
        
        # Get the query plan
        planning_response = client.chat.completions.create(
            model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
            messages=[
                {"role": "system", "content": "You are a database query planner."},
                {"role": "user", "content": planning_prompt}
            ],
            temperature=0.1
        )
        
        # Parse the planning response
        planning_content = planning_response.choices[0].message.content
        if "```" in planning_content:
            match = re.search(r"```(?:json)?(.*?)```", planning_content, re.DOTALL)
            if match:
                planning_content = match.group(1).strip()
                
        plan = json.loads(planning_content)
        
        # Now execute queries for each table and collect results
        all_results = {}
        
        # First query the primary table
        primary_table = plan.get("primary_table")
        primary_query_prompt = f"""
        Given this database schema:
        
        {get_table_schema(primary_table)}
        
        Generate a Supabase query for the table '{primary_table}' to find information relevant to: "{user_question}"
        
        Return only a JSON with:
        {{
          "table_name": "{primary_table}",
          "select": "columns to select or *",
          "filters": [{{column, operator, value}}],
          "order": "column to order by (optional)",
          "limit": number (optional)
        }}
        """
        
        primary_response = client.chat.completions.create(
            model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
            messages=[
                {"role": "system", "content": "You generate database queries in JSON format only."},
                {"role": "user", "content": primary_query_prompt}
            ],
            temperature=0.1
        )
        
        primary_query = json.loads(primary_response.choices[0].message.content.strip())
        primary_result = execute_supabase_query(primary_query)
        all_results[primary_table] = primary_result.get("data", [])
        
        # Now query each secondary table based on join conditions
        for join in plan.get("join_conditions", []):
            secondary_table = join.get("table2") if join.get("table1") == primary_table else join.get("table1")
            join_column_primary = join.get("column1") if join.get("table1") == primary_table else join.get("column2")
            join_column_secondary = join.get("column2") if join.get("table1") == primary_table else join.get("column1")
            
            # Get values from primary table for the join
            join_values = [row.get(join_column_primary) for row in all_results[primary_table] if row.get(join_column_primary) is not None]
            
            if join_values:
                secondary_query = {
                    "table_name": secondary_table,
                    "select": "*",
                    "filters": [
                        {
                            "column": join_column_secondary,
                            "operator": "in",
                            "value": join_values
                        }
                    ]
                }
                
                secondary_result = execute_supabase_query(secondary_query)
                all_results[secondary_table] = secondary_result.get("data", [])
        
        # Generate a comprehensive response using all collected data
        response_prompt = f"""
        The user asked: "{user_question}"

        I have data from multiple tables:

        {json.dumps(all_results, indent=2)}

        IMPORTANT: ONLY use the data provided above. Do NOT invent or hallucinate any additional transactions, users, or products.

        Please provide a comprehensive answer that:
        1. Combines all relevant information from the tables
        2. Presents complete user details along with their transactions
        3. Is concise and well-organized
        4. Uses appropriate formatting (bold for important details)
        5. DOES NOT ask if the user wants more information
        6. Presents ONLY the information in the data above
        7. If there are more than 10 items, indicate the total count but only show the first 10

        Your response should be complete and not suggest further queries.
        """
        
        final_response = client.chat.completions.create(
            model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
            messages=[
                {"role": "system", "content": "You provide complete answers by joining information from multiple database tables."},
                {"role": "user", "content": response_prompt}
            ],
            temperature=0.2
        )
        
        return final_response.choices[0].message.content
            
    except Exception as e:
        return f"I ran into a problem with this multi-table query: {str(e)}. Could you try a simpler question?"