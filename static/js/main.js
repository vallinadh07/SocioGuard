let currentContentType = 'text';
let platformCount = 1;

function setContentType(type) {
    currentContentType = type;
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    const label = document.getElementById('content-label');
    const textarea = document.getElementById('content-input');
    
    if (type === 'text') {
        label.textContent = 'Paste Text Here:';
        textarea.placeholder = 'Paste suspicious message here...';
        textarea.value = '';
    } else {
        label.textContent = 'Paste Link Here:';
        textarea.placeholder = 'Paste suspicious URL here...';
        textarea.value = '';
    }
}

async function analyzeProfile() {
    const platform = document.getElementById('platform').value;
    const username = document.getElementById('username').value;
    const followers = document.getElementById('followers').value;
    const following = document.getElementById('following').value;
    const posts = document.getElementById('posts').value;
    const account_age = document.getElementById('account_age').value;
    const has_profile_pic = document.getElementById('has_profile_pic').value;
    const has_bio = document.getElementById('has_bio').value;
    const avg_likes = document.getElementById('avg_likes').value;
    const avg_comments = document.getElementById('avg_comments').value;
    
    if (!username) {
        showResult('profile-result', 'Please enter username', 'warning');
        return;
    }
    
    showLoading('profile-result');
    
    try {
        const response = await fetch('/analyze-profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                platform: platform,
                username: username,
                followers: parseInt(followers) || 0,
                following: parseInt(following) || 0,
                posts: parseInt(posts) || 0,
                account_age: parseInt(account_age) || 30,
                has_profile_pic: has_profile_pic,
                has_bio: has_bio,
                avg_likes: parseInt(avg_likes) || 0,
                avg_comments: parseInt(avg_comments) || 0
            })
        });
        
        const data = await response.json();
        
        if (data.is_fake) {
            showResult('profile-result', 
                `⚠️ FAKE ACCOUNT DETECTED!\n\nConfidence: ${(data.confidence * 100).toFixed(1)}%\n\nRisk Factors:\n• ${data.risk_factors.join('\n• ')}`,
                'danger');
        } else {
            showResult('profile-result',
                `✅ ACCOUNT APPEARS GENUINE\n\nConfidence: ${(data.confidence * 100).toFixed(1)}%\n\nNotes:\n• ${data.risk_factors.join('\n• ')}`,
                'safe');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showResult('profile-result', 'Error analyzing profile. Please try again.', 'danger');
    }
}

async function analyzeContent() {
    const content = document.getElementById('content-input').value;
    const platform = document.getElementById('platform').value;
    
    if (!content) {
        showResult('content-result', 'Please paste some text or a link', 'warning');
        return;
    }
    
    showLoading('content-result');
    
    try {
        const response = await fetch('/analyze-content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content,
                type: currentContentType,
                platform: platform
            })
        });
        
        const data = await response.json();
        
        let resultMessage = '';
        
        if (data.is_scam) {
            resultMessage = `⚠️ SCAM DETECTED!\n\n`;
            resultMessage += `Confidence: ${(data.confidence * 100).toFixed(1)}%\n\n`;
            
            // Add community alert FIRST (most important)
            if (data.community_alert) {
                resultMessage += `🔔 ${data.community_alert}\n\n`;
            }
            
            resultMessage += `Warning Signs:\n• ${data.warning_flags.join('\n• ')}`;
            
            showResult('content-result', resultMessage, 'danger');
        } else {
            resultMessage = `✅ CONTENT APPEARS SAFE\n\n`;
            resultMessage += `Confidence: ${(data.confidence * 100).toFixed(1)}%\n\n`;
            
            // Show community alert even for safe content if it was reported
            if (data.community_alert) {
                resultMessage += `⚠️ ${data.community_alert}\n\n`;
            }
            
            resultMessage += `Notes:\n• ${data.warning_flags.join('\n• ')}`;
            
            showResult('content-result', resultMessage, 'safe');
        }
        
        // Clear the textarea after successful analysis
        document.getElementById('content-input').value = '';
        
    } catch (error) {
        console.error('Content error:', error);
        showResult('content-result', 'Error analyzing content. Please try again.', 'danger');
    }
}

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.textContent = 'Analyzing... 🔍';
    element.className = 'result show';
}

