DROP FUNCTION IF EXISTS select_full_weight_walkability;
CREATE OR REPLACE FUNCTION select_full_weight_walkability(attribute_input text)
RETURNS numeric AS
$$
	SELECT w.weight
	FROM walkability w 
	WHERE w.attribute = attribute_input 

$$
LANGUAGE sql immutable;