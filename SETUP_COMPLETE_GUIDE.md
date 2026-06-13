# 🚀 PlaceReady - Complete Setup Guide

> **Karo Bilkul Easy - Everything Automated!** ✨

## ✅ What's New in This Update

This update adds **automatic setup endpoints** so you never have to run SQL manually again!

### New Features:
1. ✅ **Photo Upload Support** - Users can upload profile photos to Supabase Storage
2. ✅ **Admin Setup Endpoint** - Make yourself admin without SQL
3. ✅ **Storage Bucket Setup** - Automatic storage bucket creation
4. ✅ **Source Column Initialization** - Automatic batch vs user prediction tracking
5. ✅ **Setup Status Monitor** - See what's configured and what's not
6. ✅ **Auto Setup Widget** - Small widget appears in corner for admin to complete setup

---

## 🎯 Quick Setup Steps

### Step 1: Login to Your Account
1. Go to http://localhost:8081
2. Click "Sign Up" 
3. Enter email: `sumitdangi84552@gmail.com`
4. Enter OTP (check console or `app.py` logs)
5. You'll be redirected to home page

### Step 2: Complete Setup (if showing widget)
A small widget appears in the bottom-right corner if you're not fully set up:

```
📋 System Setup
✅ Admin Access
📦 Photo Storage [Setup] button
🏷️ Data Sources [Init] button
```

Just click the buttons to complete each step!

---

## 📋 Backend Endpoints (For Reference)

### 1. Make Admin
**Endpoint:** `POST /api/setup/make-admin`
```json
{
  "email": "sumitdangi84552@gmail.com",
  "master_key": "initial-setup-key"
}
```
**Response:**
```json
{
  "status": "success",
  "message": "User sumitdangi84552@gmail.com is now admin",
  "data": {...}
}
```

### 2. Create Storage Bucket
**Endpoint:** `POST /api/setup/create-storage-bucket`
```json
{
  "master_key": "initial-setup-key"
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Storage bucket created successfully"
}
```

### 3. Initialize Source Column
**Endpoint:** `POST /api/setup/init-source-column`
**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "status": "success",
  "message": "Initialized source column for 1000+ predictions",
  "updated_count": 1000
}
```

### 4. Check Setup Status
**Endpoint:** `GET /api/setup/status`
**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "status": "success",
  "setup": {
    "admin_user": {
      "email": "sumitdangi84552@gmail.com",
      "is_admin": true
    },
    "storage_buckets": ["profile-photos"],
    "has_profile_photos_bucket": true,
    "predictions_with_source": 1000
  }
}
```

---

## 📸 Photo Upload Feature

### How It Works:
1. User goes to **Profile Page** (`/profile`)
2. Uploads a photo (PNG, JPG, GIF - max 5MB)
3. Photo is converted to base64
4. Backend uploads to Supabase Storage (`profile-photos` bucket)
5. Public URL is stored in database
6. Photo appears in profile and admin dashboard

### Photo Storage Path:
```
profile-photos/{user_id}/profile.{extension}
```

### Supported Formats:
- PNG (image/png) → `.png`
- JPG/JPEG (image/jpeg) → `.jpg`
- GIF (image/gif) → `.gif`
- WebP (image/webp) → `.webp`

---

## 🔄 Data Source Separation

The system now tracks WHERE each prediction came from:

### Sources:
- **batch** → Excel file batch upload (`/api/admin/batch-predict`)
- **user** → Manual form submission (`/api/predict`)

### Admin Dashboard Shows:
- **Batch predictions** → Name, Roll Number, Probability, Prediction, Tier
- **User predictions** → Name, Email, Phone, College, CGPA, Probability, Tier
- **All predictions** → Combined view with all data

---

## 🛠️ Manual Setup (If Widget Doesn't Work)

### Using Frontend (Recommended):
1. Login as `sumitdangi84552@gmail.com`
2. Wait for setup widget in bottom-right
3. Click buttons to complete setup

### Using cURL (Alternative):

#### Make Admin:
```bash
curl -X POST http://localhost:5000/api/setup/make-admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sumitdangi84552@gmail.com",
    "master_key": "initial-setup-key"
  }'
```

#### Create Storage Bucket:
```bash
curl -X POST http://localhost:5000/api/setup/create-storage-bucket \
  -H "Content-Type: application/json" \
  -d '{
    "master_key": "initial-setup-key"
  }'
```

