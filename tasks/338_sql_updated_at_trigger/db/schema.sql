-- Documents, and when each last changed. Nothing keeps updated_at current yet.
CREATE TABLE documents (
  id integer PRIMARY KEY,
  title text NOT NULL,
  body text NOT NULL,
  updated_at timestamp NOT NULL DEFAULT '2000-01-01'
);
