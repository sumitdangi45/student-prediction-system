# Complete Data Flow - Profile → Prediction → Recommendations

## 📊 System Overview

This document explains the complete data flow from user profile creation through prediction to personalized recommendations.

```
User Profile Data → Prediction Model → Recommendations Engine
     ↓                    ↓                      ↓
  MongoDB            MongoDB              MongoDB
  (users)          (predictions)      (recommendations)
```

## 🔄 Complete Flow

### **Step 1: User Profile Data**

**Where:** Profile Page (`/profile`)

**What Gets Saved:**
- Name
- Email
- Phone
- College/University
- Branch/Stream
- CGPA
- Graduation Year
- Profile Photo (Base64)

**Endpoint:** `POST /api/auth/update-profile`

**MongoDB Collection:** `users`

```json
{
  "_id": ObjectId("..."),
  "email": "user@email.com",
  "name": "User Name",
  "phone": "9876543210",
  "college": "College Name",
  "branch": "CSE",
  "cgpa": "7.5",
  "graduationYear": "2026",
  "photo": "data:image/jpeg;base64,...",
  "created_at": "2026-05-19T12:00:00",
  "updated_at": "2026-05-19T12:20:00"
}
```

---

### **Step 2: Prediction Data**

**Where:** Predict Page (`/predict`)

**What Gets Saved:**
- User ID (from JWT token)
- All prediction features:
  - CGPA
  - 10th Marks
  - 12th Marks
  - Total Backlogs
  - Has Experience
  - Number of Companies
  - Has Internship
  - Has Skills
  - Has Projects
  - Has Certifications
  - Academic Trend
  - Is Female
- Prediction Result:
  - Probability (0-1)
  - Tier (Tier-1, Tier-2, Tier-3, Below Tier-3)
  - Recommendation

**Endpoint:** `POST /api/predict`

**MongoDB Collection:** `predictions`

```json
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("..."),
  "timestamp": "2026-05-19T12:15:00",
  "features": {
    "CGPA": 7.5,
    "10th_Marks": 90,
    "12th_Marks": 85,
    "Total_Backlogs": 0,
    "Has_Experience": 0,
    "Num_Companies": 0,
    "Has_Internship": 1,
    "Has_Skills": 1,
    "Has_Projects": 1,
    "Has_Certifications": 0,
    "Academic_Trend": 0.5,
    "Is_Female": 0
  },
  "prediction": 1,
  "probability": 0.6532,
  "tier": "Tier-2",
  "recommendation": "Good chances! Work on technical skills."
}
```

---

### **Step 3: Recommendations Generation**

**Where:** Recommendations Page (`/recommendations`)

**Input Data Used:**
1. **From User Profile:**
   - Name
   - College
   - Branch
   - Phone

2. **From Latest Prediction:**
   - Probability
   - 10th & 12th Marks
   - Backlogs
   - Experience
   - Internship
   - Projects
   - Skills
   - Certifications

3. **From Form:**
   - Tier
   - CGPA
   - Current Skills
   - Experience Level
   - Available Timeline

**Endpoint:** `POST /api/recommendations`

**MongoDB Collection:** `recommendations`

```json
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("..."),
  "timestamp": "2026-05-19T12:20:00",
  "tier": "Tier-2",
  "cgpa": "7.5",
  "skills": "JavaScript, React",
  "experience": "No",
  "timeline": "3 months",
  "content": "Detailed roadmap content...",
  "source": "gemini-api"
}
```

---

## 🔐 Authentication Flow

### **JWT Token Usage:**

1. **User Logs In:**
   - Email + OTP verification
   - JWT token created with 7-day expiry
   - Token stored in localStorage

2. **Token Sent With Requests:**
   ```
   Authorization: Bearer <jwt_token>
   ```

3. **Backend Extracts User ID:**
   ```python
   token = request.headers.get('Authorization', '').replace('Bearer ', '')
   payload = verify_jwt_token(token)
   user_id = payload.get('user_id')
   ```

4. **Data Linked to User:**
   - Predictions saved with `user_id`
   - Recommendations saved with `user_id`
   - User profile retrieved for context

---

## 📝 Detailed Recommendation Prompt

The recommendation engine uses a comprehensive prompt that includes:

### **1. User Profile Information**
```
- Name
- College
- Branch
- Phone
```

### **2. Prediction Data**
```
- Placement Probability
- 10th & 12th Marks
- Backlogs
- Experience Status
- Internship Status
- Projects Status
- Skills Status
- Certifications Status
```

### **3. Personalized Analysis**
The prompt asks for:
- Current Situation Analysis
- Key Areas to Improve
- Skill Development Plan
- Project Ideas
- Interview Preparation Strategy
- Weekly Action Plan
- Learning Resources
- Timeline & Milestones
- Personalized Tips

---

## 🔄 API Endpoints

### **1. Update Profile**
```
POST /api/auth/update-profile
Headers: Authorization: Bearer <token>
Body: {
  "name": "User Name",
  "phone": "9876543210",
  "college": "College Name",
  "branch": "CSE",
  "cgpa": "7.5",
  "graduationYear": "2026",
  "photo": "base64_image"
}
Response: {
  "status": "success",
  "message": "Profile updated successfully",
  "profile": { ...updated_data }
}
```

