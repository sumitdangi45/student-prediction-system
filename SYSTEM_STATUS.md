# 🎯 PlaceReady System Status & Architecture

## ✅ Current System Status (May 18, 2026)

### Running Services
- ✅ **Flask API Server** - Running on `http://localhost:5000`
- ✅ **Ollama Server** - Running on `http://localhost:11434`
- ✅ **Mistral Model** - Available (4.4 GB)

### API Keys
- ✅ **Gemini API Key** - Configured in `app.py` (line 161)
- ⚠️ **Gemini Quota** - Currently EXCEEDED (429 Error)
- ✅ **Fallback System** - Ollama is active and working

---

## 🏗️ System Architecture

### Flow Diagram
```
User fills form on /predict page
        ↓
Sends data to /api/predict endpoint
        ↓
Model predicts placement probability & tier
        ↓
User clicks "View Your Roadmap"
        ↓
Redirects to /recommendations page with prediction data
        ↓
Sends request to /api/recommendations endpoint
        ↓
┌─────────────────────────────────────┐
│ Try Gemini API First (Primary)      │
│ - Uses google.genai library         │
│ - API Key: AIzaSyD4fbWDpr4lYa1...   │
└─────────────────────────────────────┘
        ↓ (if fails or quota exceeded)
┌─────────────────────────────────────┐
│ Fallback to Ollama (Secondary)      │
│ - Uses mistral:latest model         │
│ - Runs locally on port 11434        │
└─────────────────────────────────────┘
        ↓
Returns personalized recommendations
        ↓
Displays on /recommendations page
```

---

## 📡 API Endpoints

### 1. **POST /api/predict**
Predicts placement probability for a student

**Request:**
```json
{
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
```

**Response:**
```json
{
  "status": "success",
  "prediction": 1,
  "probability": 0.65,
  "percentage": "65.00%",
  "tier": "Tier-2",
  "recommendation": "Good chances! Work on technical skills.",
  "features_used": [...],
  "timestamp": "2026-05-18T10:30:00"
}
```

### 2. **POST /api/recommendations**
Generates personalized placement roadmap

**Request:**
```json
{
  "tier": "Tier-2",
  "cgpa": "7.5",
  "skills": "JavaScript, React",
  "experience": "No",
  "timeline": "3 months"
}
```

**Response (Gemini):**
```json
{
  "status": "success",
  "content": "🎯 PERSONALIZED PLACEMENT PREPARATION ROADMAP...",
  "tier": "Tier-2",
  "cgpa": "7.5",
  "timestamp": "2026-05-18T10:30:00",
  "source": "gemini-api"
}
```

**Response (Ollama Fallback):**
```json
{
  "status": "success",
  "content": "🎯 PERSONALIZED PLACEMENT PREPARATION ROADMAP...",
  "tier": "Tier-2",
  "cgpa": "7.5",
  "timestamp": "2026-05-18T10:30:00",
  "source": "ollama"
}
```

---

## 🔄 Recommendation Generation Logic

### Gemini API (Primary)
**File:** `app.py` (lines 161-180)

```python
# Try Gemini API first
try:
    from google import genai
    
    api_key = "AIzaSyD4fbWDpr4lYa1dYLbFwfnu7XbrZaTyaPo"
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt
    )
    
    return jsonify({
        'status': 'success',
        'content': response.text,
        'source': 'gemini-api'
    })
```

### Ollama Fallback (Secondary)
**File:** `app.py` (lines 182-210)

```python
# Fallback to Ollama
try:
    import requests
    
    ollama_response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'mistral',
            'prompt': prompt,
            'stream': False
        },
        timeout=60
    )
    
    if ollama_response.status_code == 200:
        ollama_data = ollama_response.json()
        
        return jsonify({
            'status': 'success',
            'content': ollama_data.get('response', ''),
            'source': 'ollama'
        })
```

---

## 🎨 Frontend Integration

### Predict Page (`/predict`)
**File:** `src/routes/predict.tsx`

1. User fills academic, experience, and skills details
2. Clicks "Get My Prediction"
3. Sends data to `/api/predict`
4. Receives prediction with tier and probability
5. Shows "View Your Roadmap" button
6. Button redirects to `/recommendations` with query parameters:
   - `tier`: Placement tier (Tier-1, Tier-2, etc.)
   - `cgpa`: Current CGPA
   - `probability`: Placement probability percentage

### Recommendations Page (`/recommendations`)
**File:** `src/routes/recommendations.tsx`

1. Receives prediction data from query parameters
2. Auto-fills form with prediction data
3. Auto-generates recommendations
4. Displays personalized roadmap from Gemini or Ollama
5. Shows source of recommendations (gemini-api or ollama)

---

## 📊 Current Status

### ✅ Working Features
- ✅ Prediction model (Random Forest V2)
- ✅ Gemini API integration (primary)
- ✅ Ollama fallback system (secondary)
- ✅ Personalized recommendations
- ✅ Frontend integration
- ✅ Auto-fill from prediction page
- ✅ Source tracking (shows which API generated recommendations)

### ⚠️ Current Issues
- ⚠️ Gemini API quota exceeded (429 error)
  - **Solution:** Ollama is automatically used as fallback
  - **Timeline:** Quota resets daily (check Google Cloud Console)

### 🔧 Configuration Files
- **API Key:** `app.py` line 161
- **Ollama Endpoint:** `app.py` line 195
- **Model:** `mistral:latest` (4.4 GB)

---

## 🚀 How to Use

### 1. Fill Prediction Form
Go to `/predict` page and fill:
- Academic details (CGPA, 10th, 12th marks)
- Experience details (internship, companies, etc.)
- Skills details (projects, certifications, etc.)

### 2. Get Prediction
Click "Get My Prediction" button

### 3. View Roadmap
Click "View Your Roadmap" button

### 4. See Recommendations
- If Gemini API quota available → Uses Gemini (faster, better quality)
- If Gemini quota exceeded → Uses Ollama (local, always available)
- Recommendations are personalized based on:
  - Placement tier
  - Current CGPA
  - Available timeline
  - Current skills
  - Professional experience

---

## 📈 Recommendation Content

Each roadmap includes:
1. **Key Areas to Improve** - Tier-specific focus areas
2. **Skill Development Plan** - Technologies to learn
3. **Project Ideas** - 2-3 concrete project suggestions
4. **Interview Preparation Strategy** - Tips and resources
5. **Weekly Action Plan** - Detailed week-by-week breakdown
6. **Learning Resources** - Courses, books, websites
7. **Timeline & Milestones** - Realistic checkpoints
8. **Personalized Tips** - Based on CGPA and experience

---

## 🔐 Security Notes

### API Keys
- ✅ Gemini API key is in `app.py` (hardcoded)
- ⚠️ Consider moving to environment variables for production
- ✅ Ollama runs locally (no external API calls)

### Data Privacy
- ✅ No student data is stored
- ✅ Recommendations are generated on-the-fly
- ✅ No external logging or tracking

---

## 📝 Summary

**The system is working correctly!**

- ✅ Gemini API is tried first (currently quota exceeded)
- ✅ Ollama automatically takes over as fallback
- ✅ Each student gets unique, personalized recommendations
- ✅ Recommendations are based on prediction data
- ✅ Frontend seamlessly integrates both pages

**No action needed!** The system is functioning as designed.

---

**Last Updated:** May 18, 2026, 10:30 AM
**Status:** ✅ All Systems Operational
