from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from flask_session import Session
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import jwt
import hashlib
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================================================
# SESSION CONFIGURATION
# ============================================================================
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = None  # Will set after MongoDB connection
app.config['SESSION_MONGODB_DB'] = 'placeready'
app.config['SESSION_MONGODB_COLLECT'] = 'sessions'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.secret_key = os.getenv('JWT_SECRET', 'your-secret-key-change-this')

# ============================================================================
# CONFIGURATION
# ============================================================================
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', 'your-email@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'your-app-password')
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-this')

# ============================================================================
# MONGODB CONNECTION
# ============================================================================
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://<db_username>:<db_password>@cluster0.tiweseu.mongodb.net/?appName=Cluster0')

try:
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    mongo_client.admin.command('ping')
    db = mongo_client['placeready']
    
    # Initialize session with MongoDB
    app.config['SESSION_MONGODB'] = mongo_client
    Session(app)
    
    print("✅ MongoDB Connected Successfully!")
    print("✅ Session Management Initialized!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
    mongo_client = None
    db = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def send_otp_email(email, otp):
    """Send OTP via Gmail"""
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_EMAIL
        msg['To'] = email
        msg['Subject'] = 'PlaceReady - Your OTP for Login/Signup'
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>PlaceReady - OTP Verification</h2>
                <p>Your One-Time Password (OTP) is:</p>
                <h1 style="color: #007bff; letter-spacing: 5px;">{otp}</h1>
                <p>This OTP is valid for 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">PlaceReady Team</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ OTP sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Error sending OTP: {e}")
        return False

