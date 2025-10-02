from supabase import create_client, Client
import os
from dotenv import load_dotenv  
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API")
supabase: Client = create_client(url, key)

# Load table configuration from environment
AVAILABLE_TABLES = os.getenv("DB_TABLES", "products,users,transactions").split(",")

def get_table_schema(table_name: str, sample_rows: int = 5):
    """
    Get schema information for a specific table.
    Returns formatted schema text with column details and example rows.
    """
    # Get columns
    columns_result = supabase.rpc('describe_table', {'table_name': table_name}).execute()
    columns = columns_result.data if hasattr(columns_result, "data") else []

    # Get descriptions
    desc_result = supabase.table("column_descriptions").select("*").eq("table_name", table_name).execute()
    descriptions = {d["column_name"]: d["description"] for d in desc_result.data}

    # Build schema text
    schema = f"Table: {table_name}\nColumns:\n"
    column_names = []
    for col in columns:
        name = col["column_name"]
        dtype = col["data_type"]
        column_names.append(name)
        desc = descriptions.get(name, "No description available")
        schema += f"- {name} ({dtype}): {desc}\n"

    # Get example rows (reduced from 10 to 5 to prevent token overflow)
    examples = supabase.table(table_name).select("*").limit(sample_rows).execute()
    example_rows = examples.data if hasattr(examples, "data") else []

    schema += "\nExample rows:\n"
    for row in example_rows:
        row_repr = ", ".join(f"{k}: {v}" for k, v in row.items())
        schema += f"- {row_repr}\n"

    return schema

def get_all_schemas(sample_rows: int = 3):
    """
    Get schema information for all available tables.
    Returns combined schema text for all tables.
    """
    all_schemas = ""
    for table in AVAILABLE_TABLES:
        # Use even fewer sample rows when getting all schemas
        schema = get_table_schema(table, sample_rows)
        all_schemas += f"\n\n{schema}"
    
    return all_schemas

def get_table_relationships():
    """
    Identify foreign key relationships between tables.
    """
    relationships = []
    
    # Define known relationships based on column names
    # Format: (table1, column1, table2, column2)
    potential_relationships = [
        ("transactions", "user_id", "users", "user_id"),
        ("transactions", "product_id", "products", "product_id"),
    ]
    
    # Validate relationships by checking if tables and columns exist
    for rel in potential_relationships:
        table1, col1, table2, col2 = rel
        
        # Skip if tables aren't in our available tables list
        if table1 not in AVAILABLE_TABLES or table2 not in AVAILABLE_TABLES:
            continue
            
        # Get columns for both tables to verify
        cols1 = supabase.rpc('describe_table', {'table_name': table1}).execute()
        cols2 = supabase.rpc('describe_table', {'table_name': table2}).execute()
        
        col1_names = [c["column_name"] for c in cols1.data]
        col2_names = [c["column_name"] for c in cols2.data]
        
        # Check if the columns exist
        if col1 in col1_names and col2 in col2_names:
            relationships.append({
                "from_table": table1,
                "from_column": col1,
                "to_table": table2,
                "to_column": col2
            })
    
    return relationships
