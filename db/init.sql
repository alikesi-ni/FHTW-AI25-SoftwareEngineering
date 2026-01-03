CREATE TABLE IF NOT EXISTS post (
  id             SERIAL PRIMARY KEY,
  image_filename TEXT,
  image_status   TEXT NOT NULL DEFAULT 'READY',
  content        TEXT,
  username       TEXT NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sentiment_status TEXT NOT NULL DEFAULT 'NONE',
  sentiment_label TEXT,
  sentiment_score REAL,


  -- At least one of content or image must be present
  CONSTRAINT post_content_or_image
    CHECK (content IS NOT NULL OR image_filename IS NOT NULL),

  -- 280-character limit on post content
  CONSTRAINT post_content_length
    CHECK (content IS NULL OR char_length(content) <= 280),

  -- If there is no image, status must be READY; otherwise status is one of PENDING/READY/FAILED
  CONSTRAINT post_image_status
    CHECK (
      (image_filename IS NULL AND image_status = 'READY')
      OR
      (image_filename IS NOT NULL AND image_status IN ('PENDING', 'READY', 'FAILED'))
    ),

  CONSTRAINT sentiment_status_check CHECK (sentiment_status IN ('NONE','PENDING','READY','FAILED'))
  
);
