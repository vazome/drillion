CREATE FUNCTION touch_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER documents_touch
BEFORE UPDATE ON documents
FOR EACH ROW
WHEN (OLD.{watched} IS DISTINCT FROM NEW.{watched})
EXECUTE FUNCTION touch_updated_at();
