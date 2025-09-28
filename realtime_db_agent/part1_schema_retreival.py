from supabase import create_client, Client
import os
from dotenv import load_dotenv  
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API")
supabase: Client = create_client(url, key)

def get_table_schema(table_name: str, sample_rows: int = 10):
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

    # Get example rows
    examples = supabase.table(table_name).select("*").limit(sample_rows).execute()
    example_rows = examples.data if hasattr(examples, "data") else []

    schema += "\nExample rows:\n"
    for row in example_rows:
        row_repr = ", ".join(f"{k}: {v}" for k, v in row.items())
        schema += f"- {row_repr}\n"

    return schema

schema_text = get_table_schema("products")