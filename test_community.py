from scam_database import scam_db

# Test 1: Check if scam exists (should be False first time)
content = "http://bit.ly/3fR9xQ2"
print(f"Testing content: {content}")
print("-" * 50)

# Check before adding
result = scam_db.check_scam(content)
print(f"Before adding: is_known_scam = {result['is_known_scam']}")

# Add the scam
add_result = scam_db.add_or_update_scam(content, 'link', 0.89, 'web')
print(f"After adding: {add_result}")

# Check again
result = scam_db.check_scam(content)
print(f"After adding: is_known_scam = {result['is_known_scam']}")
print(f"Report count: {result['report_count']}")

# Add the SAME scam again (simulating second user)
add_result2 = scam_db.add_or_update_scam(content, 'link', 0.89, 'web')
print(f"\nAfter second report: {add_result2}")

# Check final stats
result = scam_db.check_scam(content)
print(f"Final report count: {result['report_count']}")

# View all scams
print("\n" + "-" * 50)
print("All scams in database:")
stats = scam_db.get_stats()
print(f"Total unique scams: {stats['total_scams']}")
print(f"Total reports: {stats['total_reports']}")

top = scam_db.get_top_scams(5)
for scam in top:
    print(f"  - {scam['content'][:50]}... | Reports: {scam['report_count']}")