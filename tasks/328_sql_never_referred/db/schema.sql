-- The shop's customers, and who brought whom. referred_by is empty for a customer who
-- found the shop on their own.
CREATE TABLE customers (
  id integer PRIMARY KEY,
  name text NOT NULL,
  city text NOT NULL,
  referred_by integer REFERENCES customers (id)
);
