from scam_database import scam_db

# Test with a specific URL
url = "http://bit.ly/test123"

print("="*50)
print("TESTING COMMUNITY ALERT")
print("="*50)

# First time - should be new
print("\n1. First time checking:")
result1 = scam_db.check_scam(url)
print(f"   Known scam: {result1['is_known_scam']}")

# Add the scam
add1 = scam_db.add_or_update_scam(url, 'link', 0.89, 'web')
print(f"   Added: {add1}")

# Second time - should be known
print("\n2. Second time checking:")
result2 = scam_db.check_scam(url)
print(f"   Known scam: {result2['is_known_scam']}")
print(f"   Report count: {result2['report_count']}")

# Add again
add2 = scam_db.add_or_update_scam(url, 'link', 0.89, 'web')
print(f"   Updated: {add2}")

# Final check
print("\n3. Final check:")
result3 = scam_db.check_scam(url)
print(f"   Report count: {result3['report_count']}")

print("\n" + "="*50)
if result3['report_count'] == 2:
    print("✅ SUCCESS! Community alert is working!")
else:
    print("❌ Something is wrong. Report count should be 2")