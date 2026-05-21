# 🧪 Admin Panel Testing Steps

## Prerequisites
- ✅ Backend running on `http://localhost:5000`
- ✅ Frontend running on `http://localhost:3000` (or your dev server)
- ✅ MongoDB connected
- ✅ Admin user: `sumitdangi84552@gmail.com`

## Test Flow

### Test 1: Login Flow
**Goal**: Verify login works and profile avatar shows instead of signup/login buttons

**Steps**:
1. Open http://localhost:3000/auth
2. Enter email: `sumitdangi84552@gmail.com`
3. Click "Send OTP"
4. Check email for OTP
5. Enter OTP and click "Verify"
6. **Expected**: 
   - Redirected to dashboard
   - Header shows profile avatar (not signup/login buttons)
   - Profile dropdown shows "Admin Panel" option

**What's Happening**:
- AuthContext verifies token with `GET /api/auth/me`
- Backend returns user data with `is_admin: true`
- Header renders profile avatar instead of buttons

---

### Test 2: Admin Panel Access
**Goal**: Verify admin can access admin panel

**Steps**:
1. Click profile avatar in header
2. Click "Admin Panel" option
3. **Expected**: 
   - Redirected to `/admin`
   - Admin dashboard loads with statistics and charts
   - No error messages

**What's Happening**:
- Admin route checks `user.is_admin` from AuthContext
- If true, renders AdminDashboard component
- If false, redirects to dashboard

---

### Test 3: View Student Data
**Goal**: Verify admin can see student predictions

**Steps**:
1. In admin panel, look at "Students" tab
2. **Expected**:
   - Table shows all student predictions
   - Shows columns: Name, Email, Probability, Tier
   - Search and filter work

**What's Happening**:
- AdminDashboard calls `GET /api/admin/students`
- Backend verifies `is_admin` field
- Returns all predictions with analytics

---

### Test 4: Upload Excel File
**Goal**: Verify batch prediction works

**Steps**:
1. In admin panel, click "Upload Excel" button
2. Select one of the Excel files from `/dataset` folder
3. Click upload
4. **Expected**:
   - File uploads successfully
   - Predictions are generated for all students
   - New data appears in the table

**What's Happening**:
- AdminDashboard sends file to `POST /api/admin/batch-predict`
- Backend processes Excel and generates predictions
- Predictions stored in MongoDB

---

### Test 5: Export Data
**Goal**: Verify data export works

**Steps**:
1. In admin panel, click "Export to Excel" button
2. **Expected**:
   - Excel file downloads
   - File contains all student predictions
   - Columns include all features and predictions

**What's Happening**:
- AdminDashboard calls `GET /api/admin/export-excel`
- Backend generates Excel file with all predictions
- File sent to browser for download

---

### Test 6: Logout Flow
**Goal**: Verify logout clears auth state

**Steps**:
1. Click profile avatar
2. Click "Logout"
3. **Expected**:
   - Redirected to home page
   - Header shows signup/login buttons (not profile avatar)
   - localStorage cleared

**What's Happening**:
- Header calls `POST /api/auth/logout`
- AuthContext clears token and user
- localStorage cleared
- `isAuthenticated` becomes false

---

### Test 7: Non-Admin Access
**Goal**: Verify non-admin users can't access admin panel

**Steps**:
1. Create a new account with different email
2. Try to access `/admin` directly
3. **Expected**:
   - Redirected to dashboard
   - Toast error: "You don't have admin access"

**What's Happening**:
- Admin route checks `user.is_admin`
- If false, redirects to dashboard
- Non-admin users can't access admin endpoints

---

## Common Issues & Solutions

### Issue: "Admin access required" error
**Cause**: User doesn't have `is_admin = true` in database
**Solution**: Run `python setup_admin.py` to set admin role

### Issue: Login/signup buttons still showing after login
**Cause**: AuthContext not verifying token with backend
**Solution**: Check browser console for errors, verify backend is running

### Issue: Admin panel shows "Loading..." forever
**Cause**: Backend not responding or token invalid
**Solution**: Check backend logs, verify token in localStorage

### Issue: Excel upload fails
**Cause**: File format incorrect or backend error
**Solution**: Use Excel files from `/dataset` folder, check backend logs

---

## Backend Endpoints Reference

### Authentication
- `POST /api/auth/send-otp` - Send OTP to email
- `POST /api/auth/verify-otp` - Verify OTP and login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

### Admin Endpoints
- `GET /api/admin/students` - Get all students with predictions
- `POST /api/admin/batch-predict` - Batch predict from Excel
- `GET /api/admin/export-excel` - Export predictions to Excel
- `POST /api/admin/manage-roles` - Assign/revoke admin roles
- `GET /api/admin/list-admins` - List all admin users

---

## Debugging Tips

### Check Backend Logs
```bash
# Terminal where backend is running
# Look for error messages and request logs
```

### Check Browser Console
```javascript
// Open DevTools (F12)
// Check Console tab for errors
// Check Network tab for API calls
```

### Check MongoDB
```bash
# Use MongoDB Compass or CLI
# Check users collection for is_admin field
# Check predictions collection for data
```

### Check localStorage
```javascript
// In browser console
localStorage.getItem('token')
localStorage.getItem('user')
```

---

## Success Indicators

✅ All tests pass
✅ No error messages in console
✅ Admin panel loads and displays data
✅ Excel upload and export work
✅ Logout clears auth state
✅ Non-admin users can't access admin panel

---

**Ready to test!** 🚀
