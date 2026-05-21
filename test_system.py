#!/usr/bin/env python3
"""
Test script to verify PlaceReady system is working
"""

import requests
import json
import time

print("\n" + "="*70)
print("🧪 PLACEREADY SYSTEM TEST")
print("="*70 + "\n")

# Test 1: Prediction API
print("1️⃣  Testing Prediction API...")
print("-" * 70)

pred_data = {
    "CGPA": 7.5,
    "12th_Marks": 85,
    "10th_Marks": 90,
    "Total_Backlogs": 0,
    "Has_Experience": 0,
    "Num_Companies": 0,
    "Has_Internship": 0,
    "Has_Skills": 1,
    "Has_Projects": 1,
    "Has_Certifications": 0,
    "Academic_Trend": 0,
    "Is_Female": 0
}

try:
    response = requests.post(
        "http://localhost:5000/api/predict",
        json=pred_data,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Prediction API Working!")
        print(f"   Status: {result['status']}")
        print(f"   Tier: {result['tier']}")
        print(f"   Probability: {result['percentage']}")
        print(f"   Recommendation: {result['recommendation'][:60]}...")
    else:
        print(f"❌ Prediction API Error: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Prediction API Error: {str(e)[:100]}")

print("\n")

# Test 2: Recommendations API
print("2️⃣  Testing Recommendations API...")
print("-" * 70)

rec_data = {
    "tier": "Tier-2",
    "cgpa": "7.5",
    "skills": "JavaScript, React",
    "experience": "No",
    "timeline": "3 months"
}

try:
    print("Sending request (this may take 60-120 seconds)...")
    start_time = time.time()
    
    response = requests.post(
        "http://localhost:5000/api/recommendations",
        json=rec_data,
        timeout=300
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Recommendations API Working!")
        print(f"   Status: {result['status']}")
        print(f"   Source: {result['source']}")
        print(f"   Tier: {result['tier']}")
        print(f"   CGPA: {result['cgpa']}")
        print(f"   Response Time: {elapsed:.1f} seconds")
        print(f"\n   Content (first 300 chars):")
        print(f"   {result['content'][:300]}...")
    else:
        print(f"❌ Recommendations API Error: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Recommendations API Error: {str(e)[:100]}")

print("\n" + "="*70)
print("✅ TEST COMPLETE")
print("="*70 + "\n")