### **2. Get Prediction**
```
POST /api/predict
Headers: Authorization: Bearer <token>
Body: {
  "CGPA": 7.5,
  "10th_Marks": 90,
  "12th_Marks": 85,
  "Total_Backlogs": 0,
  "Has_Experience": 0,
  "Num_Companies": 0,
  "Has_Internship": 1,
  "Has_Skills": 1,
  "Has_Projects": 1,
  "Has_Certifications": 0,
  "Academic_Trend": 0.5,
  "Is_Female": 0
}
Response: {
  "status": "success",
  "prediction": 1,
  "probability": 0.6532,
  "percentage": "65.32%",
  "tier": "Tier-2",
  "recommendation": "Good chances! Work on technical skills.",
  "timestamp": "2026-05-19T12:15:00"
}
```

### **3. Get Recommendations**
```
POST /api/recommendations
Headers: Authorization: Bearer <token>
Body: {
  "tier": "Tier-2",
  "cgpa": "7.5",
  "skills": "JavaScript, React",
  "experience": "No",
  "timeline": "3 months"
}
Response: {
  "status": "success",
  "content": "Detailed roadmap...",
  "tier": "Tier-2",
  "cgpa": "7.5",
  "timestamp": "2026-05-19T12:20:00",
  "source": "gemini-api"
}
```

---

## 🧪 Testing Workflow

### **Complete User Journey:**

1. **Login**
   - Go to `/auth`
   - Enter email and verify OTP
   - Get JWT token

2. **Update Profile**
   - Go to `/profile`
   - Fill in all details
   - Upload photo
   - Click "Save Changes"
   - Data saved to MongoDB

3. **Get Prediction**
   - Go to `/predict`
   - Fill in academic details
   - Click "Get My Prediction"
   - Prediction saved with user_id

4. **Get Recommendations**
   - Click "View Your Roadmap"
   - Recommendations generated using:
     - User profile data
     - Latest prediction data
     - Form inputs
   - Detailed roadmap displayed

---

## 📊 MongoDB Collections

### **users**
```
- _id (ObjectId)
- email (String)
- name (String)
- phone (String)
- college (String)
- branch (String)
- cgpa (String)
- graduationYear (String)
- photo (String - Base64)
- created_at (String - ISO)
- updated_at (String - ISO)
- last_login (String - ISO)
```

### **predictions**
```
- _id (ObjectId)
- user_id (ObjectId)
- timestamp (String - ISO)
- features (Object)
- prediction (Number)
- probability (Number)
- tier (String)
- recommendation (String)
```

### **recommendations**
```
- _id (ObjectId)
- user_id (ObjectId)
- timestamp (String - ISO)
- tier (String)
- cgpa (String)
- skills (String)
- experience (String)
- timeline (String)
- content (String)
- source (String - "gemini-api" or "ollama")
```

---

## 🎯 Key Features

✅ **User Profile Persistence**
- All profile data saved to MongoDB
- Photo stored as Base64
- Linked to user via user_id

✅ **Prediction Tracking**
- All predictions saved with user_id
- Features stored for analysis
- Probability and tier recorded

✅ **Personalized Recommendations**
- Uses user profile data
- Uses latest prediction data
- Generates detailed roadmap
- Saved for future reference

✅ **Real-time Updates**
- Profile updates immediately
- Predictions saved instantly
- Recommendations generated on-demand

✅ **Data Privacy**
- All data linked to authenticated user
- JWT token required for sensitive operations
- User_id ensures data isolation

---

## 🔧 Troubleshooting

### **Issue: Prediction not saving**
**Solution:**
1. Verify user is logged in (token exists)
2. Check MongoDB connection
3. Verify user_id is being extracted correctly
4. Check Flask logs for errors

### **Issue: Recommendations not using user data**
**Solution:**
1. Verify profile data is saved
2. Verify prediction data is saved
3. Check that user_id is being passed
4. Verify MongoDB queries are working

### **Issue: Photo not showing in recommendations**
**Solution:**
1. Photo is not used in recommendations
2. Only profile text data is used
3. Photo is for display purposes only

---

## 📈 Data Analytics

### **Queries You Can Run:**

**Get all predictions for a user:**
```python
db.predictions.find({"user_id": ObjectId("...")})
```

**Get latest prediction:**
```python
db.predictions.find_one(
  {"user_id": ObjectId("...")},
  sort=[("timestamp", -1)]
)
```

**Get all recommendations:**
```python
db.recommendations.find({"user_id": ObjectId("...")})
```

**Get average probability:**
```python
db.predictions.aggregate([
  {"$match": {"user_id": ObjectId("...")}},
  {"$group": {"_id": None, "avg_prob": {"$avg": "$probability"}}}
])
```

---

**Last Updated:** May 19, 2026
**Status:** ✅ Complete and Tested
**Version:** 2.0.0
