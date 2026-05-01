from scam_database import scam_db

url = "https://paypal-verify.xyz/login"

print("="*50)
print("TESTING REPORT COUNT")
print("="*50)

# Check before anything
print("\n1. Checking database...")
result = scam_db.check_scam(url)
print(f"   Known scam: {result['is_known_scam']}")
if result['is_known_scam']:
    print(f"   Report count: {result['report_count']}")

# Add the scam
print("\n2. Adding scam first time...")
add1 = scam_db.add_or_update_scam(url, 'link', 0.95, 'web')
print(f"   Result: {add1}")

# Check after first add
result = scam_db.check_scam(url)
print(f"\n3. After first add - Report count: {result['report_count']}")

# Add again (simulating second paste)
print("\n4. Adding scam second time...")
add2 = scam_db.add_or_update_scam(url, 'link', 0.95, 'web')
print(f"   Result: {add2}")

# Check after second add
result = scam_db.check_scam(url)
print(f"\n5. After second add - Report count: {result['report_count']}")

print("\n" + "="*50)
if result['report_count'] == 2:
    print("✅ SUCCESS! Report count incremented correctly!")
else:
    print(f"❌ FAILED! Report count is {result['report_count']}, should be 2")