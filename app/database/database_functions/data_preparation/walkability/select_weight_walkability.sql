DROP FUNCTION IF EXISTS select_weight_walkability;
CREATE OR REPLACE FUNCTION select_weight_walkability(attribute_input text, condition_input text)
RETURNS numeric AS
$$
	SELECT (w.value*w.weight) 
	FROM walkability w 
	WHERE w.attribute = attribute_input 
	AND w.sring_condition = condition_input;

$$
LANGUAGE sql immutable;