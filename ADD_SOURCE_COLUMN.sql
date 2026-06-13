-- Add source column to predictions table to distinguish between batch uploads and user predictions
ALTER TABLE predictions ADD COLUMN source TEXT DEFAULT 'batch';

-- Update existing batch predictions (marked with batch_upload = true)
UPDATE predictions SET source = 'batch' WHERE batch_upload = true;

-- Update existing user predictions (have user_id and batch_upload = false)
UPDATE predictions SET source = 'user' WHERE batch_upload = false AND user_id IS NOT NULL;

-- For predictions without user_id, mark as batch
UPDATE predictions SET source = 'batch' WHERE user_id IS NULL;

-- Create index for faster filtering
CREATE INDEX idx_predictions_source ON predictions(source);
