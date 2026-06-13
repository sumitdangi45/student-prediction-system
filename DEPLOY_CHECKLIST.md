# ✅ DEPLOYMENT CHECKLIST - PlaceReady

**Before You Deploy - Verify Everything**

---

## 📋 PRE-DEPLOYMENT (Do This First)

### Code & Files
- [x] No syntax errors
- [x] All features working
- [x] 120 unnecessary files deleted
- [x] File structure clean
- [x] Git status clean

### Dependencies
- [x] Python 3.10+ installed
- [x] Node.js 18+ installed
- [x] pip install -r requirements.txt ✅
- [x] npm install ✅
- [x] All packages working

### Configuration
- [ ] Copy .env.example to .env
- [ ] Fill in Supabase credentials
- [ ] Fill in email credentials
- [ ] Fill in API keys (if using)
- [ ] Change MASTER_SETUP_KEY
- [ ] Verify .env is in .gitignore

### Documentation Read
- [ ] README.md (overview)
- [ ] DEPLOYMENT.md (deployment guide)
- [ ] PRODUCTION_READY.md (pre-flight)
- [ ] Your chosen platform's docs

### Local Testing
- [ ] npm run dev works
- [ ] python app.py works
- [ ] Backend runs on port 5000
- [ ] Frontend loads on port 8081
- [ ] Can login successfully
- [ ] Photo upload works
- [ ] Admin features work

---

## 🚀 DEPLOYMENT (Choose Platform)

### Option A: Railway.app

**Before:**
- [ ] Account created at railway.app
- [ ] GitHub account connected
- [ ] Repository pushed to GitHub

**Deploy:**
- [ ] Click "New Project"
- [ ] Select this GitHub repository
- [ ] Add environment variables:
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_ANON_KEY
  - [ ] SUPABASE_SERVICE_ROLE_KEY
  - [ ] GMAIL_EMAIL
  - [ ] GMAIL_PASSWORD
  - [ ] MASTER_SETUP_KEY (unique!)
- [ ] Click "Deploy"
- [ ] Wait for deployment
- [ ] Check logs for errors
- [ ] Test health endpoint

**After:**
- [ ] Backend URL noted
- [ ] Frontend environment variables updated
- [ ] Frontend deployed to Netlify

### Option B: Heroku

**Before:**
- [ ] Heroku account created
- [ ] Heroku CLI installed
- [ ] Logged in: heroku login

**Deploy:**
- [ ] Create app: heroku create placeready
- [ ] Set env vars: heroku config:set VAR=value
- [ ] Push code: git push heroku main
- [ ] Monitor: heroku logs --tail
- [ ] Check: heroku open /api/health

**After:**
- [ ] Backend URL: https://placeready.herokuapp.com
- [ ] Update frontend env vars
- [ ] Deploy frontend

### Option C: Docker + VPS

**Before:**
- [ ] Docker installed locally
- [ ] VPS rented (AWS, DigitalOcean, etc.)
- [ ] SSH key set up

**Deploy:**
- [ ] Build Docker image
- [ ] Test locally
- [ ] Push to registry
- [ ] SSH into VPS
- [ ] Pull and run container
- [ ] Set up reverse proxy (nginx)
- [ ] Configure SSL (certbot)

**After:**
- [ ] Backend running on domain
- [ ] HTTPS working
- [ ] Health check passing
- [ ] Logs accessible

### Option D: Netlify (Frontend Only)

**Before:**
- [ ] Netlify account created
- [ ] GitHub connected

**Deploy:**
- [ ] Import repository
- [ ] Configure build:
  - [ ] Build command: npm run build
  - [ ] Publish: dist
- [ ] Set environment variables:
  - [ ] VITE_API_URL (your backend URL)
  - [ ] VITE_SUPABASE_URL
  - [ ] VITE_SUPABASE_PUBLISHABLE_KEY
- [ ] Deploy
- [ ] Check build logs
- [ ] Test site

**After:**
- [ ] Frontend running on netlify.com domain
- [ ] Can configure custom domain
- [ ] SSL automatically enabled

---

## 🔒 SECURITY CHECK