def create_jwt_token(user_id, email):
    """Create JWT token"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except:
        return None

# ============================================================================
# LOAD MODELS
# ============================================================================
print("Loading models...")

model_dir = r'c:\Users\sumit\OneDrive\Desktop\New folder (13)\models'

try:
    # Try to load V5 models first (new advanced models)
    try:
        rf_model = joblib.load(os.path.join(model_dir, 'rf_model_v5.pkl'))
        gb_model = joblib.load(os.path.join(model_dir, 'gb_model_v5.pkl'))
        xgb_model = joblib.load(os.path.join(model_dir, 'xgb_model_v5.pkl'))
        scaler = joblib.load(os.path.join(model_dir, 'scaler_v5.pkl'))
        features = joblib.load(os.path.join(model_dir, 'features_v5.pkl'))
        threshold = joblib.load(os.path.join(model_dir, 'threshold_v5.pkl'))
        print("✅ Models loaded successfully (V5 - Advanced Ensemble)!")
        MODEL_VERSION = "V5"
    except:
        # Fallback to V4 if V5 not available
        rf_model = joblib.load(os.path.join(model_dir, 'rf_model_v4.pkl'))
        scaler = joblib.load(os.path.join(model_dir, 'scaler_v4.pkl'))
        features = joblib.load(os.path.join(model_dir, 'features_v4.pkl'))
        gb_model = None
        xgb_model = None
        threshold = 0.5
        print("✅ Models loaded successfully (V4 - Enhanced Features)!")
        MODEL_VERSION = "V4"
except Exception as e:
    print(f"❌ Error loading models: {e}")
    rf_model = None
    scaler = None
    features = None

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'PlaceReady API is running!',
        'timestamp': datetime.now().isoformat()
    })

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to email"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'status': 'error', 'message': 'Email required'}), 400
        
        # Generate OTP
        otp = generate_otp()
        
        # Save OTP to MongoDB with expiry
        if db is not None:
            try:
                db.otp_requests.update_one(
                    {'email': email},
                    {
                        '$set': {
                            'email': email,
                            'otp': otp,
                            'created_at': datetime.now().isoformat(),
                            'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat(),
                            'verified': False
                        }
                    },
                    upsert=True
                )
            except Exception as e:
                print(f"❌ Error saving OTP: {e}")
        
        # Send OTP via email
        if send_otp_email(email, otp):
            return jsonify({
                'status': 'success',
                'message': 'OTP sent to email',
                'email': email
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send OTP'
            }), 500
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and create/login user"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        otp = data.get('otp', '')
        name = data.get('name', '')
        
        if not email or not otp:
            return jsonify({'status': 'error', 'message': 'Email and OTP required'}), 400
        
        # Verify OTP from MongoDB
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        otp_record = db.otp_requests.find_one({'email': email})
        
        if not otp_record:
            return jsonify({'status': 'error', 'message': 'OTP not found'}), 400
        
        # Check if OTP expired
        expires_at = datetime.fromisoformat(otp_record['expires_at'])
        if datetime.now() > expires_at:
            return jsonify({'status': 'error', 'message': 'OTP expired'}), 400
        
        # Check if OTP matches
        if otp_record['otp'] != otp:
            return jsonify({'status': 'error', 'message': 'Invalid OTP'}), 400
        
        # Mark OTP as verified
        db.otp_requests.update_one(
            {'email': email},
            {'$set': {'verified': True}}
        )
        
        # Check if user exists
        user = db.users.find_one({'email': email})
        
        if not user:
            # Create new user (signup)
            user_data = {
                'email': email,
                'name': name or email.split('@')[0],
                'role': 'user',  # Default role
                'is_admin': False,  # Default not admin
                'created_at': datetime.now().isoformat(),
                'last_login': datetime.now().isoformat(),
                'is_active': True
            }
            result = db.users.insert_one(user_data)
            user_id = result.inserted_id
            is_new_user = True
        else:
            # Update last login (login)
            db.users.update_one(
                {'email': email},
                {'$set': {'last_login': datetime.now().isoformat()}}
            )
            user_id = user['_id']
            is_new_user = False
        
        # Create JWT token
        token = create_jwt_token(user_id, email)
        
        # Store session in MongoDB
        session_id = str(uuid.uuid4())
        user_obj = user if user else {}
        session_data = {
            'session_id': session_id,
            'user_id': str(user_id),
            'email': email,
            'name': user_obj.get('name', name) if user else name,
            'role': user_obj.get('role', 'user') if user else 'user',
            'is_admin': user_obj.get('is_admin', False) if user else False,
            'is_new_user': is_new_user,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        db.sessions.insert_one(session_data)
        
        # Store in Flask session
        session['user_id'] = str(user_id)
        session['email'] = email
        session['role'] = user_obj.get('role', 'user') if user else 'user'
        session['is_admin'] = user_obj.get('is_admin', False) if user else False
        session['session_id'] = session_id
        session.permanent = True
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful' if not is_new_user else 'Signup successful',
            'token': token,
            'session_id': session_id,
            'user': {
                'id': str(user_id),
                'email': email,
                'name': user_obj.get('name', name) if user else name,
                'role': user_obj.get('role', 'user') if user else 'user',
                'is_admin': user_obj.get('is_admin', False) if user else False,
                'is_new_user': is_new_user
            }
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        session_id = request.headers.get('X-Session-ID', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 400
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 400
        
        # Add token to blacklist
        if db is not None:
            try:
                db.token_blacklist.insert_one({
                    'token': token,
                    'user_id': payload['user_id'],
                    'created_at': datetime.now().isoformat()
                })
                
                # Remove session from MongoDB
                if session_id:
                    db.sessions.delete_one({'session_id': session_id})
            except Exception as e:
                print(f"❌ Error blacklisting token: {e}")
        
        # Clear Flask session
        session.clear()
        
        return jsonify({
            'status': 'success',
            'message': 'Logout successful'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # Get user from MongoDB
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        # Update last activity
        db.sessions.update_many(
            {'user_id': str(payload['user_id'])},
            {'$set': {'last_activity': datetime.now().isoformat()}}
        )
        
        return jsonify({
            'status': 'success',
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name', ''),
                'photo': user.get('photo', ''),
                'role': user.get('role', 'user'),
                'is_admin': user.get('is_admin', False),
                'is_new_user': user.get('is_new_user', False),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login')
            }
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/sessions', methods=['GET'])
def get_user_sessions():
    """Get all active sessions for current user"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # Get user sessions from MongoDB
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        sessions = list(db.sessions.find(
            {
                'user_id': str(payload['user_id']),
                'expires_at': {'$gt': datetime.now().isoformat()}
            },
            {'_id': 0}
        ).sort('created_at', -1))
        
        return jsonify({
            'status': 'success',
            'sessions': sessions,
            'total': len(sessions)
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a specific session"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # Delete session from MongoDB
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        result = db.sessions.delete_one({
            'session_id': session_id,
            'user_id': str(payload['user_id'])
        })
        
        if result.deleted_count == 0:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Session deleted successfully'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict placement probability for a student
    Uses ensemble voting with V5 models (RF + GB + XGBoost)
    """
    
    try:
        data = request.get_json()
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = None
        
        # Try to get user_id from token if provided
        if token:
            payload = verify_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
        
        # Validate input
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        print(f"Received data: {data}")
        print(f"Expected features: {features}")
        
        # Extract features in correct order
        feature_values = []
        for feature in features:
            if feature not in data:
                print(f"Missing feature: {feature}")
                return jsonify({
                    'status': 'error',
                    'message': f'Missing feature: {feature}. Received keys: {list(data.keys())}'
                }), 400
            feature_values.append(data[feature])
        
        print(f"Feature values: {feature_values}")
        
        # Convert to numpy array
        X = np.array([feature_values])
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Make predictions with ensemble voting
        if MODEL_VERSION == "V5" and gb_model is not None and xgb_model is not None:
            # V5: Ensemble voting with 3 models
            rf_prob = rf_model.predict_proba(X_scaled)[0][1]
            gb_prob = gb_model.predict_proba(X_scaled)[0][1]
            xgb_prob = xgb_model.predict_proba(X_scaled)[0][1]
            
            # Average the probabilities
            probability = (rf_prob + gb_prob + xgb_prob) / 3
            
            # Use tuned threshold
            prediction = 1 if probability >= threshold else 0
            
            model_info = "V5 Ensemble (RF + GB + XGBoost)"
        else:
            # V4: Single Random Forest model
            prediction = rf_model.predict(X_scaled)[0]
            probability = rf_model.predict_proba(X_scaled)[0][1]
            model_info = "V4 Random Forest"
        
        # Determine tier
        if probability >= 0.7:
            tier = "Tier-1"
            recommendation = "Excellent chances! Focus on interview preparation."
        elif probability >= 0.5:
            tier = "Tier-2"
            recommendation = "Good chances! Work on technical skills."
        elif probability >= 0.3:
            tier = "Tier-3"
            recommendation = "Moderate chances. Improve CGPA and projects."
        else:
            tier = "Below Tier-3"
            recommendation = "Low chances. Focus on skill development and internships."
        
        # Save to MongoDB
        if db is not None:
            try:
                prediction_record = {
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'features': dict(zip(features, feature_values)),
                    'prediction': int(prediction),
                    'probability': float(probability),
                    'tier': tier,
                    'recommendation': recommendation,
                    'model_version': MODEL_VERSION,
                    'model_info': model_info
                }
                result = db.predictions.insert_one(prediction_record)
                print(f"✅ Prediction saved to MongoDB with ID: {result.inserted_id}")
            except Exception as e:
                print(f"❌ Error saving to MongoDB: {e}")
        
        return jsonify({
            'status': 'success',
            'prediction': int(prediction),
            'probability': float(probability),
            'percentage': f"{probability * 100:.2f}%",
            'tier': tier,
            'recommendation': recommendation,
            'features_used': features,
            'model_version': MODEL_VERSION,
            'model_info': model_info,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get personalized recommendations - tries Gemini API first, falls back to Ollama"""
    try:
        data = request.get_json()
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = None
        user_profile = None
        latest_prediction = None
        
        # Try to get user_id from token if provided
        if token:
            payload = verify_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                
                # Fetch user profile from MongoDB
                if db is not None:
                    try:
                        user_profile = db.users.find_one({'_id': user_id})
                        # Get latest prediction for this user
                        latest_prediction = db.predictions.find_one(
                            {'user_id': user_id},
                            sort=[('timestamp', -1)]
                        )
                    except Exception as e:
                        print(f"Error fetching user data: {e}")
        
        tier = data.get('tier', 'Tier-2')
        cgpa = data.get('cgpa', '7.5')
        skills = data.get('skills', 'JavaScript, React')
        experience = data.get('experience', 'No')
        timeline = data.get('timeline', '3 months')
        
        # Build detailed prompt with user data
        user_info = ""
        if user_profile:
            user_info += f"\nUser Profile Information:\n"
            user_info += f"- Name: {user_profile.get('name', 'N/A')}\n"
            user_info += f"- College: {user_profile.get('college', 'N/A')}\n"
            user_info += f"- Branch: {user_profile.get('branch', 'N/A')}\n"
            user_info += f"- Phone: {user_profile.get('phone', 'N/A')}\n"
        
        prediction_info = ""
        if latest_prediction:
            prediction_info += f"\nLatest Prediction Data:\n"
            prediction_info += f"- Probability: {latest_prediction.get('probability', 0) * 100:.2f}%\n"
            prediction_info += f"- 10th Marks: {latest_prediction.get('features', {}).get('10th_Marks', 'N/A')}\n"
            prediction_info += f"- 12th Marks: {latest_prediction.get('features', {}).get('12th_Marks', 'N/A')}\n"
            prediction_info += f"- Backlogs: {latest_prediction.get('features', {}).get('Total_Backlogs', 0)}\n"
            prediction_info += f"- Has Experience: {'Yes' if latest_prediction.get('features', {}).get('Has_Experience') else 'No'}\n"
            prediction_info += f"- Has Internship: {'Yes' if latest_prediction.get('features', {}).get('Has_Internship') else 'No'}\n"
            prediction_info += f"- Has Projects: {'Yes' if latest_prediction.get('features', {}).get('Has_Projects') else 'No'}\n"
            prediction_info += f"- Has Skills: {'Yes' if latest_prediction.get('features', {}).get('Has_Skills') else 'No'}\n"
        
        prompt = f"""You are an expert career counselor for engineering students. Generate a DETAILED, ACTIONABLE personalized placement preparation roadmap for a student with the following profile:

STUDENT PROFILE:
- Placement Tier Target: {tier}
- Current CGPA: {cgpa}/10
- Current Skills: {skills}
- Professional Experience: {experience}
- Available Timeline: {timeline}
{user_info}
{prediction_info}

Please provide a COMPREHENSIVE roadmap with:

1. **CURRENT SITUATION ANALYSIS** (Based on their data)
   - Strengths to leverage
   - Weaknesses to address
   - Realistic assessment

2. **KEY AREAS TO IMPROVE** (3-5 specific points based on their tier and data)
   - Specific technical gaps
   - Soft skills needed
   - Domain-specific improvements

3. **SKILL DEVELOPMENT PLAN** (Detailed with timelines)
   - Specific technologies and skills to learn
   - Learning resources and platforms
   - Estimated time for each skill

4. **PROJECT IDEAS** (2-3 concrete project ideas with descriptions)
   - Project complexity level
   - Technologies to use
   - How it helps placement

5. **INTERVIEW PREPARATION STRATEGY** (Detailed approach)
   - Number of problems to practice
   - Interview types to prepare for
   - Mock interview schedule
   - Resources and platforms

6. **WEEKLY ACTION PLAN** (Detailed week-by-week breakdown for their timeline)
   - Specific tasks for each week
   - Milestones to achieve
   - Progress checkpoints

7. **LEARNING RESOURCES** (Specific recommendations)
   - Courses (with links if possible)
   - Books and articles
   - Websites and communities
   - YouTube channels

8. **TIMELINE & MILESTONES** (Realistic checkpoints)
   - Month-wise goals
   - Key deliverables
   - Success metrics

9. **PERSONALIZED TIPS** (Based on their specific data)
   - Specific advice for their situation
   - Common pitfalls to avoid
   - Motivation and encouragement

Format the response in a clear, well-structured way with emojis and sections. Make it motivating, actionable, and specific to their situation. Include specific numbers, dates, and concrete steps."""

        # Try Gemini API first
        print(f"[Recommendations] Trying Gemini API for tier: {tier}, CGPA: {cgpa}")
        try:
            from google import genai
            
            api_key = "AIzaSyDKedMOM17ILtRD3SmRIW9s9YEluSg6sDo"
            client = genai.Client(api_key=api_key)
            
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            print(f"[Gemini API] ✅ Success! Generated recommendations")
            
            # Save to MongoDB
            if db is not None:
                try:
                    recommendation_record = {
                        'user_id': user_id,
                        'timestamp': datetime.now().isoformat(),
                        'tier': tier,
                        'cgpa': cgpa,
                        'skills': skills,
                        'experience': experience,
                        'timeline': timeline,
                        'content': response.text,
                        'source': 'gemini-api'
                    }
                    db.recommendations.insert_one(recommendation_record)
                    print(f"✅ Recommendation saved to MongoDB")
                except Exception as e:
                    print(f"❌ Error saving to MongoDB: {e}")
            
            return jsonify({
                'status': 'success',
                'content': response.text,
                'tier': tier,
                'cgpa': cgpa,
                'timestamp': datetime.now().isoformat(),
                'source': 'gemini-api'
            })
        
        except Exception as gemini_error:
            print(f"[Gemini API] ❌ Failed: {str(gemini_error)[:100]}")
            
            # Fallback to Ollama
            print(f"[Ollama] Trying Ollama as fallback...")
            try:
                import requests
                
                # Simplified prompt for Ollama
                ollama_prompt = f"""Create a detailed placement preparation roadmap for a {tier} student with CGPA {cgpa}.

Key areas: Focus on {skills}. Timeline: {timeline}. Experience: {experience}.

Provide:
1. Current Situation Analysis
2. Top 5 areas to improve
3. Detailed skills to learn
4. 3 project ideas with descriptions
5. Interview preparation strategy
6. Week-by-week action plan
7. Learning resources
8. Milestones and checkpoints
9. Personalized advice

Be specific, detailed, and actionable. Include timelines and concrete steps."""
                
                ollama_response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': 'mistral',
                        'prompt': ollama_prompt,
                        'stream': False
                    },
                    timeout=600
                )
                
                if ollama_response.status_code == 200:
                    ollama_data = ollama_response.json()
                    print(f"[Ollama] ✅ Success! Generated recommendations")
                    
                    # Save to MongoDB
                    if db is not None:
                        try:
                            recommendation_record = {
                                'user_id': user_id,
                                'timestamp': datetime.now().isoformat(),
                                'tier': tier,
                                'cgpa': cgpa,
                                'skills': skills,
                                'experience': experience,
                                'timeline': timeline,
                                'content': ollama_data.get('response', ''),
                                'source': 'ollama'
                            }
                            db.recommendations.insert_one(recommendation_record)
                            print(f"✅ Recommendation saved to MongoDB")
                        except Exception as e:
                            print(f"❌ Error saving to MongoDB: {e}")
                    
                    return jsonify({
                        'status': 'success',
                        'content': ollama_data.get('response', ''),
                        'tier': tier,
                        'cgpa': cgpa,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'ollama'
                    })
                else:
                    raise Exception(f"Ollama returned status {ollama_response.status_code}")
            
            except Exception as ollama_error:
                print(f"[Ollama] ❌ Failed: {str(ollama_error)[:100]}")
                
                # If both fail, return error
                return jsonify({
                    'status': 'error',
                    'message': f'Both Gemini API and Ollama failed. Gemini: {str(gemini_error)[:100]}. Ollama: {str(ollama_error)[:100]}',
                    'tier': tier,
                    'cgpa': cgpa,
                    'timestamp': datetime.now().isoformat()
                }), 500
    
    except Exception as e:
        print(f"[Recommendations] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def generate_personalized_roadmap(tier, cgpa, skills, experience, timeline):
    """Generate personalized placement preparation roadmap"""
    
    roadmap = f"""
🎯 PERSONALIZED PLACEMENT PREPARATION ROADMAP
{'='*60}

📊 YOUR PROFILE
• Placement Tier: {tier}
• Current CGPA: {cgpa}
• Current Skills: {skills}
• Professional Experience: {experience}
• Available Timeline: {timeline}

{'='*60}

"""
    
    # Tier-specific recommendations
    if tier == "Tier-1":
        roadmap += """
🌟 KEY AREAS TO IMPROVE (Tier-1 Companies)
1. Advanced Problem Solving - Master complex algorithms and data structures
2. System Design - Learn to design scalable systems
3. Behavioral Excellence - Perfect your communication and leadership skills
4. Competitive Programming - Maintain high rating on coding platforms
5. Open Source Contribution - Build credibility through public projects

📚 SKILL DEVELOPMENT PLAN
• Advanced DSA: Segment Trees, Fenwick Trees, Advanced DP
• System Design: Microservices, Distributed Systems, Databases
• Cloud Platforms: AWS, GCP, or Azure certifications
• DevOps: Docker, Kubernetes, CI/CD pipelines
• Leadership: Team management and mentoring skills

💡 PROJECT IDEAS
1. Build a distributed chat application with real-time messaging
2. Create a recommendation engine using machine learning
3. Develop a microservices-based e-commerce platform

🎤 INTERVIEW PREPARATION
• Practice 50+ LeetCode hard problems
• Study 10+ system design case studies
• Prepare behavioral stories using STAR method
• Mock interviews with experienced professionals
• Focus on explaining your thought process clearly

📅 WEEKLY ACTION PLAN
Week 1-2: Review advanced DSA concepts and solve 10 hard problems
Week 3-4: Study system design patterns and complete 2 design case studies
Week 5-6: Build your portfolio project and contribute to open source
Week 7-8: Mock interviews and behavioral preparation
Week 9-10: Final revision and confidence building

📖 RESOURCES
• Courses: System Design Interview by Educative, Advanced DSA on Udemy
• Books: Designing Data-Intensive Applications, Cracking the Coding Interview
• Websites: LeetCode, HackerRank, InterviewBit, Educative
• Communities: Dev.to, GitHub, Stack Overflow

🏁 TIMELINE & MILESTONES
"""
        if timeline == "1 month":
            roadmap += """
• Week 1: Complete 15 hard DSA problems
• Week 2: Study 3 system design patterns
• Week 3: Build 1 portfolio project
• Week 4: 5 mock interviews and final prep
"""
        elif timeline == "3 months":
            roadmap += """
• Month 1: Master advanced DSA and system design basics
• Month 2: Build 2 portfolio projects and contribute to open source
• Month 3: Mock interviews, behavioral prep, and final revision
"""
        else:
            roadmap += """
• Month 1-2: Deep dive into advanced topics and system design
• Month 3-4: Build multiple portfolio projects
• Month 5-6: Mock interviews and behavioral preparation
• Month 7-12: Continuous learning and interview practice
"""
    
    elif tier == "Tier-2":
        roadmap += """
🎯 KEY AREAS TO IMPROVE (Tier-2 Companies)
1. Core DSA Concepts - Master arrays, strings, trees, graphs
2. Web Development - Full-stack development skills
3. Database Design - SQL and NoSQL fundamentals
4. Problem-Solving - Consistent practice on coding problems
5. Project Portfolio - 2-3 solid projects showcasing your skills

📚 SKILL DEVELOPMENT PLAN
• Core DSA: Arrays, Strings, Trees, Graphs, Dynamic Programming
• Web Stack: React/Vue, Node.js, Express, MongoDB/PostgreSQL
• Databases: SQL optimization, indexing, basic NoSQL
• APIs: RESTful API design and implementation
• Version Control: Git and GitHub proficiency

💡 PROJECT IDEAS
1. Build a full-stack task management application
2. Create a social media feed with real-time updates
3. Develop a weather application with advanced features

🎤 INTERVIEW PREPARATION
• Practice 30+ LeetCode medium problems
• Study 5+ system design basics
• Prepare 5-6 behavioral stories
• Mock interviews with peers
• Focus on clear communication

📅 WEEKLY ACTION PLAN
Week 1-2: Strengthen DSA fundamentals with 8 medium problems
Week 3-4: Build your first portfolio project
Week 5-6: Learn backend development and databases
Week 7-8: Build second project and practice interviews
Week 9-10: Mock interviews and final preparation

📖 RESOURCES
• Courses: Complete Web Development Bootcamp, DSA on Udemy
• Books: Cracking the Coding Interview, You Don't Know JS
• Websites: LeetCode, HackerRank, Codewars, Dev.to
• Communities: GitHub, Stack Overflow, Dev communities

🏁 TIMELINE & MILESTONES
"""
        if timeline == "1 month":
            roadmap += """
• Week 1: Complete 10 medium DSA problems
• Week 2: Build 1 portfolio project
• Week 3: Learn backend basics and practice interviews
• Week 4: 3 mock interviews and final prep
"""
        elif timeline == "3 months":
            roadmap += """
• Month 1: Master DSA fundamentals and build first project
• Month 2: Learn backend development and build second project
• Month 3: Mock interviews, behavioral prep, and final revision
"""
        else:
            roadmap += """
• Month 1-2: Master DSA and build portfolio projects
• Month 3-4: Learn backend and database design
• Month 5-6: Mock interviews and behavioral preparation
• Month 7-12: Continuous practice and skill enhancement
"""
    
    elif tier == "Tier-3":
        roadmap += """
⭐ KEY AREAS TO IMPROVE (Tier-3 Companies)
1. Basic DSA - Master fundamental data structures
2. Programming Fundamentals - Strong coding basics
3. Project Experience - Build 1-2 projects
4. Communication Skills - Clear problem explanation
5. Consistency - Regular practice and improvement

📚 SKILL DEVELOPMENT PLAN
• Basic DSA: Arrays, Strings, Linked Lists, Basic Trees
• Programming: Python/Java fundamentals and OOP
• Web Basics: HTML, CSS, JavaScript fundamentals
• Databases: Basic SQL queries and design
• Problem Solving: Logical thinking and debugging

💡 PROJECT IDEAS
1. Build a simple to-do list application
2. Create a personal portfolio website
3. Develop a basic e-commerce product listing page

🎤 INTERVIEW PREPARATION
• Practice 20+ LeetCode easy to medium problems
• Study basic system design concepts
• Prepare 3-4 behavioral stories
• Practice with friends or mentors
• Focus on explaining your approach

📅 WEEKLY ACTION PLAN
Week 1-2: Learn DSA basics and solve 6 easy problems
Week 3-4: Build your first project
Week 5-6: Strengthen coding skills with 6 more problems
Week 7-8: Build second project and practice interviews
Week 9-10: Mock interviews and confidence building

📖 RESOURCES
• Courses: Python for Everybody, Web Development Basics
• Books: Think Like a Programmer, Clean Code
• Websites: LeetCode, HackerRank, Codewars, W3Schools
• Communities: GitHub, Stack Overflow, Local meetups

🏁 TIMELINE & MILESTONES
"""
        if timeline == "1 month":
            roadmap += """
• Week 1: Learn DSA basics and solve 5 easy problems
• Week 2: Build 1 simple project
• Week 3: Practice 5 more problems
• Week 4: Mock interview and final prep
"""
        elif timeline == "3 months":
            roadmap += """
• Month 1: Master DSA basics and build first project
• Month 2: Strengthen coding skills and build second project
• Month 3: Mock interviews and final preparation
"""
        else:
            roadmap += """
• Month 1-2: Master DSA fundamentals
• Month 3-4: Build portfolio projects
• Month 5-6: Mock interviews and practice
• Month 7-12: Continuous improvement and skill building
"""
    
    else:  # Below Tier-3
        roadmap += """
💪 KEY AREAS TO IMPROVE (Below Tier-3 - Focus on Fundamentals)
1. Programming Basics - Strong foundation in coding
2. Problem Solving - Develop logical thinking
3. Project Building - Create simple but complete projects
4. Internship Experience - Gain practical experience
5. Skill Development - Learn in-demand technologies

📚 SKILL DEVELOPMENT PLAN
• Programming: Python/Java fundamentals
• Web Basics: HTML, CSS, JavaScript
• Databases: Basic SQL
• Version Control: Git basics
• Soft Skills: Communication and teamwork

💡 PROJECT IDEAS
1. Build a simple calculator or note-taking app
2. Create a personal blog or portfolio website
3. Develop a basic quiz application

🎤 INTERVIEW PREPARATION
• Practice 15+ LeetCode easy problems
• Study basic coding concepts
• Prepare 2-3 personal stories
• Practice with mentors
• Focus on fundamentals

📅 WEEKLY ACTION PLAN
Week 1-2: Learn programming basics and solve 4 easy problems
Week 3-4: Build your first simple project
Week 5-6: Practice 4 more problems
Week 7-8: Build another project and practice interviews
Week 9-10: Mock interviews and confidence building

📖 RESOURCES
• Courses: Codecademy, freeCodeCamp, Khan Academy
• Books: Python Crash Course, Eloquent JavaScript
• Websites: LeetCode, HackerRank, Codewars, Tutorialspoint
• Communities: GitHub, Stack Overflow, Local coding groups

🏁 TIMELINE & MILESTONES
"""
        if timeline == "1 month":
            roadmap += """
• Week 1: Learn basics and solve 3 easy problems
• Week 2: Build 1 simple project
• Week 3: Practice 3 more problems
• Week 4: Mock interview and final prep
"""
        elif timeline == "3 months":
            roadmap += """
• Month 1: Master programming basics and build first project
• Month 2: Strengthen skills and build second project
• Month 3: Mock interviews and final preparation
"""
        else:
            roadmap += """
• Month 1-2: Master programming fundamentals
• Month 3-4: Build portfolio projects
• Month 5-6: Internship or practice projects
• Month 7-12: Continuous learning and improvement
"""
    
    # CGPA-specific advice
    roadmap += f"""

{'='*60}
💡 PERSONALIZED ADVICE BASED ON YOUR CGPA ({cgpa})
"""
    
    if cgpa >= 8.5:
        roadmap += """
✅ Excellent CGPA! You're in a strong position.
• Focus on technical depth and advanced concepts
• Build impressive projects that showcase your skills
• Prepare for senior-level or specialized roles
• Consider internships at top companies
"""
    elif cgpa >= 7.5:
        roadmap += """
✅ Good CGPA! You have a solid foundation.
• Balance between breadth and depth of knowledge
• Build 2-3 solid projects for your portfolio
• Focus on practical skills and real-world applications
• Prepare for mid-level roles
"""
    elif cgpa >= 7.0:
        roadmap += """
⚠️ Decent CGPA. You need to compensate with skills.
• Focus on building strong projects and portfolio
• Gain practical experience through internships
• Develop specialized skills in your area of interest
• Practice coding problems consistently
"""
    else:
        roadmap += """
⚠️ Lower CGPA. Focus on skills and experience.
• Build impressive projects to showcase your abilities
• Gain internship experience to strengthen your profile
• Focus on practical skills over theoretical knowledge
• Practice coding problems and interview preparation
• Consider improving your CGPA if possible
"""
    
    # Experience-specific advice
    roadmap += f"""

{'='*60}
💼 EXPERIENCE LEVEL: {experience}
"""
    
    if experience == "Yes":
        roadmap += """
✅ Great! You have professional experience.
• Highlight your work experience in interviews
• Discuss real-world problems you've solved
• Emphasize your contributions and impact
• You're likely to get better offers
• Focus on technical depth and leadership skills
"""
    else:
        roadmap += """
⚠️ No professional experience yet.
• Prioritize getting an internship
• Build projects that simulate real-world scenarios
• Contribute to open-source projects
• Gain practical experience through freelancing
• This will significantly improve your placement chances
"""
    
    roadmap += f"""

{'='*60}
🎯 FINAL TIPS FOR SUCCESS
1. Consistency is key - Practice regularly, not just before interviews
2. Build projects - Employers want to see what you can build
3. Network - Connect with professionals and attend meetups
4. Learn continuously - Technology evolves, keep learning
5. Practice interviews - Mock interviews build confidence
6. Focus on fundamentals - Strong basics lead to success
7. Be authentic - Show your genuine interest and passion
8. Take care of yourself - Health and mental well-being matter

Good luck with your placement journey! 🚀
"""
    
    return roadmap

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """
    Predict for multiple students
    
    Expected JSON:
    {
        "students": [
            {...student1...},
            {...student2...}
        ]
    }
    """
    
    try:
        data = request.get_json()
        
        if not data or 'students' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No students data provided'
            }), 400
        
        students = data['students']
        results = []
        
        for student in students:
            try:
                # Extract features
                feature_values = []
                for feature in features:
                    if feature not in student:
                        feature_values.append(0)  # Default value
                    else:
                        feature_values.append(student[feature])
                
                # Predict
                X = np.array([feature_values])
                X_scaled = scaler.transform(X)
                probability = rf_model.predict_proba(X_scaled)[0][1]
                
                results.append({
                    'student_id': student.get('id', 'unknown'),
                    'probability': float(probability),
                    'percentage': f"{probability * 100:.2f}%"
                })
            except Exception as e:
                results.append({
                    'student_id': student.get('id', 'unknown'),
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'total': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify({
        'status': 'success',
        'model': 'Random Forest Classifier V2',
        'features': features,
        'total_features': len(features),
        'accuracy': 0.6615,
        'recall': 0.4148,
        'f1_score': 0.3587,
        'roc_auc': 0.6364,
        'training_samples': 3855,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/features', methods=['GET'])
def get_features():
    """Get required features for prediction"""
    return jsonify({
        'status': 'success',
        'features': features,
        'feature_descriptions': {
            'cgpa': 'Current CGPA (0-10)',
            '12th_marks': '12th grade marks (0-100)',
            '10th_marks': '10th grade marks (0-100)',
            'total_backlogs': 'Total backlogs (0+)',
            'has_experience': 'Has professional experience (0/1)',
            'num_companies': 'Number of companies worked (0+)',
            'has_internship': 'Has internship experience (0/1)',
            'has_skills': 'Has listed skills (0/1)',
            'has_projects': 'Has projects (0/1)',
            'has_certifications': 'Has certifications (0/1)',
            'academic_trend': 'Academic performance trend (-10 to 10)',
            'is_female': 'Gender - Female (0/1)'
        }
    })

@app.route('/api/predictions-history', methods=['GET'])
def get_predictions_history():
    """Get all predictions from MongoDB"""
    if db is None:
        return jsonify({
            'status': 'error',
            'message': 'MongoDB not connected'
        }), 500
    
    try:
        predictions = list(db.predictions.find({}, {'_id': 0}).sort('timestamp', -1).limit(100))
        return jsonify({
            'status': 'success',
            'total': len(predictions),
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/recommendations-history', methods=['GET'])
def get_recommendations_history():
    """Get all recommendations from MongoDB"""
    if db is None:
        return jsonify({
            'status': 'error',
            'message': 'MongoDB not connected'
        }), 500
    
    try:
        recommendations = list(db.recommendations.find({}, {'_id': 0, 'content': 0}).sort('timestamp', -1).limit(100))
        return jsonify({
            'status': 'success',
            'total': len(recommendations),
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # Get user from MongoDB
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        user = db.users.find_one({'_id': payload['user_id']})
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        return jsonify({
            'status': 'success',
            'profile': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name', ''),
                'phone': user.get('phone', ''),
                'college': user.get('college', ''),
                'branch': user.get('branch', ''),
                'cgpa': user.get('cgpa', ''),
                'graduationYear': user.get('graduationYear', ''),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login')
            }
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/update-profile', methods=['POST'])
def update_profile():
    """Update user profile"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Validate name
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'status': 'error', 'message': 'Name is required'}), 400
        
        # Update user in MongoDB
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        update_data = {
            'name': name,
            'phone': data.get('phone', '').strip(),
            'college': data.get('college', '').strip(),
            'branch': data.get('branch', '').strip(),
            'cgpa': data.get('cgpa', ''),
            'graduationYear': data.get('graduationYear', '').strip(),
            'photo': data.get('photo', ''),  # Store base64 photo
            'updated_at': datetime.now().isoformat()
        }
        
        result = db.users.update_one(
            {'_id': payload['user_id']},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        print(f"✅ Profile updated for user: {payload['user_id']}")
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'profile': update_data
        })
    
    except Exception as e:
        print(f"❌ Error updating profile: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/admin/students', methods=['GET'])
def get_admin_students():
    """Get all students with predictions for admin dashboard"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # Check if admin
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not user or not user.get('is_admin', False):
            return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
        
        # Get all predictions
        predictions = list(db.predictions.find({}).sort('timestamp', -1))
        
        # Calculate analytics
        total = len(predictions)
        tier1 = sum(1 for p in predictions if p.get('tier') == 'Tier-1')
        tier2 = sum(1 for p in predictions if p.get('tier') == 'Tier-2')
        tier3 = sum(1 for p in predictions if p.get('tier') == 'Tier-3')
        below_tier3 = sum(1 for p in predictions if p.get('tier') == 'Below Tier-3')
        
        avg_probability = sum(p.get('probability', 0) for p in predictions) / total if total > 0 else 0
        
        # Calculate average CGPA
        cgpas = [p.get('features', {}).get('Current Academics Aggregate Marks', 0) for p in predictions]
        avg_cgpa = sum(cgpas) / len(cgpas) if cgpas else 0
        
        # Format students data
        students = []
        for pred in predictions:
            students.append({
                '_id': str(pred.get('_id', '')),
                'name': pred.get('features', {}).get('name', 'N/A'),
                'email': pred.get('features', {}).get('email', 'N/A'),
                'probability': pred.get('probability', 0),
                'tier': pred.get('tier', 'Unknown'),
                'features': pred.get('features', {}),
                'timestamp': pred.get('timestamp', '')
            })
        
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
        })
    
    except Exception as e:
        print(f"❌ Error fetching admin students: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/batch-predict', methods=['POST'])
def admin_batch_predict():
    """Batch predict from Excel file upload"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # Check if admin
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not user or not user.get('is_admin', False):
            return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
        
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        # Read Excel file
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Failed to read file: {str(e)}'}), 400
        
        # Process predictions
        processed = 0
        failed = 0
        
        for idx, row in df.iterrows():
            try:
                # Extract features
                feature_values = []
                for feature in features:
                    if feature in row:
                        feature_values.append(float(row[feature]))
                    else:
                        feature_values.append(0)
                
                # Make prediction
                X = np.array([feature_values])
                X_scaled = scaler.transform(X)
                prediction = rf_model.predict(X_scaled)[0]
                probability = rf_model.predict_proba(X_scaled)[0][1]
                
                # Determine tier
                if probability >= 0.7:
                    tier = "Tier-1"
                elif probability >= 0.5:
                    tier = "Tier-2"
                elif probability >= 0.3:
                    tier = "Tier-3"
                else:
                    tier = "Below Tier-3"
                
                # Save to MongoDB
                prediction_record = {
                    'user_id': payload['user_id'],
                    'timestamp': datetime.now().isoformat(),
                    'features': dict(zip(features, feature_values)),
                    'prediction': int(prediction),
                    'probability': float(probability),
                    'tier': tier,
                    'batch_upload': True,
                    'row_index': idx
                }
                
                db.predictions.insert_one(prediction_record)
                processed += 1
            
            except Exception as e:
                print(f"❌ Error processing row {idx}: {str(e)}")
                failed += 1
        
        return jsonify({
            'status': 'success',
            'message': f'Processed {processed} students',
            'processed': processed,
            'failed': failed,
            'total': len(df),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Error in batch predict: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/export-excel', methods=['GET'])
def admin_export_excel():
    """Export all predictions to Excel"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        # Check if admin
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not user or not user.get('is_admin', False):
            return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
        
        # Get all predictions
        predictions = list(db.predictions.find({}).sort('timestamp', -1))
        
        # Create DataFrame
        data = []
        for pred in predictions:
            row = {
                'Timestamp': pred.get('timestamp', ''),
                'Probability': f"{pred.get('probability', 0) * 100:.2f}%",
                'Tier': pred.get('tier', ''),
                'Prediction': pred.get('prediction', 0)
            }
            
            # Add features
            features_dict = pred.get('features', {})
            for feature, value in features_dict.items():
                row[feature] = value
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Predictions', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'students-predictions-{datetime.now().strftime("%Y-%m-%d")}.xlsx'
        )
    
    except Exception as e:
        print(f"❌ Error exporting Excel: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# ADMIN MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/admin/manage-roles', methods=['POST'])
def manage_admin_roles():
    """Assign or revoke admin roles (only for current admins)"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        data = request.get_json()
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 400
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 400
        
        # Check if current user is admin
        current_user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not current_user or not current_user.get('is_admin', False):
            return jsonify({'status': 'error', 'message': 'Only admins can manage roles'}), 403
        
        # Get target user email and action
        target_email = data.get('email', '').lower().strip()
        action = data.get('action', '')  # 'grant' or 'revoke'
        
        if not target_email or action not in ['grant', 'revoke']:
            return jsonify({'status': 'error', 'message': 'Email and action (grant/revoke) required'}), 400
        
        # Find target user
        target_user = db.users.find_one({'email': target_email})
        if not target_user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        # Update admin status
        if action == 'grant':
            db.users.update_one(
                {'email': target_email},
                {'$set': {'is_admin': True, 'role': 'admin'}}
            )
            message = f'Admin role granted to {target_email}'
        else:  # revoke
            db.users.update_one(
                {'email': target_email},
                {'$set': {'is_admin': False, 'role': 'user'}}
            )
            message = f'Admin role revoked from {target_email}'
        
        return jsonify({
            'status': 'success',
            'message': message,
            'email': target_email,
            'action': action
        })
    
    except Exception as e:
        print(f"❌ Error managing roles: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/list-admins', methods=['GET'])
def list_admins():
    """Get list of all admin users (only for admins)"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token required'}), 400
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 400
        
        # Check if current user is admin
        current_user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not current_user or not current_user.get('is_admin', False):
            return jsonify({'status': 'error', 'message': 'Only admins can view admin list'}), 403
        
        # Get all admins
        admins = list(db.users.find({'is_admin': True}, {'_id': 1, 'email': 1, 'name': 1, 'created_at': 1}))
        
        return jsonify({
            'status': 'success',
            'admins': [
                {
                    'id': str(admin['_id']),
                    'email': admin['email'],
                    'name': admin.get('name', ''),
                    'created_at': admin.get('created_at', '')
                }
                for admin in admins
            ]
        })
    
    except Exception as e:
        print(f"❌ Error listing admins: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 PlaceReady API Server Starting...")
    print("=" * 80)
    print("\n📍 Server running at: http://localhost:5000")
    print("\n📚 API Endpoints:")
    print("   GET  /                    - Health check")
    print("   GET  /api/model-info      - Model information")
    print("   GET  /api/features        - Required features")
    print("   POST /api/predict         - Single prediction")
    print("   POST /api/batch-predict   - Batch predictions")
    print("\n" + "=" * 80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
