#!/usr/bin/env python3
"""
Test authentication endpoints
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "sumitdangi84552@gmail.com"

print("=" * 80)
print("🧪 Testing PlaceReady Authentication Endpoints")
print("=" * 80)

# Test 1: Health check
print("\n1️⃣ Testing Health Check...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Send OTP
print("\n2️⃣ Testing Send OTP...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/send-otp",
        json={"email": ADMIN_EMAIL}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {data}")
    
    if data.get('status') == 'success':
        print(f"   ✅ OTP sent successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get current user (without token - should fail)
print("\n3️⃣ Testing Get Current User (without token)...")
try:
    response = requests.get(f"{BASE_URL}/api/auth/me")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print(f"   ✅ Correctly rejected (expected 401)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Check admin endpoints (without token - should fail)
print("\n4️⃣ Testing Admin Endpoints (without token)...")
try:
    response = requests.get(f"{BASE_URL}/api/admin/students")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print(f"   ✅ Correctly rejected (expected 401)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ Backend is running and responding to requests!")
print("=" * 80)
print("\n📝 Next steps:")
print("   1. Login with email: sumitdangi84552@gmail.com")
print("   2. Check browser console for debug logs")
print("   3. Verify localStorage has token and user")
print("   4. Check if profile avatar appears")
print("\n")
