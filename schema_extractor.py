# comprehensive_schema_extractor.py
import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def extract_complete_schema(output_file="schema_dump.json"):
    """Extract complete schema with sample data and save to JSON"""
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API"))
    available_tables = os.getenv("DB_TABLES", "products,users,transactions").split(",")
    
    schema_dump = {
        "tables": {},
        "relationships": []
    }
    
    # Extract table schemas and data
    for table in available_tables:
        print(f"Processing table: {table}")
        table_info = {"columns": [], "sample_data": [], "row_count": 0}
        
        # Get columns
        try:
            cols = supabase.rpc('describe_table', {'table_name': table}).execute()
            if cols.data:
                table_info["columns"] = cols.data
        except Exception as e:
            print(f"  Warning: Could not get columns for {table}: {e}")
        
        # Get sample data and count
        try:
            # Get count
            count_result = supabase.table(table).select("*", count="exact").execute()
            table_info["row_count"] = count_result.count if hasattr(count_result, 'count') else 0
            
            # Get sample rows
            sample = supabase.table(table).select("*").limit(5).execute()
            if sample.data:
                table_info["sample_data"] = sample.data
        except Exception as e:
            print(f"  Warning: Could not get data for {table}: {e}")
        
        schema_dump["tables"][table] = table_info
    
    # Try to get relationships (if you have a relationships table)
    try:
        rels = supabase.table("column_descriptions").select("*").execute()
        if rels.data:
            schema_dump["column_descriptions"] = rels.data
    except:
        pass
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(schema_dump, f, indent=2, default=str)
    
    print(f"\nSchema extracted successfully to {output_file}")
    return schema_dump

if __name__ == "__main__":
    schema = extract_complete_schema()
    
    # Also print to terminal in readable format
    print("\n" + "="*60)
    print("TERMINAL SUMMARY")
    print("="*60)
    
    for table_name, table_info in schema["tables"].items():
        print(f"\n📊 TABLE: {table_name} ({table_info['row_count']} rows)")
        print("-" * 40)
        
        if table_info["columns"]:
            print("Columns:")
            for col in table_info["columns"]:
                print(f"  • {col['column_name']} ({col['data_type']})")
        
        if table_info["sample_data"]:
            print(f"\nSample Data (first {len(table_info['sample_data'])} rows):")
            for row in table_info["sample_data"]:
                print(f"  {json.dumps(row, indent=4, default=str)}")