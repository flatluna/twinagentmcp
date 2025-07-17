"""
Debug Twin Storage - Test with detailed Cosmos DB verification
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the current directory to path to import the server
sys.path.append(os.path.dirname(__file__))

from simple_mcp_server import SimpleMCPServer

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")

# Import Cosmos DB directly for verification
try:
    from azure.cosmos import CosmosClient, PartitionKey
    from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError
    COSMOS_AVAILABLE = True
    print("✅ Azure Cosmos DB SDK available")
except ImportError:
    COSMOS_AVAILABLE = False
    print("❌ Azure Cosmos DB SDK not available")


async def test_direct_cosmos_connection():
    """Test direct connection to Cosmos DB."""
    print("\n🔍 Testing DIRECT Cosmos DB Connection...")
    print("=" * 50)
    
    if not COSMOS_AVAILABLE:
        print("❌ Cannot test - Azure Cosmos DB SDK not available")
        return False
    
    try:
        # Get configuration
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        print(f"🌐 Cosmos Endpoint: {cosmos_endpoint}")
        print(f"🔑 Cosmos Key: {'*' * 20}...{cosmos_key[-10:] if cosmos_key else 'NOT SET'}")
        
        if not cosmos_endpoint or not cosmos_key:
            print("❌ Missing Cosmos DB configuration")
            return False
        
        # Connect directly
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        print("✅ Cosmos DB client created")
        
        # Get or create database
        database_name = "TwinHumanDB"
        try:
            database = client.create_database(id=database_name)
            print(f"✅ Created database: {database_name}")
        except CosmosResourceExistsError:
            database = client.get_database_client(database_name)
            print(f"✅ Connected to existing database: {database_name}")
        
        # Get or create container
        container_name = "TwinHumanContainer"
        try:
            container = database.create_container(
                id=container_name,
                partition_key=PartitionKey(path="/CountryID")
            )
            print(f"✅ Created container: {container_name}")
        except CosmosResourceExistsError:
            container = database.get_container_client(container_name)
            print(f"✅ Connected to existing container: {container_name}")
        
        # Test direct write
        test_doc = {
            "id": "direct-test@example.com",
            "firstName": "Direct",
            "lastName": "Test",
            "email": "direct-test@example.com",
            "telephoneNumber": "+1-555-DIRECT",
            "CountryID": "US",  # Use uppercase CountryID for partition key
            "createdAt": datetime.now().isoformat(),
            "lastModified": datetime.now().isoformat(),
            "testType": "direct_cosmos_test"
        }
        
        print("\n💾 Writing test document directly to Cosmos DB...")
        print(f"📄 Document: {json.dumps(test_doc, indent=2)}")
        
        response = container.upsert_item(body=test_doc)
        print("✅ Document written successfully!")
        print(f"📊 Response: {response}")
        
        # Try to read it back
        print("\n📖 Reading document back from Cosmos DB...")
        try:
            print(f"🔍 Attempting to read: ID='{test_doc['id']}', PartitionKey='{test_doc['countryId']}'")
            read_doc = container.read_item(
                item=test_doc["id"],
                partition_key=test_doc["countryId"]
            )
            print("✅ Document read successfully!")
            print(f"📄 Read document: {json.dumps(read_doc, indent=2)}")
            return True
        except Exception as e:
            print(f"❌ Failed to read document: {e}")
            
            # Try reading with different partition key approaches
            print("\n🔍 Trying alternative partition key approaches...")
            
            # Try with explicit US value
            try:
                read_doc2 = container.read_item(
                    item=test_doc["id"],
                    partition_key="US"
                )
                print("✅ Alternative read successful with 'US'!")
                return True
            except Exception as e2:
                print(f"❌ Alternative read with 'US' failed: {e2}")
            
            return False
            
    except Exception as e:
        print(f"❌ Direct Cosmos DB test failed: {e}")
        return False


async def test_mcp_server_with_debug():
    """Test MCP server with detailed debugging."""
    print("\n🔧 Testing MCP Server with Debug Info...")
    print("=" * 50)
    
    server = SimpleMCPServer()
    
    print(f"🔍 Server state:")
    print(f"   - cosmos_client: {server.cosmos_client is not None}")
    print(f"   - database: {server.database is not None}")
    print(f"   - container: {server.container is not None}")
    
    if not server.container:
        print("❌ MCP Server: Container not available")
        return False
    
    # Test Twin data with unique ID
    test_twin = {
        "firstName": "MCP",
        "lastName": "TestUser", 
        "email": f"mcp-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}@example.com",
        "telephoneNumber": "+1-555-MCP-TEST",
        "countryId": "US"
    }
    
    print(f"\n💾 Testing MCP server Twin storage...")
    print(f"📄 Twin data: {json.dumps(test_twin, indent=2)}")
    
    # Create request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "save_twin_info",
            "arguments": test_twin
        }
    }
    
    try:
        response = await server.handle_request(request)
        print(f"📋 MCP Response: {json.dumps(response, indent=2)}")
        
        if "error" in response:
            print(f"❌ MCP Error: {response['error']['message']}")
            return False
        else:
            print("✅ MCP Server reported success")
            
            # Try to verify the record exists in Cosmos DB
            if server.container:
                try:
                    print(f"\n🔍 Verifying record exists in Cosmos DB...")
                    print(f"🔍 Looking for: ID='{test_twin['email']}', PartitionKey='{test_twin['countryId']}'")
                    read_doc = server.container.read_item(
                        item=test_twin["email"],
                        partition_key=test_twin["countryId"]
                    )
                    print("✅ Record verified in Cosmos DB!")
                    print(f"📄 Stored document: {json.dumps(read_doc, indent=2)}")
                    return True
                except Exception as e:
                    print(f"❌ Failed to verify record in Cosmos DB: {e}")
                    
                    # Try alternative approaches
                    print("\n🔍 Trying alternative verification...")
                    try:
                        # Query for the document instead of direct read
                        query = f"SELECT * FROM c WHERE c.id = '{test_twin['email']}'"
                        items = list(server.container.query_items(query=query, enable_cross_partition_query=True))
                        if items:
                            print(f"✅ Found document via query!")
                            print(f"📄 Found document: {json.dumps(items[0], indent=2)}")
                            return True
                        else:
                            print("❌ Document not found via query either")
                    except Exception as e2:
                        print(f"❌ Query also failed: {e2}")
                    
                    return False
            
    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        return False


async def list_existing_records():
    """List existing records in Cosmos DB."""
    print("\n📋 Listing Existing Records in Cosmos DB...")
    print("=" * 50)
    
    if not COSMOS_AVAILABLE:
        print("❌ Cannot list - Azure Cosmos DB SDK not available")
        return
    
    try:
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        if not cosmos_endpoint or not cosmos_key:
            print("❌ Missing Cosmos DB configuration")
            return
        
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        
        try:
            database = client.get_database_client("TwinHumanDB")
            container = database.get_container_client("TwinHumanContainer")
            
            # Query all items
            query = "SELECT * FROM c"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            
            print(f"📊 Found {len(items)} records in the container:")
            
            if len(items) == 0:
                print("🔍 Container is empty - no records found")
            else:
                for i, item in enumerate(items, 1):
                    print(f"\n📄 Record {i}:")
                    print(f"   ID: {item.get('id', 'N/A')}")
                    print(f"   Name: {item.get('firstName', 'N/A')} {item.get('lastName', 'N/A')}")
                    print(f"   Email: {item.get('email', 'N/A')}")
                    print(f"   Country: {item.get('countryId', 'N/A')}")
                    print(f"   Created: {item.get('createdAt', 'N/A')}")
                    
        except Exception as e:
            print(f"❌ Database/Container not found: {e}")
            
    except Exception as e:
        print(f"❌ Failed to list records: {e}")


async def main():
    """Main debug function."""
    print("🐛 Twin Storage Debug Suite")
    print("=" * 50)
    print("")
    
    # Test 1: Direct Cosmos DB connection
    direct_success = await test_direct_cosmos_connection()
    
    # Test 2: List existing records
    await list_existing_records()
    
    # Test 3: MCP Server with debug
    mcp_success = await test_mcp_server_with_debug()
    
    # Test 4: List records again
    await list_existing_records()
    
    print("\n🏁 Debug Summary:")
    print(f"   Direct Cosmos DB: {'✅ Success' if direct_success else '❌ Failed'}")
    print(f"   MCP Server: {'✅ Success' if mcp_success else '❌ Failed'}")
    
    if direct_success and mcp_success:
        print("\n🎉 Both tests passed! Data should be in Cosmos DB.")
    elif direct_success:
        print("\n🤔 Direct Cosmos DB works but MCP Server has issues.")
    else:
        print("\n❌ Cosmos DB connection issues detected.")


if __name__ == "__main__":
    asyncio.run(main())
