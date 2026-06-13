# 🚀 PlaceReady - Quick Start Guide

**Status:** ✅ READY TO USE

---

## 🎯 What You Have

✅ **Backend Running** - Python Flask on port 5000  
✅ **Frontend Running** - React on port 8081  
✅ **Supabase Connected** - Database & Storage  
✅ **ML Models Loaded** - V8 Ensemble  
✅ **Photo Upload** - Working  
✅ **Admin Setup** - Automated  

---

## 📱 How to Access

### Frontend
```
URL: http://localhost:8081
```

### Backend API
```
URL: http://localhost:5000
Health: http://localhost:5000/api/health
```

---

## 🔐 Login

**Email:** `sumitdangi84552@gmail.com`  
**Auth:** OTP-based (check console logs)

**First Time:**
1. Click "Sign Up"
2. Enter email
3. Get OTP from console
4. Enter OTP
5. Redirected to home

---

## 📸 Photo Upload

1. Go to `/profile`
2. Click upload area
3. Select image (PNG/JPG/GIF, < 5MB)
4. Click "Save Changes"
5. ✅ Photo saved!

---

## 🎯 Making Prediction

1. Go to `/predict`
2. Fill form:
   - CGPA
   - Marks
   - Backlogs
   - Companies
   - Experience
3. Submit
4. ✅ Prediction saved!

---

## 👨‍💼 Admin Dashboard

1. Go to `/admin`
2. See all predictions
3. Filter by source (Batch/User/All)
4. Click predictions to see details
5. View user photos

---

## 🛠️ Setup (Auto)

**Widget appears in bottom-right if needed**

1. Click "Setup" for Storage
2. Click "Init" for Source Column
3. ✅ Setup complete!

---

## 📊 Dashboard

1. Go to `/dashboard`
2. See your stats:
   - Total predictions
   - Average probability
   - Account status
3. View charts (if you have predictions)
4. Auto-refresh every 3 seconds

---

## 🧪 Quick Tests

### Test Backend
```bash
curl http://localhost:5000/api/health
```

### Test Frontend
```
Open http://localhost:8081 in browser
```

### Test Login
1. Click "Sign Up"
2. Try to login
3. Should get OTP

### Test Photo
1. Go to Profile
2. Upload photo
3. Should see preview
4. Click Save
5. Success message

---

## 📁 Important Files

**New Files (Just Added):**
- `READY_TO_USE.md` - Full details
- `SETUP_COMPLETE_GUIDE.md` - Setup instructions
- `TEST_NEW_FEATURES.md` - Testing
- `IMPLEMENTATION_COMPLETE.md` - Technical
- `QUICK_START.md` - This file!

**Code:**
- `app.py` - Backend (1665 lines)
- `src/components/SetupInitializer.tsx` - Setup widget
- `src/routes/__root.tsx` - Layout

---

## ✨ Features

- ✅ Email + OTP auth
- ✅ User profiles with photos
- ✅ Photo upload to cloud storage
- ✅ Make predictions
- ✅ Batch upload predictions
- ✅ Dashboard with charts
- ✅ Admin panel with filtering
- ✅ Auto-refresh (3 seconds)
- ✅ Responsive design (mobile-friendly)
- ✅ Setup automation

---

## 🐛 If Something's Wrong

### Backend not running?
```bash
taskkill /F /IM python.exe
python app.py
```

### Frontend not running?
```bash
# Kill the process and restart
npm run dev
```

### Photo not uploading?
- Check file size (< 5MB)
- Check format (PNG, JPG, GIF, WebP)
- Check browser console (F12)

### Not seeing setup widget?
- Login first
- Check if admin: `is_admin = true`
- Refresh page

---

## 🎯 Common Tasks

### Upload Profile Photo
```
Profile → Click Upload → Select Image → Save
```

### Make Prediction
```
Predict → Fill Form → Submit
```

### See All Predictions (Admin)
```
Admin → View Table → Filter by Source
```

### Check Dashboard
```
Dashboard → See Stats → View Charts
```

---

## 🔑 Master Key

**For Setup Endpoints Only**

```
Key: initial-setup-key
```

> ⚠️ Change this before going to production!

---

## 📊 Expected Results

After completing setup, you should see:

- ✅ Admin status set
- ✅ Storage bucket created
- ✅ Source column initialized
- ✅ Photos can be uploaded
- ✅ Photos display in profile
- ✅ Photos visible in admin
- ✅ Predictions filterable by source
- ✅ Widget disappears (setup complete)

---

## 🎉 That's It!

**You're all set to use PlaceReady!**

Visit: **http://localhost:8081**

---

## 📞 Need Help?

Read these files in order:

1. **READY_TO_USE.md** - Overview
2. **SETUP_COMPLETE_GUIDE.md** - Detailed setup
3. **TEST_NEW_FEATURES.md** - Testing guide
4. **API_DOCUMENTATION.md** - API reference

---

**Happy Predicting! 🚀**
