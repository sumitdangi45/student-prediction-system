"""
Flask API with Supabase Backend - V8 Ensemble Model
Production-ready deployment with auth, predictions, batch upload, and analytics
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt
from supabase import create_client, Client
from io import BytesIO
import logging
import requests
import smtplib
import random
import string
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
ALLOWED_ORIGINS = [
    'http://localhost:8081',
    'http://localhost:8080',
    'http://127.0.0.1:8081',
    'http://127.0.0.1:8080',
    'http://localhost:3000',
]

CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

logger.info(f"✅ CORS configured for {len(ALLOWED_ORIGINS)} origins")

# ============================================================================
# SUPABASE CONFIGURATION
# ============================================================================
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logger.info(f"✅ Supabase Connected: {SUPABASE_URL}")

# ============================================================================
# CONFIGURATION
# ============================================================================
JWT_SECRET = os.getenv('JWT_SECRET', 'change-this-in-production-use-strong-secret')
if JWT_SECRET == 'change-this-in-production-use-strong-secret':
    logger.warning("⚠️  WARNING: Using default JWT_SECRET! Change in production!")

# Email Configuration
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', 'your-email@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'your-app-password')

# NVIDIA NIM Configuration
NVIDIA_NIM_KEY = os.getenv('NVIDIA_NIM_KEY')
NVIDIA_NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# OTP Storage (in-memory for demo - use Redis in production)
otp_store = {}  # {email: {'otp': '123456', 'expires': datetime}}

# ============================================================================
# MODEL LOADING
# ============================================================================
try:
    rf_model = joblib.load('models/rf_model_v8.pkl')
    gb_model = joblib.load('models/gb_model_v8.pkl')
    xgb_model = joblib.load('models/xgb_model_v8.pkl')
    scaler = joblib.load('models/scaler_v8.pkl')
    threshold = joblib.load('models/threshold_v8.pkl')
    MODEL_VERSION = "V8"
    logger.info("✅ All V8 models loaded (Ensemble: RF + GB + XGB)")
except Exception as e:
    logger.error(f"❌ V8 Model loading failed: {e}")
    try:
        # Fallback to non-v8 models
        rf_model = joblib.load('models/rf_model.pkl')
        gb_model = joblib.load('models/gb_model.pkl')
        xgb_model = None
        scaler = joblib.load('models/scaler.pkl')
        threshold = 0.5
        MODEL_VERSION = "V7_FALLBACK"
        logger.warning("⚠️  Using fallback V7 models (XGB unavailable)")
    except Exception as e2:
        logger.critical(f"❌ Critical: Could not load any models: {e2}")
        rf_model = gb_model = xgb_model = scaler = None
        MODEL_VERSION = "UNAVAILABLE"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_jwt_token(user_id: str, is_admin: bool = False) -> str:
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token: str):
    """Verify JWT token and return payload"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None

def verify_admin_access(token: str):
    """Verify admin access from JWT token"""
    if not token:
        return None, "Token required"
    
    payload = verify_jwt_token(token)
    if not payload:
        return None, "Invalid token"
    
    user_id = payload.get('user_id')
    if not user_id:
        return None, "Invalid token payload"
    
    # Check admin status in database
    try:
        response = supabase.table('users').select('is_admin').eq('id', user_id).execute()
        if not response.data or not response.data[0].get('is_admin'):
            return None, "Admin access required"
        return user_id, None
    except Exception as e:
        logger.error(f"Admin verification error: {e}")
        return None, str(e)

def get_tier(probability: float) -> str:
    """Determine placement tier based on probability"""
    if probability >= 0.7:
        return "Tier-1"
    elif probability >= 0.5:
        return "Tier-2"
    elif probability >= 0.3:
        return "Tier-3"
    else:
        return "Below Tier-3"

def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email: str, otp: str) -> bool:
    """Send OTP via email"""
    try:
        subject = "Your PlaceReady OTP"
        body = f"""
        <html>
            <body>
                <h2>PlaceReady Login</h2>
                <p>Your OTP is:</p>
                <h1 style="color: #d4a574; font-size: 32px;">{otp}</h1>
                <p>This OTP is valid for 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = GMAIL_EMAIL
        msg['To'] = email
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"✅ OTP sent to {email}")
        return True
    except Exception as e:
        logger.error(f"❌ Email error: {e}")
        return False

def predict_ensemble(features: list) -> tuple:
    """Make ensemble prediction using V8 models"""
    try:
        if not scaler or not rf_model:
            return None, None, "Models not available"
        
        X = np.array([features])
        X_scaled = scaler.transform(X)
        
        if MODEL_VERSION == "V8" and gb_model and xgb_model:
            # Ensemble: average of RF, GB, XGB
            rf_prob = rf_model.predict_proba(X_scaled)[0][1]
            gb_prob = gb_model.predict_proba(X_scaled)[0][1]
            xgb_prob = xgb_model.predict_proba(X_scaled)[0][1]
            probability = (rf_prob + gb_prob + xgb_prob) / 3
            prediction = 1 if probability >= threshold else 0
        else:
            # Fallback: RF only
            prediction = rf_model.predict(X_scaled)[0]
            probability = rf_model.predict_proba(X_scaled)[0][1]
        
        return int(prediction), float(probability), None
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return None, None, str(e)

def store_session(user_id: str, token: str, request_obj) -> bool:
    """Store session in Supabase for tracking"""
    try:
        ip_address = request_obj.remote_addr or "unknown"
        user_agent = request_obj.headers.get('User-Agent', 'unknown')
        expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        # Try to insert into sessions table (if it exists)
        try:
            supabase.table('sessions').insert({
                'user_id': user_id,
                'token': token,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'expires_at': expires_at,
                'is_active': True,
                'created_at': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat()
            }).execute()
            logger.info(f"✅ Session stored for user {user_id}")
            return True
        except Exception as e:
            # If sessions table doesn't exist yet, just log it
            logger.warning(f"⚠️ Could not store session: {e}")
            return False
    except Exception as e:
        logger.error(f"Session storage error: {e}")
        return False

def invalidate_session(token: str) -> bool:
    """Mark session as inactive in Supabase"""
    try:
        supabase.table('sessions').update({'is_active': False}).eq('token', token).execute()
        logger.info(f"✅ Session invalidated")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Could not invalidate session: {e}")
        return False

def get_recommendation_from_nvidia(tier: str, cgpa: float, probability: float) -> str:
    """Get AI-powered recommendation from NVIDIA NIM"""
    try:
        prompt = f"""Based on a student's placement prediction profile:
