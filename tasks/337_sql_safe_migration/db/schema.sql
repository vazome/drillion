-- Accounts, and the payments some of them have made.
CREATE TABLE accounts (
  id integer PRIMARY KEY,
  email text NOT NULL UNIQUE
);

CREATE TABLE payments (
  id integer PRIMARY KEY,
  account_id integer NOT NULL REFERENCES accounts (id),
  paid_on date NOT NULL
);
