# 🚀 Deployment Guide - PlaceReady

**Version:** 1.1  
**Date:** June 13, 2026  
**Status:** Ready for Production

---

## ✅ Pre-Deployment Checklist

### Code Quality
- [x] No syntax errors
- [x] All features tested
- [x] Error handling complete
- [x] Logging implemented
- [x] Comments added
- [x] Documentation complete

### Database
- [x] Schema created
- [x] Indexes added
- [x] Backups enabled
- [x] Migrations documented
- [x] Data validated

### Security
- [x] Environment variables used
- [x] Secrets not in code
- [x] CORS configured
- [x] Input validation done
- [x] Error messages safe

### Frontend
- [x] Responsive design
- [x] Mobile tested
- [x] Performance optimized
- [x] Accessibility checked
- [x] Build successful

### Backend
- [x] All endpoints working
- [x] Models loaded
- [x] Database connected
- [x] API responses validated
- [x] Rate limiting ready

---

## 📋 Deployment Steps

### STEP 1: Backend Deployment

#### Option A: Using Railway.app (Recommended - easiest)

1. **Connect GitHub**
   - Go to railway.app
   - Connect your GitHub account
   - Select this repository

2. **Configure Environment**
   - Add environment variables in Railway dashboard
   - SUPABASE_URL
   - SUPABASE_ANON_KEY
   - SUPABASE_SERVICE_ROLE_KEY
   - GMAIL_EMAIL, GMAIL_PASSWORD
   - GROQ_API_KEY (optional)
   - MASTER_SETUP_KEY (change this!)

3. **Deploy**
   - Railway auto-deploys on git push
   - Monitor logs in dashboard
   - Check health: `/api/health`

#### Option B: Using Heroku

1. **Install Heroku CLI**
```bash
npm install -g heroku
heroku login
```

2. **Create App**
```bash
heroku create placeready
```

3. **Set Environment Variables**
```bash
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_ANON_KEY=your_key
heroku config:set SUPABASE_SERVICE_ROLE_KEY=your_key
# ... set all env vars
```

4. **Deploy**
```bash
git push heroku main
```

5. **Check**
```bash
heroku open /api/health
heroku logs --tail
```

#### Option C: Using Docker + VPS

1. **Create Dockerfile**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

2. **Build Image**
```bash
docker build -t placeready .
```

3. **Run Container**
```bash
docker run -p 5000:5000 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_ANON_KEY=your_key \
  placeready
```

4. **Push to Registry**
```bash
docker push your_registry/placeready
```

---

### STEP 2: Frontend Deployment

#### Option A: Using Netlify (Recommended)

1. **Connect Repository**
   - Go to netlify.com
   - Connect your GitHub account
   - Select this repository

2. **Configure Build**
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Environment variables:
     - VITE_API_URL=your_backend_url
     - VITE_SUPABASE_URL=your_url
     - VITE_SUPABASE_PUBLISHABLE_KEY=your_key

3. **Deploy**
   - Netlify auto-deploys on git push
   - Check build logs
   - Test site

#### Option B: Using Vercel

1. **Import Project**
   - Go to vercel.com
   - Import GitHub repository
   - Select this project

2. **Set Environment Variables**
   - VITE_API_URL
   - VITE_SUPABASE_URL
   - VITE_SUPABASE_PUBLISHABLE_KEY

3. **Deploy**
   - Vercel auto-deploys on push
   - Check deployment status

#### Option C: Using Firebase Hosting

1. **Install Firebase CLI**
```bash
npm install -g firebase-tools
firebase login
```

2. **Build Project**
```bash
npm run build
```

3. **Deploy**
```bash
firebase deploy
```

---

### STEP 3: Database Backup

1. **Enable Supabase Backups**
   - Go to Supabase dashboard
   - Project settings
   - Enable automated backups
   - Set backup frequency (daily recommended)

2. **Export Data**
```sql
-- Export users table
SELECT * FROM users;

-- Export predictions table
SELECT * FROM predictions;

-- Export sessions table
SELECT * FROM sessions;
```

---

### STEP 4: Domain Configuration

1. **Update DNS Records**
   - Point domain to hosting provider
   - Update CORS in backend
   - Update API_URL in frontend

2. **SSL Certificate**
   - Most providers auto-provide SSL
   - Verify HTTPS working
   - Check certificate validity