#### Initialize Source:
```bash
curl -X POST http://localhost:5000/api/setup/init-source-column \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

#### Check Status:
```bash
curl http://localhost:5000/api/setup/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🗄️ Database Schema

### Source Column
```sql
ALTER TABLE predictions 
ADD COLUMN source TEXT DEFAULT 'batch';

CREATE INDEX idx_predictions_source ON predictions(source);
```

### Profile Photo Column
```sql
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS photo TEXT;
```

---

## ✨ Testing Photo Upload

### Step 1: Go to Profile
1. Login to http://localhost:8081
2. Click avatar dropdown
3. Click "Profile"

### Step 2: Upload Photo
1. Click upload area
2. Select an image file (PNG, JPG, GIF)
3. Max 5MB
4. Click "Save Changes"

### Step 3: Verify
1. Photo appears in profile preview
2. Navigate to dashboard and back
3. Photo persists (proof it's saved!)
4. Admin can see photo in admin dashboard

---

## 🎨 Admin Dashboard Updates

### New Features:
1. **Source Filter Dropdown** - Filter by Batch/User/All
2. **Separate Tables** - Different columns for each source
3. **Analytics Tab** - Separate stats for batch and user predictions
4. **Setup Button** - "Initialize Source Column" button in header

### Column Display:
```
Batch Mode:
- Name, Roll Number, Probability, Prediction, Tier

User Mode:
- Name, Email, Phone, College, CGPA, Probability, Tier

All Mode:
- Shows all available columns
```

---

## 🚀 Complete Feature List

### ✅ Authentication
- Email + OTP login
- JWT token management
- New user detection
- Smart redirect (new → home, returning → dashboard)

### ✅ User Profiles
- Name, email, phone, college, branch, CGPA, graduation year
- Profile photo upload to Supabase Storage
- Profile editing with validation

### ✅ Predictions
- Manual form predictions (user source)
- Batch Excel upload (batch source)
- Automatic source tracking
- Probability and tier calculation

### ✅ Dashboard
- User predictions list
- Performance graphs (tier distribution, probability trend)
- Auto-refresh every 3 seconds
- Mobile responsive

### ✅ Admin Panel
- View all predictions (batch + user)
- Filter by source
- See user profiles and details
- Batch upload with progress tracking
- Initialize source column on demand

### ✅ Responsive Design
- Mobile hamburger menu
- Adaptive layouts
- Touch-friendly UI
- Works on all devices

---

## 📊 Performance Features

### Auto-Refresh:
- Dashboard refreshes every 3 seconds
- Refreshes on window focus
- Shows last updated timestamp
- Console logs for debugging

### Batch Upload:
- Handles 1000+ records
- Progress tracking
- Error handling
- Source automatic set to 'batch'

### Admin Dashboard:
- Efficient filtering
- Indexed source column
- Fast data retrieval
- Responsive tables

---

## 🐛 Troubleshooting

### Photo Not Uploading?
1. Check file size (< 5MB)
2. Check file format (PNG, JPG, GIF)
3. Check backend logs for errors
4. Try refreshing page

### Setup Widget Not Showing?
1. Make sure you're logged in
2. Check browser console for errors
3. Manual setup using cURL above

### Admin Not Working?
1. Check `is_admin` in database: 
   ```sql
   SELECT email, is_admin FROM users WHERE email = 'sumitdangi84552@gmail.com';
   ```
2. Try making admin again via widget or cURL

### Source Column Not Initialized?
1. Click "Initialize Source Column" button
2. Check if predictions have source: 
   ```sql
   SELECT COUNT(*), source FROM predictions GROUP BY source;
   ```

---

## 📝 Environment Variables

Required in `.env`:

See `.env.example` file for all required environment variables. Copy and populate with your actual values:

```bash
cp .env.example .env
# Then fill in your actual values:
# - VITE_API_URL: Your backend URL
# - Supabase credentials from your account
# - Master setup key for initial admin creation
```

---

## 🎯 Next Steps

1. ✅ Login to app
2. ✅ Complete setup via widget
3. ✅ Upload profile photo
4. ✅ Make a prediction
5. ✅ Check admin dashboard
6. ✅ Verify everything works!

---

## 💡 Tips

- **Photos are Public** - They're stored in public storage bucket so they can be displayed
- **Base64 Conversion** - Photos are converted to base64 in frontend, then to bytes in backend
- **Automatic Indexing** - Source column is indexed for fast filtering
- **No Manual SQL** - Everything is automated, no SQL needed!

---

**Happy Predicting! 🎉**
