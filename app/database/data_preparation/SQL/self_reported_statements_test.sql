DROP TABLE IF EXISTS user_statements;
CREATE TABLE user_statements (
 characteristic text NULL,
 statement text NULL,
 geom geometry NULL);
 
INSERT INTO user_statements (characteristic, statement, geom)
VALUES
   ('w40', 'Badly visible curve. Delivery trucks enter the living street way too fast. 
	Dangerous for people walking on the street.', 
	ST_SetSRID( ST_Point(1282488.472,6139806.974), 3857)),
	('m70', 'Dark underpass, uncomfortable to walk through.', 
	ST_SetSRID( ST_Point(1283554.049,6140308.233), 3857)),
	('m40', 'Social hotspot. This area should be avoided at night.', 
	ST_SetSRID( ST_Point(1286508.91,6142432.41), 3857)),
	('w25', 'This path is very scary at night.', 
	ST_SetSRID( ST_Point(1284177.601,6139813.123), 3857)),
	('m40', 'Very confusing road crossing. Too many road users intersect in a too narrow area.', 
	ST_SetSRID( ST_Point(1282926.295,6139655.084), 3857)),
	('w70', 'There are too few road crossing possibilities at this street.', 
	ST_SetSRID( ST_Point(1282888.826,6140130.212), 3857)),
	('w25', 'Very uncomfortable area for pedestrians.', 
	ST_SetSRID( ST_Point(1285150.849,6140721.441), 3857))
	;