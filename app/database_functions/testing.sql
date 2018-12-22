SELECT * FROM user_data



SELECT * FROM ways_modified

DELETE FROM ways_modified WHERE userid = 446529

SELECT * FROM network_modification(4444789)

DELETE FROM ways_userinput

DELETE FROM ways_userinput_vertices_pgr

SELECT * FROM ways_userinput

ROLLBACK;

DROP TABLE test_vertices;
CREATE TABLE test_vertices as

SELECT * FROM intersection_existing_network

12486

WITH x_y AS (
	SELECT round(st_x(geom)::numeric,8) x,round(st_y(geom)::numeric,8) y, vertex_id,geom 
	FROM intersection_existing_network
),
all_very_similar_vertices AS (
	SELECT x.vertex_id, concat(x::varchar,' ',y::varchar)
	FROM  x_y x, intersection_existing_network i
	WHERE x.vertex_id <> i.vertex_id
	AND round(st_x(i.geom)::numeric,8) = x.x
	AND round(st_y(i.geom)::numeric,8) = x.y
),
selected_unique_vertices AS (
	SELECT DISTINCT ON (concat) concat, vertex_id 
	FROM all_very_similar_vertices a 
),
vertices_to_replace AS (
	SELECT * FROM all_very_similar_vertices a  
	WHERE a.vertex_id 
	NOT IN (SELECT vertex_id FROM selected_unique_vertices )
)

SELECT concat(substring(substring(st_astext(drawn_features.geom), '[0-9. ]+ '),1,11),
			 substring(substring(st_astext(drawn_features.geom), ' [0-9. ]+'),0,12)) 
FROM vertices_to_replace v, drawn_features

SELECT * FROM drawn_features

WHERE concat(substring(substring(st_astext(drawn_features.geom), '[0-9. ]+ '),1,11),
			 substring(substring(st_astext(drawn_features.geom), ' [0-9. ]+'),0,12))
= v.concat

	
	
	UPDATE drawn_features 
	SET geom = ST_GeomFromText(concat('LINESTRING(',v.concat,substring(st_astext(geom), ',[0-9. ,]+'))) 
SELECT * FROM drawn_features

SELECT substring(substring(st_astext(geom), ' [0-9. ]+'),1,12),substring(st_astext(geom), ',[0-9. ,]+') 
FROM ways_modified

SELECT concat('ss','ss')

SELECT * FROM ways_modified



ORDER BY geom



CREATE OR REPLACE FUNCTION public.network_modification(input_userid integer)
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
   cnt integer;
   count_bridges integer;
BEGIN
   
delete FROM ways_userinput WHERE userid = 133256;
delete FROM ways_userinput_vertices_pgr WHERE userid = 133256;
   
   
DROP TABLE IF EXISTS drawn_features;
DROP TABLE IF EXISTS existing_network;
DROP TABLE IF EXISTS intersection_existing_network;
DROP TABLE IF EXISTS drawn_features_union;
DROP TABLE IF EXISTS new_network;
DROP TABLE IF EXISTS no_intersection;
DROP TABLE IF EXISTS one_intersection;
DROP TABLE IF EXISTS two_intersections;
DROP TABLE IF EXISTS delete_extended_part; 

CREATE TEMP TABLE drawn_features as
SELECT id,geom,class_id,userid  FROM ways_modified
WHERE userid = 133256;

