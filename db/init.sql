CREATE TABLE IF NOT EXISTS post (
  id         SERIAL PRIMARY KEY,
  image      TEXT,             -- URL or path
  comment    TEXT NOT NULL,    -- the post text/comment
  username   TEXT NOT NULL,    -- user who posted
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);