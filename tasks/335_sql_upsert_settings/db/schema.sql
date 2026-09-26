-- Each user's settings, and the batch of changes that arrived overnight.
CREATE TABLE settings (
  user_id integer PRIMARY KEY,
  prefs jsonb NOT NULL,
  updated_on date NOT NULL
);

CREATE TABLE incoming (
  user_id integer PRIMARY KEY,
  prefs jsonb NOT NULL
);
