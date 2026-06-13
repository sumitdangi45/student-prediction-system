-- ============================================================================
-- ADD PROFILE COLUMNS TO USERS TABLE
-- Run this in Supabase SQL Editor to add profile fields
-- ============================================================================

-- Add profile columns if they don't exist
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS name VARCHAR(255),
ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS college VARCHAR(255),
ADD COLUMN IF NOT EXISTS branch VARCHAR(100),
ADD COLUMN IF NOT EXISTS cgpa FLOAT,
ADD COLUMN IF NOT EXISTS graduation_year VARCHAR(4),
ADD COLUMN IF NOT EXISTS photo TEXT,
ADD COLUMN IF NOT EXISTS is_new_user BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user';

-- Verify the columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;
