CREATE TEMP TABLE raw_flows(edge integer, start_cost float, end_cost float, COST float, persons integer);

DROP FUNCTION IF EXISTS compute_sequence_stream;
CREATE OR REPLACE FUNCTION compute_sequence_stream(edge_id integer)
  RETURNS TABLE(edge integer, persons integer) AS
$func$
	WITH RECURSIVE sequence_link AS (
		SELECT edge, start_cost, end_cost, COST, persons
		FROM raw_flows x
		WHERE edge = edge_id
		UNION
		SELECT t.edge, t.start_cost, t.end_cost, t.COST, s.persons + t.persons 
		FROM raw_flows t, sequence_link s
		WHERE least(s.start_cost,s.end_cost) = t.cost
	) 
	SELECT edge, persons::integer
	FROM sequence_link;

$func$  LANGUAGE sql;