CREATE TABLE IF NOT EXISTS post (
  id         SERIAL PRIMARY KEY,
  image      TEXT,             -- filename or path (optional)
  comment    TEXT,             -- post text/comment (optional)
  username   TEXT NOT NULL,    -- user who posted (required)
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

   -- At least one of comment or image must be present
    CONSTRAINT post_comment_or_image CHECK (
        comment IS NOT NULL OR image IS NOT NULL
    ),

    -- 280-character limit on comments
    CONSTRAINT post_comment_length CHECK (
        char_length(comment) <= 280
    )
);
