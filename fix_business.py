import sqlite3

conn = sqlite3.connect('backend/chatbot.db')
cursor = conn.cursor()

# Create businesses for users without business_id
print("Creating businesses for users...")
cursor.execute("""
    INSERT INTO businesses (name, owner_id, email, is_active, created_at)
    SELECT 
        COALESCE(u.full_name, SUBSTR(u.email, 1, INSTR(u.email, '@') - 1)) || '''s Business' as name,
        u.id as owner_id,
        u.email as email,
        1 as is_active,
        datetime('now') as created_at
    FROM users u
    WHERE u.business_id IS NULL
""")

print(f"Created {cursor.rowcount} businesses")

# Update users with their business_id
print("\nUpdating users with business_id...")
cursor.execute("""
    UPDATE users
    SET business_id = (
        SELECT b.id 
        FROM businesses b 
        WHERE b.owner_id = users.id
        LIMIT 1
    )
    WHERE business_id IS NULL
""")

print(f"Updated {cursor.rowcount} users")

# Verify
print("\n=== Verification ===")
cursor.execute("""
    SELECT 
        u.id, 
        u.email, 
        u.business_id, 
        b.name as business_name
    FROM users u
    LEFT JOIN businesses b ON u.business_id = b.id
""")

results = cursor.fetchall()
for row in results:
    print(f"User ID: {row[0]}, Email: {row[1]}, Business ID: {row[2]}, Business: {row[3]}")

conn.commit()
conn.close()

print("\n✅ Done!")
