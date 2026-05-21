#!/usr/bin/env python3
"""
Setup admin user in MongoDB
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://<db_username>:<db_password>@cluster0.tiweseu.mongodb.net/?appName=Cluster0')

try:
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    db = mongo_client['placeready']
    
    print("✅ MongoDB Connected!")
    
    # Set admin for sumitdangi84552@gmail.com
    admin_email = 'sumitdangi84552@gmail.com'
    
    result = db.users.update_one(
        {'email': admin_email},
        {'$set': {'is_admin': True, 'role': 'admin'}}
    )
    
    if result.matched_count > 0:
        print(f"✅ Admin role set for {admin_email}")
        print(f"   Modified: {result.modified_count} document(s)")
    else:
        print(f"⚠️  User {admin_email} not found in database")
        print("   Please login first to create the user account")
    
    # Show all admins
    admins = list(db.users.find({'is_admin': True}))
    print(f"\n📋 Total admins in database: {len(admins)}")
    for admin in admins:
        print(f"   - {admin.get('email')} (Role: {admin.get('role', 'N/A')})")
    
except Exception as e:
    print(f"❌ Error: {e}")
