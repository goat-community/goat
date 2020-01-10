DROP TABLE IF EXISTS user_statements;
CREATE TABLE user_statements (
 characteristic text NULL,
 statement text NULL,
 geom geometry NULL);
 
INSERT INTO user_statements (characteristic, statement, geom)
VALUES
   ('w40', 'Badly visible curve. Delivery trucks enter the living street way too fast. 
	Dangerous for people walking on the street.', 
	ST_SetSRID( ST_Point(11.5207902999,48.1976916310), 4326)),
	('m70', 'Dark underpass, uncomfortable to walk through.', 
	ST_SetSRID( ST_Point(11.5303652325,48.2006969161), 4326)),
	('m40', 'Social hotspot. This area should be avoided at night.', 
	ST_SetSRID( ST_Point(11.556906316,48.213408834), 4326)),
	('w25', 'This path is very scary at night.', 
	ST_SetSRID( ST_Point(11.535963676,48.197728236), 4326)),
	('m40', 'Very confusing road crossing. Too many road users intersect in a too narrow area.', 
	ST_SetSRID( ST_Point(11.52471042,48.19677199), 4326)),
	('w70', 'There are too few road crossing possibilities at this street.', 
	ST_SetSRID( ST_Point(11.524383135,48.199623895), 4326)),
	('w25', 'Very uncomfortable area for pedestrians.', 
	ST_SetSRID( ST_Point(11.544706173,48.203166156), 4326))
	;