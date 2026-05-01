# create_db.py
from scam_database import scam_db

print("="*50)
print("CREATING DATABASE")
print("="*50)

# This will automatically create the database file
print("✅ Database created at: backend/scam_reports.db")

# Test adding a scam
result = scam_db.add_or_update_scam("http://test.com", "link", 0.95, "web")
print(f"Test scam added: {result}")

# Verify
stats = scam_db.get_stats()
print(f"Total scams in database: {stats['total_scams']}")
print(f"Total reports: {stats['total_reports']}")

print("\n✅ Database is ready!")