3. **Update Environment Variables**
   - Change localhost to production URL
   - Update API endpoints
   - Test all links

---

### STEP 5: Monitoring Setup

1. **Error Tracking (Sentry)**
```bash
pip install sentry-sdk
```

Add to app.py:
```python
import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

2. **Logging**
   - Check backend logs
   - Monitor error rates
   - Set up alerts

3. **Performance Monitoring**
   - Monitor response times
   - Track database queries
   - Check CPU usage

---

## 🔄 Post-Deployment

### Verify Everything

1. **Test Frontend**
   - Open site in browser
   - Test all pages
   - Test mobile view
   - Check links

2. **Test Backend**
```bash
curl https://your-domain.com/api/health
```

3. **Test Auth**
   - Sign up with test email
   - Verify OTP flow
   - Check token handling
   - Test logout

4. **Test Photo Upload**
   - Go to profile
   - Upload photo
   - Verify in database
   - Check in admin

5. **Test Admin**
   - Go to admin panel
   - Check predictions
   - Test filters
   - Verify photos display

### Configuration Changes

1. **Update Security**
   - Change MASTER_SETUP_KEY
   - Update CORS domains
   - Configure firewall rules
   - Set up rate limiting

2. **Update Environment**
   - Production API URLs
   - Production database
   - Production email
   - Production keys

---

## 📊 Monitoring Dashboard

### Key Metrics to Track
- API response time
- Error rate
- Database query time
- User count
- Prediction accuracy
- Storage usage

### Set Up Alerts For:
- High error rate (> 5%)
- Slow API (> 1s)
- Database down
- Storage quota exceeded
- SSL certificate expiring

---

## 🔐 Security Hardening

### Before Going Live

1. **Environment Variables**
   - Never commit secrets
   - Use .env.production
   - Rotate keys periodically
   - Use secrets manager

2. **Database**
   - Enable RLS policies
   - Add column-level security
   - Regular backups
   - Monitor access logs

3. **API**
   - Rate limiting
   - Input validation
   - HTTPS only
   - CORS whitelisting
   - API versioning

4. **Frontend**
   - No secrets in code
   - Security headers
   - CSP headers
   - HTTPS redirect

---

## 📈 Scaling Considerations

### If You Get Popular

1. **Database**
   - Use read replicas
   - Connection pooling
   - Query optimization
   - Caching layer

2. **Backend**
   - Load balancing
   - Horizontal scaling
   - Cache results
   - Async jobs

3. **Frontend**
   - CDN distribution
   - Image optimization
   - Code splitting
   - Service worker

4. **Storage**
   - S3 or similar
   - CDN for files
   - Compression
   - Cleanup old files

---

## 🆘 Rollback Plan

### If Deployment Fails

1. **Immediate**
   - Revert to previous version
   - Check error logs
   - Notify team

2. **Investigation**
   - Check backend logs
   - Check database logs
   - Check frontend console
   - Review recent changes

3. **Fix & Retry**
   - Fix the issue locally
   - Test thoroughly
   - Deploy again
   - Monitor closely

### Rollback Commands

**Backend (Heroku)**
```bash
heroku releases
heroku rollback  # Rollback to previous
```

**Frontend (Netlify)**
```bash
# Redeploy previous commit
git push origin main
```

---

## 📞 Production Support

### Emergency Contacts
- Backend: Check logs in production dashboard
- Database: Supabase status page
- Frontend: Browser console errors
- Email: Set up support email

### Documentation
- README.md - Quick start
- API_DOCUMENTATION.md - API reference
- Logs - Check service logs

---

## ✅ Launch Checklist

- [ ] Backend deployed and running
- [ ] Frontend deployed and running
- [ ] Domain configured
- [ ] SSL certificate active
- [ ] Database backups enabled
- [ ] Monitoring set up
- [ ] Error tracking configured
- [ ] Security hardened
- [ ] All tests passed
- [ ] Documentation updated
- [ ] Team notified
- [ ] Support process ready

---

## 🎉 You're Live!

Once all steps are complete, PlaceReady is in production!

### Monitor for:
- Error rates
- Response times
- User feedback
- Performance metrics
- Security issues

### Regular Maintenance:
- Weekly backup verification
- Monthly security audit
- Quarterly performance review
- Annual disaster recovery test

---

**Deployment Status:** ✅ READY  
**Next Step:** Deploy to production!
