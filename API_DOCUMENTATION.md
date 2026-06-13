# Flask API - Supabase Backend Documentation

## Overview
Production-ready Flask API with Supabase PostgreSQL backend for student placement predictions using V8 ensemble model (RF + GB + XGB).

- **Models**: Random Forest + Gradient Boosting + XGBoost (averaged ensemble)
- **Database**: Supabase PostgreSQL
- **Authentication**: JWT tokens (7-day expiry)
- **Debug Mode**: OFF (production-ready)

---

## Base URL
```
http://localhost:5000/api
```

---

## 1. Authentication Endpoints

### Register User
**POST** `/auth/register`

Register new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Registration successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": "uuid-string",
  "email": "user@example.com",
  "is_admin": false
}
```

**Error Responses:**
- `400` - Email and password required / Email already registered
- `500` - Registration failed

---

### Login User
**POST** `/auth/login`

Authenticate user and get JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": "uuid-string",
  "email": "user@example.com",
  "is_admin": false
}
```

**Error Responses:**
- `400` - Email and password required
- `401` - Invalid credentials
- `500` - Login failed

---

## 2. Prediction Endpoints

### Individual Prediction
**POST** `/predict`

Make single student placement prediction.

**Request Body:**
```json
{
  "cgpa": 8.5,
  "marks_12": 92.5,
  "marks_10": 95.0,
  "closed_backlogs": 0,
  "live_backlogs": 1,
  "num_companies": 3,
  "has_experience": 1
}
```

**Features Description:**
- `cgpa` (float): Current academics aggregate marks (0-10)
- `marks_12` (float): 12th standard marks (0-100)
- `marks_10` (float): 10th standard marks (0-100)
- `closed_backlogs` (int): Closed backlogs count
- `live_backlogs` (int): Live backlogs count
- `num_companies` (int): Number of professional experience companies
- `has_experience` (int): 1 if has professional experience, 0 otherwise

**Response (200):**
```json
{
  "status": "success",
  "prediction": 1,
  "probability": 0.78,
  "tier": "Tier-1",
  "model_version": "V8"
}
```

**Tier Logic:**
- `Tier-1`: probability ≥ 0.7 (High placement chances)
- `Tier-2`: probability ≥ 0.5 (Moderate placement chances)
- `Tier-3`: probability ≥ 0.3 (Low placement chances)
- `Below Tier-3`: probability < 0.3 (Very low placement chances)

**Error Responses:**
- `400` - Invalid input format
- `500` - Models not available / Prediction failed

---

## 3. Admin Endpoints

### Get Dashboard Analytics
**GET** `/admin/students`

Fetch all students with predictions and analytics.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response (200):**
```json
{
  "status": "success",
  "students": [
    {
      "id": "pred-id",
      "name": "John Doe",
      "roll_no": "0501CS221001",
      "cgpa": 8.5,
      "probability": 0.78,
      "tier": "Tier-1",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "analytics": {
    "totalStudents": 1032,
    "tier1Count": 120,
    "tier2Count": 280,
    "tier3Count": 350,
    "belowTier3Count": 282,
    "averageProbability": 0.54,
    "averageCGPA": 7.8
  }
}
```

**Error Responses:**
- `401` - Token required / Invalid token
- `403` - Admin access required
- `500` - Fetch failed

---

### Batch Upload (Excel)
**POST** `/admin/batch-predict`

Process entire Excel file (~1032 students) and save predictions.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data
```

**Request:**
- File: Excel file (.xlsx)
- Expected rows: ~1032 students

**Excel Column Mapping:**
| Excel Column | Internal Key |
|---|---|
| First Name | first_name |
| Last Name | last_name |
| Roll No | roll_no |
| Current Academics Aggregate Marks | cgpa |
| 12th - Aggregate Marks | marks_12 |
| 10th - Aggregate Marks | marks_10 |
| Current Academics Closed Backlogs | closed_backlogs |
| Current Academics Live Backlogs | live_backlogs |
| Number of Professional Experience Companies | num_companies |
| Has Professional Experience | has_experience |

**Response (200):**
```json
{
  "status": "success",
  "message": "Processed 1032 students",
  "processed": 1032,
  "failed": 0,
  "total": 1032,
  "errors": []
}
```

**Response (200 - Partial):**
```json
{
  "status": "partial",
  "message": "Processed 1030 students",
  "processed": 1030,
  "failed": 2,
  "total": 1032,
  "errors": [
    "Row 45: Invalid CGPA value",
    "Row 128: DB insert failed"
  ]
}
```

**Error Responses:**
- `400` - No file provided / File empty
- `401` - Token required / Invalid token
- `403` - Admin access required
- `500` - Batch processing failed

---

### Export Predictions (Excel)
**GET** `/admin/export-excel`

Export all predictions as 13-column Excel file.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response (200):**
Downloads Excel file: `students-predictions-2024-01-15_10-30-00.xlsx`

**Columns (13):**
1. First Name
2. Last Name
3. Roll No
4. CGPA
5. 12th Marks
6. 10th Marks
7. Closed Backlogs
8. Live Backlogs
9. Num Companies
10. Has Experience
11. Prediction (0 or 1)
12. Probability (0-1 float)
13. Tier (Tier-1, Tier-2, Tier-3, Below Tier-3)

**Error Responses:**
- `400` - No predictions found
- `401` - Token required / Invalid token
- `403` - Admin access required
- `500` - Export failed

---

## 4. Health Check

### Endpoint Status
**GET** `/health`

Check API and database connection status.

**Response (200):**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z",
  "supabase": "connected",
  "models": "V8"
}
```