function showResult(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `result show ${type}`;
}

// ========== COMMUNITY STATS FUNCTION ==========
async function viewScamStats() {
    showLoading('content-result');
    
    try {
        const response = await fetch('/scam-stats');
        const data = await response.json();
        
        let statsText = `📊 COMMUNITY SCAM INTELLIGENCE\n\n`;
        statsText += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        statsText += `📈 Total unique scams detected: ${data.total_scams}\n`;
        statsText += `👥 Total community reports: ${data.total_reports}\n`;
        statsText += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
        
        if (data.top_scams && data.top_scams.length > 0) {
            statsText += `🏆 TOP REPORTED SCAMS:\n\n`;
            data.top_scams.forEach((scam, index) => {
                statsText += `${index + 1}. "${scam.content.substring(0, 60)}${scam.content.length > 60 ? '...' : ''}"\n`;
                statsText += `   📍 Reported: ${scam.report_count} times | Type: ${scam.type}\n`;
                statsText += `   📅 First seen: ${scam.first_seen}\n\n`;
            });
        } else {
            statsText += `✨ No scams reported yet. Be the first to report a scam!\n`;
        }
        
        statsText += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        statsText += `💡 Tip: When you detect a scam, it gets added to this database\n`;
        statsText += `   and helps protect other users automatically!`;
        
        showResult('content-result', statsText, 'info');
    } catch (error) {
        console.error('Stats error:', error);
        showResult('content-result', 'Error loading scam statistics', 'danger');
    }
}

// ========== CROSS-PLATFORM CORRELATION FUNCTIONS ==========

function addPlatform() {
    platformCount++;
    const container = document.getElementById('platforms-container');
    const newPlatform = document.createElement('div');
    newPlatform.className = 'platform-entry';
    newPlatform.id = `platform-${platformCount}`;
    newPlatform.innerHTML = `
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #e0e0e0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <strong>📱 Platform ${platformCount}</strong>
                <button type="button" class="remove-platform" onclick="removePlatform(${platformCount})" style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">✖ Remove</button>
            </div>
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <select class="platform-select" style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="instagram">📸 Instagram</option>
                    <option value="twitter">🐦 Twitter/X</option>
                    <option value="facebook">📘 Facebook</option>
                    <option value="linkedin">💼 LinkedIn</option>
                    <option value="tiktok">🎵 TikTok</option>
                </select>
                <input type="text" class="username-input" placeholder="Username" style="flex: 2; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                <input type="number" class="platform-followers" placeholder="Followers" style="padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                <input type="number" class="platform-following" placeholder="Following" style="padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                <input type="number" class="platform-posts" placeholder="Total Posts" style="padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                <input type="number" class="platform-age" placeholder="Account Age (days)" style="padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                <select class="platform-pic" style="padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="yes">Has Profile Pic ✅</option>
                    <option value="no">No Profile Pic ❌</option>
                </select>
                <select class="platform-bio" style="padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="yes">Has Bio ✅</option>
                    <option value="no">No Bio ❌</option>
                </select>
                <input type="number" class="platform-likes" placeholder="Avg Likes" style="padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                <input type="number" class="platform-comments" placeholder="Avg Comments" style="padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
            </div>
        </div>
    `;
    container.appendChild(newPlatform);
}

function removePlatform(id) {
    if (platformCount <= 1) {
        showResult('cross-platform-result', 'At least one platform is required', 'warning');
        return;
    }
    const element = document.getElementById(`platform-${id}`);
    if (element) {
        element.remove();
        platformCount--;
    }
}

