# Security Configuration - Quick Reference

## ✅ What's Configured

Your UniversityPredictor project now uses environment variables for security.

## 📁 Files Created/Modified

### 1. `.env` (NEW)
**Location:** `UniversityPredictor/.env`  
**Purpose:** Stores sensitive configuration  
**Status:** ✅ Created, ✅ In .gitignore

### 2. `settings.py` (MODIFIED)
**Location:** `UniversityPredictor/UniversityPredictor/settings.py`  
**Changes:** Now reads from .env instead of hardcoded values

## 🔐 Current Configuration

```env
SECRET_KEY=django-insecure-xoo+!af(2kl-h*vqb8vi2+1k%7h-&=@@zy-(7juu3bs^ikonlg
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=university_predictor
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432
```

## ⚠️ Before Production

**MUST DO:**
1. Generate new SECRET_KEY (visit https://djecrety.ir/)
2. Set DEBUG=False
3. Add your domain to ALLOWED_HOSTS
4. Use strong database password

## 🚀 Quick Commands

```bash
# Check configuration
python manage.py check

# Check deployment readiness
python manage.py check --deploy

# Test database connection
python manage.py migrate --dry-run
```

## 📝 To Change Settings

1. Open `UniversityPredictor/.env`
2. Edit the values
3. Restart Django server
4. Changes take effect immediately

## 🔒 Security Reminders

- ✅ .env is in .gitignore
- ✅ Never commit .env to Git
- ✅ Keep backup of .env in secure location
- ✅ Use different .env for dev/staging/production

---

*Security configured: January 21, 2026*
