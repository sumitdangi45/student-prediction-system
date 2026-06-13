-- ============================================================================
-- CREATE SUPABASE STORAGE BUCKET FOR PROFILE PHOTOS
-- Run this in Supabase SQL Editor
-- ============================================================================

-- Create storage bucket for profile photos
-- Note: This creates the bucket via RLS policy, but easier via dashboard

-- Go to Supabase Dashboard -> Storage
-- Click "New Bucket"
-- Bucket name: profile-photos
-- Privacy: Public (so images can be accessed via URL)
-- Click "Create Bucket"

-- After creating bucket, set public access policy:
INSERT INTO storage.buckets (id, name, public)
VALUES ('profile-photos', 'profile-photos', true)
ON CONFLICT (id) DO NOTHING;

-- Allow anyone to read files
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'profile-photos');

-- Allow authenticated users to upload
CREATE POLICY "Authenticated users can upload"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'profile-photos' 
  AND auth.role() = 'authenticated'
);

-- Allow users to delete their own files
CREATE POLICY "Users can delete own files"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'profile-photos'
  AND auth.uid() = owner
);
