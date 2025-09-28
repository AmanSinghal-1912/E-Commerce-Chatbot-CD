import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import os   
load_dotenv()

# Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API")

supabase: Client = create_client(url, key)

# Load CSV
df = pd.read_csv("realtime_db_agent/dataset/products.csv")

# Rename columns to match DB table
df.rename(columns={
    "Product ID": "product_id",
    "Product Name": "product_name",
    "Product Category": "product_category",
    "Product Description": "product_description",
    "Price": "price",
    "Stock Quantity": "stock_quantity",
    "Warranty Period": "warranty_period",
    "Product Dimensions": "product_dimensions",
    "Manufacturing Date": "manufacturing_date",
    "Expiration Date": "expiration_date",
    "SKU": "sku",
    "Product Tags": "product_tags",
    "Color/Size Variations": "color_size_variations",
    "Product Ratings": "product_ratings"
}, inplace=True)

# Insert into Supabase
for row in df.to_dict(orient="records"):
    supabase.table("products").insert(row).execute()

print("✅ Products inserted successfully!")
