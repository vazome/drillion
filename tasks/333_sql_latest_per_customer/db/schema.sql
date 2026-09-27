-- The shop's database. Your task.sql runs against this, on this sitting's data.
CREATE TABLE customers (
  id integer PRIMARY KEY,
  name text NOT NULL,
  city text NOT NULL,
  joined date NOT NULL
);

CREATE TABLE orders (
  id integer PRIMARY KEY,
  customer_id integer NOT NULL REFERENCES customers (id),
  placed_at timestamp NOT NULL,
  status text NOT NULL CHECK (status IN ('paid', 'shipped', 'refunded')),
  total numeric(10, 2) NOT NULL
);
