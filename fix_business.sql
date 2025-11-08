-- Create businesses for users without business_id
INSERT INTO businesses (name, owner_id, email, is_active, created_at)
SELECT 
    COALESCE(u.full_name, SUBSTR(u.email, 1, INSTR(u.email, '@') - 1)) || '''s Business' as name,
    u.id as owner_id,
    u.email as email,
    1 as is_active,
    datetime('now') as created_at
FROM users u
WHERE u.business_id IS NULL;

-- Update users with their business_id
UPDATE users
SET business_id = (
    SELECT b.id 
    FROM businesses b 
    WHERE b.owner_id = users.id
    LIMIT 1
)
WHERE business_id IS NULL;

-- Verify
SELECT 
    u.id, 
    u.email, 
    u.business_id, 
    b.name as business_name
FROM users u
LEFT JOIN businesses b ON u.business_id = b.id;