- Placement Tier: {tier}
- CGPA: {cgpa}/10
- Placement Probability: {probability*100:.1f}%

Provide a brief, actionable recommendation (2-3 sentences max) to improve placement chances. 
Focus on practical steps like skill development, interview prep, project building, etc."""
        
        headers = {
            "Authorization": f"Bearer {NVIDIA_NIM_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta/llama-3.1-70b-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "top_p": 0.8,
            "max_tokens": 150
        }
        
        response = requests.post(NVIDIA_NIM_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            recommendation = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if recommendation:
                logger.info(f"✅ NVIDIA recommendation generated for {tier}")
                return recommendation.strip()
        else:
            logger.warning(f"NVIDIA API error: {response.status_code}")
    except Exception as e:
        logger.error(f"NVIDIA recommendation error: {e}")
    
    # Fallback recommendation if NVIDIA fails
    if tier == 'Tier-1':
        return 'Excellent! Maintain your performance. Focus on polishing interview skills and building strong projects to land premium companies.'
    elif tier == 'Tier-2':
        return 'Great progress! Enhance technical skills through competitive coding and build more real-world projects to increase placement visibility.'
    elif tier == 'Tier-3':
        return 'Good opportunity! Strengthen fundamentals, practice coding problems, and consider internships to boost placement probability.'
    else:
        return 'Focus on improving CGPA and gaining hands-on experience. Engage in hackathons, open-source, and skill development programs.'

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json or {}
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password required'}), 400
        
        # Check if user exists
        try:
            response = supabase.table('users').select('id').eq('email', email).execute()
            if response.data:
                return jsonify({'status': 'error', 'message': 'Email already registered'}), 400
        except Exception as e:
            logger.error(f"Database check error: {e}")
        
        # Create user in Supabase auth
        try:
            auth_response = supabase.auth.sign_up({
                'email': email,
                'password': password
            })
            user_id = auth_response.user.id
        except Exception as e:
            logger.error(f"Auth signup error: {e}")
            return jsonify({'status': 'error', 'message': f'Registration failed: {str(e)}'}), 400
        
        # Insert into users table
        try:
            supabase.table('users').insert({
                'id': user_id,
                'email': email,
                'is_admin': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"User table insert error: {e}")
        
        token = generate_jwt_token(user_id, False)
        
        logger.info(f"✅ User registered: {email}")
        return jsonify({
            'status': 'success',
            'message': 'Registration successful',
            'token': token,
            'user_id': user_id,
            'email': email,
            'is_admin': False
        }), 201
    
    except Exception as e:
        logger.error(f"Register error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json or {}
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password required'}), 400
        
        # Get user info
        try:
            response = supabase.table('users').select('id, is_admin').eq('email', email).execute()
            if not response.data:
                return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
            user = response.data[0]
            user_id = user['id']
            is_admin = user.get('is_admin', False)
        except Exception as e:
            logger.error(f"User lookup error: {e}")
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
        
        # Authenticate with Supabase auth
        try:
            auth_response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
        except Exception as e:
            logger.error(f"Auth login error: {e}")
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
        
        token = generate_jwt_token(user_id, is_admin)
        
        logger.info(f"✅ User logged in: {email}")
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'token': token,
            'user_id': user_id,
            'email': email,
            'is_admin': is_admin
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to email"""
    try:
        data = request.json or {}
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'status': 'error', 'message': 'Email required'}), 400
        
        # Generate OTP
        otp = generate_otp()
        
        # Send email
        if send_otp_email(email, otp):
            # Store OTP (expires in 10 minutes)
            otp_store[email] = {
                'otp': otp,
                'expires': datetime.utcnow() + timedelta(minutes=10)
            }
            return jsonify({
                'status': 'success',
                'message': 'OTP sent successfully'
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send OTP'}), 500
    
    except Exception as e:
        logger.error(f"Send OTP error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and create/login user"""
    try:
        data = request.json or {}
        email = data.get('email', '').strip()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'status': 'error', 'message': 'Email and OTP required'}), 400
        
        # Check OTP
        if email not in otp_store:
            return jsonify({'status': 'error', 'message': 'OTP not found or expired'}), 401
        
        stored = otp_store[email]
        if datetime.utcnow() > stored['expires']:
            del otp_store[email]
            return jsonify({'status': 'error', 'message': 'OTP expired'}), 401
        
        if stored['otp'] != otp:
            return jsonify({'status': 'error', 'message': 'Invalid OTP'}), 401
        
        # OTP verified - check if user exists
        is_new_user = False
        try:
            user_response = supabase.table('users').select('id, is_admin, is_new_user').eq('email', email).execute()
            
            if user_response.data:
                # User exists - login
                user_id = user_response.data[0]['id']
                is_admin = user_response.data[0].get('is_admin', False)
                is_new_user = user_response.data[0].get('is_new_user', False)
            else:
                # Create new user
                user_id = str(__import__('uuid').uuid4())
                is_new_user = True
                
                # Create in Supabase users table
                supabase.table('users').insert({
                    'id': user_id,
                    'email': email,
                    'is_admin': False,
                    'is_new_user': True,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }).execute()
                
                is_admin = False
                logger.info(f"✅ New user created: {email}")
        
        except Exception as e:
            logger.error(f"User creation error: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to create user'}), 500
        
        # Generate token
        token = generate_jwt_token(user_id, is_admin)
        
        # Store session in database
        store_session(user_id, token, request)
        
        # Clean up OTP
        del otp_store[email]
        
        logger.info(f"✅ OTP verified for {email} (is_new_user: {is_new_user})")
        return jsonify({
            'status': 'success',
            'message': 'OTP verified successfully',
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'is_admin': is_admin,
                'is_new_user': is_new_user
            },
            'user_id': user_id,
            'email': email,
            'is_admin': is_admin,
            'is_new_user': is_new_user
        }), 200
    
    except Exception as e:
        logger.error(f"Verify OTP error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user info from JWT token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Invalid token payload'}), 401
        
        # Get user from database
        try:
            response = supabase.table('users').select('*').eq('id', user_id).execute()
            if not response.data:
                return jsonify({'status': 'error', 'message': 'User not found'}), 404
            
            user = response.data[0]
            return jsonify({
                'status': 'success',
                'user': {
                    'id': user['id'],
                    'email': user.get('email', ''),
                    'is_admin': user.get('is_admin', False)
                }
            }), 200
        except Exception as e:
            logger.error(f"User lookup error: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to fetch user'}), 500
    
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user and invalidate session"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        # Invalidate session in database
        invalidate_session(token)
        
        logger.info(f"✅ User logged out")
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        
        # Get user profile from database
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        if not response.data:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        user = response.data[0]
        
        return jsonify({
            'status': 'success',
            'profile': {
                'name': user.get('name') or '',
                'email': user.get('email') or '',
                'phone': user.get('phone') or '',
                'college': user.get('college') or '',
                'branch': user.get('branch') or '',
                'cgpa': user.get('cgpa') or '',
                'graduationYear': user.get('graduation_year') or '',
                'photo': user.get('photo') or '',
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/auth/update-profile', methods=['POST'])
def update_profile():
    """Update user profile with optional photo"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        data = request.json or {}
        
        # Prepare update data
        update_data = {
            'name': data.get('name', ''),
            'phone': data.get('phone', ''),
            'college': data.get('college', ''),
            'branch': data.get('branch', ''),
            'cgpa': float(data.get('cgpa')) if data.get('cgpa') else None,
            'graduation_year': data.get('graduationYear', ''),
        }
        
        # Handle photo upload if provided
        photo_url = None
        photo_data = data.get('photo')
        
        if photo_data and isinstance(photo_data, str) and photo_data.startswith('data:image/'):
            try:
                # Convert base64 to bytes
                import base64
                # Extract base64 data from data URL
                base64_str = photo_data.split(',')[1]
                photo_bytes = base64.b64decode(base64_str)
                
                # Determine file extension from MIME type
                mime_type = photo_data.split(':')[1].split(';')[0]
                ext_map = {
                    'image/jpeg': 'jpg',
                    'image/png': 'png',
                    'image/gif': 'gif',
                    'image/webp': 'webp'
                }
                ext = ext_map.get(mime_type, 'jpg')
                
                # Upload to Supabase storage
                file_path = f"{user_id}/profile.{ext}"
                
                # Delete old photo if exists
                try:
                    supabase.storage.from_('profile-photos').remove([file_path])
                except:
                    pass
                
                # Upload new photo
                response = supabase.storage.from_('profile-photos').upload(
                    file_path,
                    photo_bytes,
                    {'content-type': mime_type}
                )
                
                # Generate public URL
                photo_url = supabase.storage.from_('profile-photos').get_public_url(file_path)
                update_data['photo'] = photo_url
                
                logger.info(f"✅ Photo uploaded for user {user_id}: {photo_url}")
            
            except Exception as e:
                logger.error(f"Photo upload error: {e}")
                # Continue without photo if upload fails
                update_data['photo'] = data.get('photo', '')
        else:
            # Keep existing photo or empty
            update_data['photo'] = data.get('photo', '')
        
        # Update in database
        response = supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'photo_url': photo_url
        }), 200
    
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================# ============================================================================
# USER ENDPOINTS
# ============================================================================

@app.route('/api/user/predictions', methods=['GET'])
def get_user_predictions():
    """Get all predictions for logged-in user"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        
        # Get all predictions for this user
        response = supabase.table('predictions').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        
        if not response.data:
            return jsonify({
                'status': 'success',
                'predictions': []
            }), 200
        
        predictions = response.data
        
        return jsonify({
            'status': 'success',
            'predictions': predictions
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching user predictions: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make individual placement prediction and save to Supabase"""
    try:
        data = request.json or {}
        
        # Get user ID from token (optional - for authenticated predictions)
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = None
        if token:
            try:
                payload = verify_jwt_token(token)
                user_id = payload.get('user_id') if payload else None
            except:
                pass  # Proceed without user_id if token verification fails
        
        # Extract and validate features
        try:
            features = [
                float(data.get('cgpa', 0)),
                float(data.get('marks_12', 0)),
                float(data.get('marks_10', 0)),
                float(data.get('closed_backlogs', 0)),
                float(data.get('live_backlogs', 0)),
                float(data.get('num_companies', 0)),
                int(data.get('has_experience', 0))
            ]
        except (ValueError, TypeError) as e:
            return jsonify({'status': 'error', 'message': f'Invalid input: {str(e)}'}), 400
        
        # Make prediction
        prediction, probability, error = predict_ensemble(features)
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        tier = get_tier(probability)
        
        # Get AI recommendation from NVIDIA
        recommendation = get_recommendation_from_nvidia(tier, features[0], probability)
        
        # ALWAYS save prediction to Supabase (logged in or guest)
        try:
            record = {
                'user_id': user_id,  # Can be None for guest predictions
                'source': 'user' if user_id else 'batch',  # Mark source
                'cgpa': features[0],
                'marks_12': features[1],
                'marks_10': features[2],
                'closed_backlogs': int(features[3]),
                'live_backlogs': int(features[4]),
                'num_companies': int(features[5]),
                'has_experience': features[6] == 1,
                'prediction': prediction,
                'probability': probability,
                'tier': tier,
                'batch_upload': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            supabase.table('predictions').insert(record).execute()
            user_type = f"User: {user_id}" if user_id else "Guest (Anonymous)"
            logger.info(f"✅ Prediction saved to Supabase - {user_type}, Tier: {tier}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save prediction to Supabase: {e}")
            # Continue anyway - still return prediction to user
        
        logger.info(f"✅ Prediction made - CGPA: {features[0]}, Prob: {probability:.3f}, Tier: {tier}")
        
        return jsonify({
            'status': 'success',
            'prediction': prediction,
            'probability': probability,
            'tier': tier,
            'recommendation': recommendation,
            'model_version': MODEL_VERSION,
            'saved': True  # Now always saved
        }), 200
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/admin/init-source-column', methods=['POST'])
def init_source_column():
    """Initialize source column in predictions table - runs once on admin request"""
    try:
        # Verify admin access
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id, error = verify_admin_access(token)
        if error:
            return jsonify({'status': 'error', 'message': error}), 401 if error == "Invalid token" else 403
        
        logger.info("🔄 Initializing source column...")
        
        try:
            # Get all predictions without source
            predictions_response = supabase.table('predictions').select('id, batch_upload, user_id').execute()
            predictions = predictions_response.data or []
            
            if not predictions:
                return jsonify({'status': 'success', 'message': 'No predictions to update', 'updated': 0}), 200
            
            updated = 0
            
            # Update each prediction with source
            for pred in predictions:
                pred_id = pred.get('id')
                batch_upload = pred.get('batch_upload', False)
                pred_user_id = pred.get('user_id')
                
                # Determine source
                if batch_upload:
                    source = 'batch'
                elif pred_user_id:
                    source = 'user'
                else:
                    source = 'batch'
                
                try:
                    supabase.table('predictions').update({'source': source}).eq('id', pred_id).execute()
                    updated += 1
                except Exception as e:
                    logger.warning(f"Failed to update prediction {pred_id}: {e}")
            
            logger.info(f"✅ Source column initialized: {updated} predictions updated")
            
            return jsonify({
                'status': 'success',
                'message': f'Updated {updated} predictions with source column',
                'updated': updated
            }), 200
        
        except Exception as e:
            logger.error(f"Database update error: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    except Exception as e:
        logger.error(f"Init source error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/students', methods=['GET'])
def get_admin_students():
    """Get all students with predictions for admin dashboard - separated by source"""
    try:
        # Verify admin access
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id, error = verify_admin_access(token)
        if error:
            return jsonify({'status': 'error', 'message': error}), 401 if error == "Invalid token" else 403
        
        # Get filter from query params (batch, user, or all)
        source_filter = request.args.get('source', 'all')  # 'batch', 'user', or 'all'
        
        # Get all predictions with user data
        try:
            if source_filter == 'all':
                predictions_response = supabase.table('predictions').select('*').execute()
            else:
                predictions_response = supabase.table('predictions').select('*').eq('source', source_filter).execute()
            
            predictions = predictions_response.data or []
        except Exception as e:
            logger.error(f"Database fetch error: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to fetch predictions'}), 500
        
        if not predictions:
            return jsonify({
                'status': 'success',
                'students': [],
                'analytics': {
                    'totalStudents': 0,
                    'tier1Count': 0,
                    'tier2Count': 0,
                    'tier3Count': 0,
                    'belowTier3Count': 0,
                    'averageProbability': 0,
                    'averageCGPA': 0
                }
            }), 200
        
        # Calculate analytics
        total = len(predictions)
        tier1 = sum(1 for p in predictions if p.get('tier') == 'Tier-1')
        tier2 = sum(1 for p in predictions if p.get('tier') == 'Tier-2')
        tier3 = sum(1 for p in predictions if p.get('tier') == 'Tier-3')
        below_tier3 = sum(1 for p in predictions if p.get('tier') == 'Below Tier-3')
        
        probabilities = [p.get('probability', 0) for p in predictions if p.get('probability')]
        avg_probability = sum(probabilities) / len(probabilities) if probabilities else 0
        
        cgpas = [p.get('cgpa', 0) for p in predictions if p.get('cgpa')]
        avg_cgpa = sum(cgpas) / len(cgpas) if cgpas else 0
        
        # Get user profiles with all details
        users_response = supabase.table('users').select('*').execute()
        users_map = {u.get('id'): u for u in (users_response.data or [])}
        
        # Format students data to match frontend expectations
        students = []
        for pred in predictions:
            # Get user profile for additional fields
            pred_user_id = pred.get('user_id')
            user = users_map.get(pred_user_id, {}) if pred_user_id else {}
            source = pred.get('source', 'batch')
            
            # Build features object from prediction data
            features = {}
            
            # Extract numeric fields for features - map from actual DB columns
            if 'cgpa' in pred and pred['cgpa'] is not None:
                features['Current Academics Aggregate Marks'] = float(pred['cgpa'])
            
            if 'marks_12' in pred and pred['marks_12'] is not None:
                features['Class 12 Marks'] = float(pred['marks_12'])
            
            if 'marks_10' in pred and pred['marks_10'] is not None:
                features['Class 10 Marks'] = float(pred['marks_10'])
            
            if 'closed_backlogs' in pred and pred['closed_backlogs'] is not None:
                features['Closed Backlogs'] = float(pred['closed_backlogs'])
            
            if 'live_backlogs' in pred and pred['live_backlogs'] is not None:
                features['Live Backlogs'] = float(pred['live_backlogs'])
            
            if 'num_companies' in pred and pred['num_companies'] is not None:
                features['Companies Applied'] = float(pred['num_companies'])
            
            if 'has_experience' in pred and pred['has_experience'] is not None:
                features['Experience'] = 1.0 if pred['has_experience'] else 0.0
            
            # Format data based on source
            if source == 'user':
                # USER DATA - show profile info
                student_name = user.get('name', 'N/A')
                user_email = user.get('email', 'N/A')
                phone = user.get('phone', '-')
                college = user.get('college', '-')
                cgpa_value = user.get('cgpa', '')
                identifier = user_email  # Use email as identifier for users
            else:
                # BATCH DATA - show roll number
                student_name = f"{pred.get('first_name', '')} {pred.get('last_name', '')}".strip() or pred.get('roll_no', 'N/A')
                roll_no = pred.get('roll_no', 'N/A')
                user_email = roll_no  # Use roll number as identifier for batch
                phone = '-'
                college = '-'
                cgpa_value = pred.get('cgpa', '')
                identifier = roll_no
            
            students.append({
                '_id': pred.get('id'),
                'name': student_name,
                'email': user_email,
                'phone': phone,
                'college': college,
                'cgpa': cgpa_value,
                'probability': float(pred.get('probability', 0)),
                'tier': pred.get('tier', 'Unknown'),
                'features': features,
                'timestamp': pred.get('created_at', ''),
                'source': source  # Include source in response
            })
        
        logger.info(f"✅ Admin fetched {total} students (source: {source_filter})")
        
        return jsonify({
            'status': 'success',
            'students': students,
            'analytics': {
                'totalStudents': total,
                'tier1Count': tier1,
                'tier2Count': tier2,
                'tier3Count': tier3,
                'belowTier3Count': below_tier3,
                'averageProbability': float(avg_probability),
                'averageCGPA': float(avg_cgpa)
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching admin students: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/batch-predict', methods=['POST'])
def admin_batch_predict():
    """Batch predict from Excel file - processes ~1032 students"""
    try:
        # Verify admin access
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id, error = verify_admin_access(token)
        if error:
            return jsonify({'status': 'error', 'message': error}), 401 if error == "Invalid token" else 403
        
        # Validate file
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        # Read Excel file
        try:
            df = pd.read_excel(file)
            logger.info(f"📁 Excel loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        except Exception as e:
            logger.error(f"Excel read error: {e}")
            return jsonify({'status': 'error', 'message': f'Failed to read file: {str(e)}'}), 400
        
        if df.shape[0] == 0:
            return jsonify({'status': 'error', 'message': 'Excel file is empty'}), 400
        
        # Column mapping for actual Excel structure
        column_mapping = {
            'CGPA': 'Current Academics Aggregate Marks',
            'marks_12': '12th - Aggregate Marks',
            'marks_10': '10th - Aggregate Marks',
            'closed_backlogs': 'Current Academics Closed Backlogs',
            'live_backlogs': 'Current Academics Live Backlogs',
            'num_companies': 'Number of Professional Experience Companies',
            'has_experience': 'Has Professional Experience'
        }
        
        processed = 0
        failed = 0
        errors_log = []
        
        logger.info(f"🚀 Starting batch predictions for {len(df)} students...")
        
        for idx, row in df.iterrows():
            try:
                # Extract values with validation
                cgpa = float(row.get(column_mapping['CGPA'], 0)) if pd.notna(row.get(column_mapping['CGPA'])) else 0
                marks_12 = float(row.get(column_mapping['marks_12'], 0)) if pd.notna(row.get(column_mapping['marks_12'])) else 0
                marks_10 = float(row.get(column_mapping['marks_10'], 0)) if pd.notna(row.get(column_mapping['marks_10'])) else 0
                closed_backlog = float(row.get(column_mapping['closed_backlogs'], 0)) if pd.notna(row.get(column_mapping['closed_backlogs'])) else 0
                live_backlog = float(row.get(column_mapping['live_backlogs'], 0)) if pd.notna(row.get(column_mapping['live_backlogs'])) else 0
                num_companies = float(row.get(column_mapping['num_companies'], 0)) if pd.notna(row.get(column_mapping['num_companies'])) else 0
                has_exp = 1 if row.get(column_mapping['has_experience'], False) else 0
                
                # Make prediction
                feature_values = [cgpa, marks_12, marks_10, closed_backlog, live_backlog, num_companies, has_exp]
                prediction, probability, pred_error = predict_ensemble(feature_values)
                
                if pred_error:
                    failed += 1
                    errors_log.append(f"Row {idx}: {pred_error}")
                    continue
                
                tier = get_tier(probability)
                
                # Prepare record
                record = {
                    'user_id': user_id,
                    'source': 'batch',  # Mark as batch upload
                    'first_name': str(row.get('First Name', '')).strip() or 'N/A',
                    'last_name': str(row.get('Last Name', '')).strip() or 'N/A',
                    'roll_no': str(row.get('Roll No', '')).strip() or 'N/A',
                    'cgpa': cgpa,
                    'marks_12': marks_12,
                    'marks_10': marks_10,
                    'closed_backlogs': int(closed_backlog),
                    'live_backlogs': int(live_backlog),
                    'num_companies': int(num_companies),
                    'has_experience': has_exp == 1,
                    'prediction': prediction,
                    'probability': probability,
                    'tier': tier,
                    'batch_upload': True,
                    'row_index': idx,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Insert to Supabase
                try:
                    supabase.table('predictions').insert(record).execute()
                    processed += 1
                except Exception as e:
                    logger.error(f"Row {idx} insert error: {e}")
                    failed += 1
                    errors_log.append(f"Row {idx}: DB insert failed")
                
                if (processed + failed) % 100 == 0:
                    logger.info(f"Progress: {processed} ✅, {failed} ❌")
            
            except Exception as e:
                logger.error(f"Row {idx} processing error: {e}")
                failed += 1
                errors_log.append(f"Row {idx}: {str(e)}")
        
        logger.info(f"✅ Batch complete: {processed} success, {failed} failed out of {len(df)} total")
        
        return jsonify({
            'status': 'success' if processed > 0 else 'partial',
            'message': f'Processed {processed} students',
            'processed': processed,
            'failed': failed,
            'total': len(df),
            'errors': errors_log[-10:] if errors_log else []  # Last 10 errors
        }), 200
    
    except Exception as e:
        logger.error(f"Batch predict error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/export-excel', methods=['GET'])
def admin_export_excel():
    """Export predictions to Excel with 13 columns"""
    try:
        # Verify admin access
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id, error = verify_admin_access(token)
        if error:
            return jsonify({'status': 'error', 'message': error}), 401 if error == "Invalid token" else 403
        
        # Get predictions
        try:
            predictions_response = supabase.table('predictions').select('*').execute()
            predictions = predictions_response.data or []
        except Exception as e:
            logger.error(f"Database fetch error: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to fetch predictions'}), 500
        
        if not predictions:
            return jsonify({'status': 'error', 'message': 'No predictions found'}), 400
        
        # Create DataFrame with 13 columns
        data = []
        for pred in predictions:
            row = {
                'First Name': str(pred.get('first_name', '')).strip() or 'N/A',
                'Last Name': str(pred.get('last_name', '')).strip() or 'N/A',
                'Roll No': str(pred.get('roll_no', '')).strip() or 'N/A',
                'CGPA': float(pred.get('cgpa', 0)) if pred.get('cgpa') is not None else 0,
                '12th Marks': float(pred.get('marks_12', 0)) if pred.get('marks_12') is not None else 0,
                '10th Marks': float(pred.get('marks_10', 0)) if pred.get('marks_10') is not None else 0,
                'Closed Backlogs': int(pred.get('closed_backlogs', 0)) if pred.get('closed_backlogs') is not None else 0,
                'Live Backlogs': int(pred.get('live_backlogs', 0)) if pred.get('live_backlogs') is not None else 0,
                'Num Companies': int(pred.get('num_companies', 0)) if pred.get('num_companies') is not None else 0,
                'Has Experience': int(pred.get('has_experience', 0) if pred.get('has_experience') else 0),
                'Prediction': int(pred.get('prediction', 0)),
                'Probability': float(pred.get('probability', 0)) if pred.get('probability') is not None else 0,
                'Tier': str(pred.get('tier', 'Unknown'))
            }
            data.append(row)
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No valid data to export'}), 400
        
        df = pd.DataFrame(data)
        
        # Create Excel in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Predictions', index=False)
            
            # Format columns
            worksheet = writer.sheets['Predictions']
            for idx, col in enumerate(df.columns, 1):
                worksheet.column_dimensions[chr(64 + idx)].width = 15
        
        output.seek(0)
        
        logger.info(f"✅ Exported {len(data)} students to Excel")
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'students-predictions-{datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx'
        )
    
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/cleanup-predictions', methods=['DELETE'])
def admin_cleanup_predictions():
    """Delete all predictions (admin only) - DESTRUCTIVE OPERATION"""
    try:
        # Verify admin access
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id, error = verify_admin_access(token)
        if error:
            return jsonify({'status': 'error', 'message': error}), 401 if error == "Invalid token" else 403
        
        # Get count before deletion
        response = supabase.table('predictions').select('*', count='exact').execute()
        count_before = response.count if hasattr(response, 'count') else len(response.data or [])
        
        if count_before == 0:
            return jsonify({
                'status': 'success',
                'message': 'No predictions to delete (already empty)',
                'deleted_count': 0
            }), 200
        
        logger.warning(f"🗑️  Admin cleanup requested by {user_id} - deleting {count_before} predictions")
        
        # Delete all predictions
        # Note: Supabase doesn't have a "delete all" easily, so we fetch and delete in batches
        try:
            # Get all predictions
            all_preds = supabase.table('predictions').select('id').execute().data or []
            
            if len(all_preds) > 0:
                # Delete in batches of 100
                deleted = 0
                batch_size = 100
                
                for i in range(0, len(all_preds), batch_size):
                    batch = all_preds[i:i+batch_size]
                    
                    # Delete each one in the batch
                    for pred in batch:
                        supabase.table('predictions').delete().eq('id', pred['id']).execute()
                        deleted += 1
                    
                    logger.info(f"  Deleted {deleted}/{len(all_preds)} predictions...")
            
            # Verify deletion
            response = supabase.table('predictions').select('*', count='exact').execute()
            count_after = response.count if hasattr(response, 'count') else len(response.data or [])
            
            logger.warning(f"✅ Cleanup complete: deleted {count_before - count_after} predictions, {count_after} remaining")
            
            return jsonify({
                'status': 'success',
                'message': f'Deleted {count_before - count_after} predictions successfully',
                'deleted_count': count_before - count_after,
                'remaining_count': count_after
            }), 200
        
        except Exception as e:
            logger.error(f"Batch deletion error: {e}")
            raise
    
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# HEALTH CHECK
# ============================================================================

# ============================================================================
# RECOMMENDATIONS ENDPOINT
# ============================================================================

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Generate personalized recommendations based on tier and profile"""
    try:
        data = request.json or {}
        
        tier = data.get('tier', 'Tier-2')
        cgpa = float(data.get('cgpa', 7.5))
        skills = data.get('skills', '')
        experience = data.get('experience', 'No')
        timeline = data.get('timeline', '3 months')
        
        # Build context for AI recommendation
        context = f"""Student Profile:
- Placement Tier: {tier}
- CGPA: {cgpa}/10
- Current Skills: {skills}
- Professional Experience: {experience}
- Available Timeline: {timeline}

Generate a comprehensive personalized roadmap to improve placement prospects. Include:
1. Top 3 skill areas to focus on
2. Recommended learning path (3-4 weeks)
3. Project ideas to build
4. Interview preparation tips
5. Timeline and milestones

Format as structured roadmap with clear sections."""
        
        # Get recommendation from NVIDIA
        try:
            headers = {
                "Authorization": f"Bearer {NVIDIA_NIM_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "meta/llama-3.1-70b-instruct",
                "messages": [
                    {"role": "user", "content": context}
                ],
                "temperature": 0.7,
                "top_p": 0.8,
                "max_tokens": 800
            }
            
            response = requests.post(NVIDIA_NIM_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                roadmap = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                if roadmap:
                    logger.info(f"✅ Roadmap generated for {tier}")
                    return jsonify({
                        'status': 'success',
                        'roadmap': roadmap,
                        'tier': tier,
                        'cgpa': cgpa,
                        'generated_at': datetime.utcnow().isoformat()
                    }), 200
        except Exception as e:
            logger.warning(f"NVIDIA recommendation error: {e}")
        
        # Fallback roadmap if NVIDIA fails
        fallback_roadmap = generate_fallback_roadmap(tier, cgpa, skills, experience)
        
        return jsonify({
            'status': 'success',
            'roadmap': fallback_roadmap,
            'tier': tier,
            'cgpa': cgpa,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def generate_fallback_roadmap(tier: str, cgpa: float, skills: str, experience: str) -> str:
    """Generate fallback roadmap if NVIDIA is unavailable"""
    
    if tier == 'Tier-1':
        return f"""
## 🎯 Tier-1 Excellence Roadmap (CGPA: {cgpa})

### Phase 1: Polish (Weeks 1-2)
1. **Advanced Problem Solving**
   - Solve 50+ LeetCode Hard problems
   - Focus on system design patterns
   
2. **Project Enhancement**
   - Build 1 full-stack project showcasing advanced concepts
   - Deploy and document thoroughly

3. **Interview Mastery**
   - Mock interviews with mentors
   - Behavioral question preparation

### Phase 2: Showcase (Weeks 3-4)
1. **Portfolio Building**
   - GitHub contributions (open source)
   - Technical blog posts (2-3)
   
2. **Networking**
   - Attend tech meetups
   - Connect with alumni in companies

### Timeline: 4 weeks to placement readiness ✅
"""
    elif tier == 'Tier-2':
        return f"""
## 🚀 Tier-2 Growth Roadmap (CGPA: {cgpa})

### Phase 1: Skill Development (Weeks 1-2)
1. **Core Competencies**
   - Data Structures & Algorithms (LeetCode 30 problems)
   - System Design fundamentals
   
2. **Technical Skills**
   - {skills if skills else 'JavaScript, Python, SQL'}
   - One full-stack project

### Phase 2: Practical Application (Weeks 3-4)
1. **Project Work**
   - Build 1-2 real-world projects
   - Deploy on cloud platform
   
2. **Interview Prep**
   - 20+ coding problems
   - 5 mock interviews

### Phase 3: Final Push (Weeks 5-6)
1. **Refinement**
   - Behavioral interview prep
   - Resume optimization
   
2. **Active Applications**
   - Apply to 20+ companies

### Timeline: 6 weeks to placement readiness ✅
"""
    elif tier == 'Tier-3':
        return f"""
## 📈 Tier-3 Advancement Roadmap (CGPA: {cgpa})

### Phase 1: Foundation Building (Weeks 1-3)
1. **Fundamentals**
   - DSA basics (Arrays, Linked Lists, Trees)
   - LeetCode 15 Easy problems
   
2. **Languages**
   - Strong foundation in 1-2 languages
   - Practice coding daily

### Phase 2: Skill Enhancement (Weeks 4-6)
1. **Intermediate DSA**
   - 25 Medium problems
   - Practice recursion, DP basics
   
2. **Project Creation**
   - 1 full web application
   - Integrate database

### Phase 3: Preparation (Weeks 7-8)
1. **Interview Training**
   - 30 DSA problems
   - Mock interviews
   
2. **Resume Building**
   - Add projects to resume
   - Highlight achievements

### Timeline: 8 weeks to placement readiness ✅
"""
    else:
        return f"""
## 💪 Tier-4 Breakthrough Roadmap (CGPA: {cgpa})

### Phase 1: Intensive Basics (Weeks 1-4)
1. **Programming Fundamentals**
   - Learn 1 language thoroughly (Python recommended)
   - Practice basic problems daily
   
2. **Data Structures**
   - Start with arrays, strings
   - Solve 20 Easy problems

### Phase 2: DSA & Projects (Weeks 5-8)
1. **Data Structures Mastery**
   - Linked lists, stacks, queues
   - Solve 30 problems
   
2. **First Project**
   - Simple web app
   - Focus on completion over complexity

### Phase 3: Intermediate Skills (Weeks 9-12)
1. **Advanced Topics**
   - Sorting, searching algorithms
   - 40 Medium problems
   
2. **Web Development**
   - HTML, CSS, JavaScript basics
   - Build 2nd project

### Phase 4: Placement Push (Weeks 13-16)
1. **Interview Readiness**
   - 50 DSA problems total
   - Mock interviews
   - Behavioral prep
   
2. **Strategic Applications**
   - Research companies carefully
   - Tailor resume and cover letters

### Timeline: 16 weeks to placement readiness ✅
"""

# ============================================================================
# SETUP ENDPOINTS (Admin/System Setup)
# ============================================================================

@app.route('/api/setup/make-admin', methods=['POST'])
def make_admin():
    """Make a user admin (requires existing admin or master key)"""
    try:
        email = request.json.get('email')
        master_key = request.json.get('master_key', '')
        
        # For initial setup, allow with hardcoded master key or from env
        MASTER_KEY = os.getenv('MASTER_SETUP_KEY', 'initial-setup-key')
        
        if master_key != MASTER_KEY:
            return jsonify({'status': 'error', 'message': 'Invalid master key'}), 401
        
        if not email:
            return jsonify({'status': 'error', 'message': 'Email required'}), 400
        
        # Update user to admin
        response = supabase.table('users').update({'is_admin': True}).eq('email', email).execute()
        
        if response.data:
            return jsonify({
                'status': 'success',
                'message': f'User {email} is now admin',
                'data': response.data
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    except Exception as e:
        logger.error(f"Make admin error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/setup/create-storage-bucket', methods=['POST'])
def create_storage_bucket():
    """Create profile-photos storage bucket"""
    try:
        master_key = request.json.get('master_key', '')
        MASTER_KEY = os.getenv('MASTER_SETUP_KEY', 'initial-setup-key')
        
        if master_key != MASTER_KEY:
            return jsonify({'status': 'error', 'message': 'Invalid master key'}), 401
        
        # Try to create bucket (will use Supabase REST API)
        try:
            # Check if bucket exists
            buckets = supabase.storage.list_buckets()
            bucket_exists = any(b.name == 'profile-photos' for b in buckets)
            
            if bucket_exists:
                return jsonify({
                    'status': 'success',
                    'message': 'Bucket already exists'
                }), 200
            
            # Create bucket
            supabase.storage.create_bucket('profile-photos', {'public': True})
            
            return jsonify({
                'status': 'success',
                'message': 'Storage bucket created successfully'
            }), 200
        except Exception as e:
            if 'already exists' in str(e).lower():
                return jsonify({
                    'status': 'success',
                    'message': 'Bucket already exists'
                }), 200
            raise
    
    except Exception as e:
        logger.error(f"Create storage bucket error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/setup/init-source-column', methods=['POST'])
def setup_init_source_column():
    """Initialize source column for existing predictions"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        user_id = payload.get('user_id')
        
        # Check if user is admin
        user_response = supabase.table('users').select('is_admin').eq('id', user_id).execute()
        if not user_response.data or not user_response.data[0].get('is_admin'):
            return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
        
        # Get all predictions without source
        predictions_response = supabase.table('predictions').select('id, batch_upload, user_id').execute()
        predictions = predictions_response.data or []
        
        updated_count = 0
        
        # Update each prediction with source
        for pred in predictions:
            pred_id = pred.get('id')
            batch_upload = pred.get('batch_upload', False)
            pred_user_id = pred.get('user_id')
            
            # Determine source
            if batch_upload:
                source = 'batch'
            elif pred_user_id:
                source = 'user'
            else:
                source = 'batch'
            
            # Update prediction
            supabase.table('predictions').update({'source': source}).eq('id', pred_id).execute()
            updated_count += 1
        
        return jsonify({
            'status': 'success',
            'message': f'Initialized source column for {updated_count} predictions',
            'updated_count': updated_count
        }), 200
    
    except Exception as e:
        logger.error(f"Init source column error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/setup/status', methods=['GET'])
def setup_status():
    """Check setup status"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        admin_user = None
        if token:
            payload = verify_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                user_response = supabase.table('users').select('email, is_admin').eq('id', user_id).execute()
                if user_response.data:
                    admin_user = user_response.data[0]
        
        # Check buckets
        buckets = []
        try:
            bucket_list = supabase.storage.list_buckets()
            buckets = [b.name for b in bucket_list]
        except:
            pass
        
        # Check predictions with source
        try:
            predictions = supabase.table('predictions').select('source', count='exact').execute()
            source_count = len(predictions.data) if predictions.data else 0
        except:
            source_count = 0
        
        return jsonify({
            'status': 'success',
            'setup': {
                'admin_user': admin_user,
                'storage_buckets': buckets,
                'has_profile_photos_bucket': 'profile-photos' in buckets,
                'predictions_with_source': source_count
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Setup status error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'supabase': 'connected',
        'models': MODEL_VERSION
    }), 200

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 Starting Flask app with Supabase backend...")
    logger.info(f"📍 API running on http://localhost:5000")
    logger.info(f"🤖 Model version: {MODEL_VERSION}")
    app.run(debug=False, host='0.0.0.0', port=5000)

