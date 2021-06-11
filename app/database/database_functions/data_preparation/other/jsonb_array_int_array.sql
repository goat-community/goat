DROP FUNCTION IF EXISTS jsonb_array_int_array;
CREATE OR REPLACE FUNCTION jsonb_array_int_array(jsonb) RETURNS int[] AS $f$
    SELECT array_agg(x)::int[] || ARRAY[]::int[] FROM jsonb_array_elements_text($1) t(x);
$f$ LANGUAGE sql IMMUTABLE;