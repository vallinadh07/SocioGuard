import sqlite3
import hashlib
from datetime import datetime
import os

class ScamDatabase:
    def __init__(self, db_path='backend/scam_reports.db'):
        self.db_path = db_path
        # Create backend directory if it doesn't exist
        os.makedirs('backend', exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Create the scam reports table if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scam_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_hash TEXT UNIQUE,
                    content TEXT,
                    content_type TEXT,
                    report_count INTEGER DEFAULT 1,
                    first_seen TEXT,
                    last_seen TEXT,
                    avg_confidence REAL,
                    platforms TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scam_id INTEGER,
                    user_agreed BOOLEAN,
                    timestamp TEXT,
                    FOREIGN KEY (scam_id) REFERENCES scam_reports(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully")
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            # If database is corrupt, delete and recreate
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print("🔄 Deleted corrupt database. Creating new one...")
                self.init_database()
    
    def get_content_hash(self, content):
        """Create a unique hash for the content"""
        return hashlib.md5(content.lower().strip().encode()).hexdigest()
    
    def add_or_update_scam(self, content, content_type, confidence, platform):
        """Add a new scam report or update existing one"""
        content_hash = self.get_content_hash(content)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if scam already exists
        cursor.execute('SELECT id, report_count, avg_confidence, platforms FROM scam_reports WHERE content_hash = ?', (content_hash,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing scam
            scam_id, report_count, avg_conf, platforms_str = existing
            new_count = report_count + 1
            new_avg_conf = (avg_conf * report_count + confidence) / new_count
            
            # Update platforms list
            platform_list = platforms_str.split(',') if platforms_str else []
            if platform not in platform_list:
                platform_list.append(platform)
            new_platforms = ','.join(platform_list)
            
            cursor.execute('''
                UPDATE scam_reports 
                SET report_count = ?, last_seen = ?, avg_confidence = ?, platforms = ?
                WHERE id = ?
            ''', (new_count, current_time, new_avg_conf, new_platforms, scam_id))
            
            conn.commit()
            conn.close()
            print(f"✅ UPDATED: Report count now {new_count}")
            return {'action': 'updated', 'report_count': new_count}
        else:
            # Add new scam
            cursor.execute('''
                INSERT INTO scam_reports (content_hash, content, content_type, first_seen, last_seen, avg_confidence, platforms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (content_hash, content, content_type, current_time, current_time, confidence, platform))
            
            conn.commit()
            conn.close()
            print(f"✅ ADDED: New scam with report count 1")
            return {'action': 'added', 'report_count': 1}
    
    def check_scam(self, content):
        """Check if content is known scam and return report data"""
        content_hash = self.get_content_hash(content)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content, report_count, first_seen, last_seen, avg_confidence, platforms 
            FROM scam_reports 
            WHERE content_hash = ?
        ''', (content_hash,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'is_known_scam': True,
                'content': result[0],
                'report_count': result[1],
                'first_seen': result[2],
                'last_seen': result[3],
                'avg_confidence': result[4],
                'platforms': result[5].split(',') if result[5] else []
            }
        else:
            return {'is_known_scam': False}
    
    def get_top_scams(self, limit=10):
        """Get most reported scams"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content, report_count, first_seen, content_type
            FROM scam_reports
            ORDER BY report_count DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{'content': r[0], 'report_count': r[1], 'first_seen': r[2], 'type': r[3]} for r in results]
    
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM scam_reports')
        total_scams = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(report_count) FROM scam_reports')
        total_reports = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {'total_scams': total_scams, 'total_reports': total_reports}

# Create global instance
scam_db = ScamDatabase()