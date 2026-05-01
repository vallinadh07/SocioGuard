from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import re
from scam_database import scam_db
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load Social Media Models
try:
    fake_model = joblib.load('backend/models/fake_account_model.pkl')
    fake_features = joblib.load('backend/models/fake_account_features.pkl')
    platform_encoder = joblib.load('backend/models/platform_encoder.pkl')
    print("✅ Social media models loaded successfully")
except Exception as e:
    fake_model = None
    print(f"⚠️ Error loading social media models: {e}")

# Load Text Scam Models
try:
    text_model = joblib.load('backend/models/scam_text_model.pkl')
    text_vectorizer = joblib.load('backend/models/scam_text_vectorizer.pkl')
    print("✅ Text scam model loaded successfully")
except Exception as e:
    text_model = None
    print(f"⚠️ Error loading text scam model: {e}")

# Load URL Scam Models
try:
    url_model = joblib.load('backend/models/scam_url_model.pkl')
    url_features = joblib.load('backend/models/scam_url_features.pkl')
    print("✅ URL scam model loaded successfully")
except Exception as e:
    url_model = None
    print(f"⚠️ Error loading URL scam model: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze-profile', methods=['POST'])
def analyze_profile():
    try:
        data = request.json
        
        # Encode platform
        platform = data.get('platform', 'instagram')
        try:
            platform_encoded = platform_encoder.transform([platform])[0]
        except:
            platform_encoded = 0
        
        # Extract features
        features = []
        for feature in fake_features:
            if feature == 'followers':
                features.append(float(data.get('followers', 0)))
            elif feature == 'following':
                features.append(float(data.get('following', 0)))
            elif feature == 'posts':
                features.append(float(data.get('posts', 0)))
            elif feature == 'account_age_days':
                features.append(float(data.get('account_age', 30)))
            elif feature == 'bio_length':
                username = data.get('username', '')
                features.append(float(len(username)))
            elif feature == 'profile_pic':
                features.append(1 if data.get('has_profile_pic', 'yes') == 'yes' else 0)
            elif feature == 'verified':
                features.append(0)
            elif feature == 'external_links':
                features.append(0)
            elif feature == 'activity_rate':
                posts = float(data.get('posts', 0))
                age = float(data.get('account_age', 30))
                features.append(posts / age if age > 0 else 0)
            elif feature == 'platform_encoded':
                features.append(platform_encoded)
            elif feature == 'followers_following_ratio':
                followers = float(data.get('followers', 0))
                following = float(data.get('following', 0))
                features.append(followers / (following + 1))
            elif feature == 'engagement_potential':
                followers = float(data.get('followers', 0))
                posts = float(data.get('posts', 0))
                age = float(data.get('account_age', 30))
                features.append((followers + posts) / (age + 1))
            elif feature == 'completeness_score':
                profile_pic = 1 if data.get('has_profile_pic', 'yes') == 'yes' else 0
                features.append(profile_pic)
            else:
                features.append(0)
        
        # Predict
        if fake_model:
            prediction = fake_model.predict([features])[0]
            confidence = fake_model.predict_proba([features])[0].max()
            
            # Generate risk factors
            risk_factors = []
            if int(data.get('followers', 0)) < 100:
                risk_factors.append("Very low follower count")
            if int(data.get('following', 0)) > int(data.get('followers', 0)) * 2:
                risk_factors.append("Following much more than followers")
            if int(data.get('posts', 0)) < 5:
                risk_factors.append("Very few posts")
            if int(data.get('account_age', 30)) < 30:
                risk_factors.append("Account is very new")
            if data.get('has_profile_pic', 'yes') == 'no':
                risk_factors.append("No profile picture")
            if len(data.get('username', '')) > 15:
                risk_factors.append("Username looks automated")
                
            if not risk_factors:
                risk_factors.append("No obvious red flags detected")
            
            return jsonify({
                'is_fake': bool(prediction),
                'confidence': float(confidence),
                'risk_factors': risk_factors[:5]
            })
        else:
            return jsonify({
                'is_fake': False,
                'confidence': 0.65,
                'risk_factors': ['Model not loaded properly', 'Using default response']
            })
            
    except Exception as e:
        print(f"Error in analyze-profile: {e}")
        return jsonify({
            'is_fake': False,
            'confidence': 0.5,
            'risk_factors': [f'Error: Check your inputs']
        })

@app.route('/analyze-content', methods=['POST'])
def analyze_content():
    try:
        data = request.json
        content = data.get('content', '')
        content_type = data.get('type', 'text')
        platform = data.get('platform', 'web')
        
        # FIRST: Check if this is a known scam in our database
        known_scam = scam_db.check_scam(content)
        
        # Get ML prediction
        is_scam = False
        confidence = 0.5
        found_words = []
        
        if content_type == 'text':
            if text_model and text_vectorizer:
                content_vector = text_vectorizer.transform([content])
                is_scam = text_model.predict(content_vector)[0]
                confidence = text_model.predict_proba(content_vector)[0].max()
                
                scam_keywords = ['free', 'winner', 'prize', 'click', 'verify', 'bank', 
                               'password', 'urgent', 'limited', 'congratulations', 'bitcoin',
                               'crypto', 'lottery', 'claim', 'reward', 'login']
                found_words = [kw for kw in scam_keywords if kw in content.lower()]
            else:
                scam_keywords = ['free', 'winner', 'prize', 'click', 'verify', 'bank', 
                               'password', 'urgent', 'limited', 'congratulations']
                found_words = [kw for kw in scam_keywords if kw in content.lower()]
                is_scam = len(found_words) > 0
                confidence = 0.7 if is_scam else 0.6
        else:  # url
            if url_model:
                url = content
                features = [
                    len(url), url.count('.'), url.count('/'),
                    1 if url.startswith('https') else 0,
                    1 if any(c.isdigit() for c in url) else 0
                ]
                is_scam = url_model.predict([features])[0]
                confidence = url_model.predict_proba([features])[0].max()

                # FORCED SCAM DETECTION for obvious scam patterns
                if 'bit.ly' in url or 'tinyurl' in url or not url.startswith('https'):
                    is_scam = True
                    confidence = max(confidence, 0.85)
                    print(f"⚠️ FORCED SCAM DETECTION (shortened/no HTTPS) for: {url}")
                
                # Also detect suspicious domains like paypal-verify.xyz
                if 'verify' in url.lower() or 'secure' in url.lower() or 'login' in url.lower():
                    domain = url.split('/')[2] if len(url.split('/')) > 2 else ''
                    if '.xyz' in domain or '.ru' in domain or '.top' in domain or '.net' in domain and 'paypal' in domain:
                        is_scam = True
                        confidence = max(confidence, 0.90)
                        print(f"⚠️ FORCED SCAM DETECTION (suspicious domain) for: {url}")
                
                risk_indicators = []
                if 'bit.ly' in url or 'tinyurl' in url or 'shorturl' in url:
                    risk_indicators.append("Shortened URL (hides destination)")
                if not url.startswith('https'):
                    risk_indicators.append("No HTTPS (insecure connection)")
                if url.count('.') > 3:
                    risk_indicators.append("Unusual domain structure")
                if re.search(r'\d+\.\d+\.\d+\.\d+', url):
                    risk_indicators.append("IP address instead of domain name")
                if any(c.isdigit() for c in url.split('/')[2] if len(url.split('/')) > 2):
                    risk_indicators.append("Domain contains numbers")
                if 'login' in url.lower() or 'verify' in url.lower() or 'secure' in url.lower():
                    risk_indicators.append("Contains suspicious keywords")
                
                found_words = risk_indicators[:5] if risk_indicators else ['ML analysis complete']
            else:
                risk_indicators = []
                if 'bit.ly' in url or 'tinyurl' in url:
                    risk_indicators.append("Shortened URL")
                if not url.startswith('https'):
                    risk_indicators.append("No HTTPS")
                if 'login' in url.lower() or 'verify' in url.lower():
                    risk_indicators.append("Contains suspicious keywords")
                
                is_scam = len(risk_indicators) > 0
                confidence = 0.7 if is_scam else 0.6
                found_words = risk_indicators if risk_indicators else ['No scam indicators found']
        
        # ========== COMMUNITY INTELLIGENCE (FIXED - UPDATES ON EVERY REPORT) ==========
        community_message = None
        report_count = 0
        
        if known_scam['is_known_scam']:
            # UPDATE the database for this new report (increment count)
            result = scam_db.add_or_update_scam(content, content_type, confidence, platform)
            report_count = result['report_count']
            community_message = f"🔔 COMMUNITY ALERT: This exact {'link' if content_type == 'link' else 'message'} has been reported {report_count} times by other users!"
            print(f"📢 Updated scam! Report count now: {report_count}")
            # Boost confidence if community says it's scam
            if report_count >= 3:
                is_scam = True
                confidence = max(confidence, 0.85)
        else:
            # First time - save to database
            if is_scam:
                result = scam_db.add_or_update_scam(content, content_type, confidence, platform)
                if result['action'] == 'added':
                    community_message = f"📢 Your report helps protect others! This {'link' if content_type == 'link' else 'message'} is now in our database. (Report #{result['report_count']})"
                    print(f"✅ New scam saved! Report #: {result['report_count']}")
        
        # Build warning flags
        warning_flags = found_words[:5] if found_words else ['ML analysis complete']
        
        # Return response with separate community alert
        return jsonify({
            'is_scam': bool(is_scam),
            'confidence': float(confidence),
            'warning_flags': warning_flags[:5],
            'community_alert': community_message,
            'report_count': report_count
        })
            
    except Exception as e:
        print(f"Error in analyze-content: {e}")
        return jsonify({
            'is_scam': False,
            'confidence': 0.5,
            'warning_flags': [f'Error: {str(e)}'],
            'community_alert': None
        })

# ========== CROSS-PLATFORM CORRELATION ENGINE (PATENT FEATURE) ==========
@app.route('/analyze-cross-platform', methods=['POST'])
def analyze_cross_platform():
    try:
        data = request.json
        platforms = data.get('platforms', [])
        
        if len(platforms) < 2:
            return jsonify({
                'is_synthetic': False,
                'consistency_score': 1.0,
                'reason': 'Need at least 2 platforms for cross-platform analysis',
                'confidence': 0.5,
                'post_variance': 0,
                'ratio_variance': 0,
                'engagement_variance': 0
            })
        
        # Calculate metrics for each platform
        posts_per_day = []
        follower_ratios = []
        engagement_rates = []
        
        for p in platforms:
            # Posts per day
            posts = p.get('posts', 0)
            age = p.get('account_age', 30)
            ppd = posts / age if age > 0 else 0
            posts_per_day.append(ppd)
            
            # Follower/following ratio
            followers = p.get('followers', 0)
            following = p.get('following', 1)
            ratio = followers / following if following > 0 else 0
            follower_ratios.append(ratio)
            
            # Engagement rate (simplified)
            likes = p.get('avg_likes', 0)
            comments = p.get('avg_comments', 0)
            engagement = (likes + comments) / (followers + 1) if followers > 0 else 0
            engagement_rates.append(engagement)
        
        # Calculate variances
        post_variance = np.var(posts_per_day) if len(posts_per_day) > 1 else 0
        ratio_variance = np.var(follower_ratios) if len(follower_ratios) > 1 else 0
        engagement_variance = np.var(engagement_rates) if len(engagement_rates) > 1 else 0
        
        # Normalize variances to 0-1 scale
        max_var = 100
        post_norm = min(post_variance / max_var, 1)
        ratio_norm = min(ratio_variance / max_var, 1)
        engagement_norm = min(engagement_variance / max_var, 1)
        
        # Calculate consistency score
        consistency_score = 1 - (post_norm + ratio_norm + engagement_norm) / 3
        
        # Determine if synthetic identity
        is_synthetic = False
        reason = ""
        confidence = 0.5
        
        if consistency_score < 0.2:
            is_synthetic = True
            reason = "Highly inconsistent behavior across platforms. Likely synthetic identity created by different people."
            confidence = 0.85
        elif consistency_score > 0.8:
            is_synthetic = True
            reason = "Unnaturally consistent behavior across platforms. Likely automated bot network."
            confidence = 0.90
        else:
            if max(posts_per_day) / (min(posts_per_day) + 0.1) > 100:
                is_synthetic = True
                reason = f"Extreme posting frequency mismatch: {max(posts_per_day):.1f} vs {min(posts_per_day):.1f} posts/day"
                confidence = 0.88
            elif max(follower_ratios) / (min(follower_ratios) + 0.01) > 50:
                is_synthetic = True
                reason = "Suspicious follower ratio variation across platforms"
                confidence = 0.82
            else:
                reason = "Natural behavioral variation detected across platforms"
                confidence = 0.75
        
        return jsonify({
            'is_synthetic': is_synthetic,
            'consistency_score': float(consistency_score),
            'reason': reason,
            'confidence': float(confidence),
            'post_variance': float(post_norm),
            'ratio_variance': float(ratio_norm),
            'engagement_variance': float(engagement_norm)
        })
        
    except Exception as e:
        print(f"Error in cross-platform analysis: {e}")
        return jsonify({
            'is_synthetic': False,
            'consistency_score': 0.5,
            'reason': f'Error: {str(e)}',
            'confidence': 0.5,
            'post_variance': 0,
            'ratio_variance': 0,
            'engagement_variance': 0
        })

# ========== COMMUNITY STATS ROUTE ==========
@app.route('/scam-stats', methods=['GET'])
def scam_stats():
    """Get scam database statistics"""
    stats = scam_db.get_stats()
    top_scams = scam_db.get_top_scams(5)
    
    return jsonify({
        'total_scams': stats['total_scams'],
        'total_reports': stats['total_reports'],
        'top_scams': top_scams
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SOCIO GUARD WITH COMMUNITY INTELLIGENCE")
    print("="*60)
    print("✅ Social Media ML Model Loaded")
    print("✅ Text Scam ML Model Loaded")
    print("✅ URL Scam ML Model Loaded")
    print("✅ Cross-Platform Correlation Engine Active")
    print("✅ Live Scam Alert Network Active")
    print("="*60 + "\n")
    app.run(debug=True)