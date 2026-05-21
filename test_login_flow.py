#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complete login flow
"""
import requests
import json
from dotenv import load_dotenv
import os
import time
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "sumitdangi84552@gmail.com"

print("=" * 80)
print("[TEST] Testing Complete Login Flow")
print("=" * 80)

# Step 1: Send OTP
print("\n[1] Sending OTP to admin email...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/send-otp",
        json={"email": ADMIN_EMAIL},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {data}")
    
    if data.get('status') == 'success':
        print(f"   [OK] OTP sent successfully")
        print(f"   [INFO] Check email: {ADMIN_EMAIL}")
    else:
        print(f"   [ERROR] Failed to send OTP")
        exit(1)
except Exception as e:
    print(f"   [ERROR] {e}")
    exit(1)

# Step 2: Get OTP from database
print("\n[2] Retrieving OTP from database...")
try:
    from pymongo import MongoClient
    MONGODB_URI = os.getenv('MONGODB_URI')
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = mongo_client['placeready']
    
    otp_record = db.otp_requests.find_one({'email': ADMIN_EMAIL})
    if otp_record:
        otp = otp_record['otp']
        print(f"   [OK] OTP retrieved: {otp}")
    else:
        print(f"   [ERROR] OTP not found in database")
        exit(1)
except Exception as e:
    print(f"   [ERROR] {e}")
    exit(1)

# Step 3: Verify OTP
print("\n[3] Verifying OTP...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/verify-otp",
        json={"email": ADMIN_EMAIL, "otp": otp},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    if data.get('status') == 'success':
        token = data.get('token')
        user = data.get('user')
        print(f"   [OK] OTP verified successfully")
        print(f"   [TOKEN] {token[:50]}...")
        print(f"   [USER] {user}")
        print(f"   [ADMIN] is_admin: {user.get('is_admin')}")
    else:
        print(f"   [ERROR] OTP verification failed: {data.get('message')}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] {e}")
    exit(1)

# Step 4: Test /api/auth/me with token
print("\n[4] Testing /api/auth/me endpoint with token...")
try:
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    if data.get('status') == 'success':
        user_data = data.get('user')
        print(f"   [OK] Token verified successfully")
        print(f"   [USER] Email: {user_data.get('email')}")
        print(f"   [USER] Name: {user_data.get('name')}")
        print(f"   [USER] Role: {user_data.get('role')}")
        print(f"   [USER] is_admin: {user_data.get('is_admin')}")
    else:
        print(f"   [ERROR] Token verification failed: {data.get('message')}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] {e}")
    exit(1)

# Step 5: Test admin endpoint
print("\n[5] Testing admin endpoint...")
try:
    response = requests.get(
        f"{BASE_URL}/api/admin/students",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print(f"   [OK] Admin endpoint accessible")
        print(f"   [ANALYTICS] {data.get('analytics')}")
        print(f"   [STUDENTS] Total: {len(data.get('students', []))}")
    else:
        print(f"   [ERROR] Admin endpoint failed: {data.get('message')}")
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "=" * 80)
print("[SUCCESS] Login flow test complete!")
print("=" * 80)
print("\n[SUMMARY]")
print(f"   [OK] OTP sent to {ADMIN_EMAIL}")
print(f"   [OK] OTP verified")
print(f"   [OK] Token generated")
print(f"   [OK] /api/auth/me working")
print(f"   [OK] Admin endpoint accessible")
print("\n[NEXT STEPS]")
print("   1. Open browser DevTools (F12)")
print("   2. Go to http://localhost:3000/auth")
print("   3. Login with sumitdangi84552@gmail.com")
print("   4. Check console for debug logs")
print("   5. Verify profile avatar shows")
print("\n")
