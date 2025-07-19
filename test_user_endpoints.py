#!/usr/bin/env python
"""
Test script to verify that user endpoints include country and region information.
"""
import asyncio
import json
from uuid import UUID

import httpx
from tortoise import Tortoise

from app.config import settings


async def test_user_endpoints():
    """Test that user endpoints include country and region information."""
    print("Testing user endpoints for country and region information...")
    
    # Initialize database connection
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.infra.postgres.models"]}
    )
    
    # Create a client
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Test get all users endpoint
        print("\n1. Testing GET /api/v1/users/ endpoint")
        response = await client.get("/api/v1/users/")
        if response.status_code == 200:
            users = response.json()
            if users:
                user = users[0]
                print(f"User: {user['first_name']} {user['last_name']}")
                if user.get('city'):
                    print(f"City: {user['city']['name']}")
                    if user['city'].get('region'):
                        print(f"Region: {user['city']['region']['name']}")
                        if user['city']['region'].get('country'):
                            print(f"Country: {user['city']['region']['country']['name']} ({user['city']['region']['country']['code']})")
                            print("✅ Country and region information is included in the response!")
                        else:
                            print("❌ Country information is missing!")
                    else:
                        print("❌ Region information is missing!")
                else:
                    print("❌ City information is missing or user has no city assigned!")
            else:
                print("No users found in the database.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        # Test get user by ID endpoint (if we have users)
        if response.status_code == 200 and users:
            user_id = users[0]['user_id']
            print(f"\n2. Testing GET /api/v1/users/{user_id} endpoint")
            response = await client.get(f"/api/v1/users/{user_id}")
            if response.status_code == 200:
                user = response.json()
                print(f"User: {user['first_name']} {user['last_name']}")
                if user.get('city'):
                    print(f"City: {user['city']['name']}")
                    if user['city'].get('region'):
                        print(f"Region: {user['city']['region']['name']}")
                        if user['city']['region'].get('country'):
                            print(f"Country: {user['city']['region']['country']['name']} ({user['city']['region']['country']['code']})")
                            print("✅ Country and region information is included in the response!")
                        else:
                            print("❌ Country information is missing!")
                    else:
                        print("❌ Region information is missing!")
                else:
                    print("❌ City information is missing or user has no city assigned!")
            else:
                print(f"Error: {response.status_code} - {response.text}")
    
    # Close database connection
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_user_endpoints())