--Extends drawn lines by a distance of approx. 1 meter
WITH extend_first_part AS (
	SELECT u.id,st_addpoint(u.geom,end_point) as geom
	FROM
	--Line is extended on the end_point part
	(SELECT id,st_translate(a,sin(azimuth) * newlength,cos(azimuth) * newlength) as end_point
	FROM
		--Calculates a extended distance of the line
		(SELECT id,a,b,st_azimuth(a,b) azimuth,st_distance(a,b) as length,
		(st_distance(a,b) + (st_distance(a,b)*(0.00000957046/st_distance(a,b)))) as newlength
		FROM
			-- Extracts the starting AND end point of each line
			(SELECT id,st_startpoint(geom) a,st_endpoint(geom) b
			FROM drawn_features) x
		) y
	) z,
	drawn_features u
	WHERE z.id=u.id
),
extend_both_parts AS (
	SELECT u.id,st_addpoint(u.geom,start_point,0) geom
	FROM
	(SELECT id,st_translate(a,sin(azimuth) * newlength,cos(azimuth) * newlength) as start_point
	FROM
	(SELECT id,a,b,st_azimuth(a,b) azimuth,st_distance(a,b) as length,
	(st_distance(a,b) + (st_distance(a,b)*(0.00000957046/st_distance(a,b)))) as newlength
	FROM
		(SELECT id,st_startpoint(geom) b,st_endpoint(geom) a
		FROM drawn_features) x
		) y
	) 
	t,extend_first_part u
	WHERE t.id=u.id
)
UPDATE drawn_features set geom = b.geom 
FROM extend_both_parts b
WHERE drawn_features.id = b.id;

CREATE TABLE delete_extended_part AS 
SELECT st_startpoint(geom) 
FROM drawn_features
UNION ALL 
SELECT st_endpoint(geom)
FROM drawn_features;

/*Intersects with the existing network and creates a table with new vertices. 
  Each vertex is only added once to the table, in the case there are multiple intersections.
*/
CREATE TEMP TABLE intersection_existing_network as
WITH intersection_points AS (
	SELECT i.userid,st_intersection(i.geom,w.geom) as geom 
	FROM drawn_features i,ways_userinput w 
	WHERE st_intersects(i.geom,w.geom)
	AND w.userid IS NULL
	AND ST_geometrytype(st_intersection(i.geom,w.geom)) = 'ST_Point'
	UNION ALL
	SELECT i.userid, (st_dump(st_intersection(i.geom,w.geom))).geom as geom 
	FROM drawn_features i,ways_userinput w
	WHERE ST_geometryType(st_intersection(i.geom,w.geom)) ='ST_MultiPoint'
	AND w.userid IS NULL
	AND st_intersects(i.geom,w.geom)
)
SELECT (SELECT max(id) FROM ways_userinput_vertices_pgr) + row_number() over() as vertex_id,x.* 
FROM (SELECT DISTINCT * FROM intersection_points) x

----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
--------------------------------EXISTING NETWorK----------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------	
--All the lines FROM the existing network which intersect with the draw network are split, this
--is done as a new node now is added	

PERFORM 

SELECT * FROM split_existing_network();


CREATE TEMP TABLE existing_network as 
SELECT distinct * FROM pre_network;  


UPDATE existing_network set source = x.id 
FROM (
	SELECT v.id,v.geom 
	FROM ways_userinput_vertices_pgr v, pre_network i
	WHERE st_intersects(v.geom,i.geom)
	AND v.userid IS NULL
	UNION ALL
	SELECT vertex_id,geom FROM intersection_existing_network
	) x
WHERE st_startpoint(existing_network.geom) = x.geom;


UPDATE existing_network set target = x.id 
FROM (
	SELECT v.id,v.geom 
	FROM ways_userinput_vertices_pgr v, pre_network i
	WHERE st_intersects(v.geom,i.geom)
	AND v.userid IS NULL
	UNION ALL
	SELECT vertex_id,geom FROM intersection_existing_network
) x
WHERE st_endpoint(existing_network.geom) = x.geom;

SELECT st_length(geom::geography) FROM existing_network

--Unions the input geometry so each linestring on the next step is split by the whole the geometries as a whole
--It is checked how many geometries are inserted by the user. If only one the can be no intersection between the inserted lines.


SELECT count(*) INTO cnt
FROM drawn_features;


IF cnt = 1 THEN
    CREATE TEMP TABLE drawn_features_union as
    SELECT geometry as geom
    FROM drawn_features;
ELSE
	    --Split_userinput is a funtion which needs userid as input
	CREATE TEMP TABLE drawn_features_union as
	SELECT st_union(split_userinput) as geom 
	FROM split_userinput();