---

## Authentication

### JWT Token Format
Tokens are valid for **7 days**.

**Token Payload:**
```json
{
  "user_id": "uuid-string",
  "is_admin": false,
  "exp": 1705329000,
  "iat": 1704724200
}
```

**How to use:**
1. Call `/auth/register` or `/auth/login` to get token
2. Include token in request header:
   ```
   Authorization: Bearer <TOKEN>
   ```

---

## Data Models

### User (Supabase Auth + users table)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Predictions (Supabase predictions table)
```sql
CREATE TABLE predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  roll_no VARCHAR(50),
  cgpa FLOAT NOT NULL,
  marks_12 FLOAT NOT NULL,
  marks_10 FLOAT NOT NULL,
  closed_backlogs INT NOT NULL,
  live_backlogs INT NOT NULL,
  num_companies INT NOT NULL,
  has_experience BOOLEAN NOT NULL,
  prediction INT NOT NULL,
  probability FLOAT NOT NULL,
  tier VARCHAR(50) NOT NULL,
  batch_upload BOOLEAN DEFAULT FALSE,
  row_index INT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Model Information

### V8 Ensemble Model
**Components:**
- Random Forest (RF)
- Gradient Boosting (GB)
- XGBoost (XGB)

**Ensemble Method:** Average of predict_proba from all 3 models

**Input Features (7):**
1. CGPA (0-10)
2. 12th Marks (0-100)
3. 10th Marks (0-100)
4. Closed Backlogs (int)
5. Live Backlogs (int)
6. Number of Companies (int)
7. Has Professional Experience (0/1)

**Output:**
- Probability: 0-1 (ensemble average)
- Prediction: 0 (not placed) or 1 (placed)
- Tier: Based on probability thresholds

**Model Files Location:**
- `models/rf_model_v8.pkl`
- `models/gb_model_v8.pkl`
- `models/xgb_model_v8.pkl`
- `models/scaler_v8.pkl`
- `models/threshold_v8.pkl`

---

## Error Handling

### Common Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request (invalid input, missing fields) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 500 | Internal Server Error |

### Error Response Format
```json
{
  "status": "error",
  "message": "Descriptive error message"
}
```

---

## Environment Variables

Required variables in `.env`:
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT
JWT_SECRET=your-strong-secret-key-change-in-production
```

---

## Usage Examples

### Example 1: Register & Login
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'
```

### Example 2: Make Prediction
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cgpa": 8.5,
    "marks_12": 92.5,
    "marks_10": 95.0,
    "closed_backlogs": 0,
    "live_backlogs": 1,
    "num_companies": 3,
    "has_experience": 1
  }'
```

### Example 3: Get Admin Analytics
```bash
curl -X GET http://localhost:5000/api/admin/students \
  -H "Authorization: Bearer <TOKEN>"
```

### Example 4: Batch Upload
```bash
curl -X POST http://localhost:5000/api/admin/batch-predict \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@Students-List-15-05-2026-07-08-24-0KBlEw.xlsx"
```

### Example 5: Export Excel
```bash
curl -X GET http://localhost:5000/api/admin/export-excel \
  -H "Authorization: Bearer <TOKEN>" \
  -o predictions.xlsx
```

---

## Performance Notes

- **Batch Upload**: Processes ~1032 students in ~30-60 seconds
- **Export**: Generates Excel with 1032+ rows in <5 seconds
- **Single Prediction**: <100ms response time
- **Model Loading**: ~5 seconds on startup

---

## Production Checklist

- ✅ Debug mode: OFF
- ✅ Proper error handling and logging
- ✅ JWT token expiration (7 days)
- ✅ Admin access verification
- ✅ Input validation
- ✅ CORS configuration
- ✅ Model ensemble implementation
- ✅ Supabase connection pooling
- ⚠️ Change JWT_SECRET in production
- ⚠️ Set CORS allowed origins for your domain

---

## Support & Logging

All requests are logged with timestamps and levels (INFO, WARNING, ERROR).

Logs include:
- User authentication events
- Prediction requests
- Batch processing progress
- Database operations
- Model loading status

Check console output for detailed logs during development.
