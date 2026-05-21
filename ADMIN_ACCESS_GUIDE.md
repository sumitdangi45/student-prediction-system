# 🎯 Admin Panel Access Guide

## ✅ System Status
- **Backend**: Running on `http://localhost:5000` ✅
- **Frontend**: Running on `http://localhost:8080` ✅
- **MongoDB**: Connected ✅
- **Predictions in DB**: 16 students ✅

---

## 📊 Admin Panel Features

### 1. **Statistics Cards** (5 cards)
- Total Students: 16
- Tier-1: 6 students (37.5%)
- Tier-2: 3 students (18.75%)
- Average Probability: 57.14%
- Average CGPA: 0.47

### 2. **Analytics Tab** (4 Charts)
1. **Tier Distribution (Pie Chart)**
   - Shows breakdown of students by tier
   - Tier-1: 6, Tier-2: 3, Tier-3: 6, Below Tier-3: 1

2. **CGPA Distribution (Bar Chart)**
   - Shows number of students by CGPA range

3. **Placement Probability Distribution (Line Chart)**
   - Shows trend of placement probabilities
   - Sorted from lowest to highest

4. **Average Probability by Tier (Bar Chart)**
   - Compares average placement probability across tiers
   - Tier-1: ~74.73%, Tier-2: ~63.78%, Tier-3: ~41.93%, Below Tier-3: ~22.87%

### 3. **Students Tab**
- Table with all 16 students
- Columns: Name, Email, CGPA, Probability, Tier, Date
- Search by name/email
- Filter by tier

### 4. **File Operations**
- **Upload Excel**: Batch predict from Excel file
- **Download Data**: Export all predictions to Excel

---

## 🔐 How to Login

### Step 1: Go to Frontend
Open browser and go to: `http://localhost:8080`

### Step 2: Click "Login/Signup"
- Click the login button in the header

### Step 3: Enter Admin Email
- Email: `sumitdangi84552@gmail.com`
- Click "Send OTP"

### Step 4: Check Gmail
- Open Gmail inbox
- Find email from PlaceReady
- Copy the 6-digit OTP

### Step 5: Enter OTP
- Paste OTP in the form
- Click "Verify OTP"

### Step 6: Access Admin Panel
- After login, click on your profile avatar
- Select "Admin Dashboard"
- Or go directly to: `http://localhost:8080/admin`

---

## 📈 What You'll See

### Dashboard Overview
```
┌─────────────────────────────────────────────────────────┐
│                   ADMIN DASHBOARD                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Total Students: 16] [Tier-1: 6] [Tier-2: 3]         │
│  [Avg Prob: 57.14%] [Avg CGPA: 0.47]                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  ANALYTICS TAB          │  STUDENTS TAB                 │
│                         │                               │
│  [Tier Distribution]    │  [Search & Filter]            │
│  [CGPA Distribution]    │  [Student Table]              │
│  [Probability Trend]    │  - 16 students listed         │
│  [Tier Comparison]      │  - Sortable columns           │
│                         │                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Tier Breakdown (16 Students)

### Tier-1 (6 students) - EXCELLENT
- Average Probability: 74.73%
- Status: Ready for placement
- Probability Range: 70.9% - 78.4%

### Tier-2 (3 students) - GOOD
- Average Probability: 63.78%
- Status: Good chances
- Probability Range: 54.1% - 69.7%

### Tier-3 (6 students) - MODERATE
- Average Probability: 41.93%
- Status: Needs improvement
- Probability Range: 30.8% - 49.1%

### Below Tier-3 (1 student) - LOW
- Average Probability: 22.87%
- Status: Needs intensive support

---

## 📊 Data Analysis

### From 16 Predictions:
- **Total Placed (Tier-1 + Tier-2)**: 9 students (56.25%)
- **Moderate Chances (Tier-3)**: 6 students (37.5%)
- **Low Chances (Below Tier-3)**: 1 student (6.25%)

### Probability Distribution:
- **70%+**: 6 students (Tier-1)
- **50-70%**: 3 students (Tier-2)
- **30-50%**: 6 students (Tier-3)
- **<30%**: 1 student (Below Tier-3)

---

## 🔧 Troubleshooting

### Issue: Can't login
- **Solution**: Check if backend is running on port 5000
- **Check**: `netstat -ano | findstr :5000`

### Issue: Admin panel not loading
- **Solution**: Make sure you're logged in as admin user
- **Check**: Email should be `sumitdangi84552@gmail.com`

### Issue: No data showing
- **Solution**: Backend might not be connected to MongoDB
- **Check**: Look at backend console for connection status

### Issue: Charts not rendering
- **Solution**: Try refreshing the page
- **Check**: Open browser console (F12) for errors

---

## 📱 Quick Links

| Page | URL |
|------|-----|
| Home | `http://localhost:8080/` |
| Login | `http://localhost:8080/auth` |
| Dashboard | `http://localhost:8080/dashboard` |
| Admin Panel | `http://localhost:8080/admin` |
| Predict | `http://localhost:8080/predict` |
| Profile | `http://localhost:8080/profile` |

---

## 🚀 Next Steps

1. **Login** with admin email
2. **View Analytics** - See all 4 charts
3. **Check Students** - View all 16 predictions
4. **Upload Excel** - Add more students
5. **Download Data** - Export predictions

---

## 📞 Support

If you face any issues:
1. Check backend console for errors
2. Check browser console (F12) for frontend errors
3. Verify MongoDB connection
4. Restart servers if needed

---

**Status**: ✅ Ready to Use
**Last Updated**: May 20, 2026
**Admin Email**: sumitdangi84552@gmail.com