END IF;
--Split the new lines WHERE they intersect with the new network
CREATE TEMP TABLE new_network as
SELECT row_number() over() as gid,geom 
FROM(
	SELECT (st_dump(ST_CollectionExtract(st_split(x.geom,i.geom),2))).geom as geom
	FROM 
	(SELECT st_union(w.geom) as geom 
	FROM ways_userinput w,drawn_features_union n 
	WHERE st_intersects(w.geom,n.geom)
	AND w.userid IS NULL) i,
	drawn_features_union x) t 
WHERE st_length(geom::geography) <> 0;

ALTER TABLE new_network  add column source integer;
ALTER TABLE new_network  add column target integer;

/*
CREATE TABLE test_vertices AS

SELECT geom,count(*) FROM intersection_existing_network
GROUP BY geom


DROP TABLE IF EXISTS test;
CREATE TABLE test AS 
SELECT * FROM new_network;
*/

DELETE FROM new_network
WHERE st_startpoint(geom) IN (SELECT * FROM delete_extended_part);
DELETE FROM new_network
WHERE st_endpoint(geom) IN (SELECT * FROM delete_extended_part);

WITH start_point AS (
	SELECT gid,st_startpoint(geom) geom
	FROM new_network
),
vertex_source AS (
	SELECT gid,vertex_id source
	FROM intersection_existing_network i, start_point s
	WHERE i.geom = s.geom 
)
UPDATE new_network SET SOURCE = v.SOURCE 
FROM vertex_source v
WHERE new_network.gid = v.gid;


WITH end_point AS (
	SELECT gid,st_endpoint(geom) geom
	FROM new_network
),
vertex_target AS (
	SELECT gid,vertex_id target
	FROM intersection_existing_network i, end_point s
	WHERE i.geom = s.geom 
)
UPDATE new_network SET target = v.target 
FROM vertex_target v
WHERE new_network.gid = v.gid;

DROP TABLE test;
CREATE TABLE test AS 
SELECT * FROM new_network
DROP TABLE test_vertices;
CREATE TABLE test_vertices as
SELECT * FROM intersection_existing_network;

CREATE TABLE test_existing AS 
SELECT * FROM existing_network


--For each line the start AND endpoint is created AND saved 
WITH one_intersection AS
(
	SELECT distinct t.geom geom ,_1,_2,i.geom point,vertex_id
	FROM (SELECT geom,st_startpoint(geom) _1, st_endpoint(geom) _2
	FROM new_network ) t,
	intersection_existing_network i
	WHERE st_astext(i.geom) = st_astext(t._1)
	OR st_astext(i.geom) = st_astext(t._2)
),
update_1 AS (
		--All new edges which have one intersecting point with the already existing network are SELECTed 
	--AND the corresponding vertex is SELECTed
	UPDATE new_network  set source = x.vertex_id 
	FROM (
	SELECT geom, vertex_id,_2 point FROM one_intersection WHERE geom  
	in(
		SELECT t.geom geom 
		FROM (SELECT geom,st_startpoint(geom) _1, st_endpoint(geom) _2
		FROM new_network ) t,
		intersection_existing_network i
		WHERE st_astext(i.geom) = st_astext(t._1)
		OR st_astext(i.geom) = st_astext(t._2)
		GROUP BY t.geom
		having count(*) = 1)
	AND _1 = point) x
	WHERE new_network .geom = x.geom
)
UPDATE new_network  set target = x.vertex_id 
FROM(
SELECT geom, vertex_id,_1 as point FROM one_intersection WHERE geom  
in(
	SELECT t.geom geom 
	FROM (SELECT geom,st_startpoint(geom) _1, st_endpoint(geom) _2
	FROM new_network ) t,
	intersection_existing_network i
	WHERE st_astext(i.geom) = st_astext(t._1)
	OR st_astext(i.geom) = st_astext(t._2)
	GROUP BY t.geom
	having count(*) = 1)
AND _2 = point) x
WHERE new_network .geom = x.geom;