- [ ] MASTER_SETUP_KEY changed
- [ ] No secrets in .env on GitHub
- [ ] .env in .gitignore
- [ ] Supabase RLS policies reviewed
- [ ] CORS configured for production
- [ ] Database backups enabled
- [ ] Monitoring set up
- [ ] Error tracking enabled (Sentry)

---

## 🌐 DOMAIN & SSL

- [ ] Domain purchased (if custom)
- [ ] DNS records configured
- [ ] A record pointing to server
- [ ] SSL certificate requested
- [ ] HTTPS certificate installed
- [ ] Redirect HTTP → HTTPS
- [ ] Certificate renewal automated

---

## 📊 MONITORING & ALERTS

- [ ] Error monitoring set up (Sentry)
- [ ] Database backup monitoring
- [ ] Response time alerts
- [ ] Error rate alerts (> 5%)
- [ ] Disk space alerts
- [ ] Memory usage alerts
- [ ] SSL certificate expiry alert

---

## 🧪 POST-DEPLOYMENT TESTING

### Backend
- [ ] Health check passes: GET /api/health
- [ ] Can login: POST /api/auth/login
- [ ] Can verify OTP: POST /api/auth/verify-otp
- [ ] Can make prediction: POST /api/predict
- [ ] Admin endpoints work
- [ ] Photo upload works
- [ ] Database queries work

### Frontend
- [ ] Homepage loads
- [ ] Can sign up
- [ ] Can login
- [ ] Profile page loads
- [ ] Photo upload works
- [ ] Dashboard displays
- [ ] Admin panel works
- [ ] Responsive on mobile

### Database
- [ ] Tables created
- [ ] Data accessible
- [ ] Backups working
- [ ] Indexes performing well
- [ ] No error logs

### Third-Party
- [ ] Email sending works
- [ ] Supabase connected
- [ ] Storage bucket accessible
- [ ] AI models responding (if used)

---

## 📈 PERFORMANCE CHECK

- [ ] Backend response time < 500ms
- [ ] Frontend load time < 1s
- [ ] Dashboard auto-refresh working
- [ ] Photo upload < 2s
- [ ] Prediction < 1s
- [ ] No 404 errors
- [ ] No 500 errors
- [ ] No console errors

---

## 🔄 DATA VERIFICATION

- [ ] Users table populated
- [ ] Predictions table working
- [ ] Admin can see all predictions
- [ ] Source column working
- [ ] Photos storing correctly
- [ ] Photo URLs accessible
- [ ] No data loss

---

## 📞 SUPPORT SETUP

- [ ] Support email configured
- [ ] Error notifications enabled
- [ ] Slack alerts set up (if using)
- [ ] Runbook created for team
- [ ] On-call schedule established
- [ ] Escalation process defined

---

## ✅ FINAL VERIFICATION

- [ ] All checklist items completed
- [ ] All tests passing
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Backups working
- [ ] Monitoring active
- [ ] Documentation up to date

---

## 🎉 LAUNCH

- [ ] Team briefing done
- [ ] Users notified
- [ ] Social media updated
- [ ] Press release (if applicable)
- [ ] Monitor closely first 24 hours
- [ ] Response team on standby

---

## 📊 ONGOING MAINTENANCE

### Daily
- [ ] Check error logs
- [ ] Monitor performance
- [ ] Verify backups

### Weekly
- [ ] Review user feedback
- [ ] Check security alerts
- [ ] Update dependencies

### Monthly
- [ ] Performance audit
- [ ] Security audit
- [ ] Backup test
- [ ] Capacity planning

### Quarterly
- [ ] Full system review
- [ ] Update documentation
- [ ] Plan improvements
- [ ] Team training

---

## 🆘 Emergency Contacts

- Backend: [Your contact]
- Database: [Your contact]
- DevOps: [Your contact]
- On-call: [On-call number]

---

## 📝 DEPLOYMENT NOTES

**Date:** _______________

**Platform:** _______________

**Backend URL:** _______________

**Frontend URL:** _______________

**Deployed By:** _______________

**Issues Encountered:** 

_______________________________________________

**Resolution:** 

_______________________________________________

**Notes:** 

_______________________________________________

---

## ✨ READY TO DEPLOY!

Once all items are checked, you're good to go! 🚀

---

**Deployment Status:** Ready  
**Last Updated:** June 13, 2026  
**Next Step:** Choose platform & deploy