async function analyzeCrossPlatform() {
    const platforms = [];
    const entries = document.querySelectorAll('.platform-entry');
    
    if (entries.length === 0) {
        showResult('cross-platform-result', 'Please add at least one platform', 'warning');
        return;
    }
    
    for (let entry of entries) {
        const platform = entry.querySelector('.platform-select').value;
        const username = entry.querySelector('.username-input').value;
        
        if (!username) {
            showResult('cross-platform-result', 'Please enter username for all platforms', 'warning');
            return;
        }
        
        platforms.push({
            platform: platform,
            username: username,
            followers: parseInt(entry.querySelector('.platform-followers').value) || 0,
            following: parseInt(entry.querySelector('.platform-following').value) || 0,
            posts: parseInt(entry.querySelector('.platform-posts').value) || 0,
            account_age: parseInt(entry.querySelector('.platform-age').value) || 30,
            has_profile_pic: entry.querySelector('.platform-pic').value,
            has_bio: entry.querySelector('.platform-bio').value,
            avg_likes: parseInt(entry.querySelector('.platform-likes').value) || 0,
            avg_comments: parseInt(entry.querySelector('.platform-comments').value) || 0
        });
    }
    
    showLoading('cross-platform-result');
    
    try {
        const response = await fetch('/analyze-cross-platform', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ platforms: platforms })
        });
        
        const data = await response.json();
        
        let resultText = `🔗 CROSS-PLATFORM CORRELATION ANALYSIS\n\n`;
        resultText += `📊 Platforms Analyzed: ${platforms.length}\n`;
        resultText += `📋 Profiles: ${platforms.map(p => `${p.platform}: @${p.username}`).join(', ')}\n\n`;
        
        resultText += `📈 BEHAVIORAL COMPARISON:\n`;
        resultText += `• Posts per day: ${platforms.map(p => `${p.platform}=${(p.posts/p.account_age).toFixed(1)}`).join(', ')}\n`;
        resultText += `• Follower/Following ratio: ${platforms.map(p => `${p.platform}=${(p.followers/(p.following+1)).toFixed(1)}`).join(', ')}\n`;
        resultText += `• Engagement rate: ${platforms.map(p => `${p.platform}=${((p.avg_likes+p.avg_comments)/(p.followers+1)*100).toFixed(1)}%`).join(', ')}\n\n`;
        
        resultText += `📊 VARIANCE SCORES:\n`;
        resultText += `• Posts per day variance: ${(data.post_variance * 100).toFixed(1)}%\n`;
        resultText += `• Follower ratio variance: ${(data.ratio_variance * 100).toFixed(1)}%\n`;
        resultText += `• Engagement variance: ${(data.engagement_variance * 100).toFixed(1)}%\n\n`;
        
        resultText += `🎯 CROSS-PLATFORM CONSISTENCY SCORE: ${(data.consistency_score * 100).toFixed(1)}%\n\n`;
        
        if (data.is_synthetic) {
            resultText += `⚠️ VERDICT: SYNTHETIC IDENTITY DETECTED!\n`;
            resultText += `🔍 Reason: ${data.reason}\n`;
            resultText += `💡 Confidence: ${(data.confidence * 100).toFixed(1)}%\n\n`;
            resultText += `🏆 This is a UNIQUE detection that no single-platform tool can identify!`;
            showResult('cross-platform-result', resultText, 'danger');
        } else {
            resultText += `✅ VERDICT: GENUINE HUMAN BEHAVIOR\n`;
            resultText += `🔍 Reason: ${data.reason}\n`;
            resultText += `💡 Confidence: ${(data.confidence * 100).toFixed(1)}%`;
            showResult('cross-platform-result', resultText, 'safe');
        }
        
    } catch (error) {
        console.error('Cross-platform error:', error);
        showResult('cross-platform-result', 'Error analyzing cross-platform data. Please try again.', 'danger');
    }
}