-- All lines, which have two intersection points with the existing network are assigned with vertices

--First the source vertext is assign AND put INTO a new preliminary table 
CREATE TEMP TABLE two_intersections as
SELECT t.geom geom,i.vertex_id AS source, 0 target
FROM (
	SELECT geom,st_startpoint(geom) _1
	FROM 
	(
		SELECT distinct t.* FROM new_network t,intersection_existing_network i
		WHERE source IS NULL AND target IS NULL
		AND st_intersects(i.geom,t.geom)) x
	) t,
	intersection_existing_network i
--geometries are compared as text
WHERE st_astext(i.geom) = st_astext(t._1);

UPDATE two_intersections set target = x.target 
FROM (
	SELECT t.geom geom,i.vertex_id as target
	FROM (
		SELECT geom, st_endpoint(geom) _2
		FROM 
		(
			SELECT distinct t.* FROM new_network t,intersection_existing_network i
			WHERE source IS NULL AND target IS NULL
			AND st_intersects(i.geom,t.geom)) x
		) t,intersection_existing_network i
--geometries are compared as text
	WHERE st_astext(i.geom) = st_astext(t._2)
	)x
WHERE two_intersections.geom = x.geom;


UPDATE new_network set source = two_intersections.source, target = two_intersections.target
FROM two_intersections 
WHERE new_network.geom = two_intersections.geom;

/*
DROP TABLE IF EXISTS test;
CREATE TABLE test AS 
SELECT * FROM new_network;
*/



--All new lines which are not interseting with the already existing network are getting new vertices as well
CREATE TEMP TABLE no_intersection as
SELECT y.st_startpoint as vertex,
--SELECT the max vertex_id so far
(SELECT max(max) FROM (
SELECT max(source) FROM new_network
UNION ALL 
SELECT max(target) FROM new_network) x) + row_number() over() as vertex_id
---------------------------------------------------------
FROM 
--SELECTs distinct vertices 
(SELECT distinct *
FROM (
	SELECT st_startpoint(geom),source 
	FROM new_network
	WHERE source IS NULL
	UNION ALL
	SELECT st_endpoint(geom),target 
	FROM new_network
	WHERE target IS NULL) x
) y;
	
UPDATE new_network set source = v.vertex_id
FROM no_intersection v
WHERE st_startpoint(geom) = v.vertex;

UPDATE new_network set target = v.vertex_id
FROM no_intersection v
WHERE st_endpoint(geom) = v.vertex;

--Delte those WHERE source AND target are so close to each other that they are identical 
delete FROM new_network 
WHERE source=target;


----------------------------------------------------------------------------------------------------------------------
--INSERT NEW VERTICES AND WAYS INTO THE EXISTING TABLES
----------------------------------------------------------------------------------------------------------------------

insert INTO ways_userinput_vertices_pgr(id,geom,userid)
SELECT vertex_id::bigint,geom,133256 FROM intersection_existing_network;

insert INTO ways_userinput_vertices_pgr(id,geom,userid)
SELECT distinct *,133256 FROM (
SELECT source::bigint,st_startpoint(geom) FROM new_network
WHERE source not in (SELECT vertex_id FROM intersection_existing_network)
UNION ALL
SELECT target::bigint,st_endpoint(geom) FROM new_network
WHERE target not in (SELECT vertex_id FROM intersection_existing_network)) x;

insert INTO ways_userinput(id,source,target,geom,userid)
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),source,target,geom,133256 FROM new_network;

insert INTO ways_userinput(id,source,target,geom,userid) 
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),source,target,geom,133256 FROM existing_network;

UPDATE ways_userinput 
set length_m = st_length(geom::geography)
WHERE length_m IS NULL;

--DELETE FROM ways_userinput WHERE source IS NULL OR target IS NULL;

---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------


END
$function$


DROP TABLE IF EXISTS test;
CREATE TABLE test as
SELECT * FROM ways_userinput WHERE SOURCE IS NULL OR target IS null

