-- The shop's catalogue. attrs holds whatever the supplier sent, as JSON.
CREATE TABLE products (
  id integer PRIMARY KEY,
  name text NOT NULL UNIQUE,
  price numeric(10, 2) NOT NULL,
  attrs jsonb NOT NULL
);
