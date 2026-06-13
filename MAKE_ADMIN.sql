-- ============================================================================
-- Make Your Account Admin in Supabase
-- ============================================================================
-- Run this SQL in Supabase SQL Editor to make yourself admin
-- ============================================================================

-- Update your account to admin (change email to yours)
UPDATE public.users 
SET is_admin = TRUE 
WHERE email = 'sumitdangi84552@gmail.com';

-- Verify it worked:
SELECT email, is_admin FROM public.users WHERE email = 'sumitdangi84552@gmail.com';

-- Or if you want to see all users:
SELECT email, is_admin, created_at FROM public.users ORDER BY created_at DESC;

-- ============================================================================
-- Done! Now you should have admin access
-- ============================================================================
