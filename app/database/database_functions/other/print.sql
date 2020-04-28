DROP FUNCTION IF EXISTS print;
CREATE OR REPLACE FUNCTION print(txt TEXT)
RETURNS void
AS $$
BEGIN
  RAISE NOTICE '%', txt;

END;
$$ language 'plpgsql' STRICT;


--SELECT print('Hooo');