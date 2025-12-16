CREATE TABLE IF NOT EXISTS post (
  id             SERIAL PRIMARY KEY,
  image_filename TEXT,
  image_status   TEXT NOT NULL DEFAULT 'READY',
  comment        TEXT,
  username       TEXT NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- At least one of comment or image must be present
  CONSTRAINT post_comment_or_image
    CHECK (comment IS NOT NULL OR image_filename IS NOT NULL),

  -- 280-character limit on comments
  CONSTRAINT post_comment_length
    CHECK (comment IS NULL OR char_length(comment) <= 280),

  -- If there is no image, status must be READY; otherwise status is one of PENDING/READY/FAILED
  CONSTRAINT post_image_status
    CHECK (
      (image_filename IS NULL AND image_status = 'READY')
      OR
      (image_filename IS NOT NULL AND image_status IN ('PENDING', 'READY', 'FAILED'))
    )
);
