# test_db_connection.py
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Test with the same credentials as your db_tool
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API"))

print("Testing direct database access...")
try:
    # Test products table
    result = supabase.table("products").select("*").limit(1).execute()
    print(f"Products test - Count: {len(result.data)}")
    if result.data:
        print(f"Sample: {result.data[0]}")
    
    # Test users table  
    result = supabase.table("users").select("*").limit(1).execute()
    print(f"Users test - Count: {len(result.data)}")
    
    # Test transactions table
    result = supabase.table("transactions").select("*").limit(1).execute()
    print(f"Transactions test - Count: {len(result.data)}")
    
except Exception as e:
    print(f"ERROR: {e}")