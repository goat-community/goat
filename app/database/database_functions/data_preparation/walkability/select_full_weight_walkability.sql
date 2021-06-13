-- Load walkability table 
DROP TABLE IF EXISTS walkability;
CREATE TABLE walkability(
	category varchar,
	criteria varchar,
	attribute varchar,
	sring_condition varchar,
	min_value numeric,
	max_value numeric,
	value numeric,
	weight numeric
);

COPY walkability
FROM '/opt/data_preparation//walkability.csv'
DELIMITER ';'
CSV HEADER;

ALTER TABLE walkability ADD COLUMN gid serial;
ALTER TABLE walkability ADD PRIMARY KEY(gid);

DROP FUNCTION IF EXISTS select_full_weight_walkability;
CREATE OR REPLACE FUNCTION select_full_weight_walkability(attribute_input text)
RETURNS numeric AS
$$
	SELECT w.weight
	FROM walkability w 
	WHERE w.attribute = attribute_input 

$$
LANGUAGE sql immutable;