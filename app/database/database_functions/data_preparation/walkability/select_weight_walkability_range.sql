DROP FUNCTION IF EXISTS select_weight_walkability_range;
CREATE OR REPLACE FUNCTION select_weight_walkability_range(attribute_input text, condition_input numeric)
RETURNS numeric AS
$$
	SELECT (w.value*w.weight)
	FROM walkability w
	WHERE w.attribute = attribute_input
	AND (w.min_value < condition_input or w.min_value IS NULL)
	AND (w.max_value >= condition_input or w.max_value IS NULL) 
$$
LANGUAGE sql immutable;