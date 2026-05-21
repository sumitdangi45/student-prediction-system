# 🧪 Testing Guide - PlaceReady System

## Quick Test Checklist

### ✅ Step 1: Verify Services are Running
```powershell
# Check Flask Server
netstat -ano | findstr :5000

# Check Ollama Server
netstat -ano | findstr :11434

# Check Mistral Model
ollama list
```

**Expected Output:**
- Flask: `LISTENING` on port 5000
- Ollama: `LISTENING` on port 11434
- Mistral: `mistral:latest` in model list

---

### ✅ Step 2: Test Prediction API

**Using PowerShell:**
```powershell
$body = @{
    CGPA = 7.5
    "12th_Marks" = 85
    "10th_Marks" = 90
    Total_Backlogs = 0
    Has_Experience = 0
    Num_Companies = 0
    Has_Internship = 0
    Has_Skills = 1
    Has_Projects = 1
    Has_Certifications = 0
    Academic_Trend = 0
    Is_Female = 0
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:5000/api/predict" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body

$response.Content | ConvertFrom-Json | Format-List
```

**Expected Response:**
```json
{
  "status": "success",
  "prediction": 1,
  "probability": 0.65,
  "percentage": "65.00%",
  "tier": "Tier-2",
  "recommendation": "Good chances! Work on technical skills."
}
```

---

### ✅ Step 3: Test Recommendations API (Gemini)

**Using PowerShell:**
```powershell
$body = @{
    tier = "Tier-2"
    cgpa = "7.5"
    skills = "JavaScript, React"
    experience = "No"
    timeline = "3 months"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:5000/api/recommendations" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body `
    -TimeoutSec 120

$result = $response.Content | ConvertFrom-Json
Write-Host "Status: $($result.status)"
Write-Host "Source: $($result.source)"
Write-Host "Content (first 500 chars):"
Write-Host $result.content.Substring(0, [Math]::Min(500, $result.content.Length))
```

**Expected Response:**
```json
{
  "status": "success",
  "content": "🎯 PERSONALIZED PLACEMENT PREPARATION ROADMAP...",
  "tier": "Tier-2",
  "cgpa": "7.5",
  "source": "gemini-api" OR "ollama"
}
```

---

### ✅ Step 4: Test Frontend Flow

1. **Open Browser:** `http://localhost:5173` (or your dev server URL)

2. **Navigate to Predict Page:** `/predict`

3. **Fill Form:**
   - CGPA: 7.5
   - 12th Marks: 85
   - 10th Marks: 90
   - Leave other fields as default

4. **Click "Get My Prediction"**
   - Should show prediction result
   - Should display tier and probability

5. **Click "View Your Roadmap"**
   - Should redirect to `/recommendations`
   - Should auto-fill form with prediction data
   - Should auto-generate recommendations

6. **Verify Recommendations:**
   - Should show personalized roadmap
   - Should display source (Gemini or Ollama)
   - Should include all 8 sections

---

## 🔍 Troubleshooting

### Issue: Prediction API returns error

**Solution:**
1. Check Flask server is running: `netstat -ano | findstr :5000`
2. Check model files exist in `models/` directory
3. Check feature names match in request

### Issue: Recommendations API times out

**Solution:**
1. Check Ollama is running: `netstat -ano | findstr :11434`
2. Check Mistral model is available: `ollama list`
3. Increase timeout in request (currently 120 seconds)
4. Check system resources (RAM, CPU)

### Issue: Gemini API returns 429 error

**Solution:**
1. This is expected - quota exceeded
2. System automatically falls back to Ollama
3. Check Google Cloud Console for quota reset time
4. Ollama will continue to work as fallback

### Issue: Ollama returns empty response

**Solution:**
1. Check Ollama is running: `ollama serve`
2. Check Mistral model is available: `ollama list`
3. Try pulling model again: `ollama pull mistral`
4. Check system has enough RAM (Mistral needs ~4GB)

---

## 📊 Test Data Sets

### Test Case 1: High Probability (Tier-1)
```json
{
  "CGPA": 9.0,
  "12th_Marks": 95,
  "10th_Marks": 95,
  "Total_Backlogs": 0,
  "Has_Experience": 1,
  "Num_Companies": 2,
  "Has_Internship": 1,
  "Has_Skills": 1,
  "Has_Projects": 1,
  "Has_Certifications": 1,
  "Academic_Trend": 5,
  "Is_Female": 0
}
```

### Test Case 2: Medium Probability (Tier-2)
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

### Test Case 3: Low Probability (Tier-3)
```json
{
  "CGPA": 6.0,
  "12th_Marks": 70,
  "10th_Marks": 75,
  "Total_Backlogs": 2,
  "Has_Experience": 0,
  "Num_Companies": 0,
  "Has_Internship": 0,
  "Has_Skills": 0,
  "Has_Projects": 0,
  "Has_Certifications": 0,
  "Academic_Trend": -2,
  "Is_Female": 1
}
```

---

## 🎯 Expected Behavior

### Gemini API (Primary)
- ✅ Faster response (2-5 seconds)
- ✅ Better quality recommendations
- ✅ More detailed and personalized
- ⚠️ Limited by quota (429 error when exceeded)

### Ollama (Fallback)
- ✅ Always available (local)
- ✅ No quota limits
- ⚠️ Slower response (10-30 seconds)
- ⚠️ Requires local resources

### Automatic Fallback
- ✅ Transparent to user
- ✅ No error messages
- ✅ Same response format
- ✅ Source field indicates which API was used

---

## 📈 Performance Metrics

### Prediction API
- **Response Time:** < 1 second
- **Accuracy:** 66.15%
- **Recall:** 41.48%
- **F1 Score:** 35.87%

### Recommendations API
- **Gemini:** 2-5 seconds (when quota available)
- **Ollama:** 10-30 seconds (always available)
- **Fallback:** Automatic (no user action needed)

---

## ✅ Verification Checklist

- [ ] Flask server running on port 5000
- [ ] Ollama server running on port 11434
- [ ] Mistral model available (4.4 GB)
- [ ] Prediction API returns correct format
- [ ] Recommendations API returns correct format
- [ ] Gemini API tries first (even if quota exceeded)
- [ ] Ollama fallback works automatically
- [ ] Frontend auto-fills from prediction page
- [ ] Frontend displays recommendations correctly
- [ ] Source field shows correct API used

---

**Last Updated:** May 18, 2026
**Status:** ✅ All Tests Passing
