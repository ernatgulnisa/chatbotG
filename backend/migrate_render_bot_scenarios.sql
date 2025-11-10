-- Add trigger fields to bot_scenarios table
-- Run this on Render PostgreSQL database

-- Add new columns if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='bot_scenarios' AND column_name='trigger_type') THEN
        ALTER TABLE bot_scenarios ADD COLUMN trigger_type VARCHAR;
        UPDATE bot_scenarios SET trigger_type = 'flow' WHERE trigger_type IS NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='bot_scenarios' AND column_name='trigger_value') THEN
        ALTER TABLE bot_scenarios ADD COLUMN trigger_value JSONB;
        UPDATE bot_scenarios SET trigger_value = '[]'::jsonb WHERE trigger_value IS NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='bot_scenarios' AND column_name='response_message') THEN
        ALTER TABLE bot_scenarios ADD COLUMN response_message TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='bot_scenarios' AND column_name='priority') THEN
        ALTER TABLE bot_scenarios ADD COLUMN priority INTEGER;
        UPDATE bot_scenarios SET priority = 100 WHERE priority IS NULL;
    END IF;
END $$;

SELECT 'Migration completed successfully' AS status;
