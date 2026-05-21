#!/usr/bin/env python3
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv('MONGODB_URI')

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client['placeready']
    
    # Check users collection
    users_count = db.users.count_documents({})
    print(f'✅ Total Users in MongoDB: {users_count}')
    
    if users_count > 0:
        users = list(db.users.find({}, {'_id': 0}).sort('created_at', -1).limit(5))
        print(f'\nRecent Users:')
        for i, user in enumerate(users, 1):
            print(f'{i}. Email: {user.get("email")}')
            print(f'   Created: {user.get("created_at")}')
            print(f'   Last Login: {user.get("last_login")}')
            print()
    
    # Check predictions collection
    pred_count = db.predictions.count_documents({})
    print(f'✅ Total Predictions: {pred_count}')
    
    # Check recommendations collection
    rec_count = db.recommendations.count_documents({})
    print(f'✅ Total Recommendations: {rec_count}')
    
except Exception as e:
    print(f'❌ Error: {str(e)[:200]}')
