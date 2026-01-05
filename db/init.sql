CREATE TABLE IF NOT EXISTS post (
  id                SERIAL PRIMARY KEY,

  -- Image
  image_filename    TEXT,
  image_status      TEXT NOT NULL DEFAULT 'READY',

  -- Post content
  content           TEXT,
  username          TEXT NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Image description (AI)
  image_description  TEXT,
  description_status TEXT NOT NULL DEFAULT 'NONE',

  -- Sentiment analysis
  sentiment_status  TEXT NOT NULL DEFAULT 'NONE',
  sentiment_label   TEXT,
  sentiment_score   REAL,

  -- At least one of content or image must be present
  CONSTRAINT post_content_or_image
    CHECK (content IS NOT NULL OR image_filename IS NOT NULL),

  -- 280-character limit on post content
  CONSTRAINT post_content_length
    CHECK (content IS NULL OR char_length(content) <= 280),

  -- Image description max length (≤ 300 chars)
  CONSTRAINT post_image_description_length
    CHECK (image_description IS NULL OR char_length(image_description) <= 300),

  -- Image status logic
  CONSTRAINT post_image_status
    CHECK (
      (image_filename IS NULL AND image_status = 'READY')
      OR
      (image_filename IS NOT NULL AND image_status IN ('PENDING', 'READY', 'FAILED'))
    ),

  -- Image description status logic
  CONSTRAINT post_description_status
    CHECK (
      (image_filename IS NULL AND description_status = 'NONE')
      OR
      (image_filename IS NOT NULL AND description_status IN ('NONE', 'PENDING', 'READY', 'FAILED'))
    ),

  -- Sentiment status logic
  CONSTRAINT post_sentiment_status
    CHECK (sentiment_status IN ('NONE', 'PENDING', 'READY', 'FAILED'))
);
