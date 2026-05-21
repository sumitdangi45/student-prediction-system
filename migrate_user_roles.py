#!/usr/bin/env python3
"""
Migration script to add role and is_admin fields to existing users
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://<db_username>:<db_password>@cluster0.tiweseu.mongodb.net/?appName=Cluster0')
ADMIN_EMAIL = os.getenv('GMAIL_EMAIL', 'sumitdangi84552@gmail.com')

try:
    # Connect to MongoDB
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    db = mongo_client['placeready']
    
    print("✅ MongoDB Connected Successfully!")
    
    # Get all users
    users = list(db.users.find({}))
    print(f"\n📊 Found {len(users)} users in database")
    
    # Update users without role/is_admin fields
    updated_count = 0
    admin_count = 0
    
    for user in users:
        email = user.get('email', '')
        has_role = 'role' in user
        has_is_admin = 'is_admin' in user
        
        if not has_role or not has_is_admin:
            # Determine if this user should be admin
            is_admin = email.lower() == ADMIN_EMAIL.lower()
            role = 'admin' if is_admin else 'user'
            
            # Update user
            db.users.update_one(
                {'_id': user['_id']},
                {'$set': {
                    'role': role,
                    'is_admin': is_admin,
                    'updated_at': datetime.now().isoformat()
                }}
            )
            
            updated_count += 1
            if is_admin:
                admin_count += 1
                print(f"  ✅ Updated {email} → role: {role}, is_admin: {is_admin} (ADMIN)")
            else:
                print(f"  ✅ Updated {email} → role: {role}, is_admin: {is_admin}")
    
    print(f"\n📈 Migration Summary:")
    print(f"  • Total users updated: {updated_count}")
    print(f"  • Admin users: {admin_count}")
    print(f"  • Regular users: {updated_count - admin_count}")
    
    # Verify the update
    users_with_role = db.users.count_documents({'role': {'$exists': True}})
    users_with_admin = db.users.count_documents({'is_admin': {'$exists': True}})
    admins = db.users.count_documents({'is_admin': True})
    
    print(f"\n✅ Verification:")
    print(f"  • Users with role field: {users_with_role}/{len(users)}")
    print(f"  • Users with is_admin field: {users_with_admin}/{len(users)}")
    print(f"  • Total admins: {admins}")
    
    print("\n✅ Migration completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if mongo_client:
        mongo_client.close()
