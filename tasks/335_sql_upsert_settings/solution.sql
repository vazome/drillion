INSERT INTO settings (user_id, prefs, updated_on)
SELECT user_id, prefs, DATE '{today}'
FROM incoming
ON CONFLICT (user_id) DO UPDATE
SET prefs = settings.prefs || excluded.prefs,
    updated_on = excluded.updated_on;
