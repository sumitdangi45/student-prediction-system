# 🛡️ Admin Panel - Complete Guide

## Overview
Admin panel is now live! Only **sumitdangi84551@gmail.com** can access it.

---

## ✅ What's Been Built

### 1. **Admin Route** (`/admin`)
- Protected route that checks if user is admin
- Redirects non-admin users to dashboard
- Requires authentication

### 2. **Admin Dashboard Component**
Located at: `src/components/AdminDashboard.tsx`

Features:
- **Statistics Cards** - Total students, Tier distribution, Average probability, Average CGPA
- **Analytics Tab** - Charts and visualizations
- **Students Tab** - Searchable, filterable student table
- **File Upload** - Upload Excel files for batch predictions
- **Data Export** - Download all predictions as Excel

### 3. **Backend Admin Endpoints**

#### `GET /api/admin/students`
- Fetches all student predictions
- Returns analytics summary
- Requires admin authentication

#### `POST /api/admin/batch-predict`
- Accepts Excel file upload
- Processes all students in file
- Saves predictions to MongoDB
- Returns processing summary

#### `GET /api/admin/export-excel`
- Exports all predictions to Excel file
- Includes all features and predictions
- Downloads as attachment

---

## 🚀 How to Access

### Step 1: Login
1. Go to http://localhost:8080/auth
2. Enter email: **sumitdangi84551@gmail.com**
3. Verify OTP from email
4. Click "Login"

### Step 2: Access Admin Panel
1. Click on profile avatar (top right)
2. You'll see "Admin Panel" option (with shield icon)
3. Click it to go to admin dashboard

---

## 📊 Admin Dashboard Features

### Statistics Section
- **Total Students** - Count of all predictions
- **Tier-1** - Students with ≥70% probability
- **Tier-2** - Students with 50-69% probability
- **Avg Probability** - Average placement probability
- **Avg CGPA** - Average CGPA of all students

### Analytics Tab

#### Tier Distribution (Pie Chart)
- Visual breakdown of students by tier
- Color-coded: Green (Tier-1), Blue (Tier-2), Amber (Tier-3), Red (Below Tier-3)

#### CGPA Distribution (Bar Chart)
- Shows number of students in each CGPA range
- Helps identify academic strength distribution

#### Probability Distribution (Line Chart)
- Shows trend of placement probabilities
- Helps identify overall placement chances

### Students Tab

#### Search & Filter
- **Search** - Find students by name or email
- **Filter by Tier** - View specific tier students
- **Real-time filtering** - Results update instantly

#### Student Table
Shows:
- Student Name
- Email
- CGPA
- Placement Probability (%)
- Tier (color-coded)
- Prediction Date

---

## 📤 Upload Excel File

### File Format Required
Excel file should have these columns:
```
Current Academics Aggregate Marks
Current Academics Closed Backlogs
Current Academics Live Backlogs
12th - Aggregate Marks
10th - Aggregate Marks
Has Professional Experience
Number of Professional Experience Companies
Total Gap In Education
Count of Companies Registered in - Job
Count of Companies Registered in - Internship
```

### How to Upload
1. Click "Upload Excel" button (top right)
2. Select your Excel file (.xlsx, .xls, or .csv)
3. System will process all students
4. Results appear in Students tab
5. Success message shows number processed

### Processing
- Each student's data is validated
- ML model makes prediction
- Results saved to MongoDB
- Takes ~2-3 minutes for 500 students

---

## 📥 Download Data

### How to Download
1. Click "Download Data" button (top right)
2. Excel file downloads automatically
3. Filename: `students-predictions-YYYY-MM-DD.xlsx`

### What's Included
- All student predictions
- Probability percentages
- Tier classification
- All input features
- Timestamp of prediction

---

## 🔐 Security

### Admin Access Control
- Only **sumitdangi84551@gmail.com** can access
- JWT token verification required
- All endpoints check admin status
- Unauthorized access returns 403 error

### Data Protection
- All data stored in MongoDB
- Predictions linked to admin user
- Batch uploads tracked with timestamp
- Export includes all historical data

---

## 📈 Analytics Insights

### What to Look For

#### Tier Distribution
- **High Tier-1 %** = Strong student batch
- **High Tier-3+ %** = Need more skill development

#### CGPA Distribution
- **Concentrated around 7-8** = Consistent batch
- **Wide spread** = Diverse student abilities

#### Probability Trend
- **Upward trend** = Improving students
- **Downward trend** = Struggling students

#### Average Metrics
- **Avg Probability > 60%** = Good placement chances
- **Avg CGPA > 7.5** = Strong academic performance

---

## 🛠️ Technical Details

### Frontend
- **Route**: `src/routes/admin.tsx`
- **Component**: `src/components/AdminDashboard.tsx`
- **Charts**: Recharts library
- **Tables**: Shadcn UI components

### Backend
- **Endpoints**: Added to `app.py`
- **Database**: MongoDB
- **Authentication**: JWT tokens
- **File Processing**: Pandas + NumPy

### API Endpoints
```
GET  /api/admin/students          - Fetch all students
POST /api/admin/batch-predict     - Upload and predict
GET  /api/admin/export-excel      - Download Excel
```

---

## ⚠️ Troubleshooting

### Issue: "Admin access required"
**Solution**: Make sure you're logged in with sumitdangi84551@gmail.com

### Issue: File upload fails
**Solution**: 
- Check file format (Excel/CSV)
- Ensure all required columns present
- File size should be reasonable

### Issue: No data showing
**Solution**:
- Upload Excel file first
- Wait for processing to complete
- Refresh page after upload

### Issue: Charts not displaying
**Solution**:
- Ensure data is uploaded
- Check browser console for errors
- Try refreshing page

---

## 📝 Next Steps

1. **Upload your 500 students Excel file**
2. **Review analytics and tier distribution**
3. **Export data for further analysis**
4. **Monitor placement trends**
5. **Use insights for student guidance**

---

## 🎯 Use Cases

### For College Administration
- Track overall placement statistics
- Identify weak areas in student batch
- Monitor tier distribution
- Generate reports for stakeholders

### For Placement Cell
- Identify students needing support
- Track improvement over time
- Export data for analysis
- Share insights with faculty

### For Career Counseling
- Understand student strengths/weaknesses
- Provide targeted guidance
- Track progress
- Measure intervention effectiveness

---

## 📞 Support

If you face any issues:
1. Check this guide
2. Review browser console for errors
3. Verify MongoDB connection
4. Check API logs in terminal
5. Ensure all services running

---

**Status**: ✅ LIVE  
**Last Updated**: May 19, 2026  
**Admin Email**: sumitdangi84551@gmail.com

