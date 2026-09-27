-- The shop's customers. Your task.sql runs against this, on this sitting's data.
CREATE TABLE customers (
  id integer PRIMARY KEY,
  name text NOT NULL,
  city text NOT NULL,
  joined date NOT NULL
);
