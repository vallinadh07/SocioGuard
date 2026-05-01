import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json

class SocialMediaScraper:
    
    @staticmethod
    def extract_username(url, platform):
        """Extract username from profile URL"""
        patterns = {
            'instagram': r'instagram\.com/([^/?]+)',
            'twitter': r'twitter\.com/([^/?]+)|x\.com/([^/?]+)',
            'facebook': r'facebook\.com/([^/?]+)',
            'tiktok': r'tiktok\.com/@([^/?]+)'
        }
        
        pattern = patterns.get(platform, '')
        match = re.search(pattern, url)
        if match:
            return match.group(1) or match.group(2)
        return None
    
    @staticmethod
    def scrape_instagram(username):
        """Scrape Instagram profile data"""
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        
        url = f"https://www.instagram.com/{username}/"
        
        try:
            # Note: Instagram requires login for full data
            # This is a simplified version using public endpoints
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Extract data from page source using regex
                html = response.text
                
                # Look for JSON data in script tags
                import re
                json_pattern = r'window\._sharedData\s*=\s*({.*?});'
                match = re.search(json_pattern, html)
                
                if match:
                    data = json.loads(match.group(1))
                    user_data = data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user', {})
                    
                    return {
                        'username': username,
                        'followers': user_data.get('edge_followed_by', {}).get('count', 0),
                        'following': user_data.get('edge_follow', {}).get('count', 0),
                        'posts': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'has_profile_pic': 'yes' if user_data.get('profile_pic_url') else 'no',
                        'has_bio': 'yes' if user_data.get('biography') else 'no',
                        'bio_length': len(user_data.get('biography', '')),
                        'is_verified': 'yes' if user_data.get('is_verified') else 'no',
                        'success': True
                    }
        except Exception as e:
            print(f"Error scraping Instagram: {e}")
        
        return {'success': False, 'error': 'Could not fetch data'}
    
    @staticmethod
    def scrape_twitter(username):
        """Scrape Twitter/X profile data using API"""
        # Twitter API v2 (free tier available)
        # You'll need to sign up for a Twitter Developer account
        pass
    
    @staticmethod
    def get_profile_data(url, platform):
        """Main method to get profile data from URL"""
        username = SocialMediaScraper.extract_username(url, platform)
        
        if not username:
            return {'success': False, 'error': 'Invalid URL'}
        
        if platform == 'instagram':
            return SocialMediaScraper.scrape_instagram(username)
        elif platform == 'twitter':
            return SocialMediaScraper.scrape_twitter(username)
        # Add more platforms as needed
        
        return {'success': False, 'error': f'{platform} scraping not yet implemented'}