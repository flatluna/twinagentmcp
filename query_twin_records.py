#!/usr/bin/env python3
"""
Query Cosmos DB to verify document structure and show all Twin records
"""

import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
import json
from datetime import datetime

def query_twin_records():
    """Query and display all Twin records with their structure"""
    
    # Load environment variables
    load_dotenv()
    
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    
    if not endpoint or not key:
        print("❌ Missing COSMOS_ENDPOINT or COSMOS_KEY environment variables")
        return
    
    print("🔍 Querying Twin Records in Cosmos DB")
    print("=" * 60)
    
    try:
        # Initialize Cosmos DB client
        client = CosmosClient(endpoint, key)
        database = client.get_database_client("TwinHumanDB")
        container = database.get_container_client("TwinHumanContainer")
        
        # Query all items
        items = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        print(f"📊 Found {len(items)} total records")
        print("\n" + "=" * 60)
        
        for i, item in enumerate(items, 1):
            print(f"📄 Record {i}:")
            print(f"   ID: {item.get('id', 'N/A')}")
            print(f"   CountryID: {item.get('CountryID', 'N/A')}")
            
            # Check if it has the new Profile structure
            if 'Profile' in item:
                profile = item['Profile']
                print(f"   📋 Profile Structure (NEW FORMAT):")
                print(f"      First Name: {profile.get('firstName', 'N/A')}")
                print(f"      Last Name: {profile.get('lastName', 'N/A')}")
                print(f"      Email: {profile.get('email', 'N/A')}")
                print(f"      Phone: {profile.get('telephoneNumber', 'N/A')}")
            else:
                # Old flat structure
                print(f"   📋 Flat Structure (OLD FORMAT):")
                print(f"      First Name: {item.get('firstName', 'N/A')}")
                print(f"      Last Name: {item.get('lastName', 'N/A')}")
                print(f"      Email: {item.get('email', 'N/A')}")
                print(f"      Phone: {item.get('telephoneNumber', 'N/A')}")
            
            print(f"   Created: {item.get('createdAt', 'N/A')}")
            
            # Show if it's a test record
            if item.get('testType'):
                print(f"   🧪 Test Type: {item.get('testType')}")
            
            print("-" * 40)
        
        # Show the most recent record in full detail
        if items:
            latest = max(items, key=lambda x: x.get('createdAt', ''))
            print(f"\n🕐 Most Recent Record (Full JSON):")
            print(json.dumps({k: v for k, v in latest.items() if not k.startswith('_')}, indent=2))
            
    except Exception as e:
        print(f"❌ Error querying records: {e}")

if __name__ == "__main__":
    query_twin_records()
