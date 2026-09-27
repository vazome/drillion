ALTER TABLE accounts ADD COLUMN plan text;

UPDATE accounts
SET plan = CASE
  WHEN EXISTS (SELECT 1 FROM payments AS p WHERE p.account_id = accounts.id) THEN '{paid}'
  ELSE 'free'
END;

ALTER TABLE accounts
  ALTER COLUMN plan SET NOT NULL,
  ALTER COLUMN plan SET DEFAULT 'free',
  ADD CONSTRAINT accounts_plan_known CHECK (plan IN ('free', '{paid}'));
