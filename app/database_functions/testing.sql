SELECT * FROM network_modification(133256)

DROP TABLE vertices_to_assign

SELECT * FROM ways_userinput

SELECT * FROM edges

DROP TABLE test;
CREATE TABLE test1 as
SELECT * FROM pgrouting_edges(15,11.75011,48.41205,83.33,133256,1)

SELECT * FROM variable_container

CREATE OR REPLACE FUNCTION public.pgrouting_edges_input(minutes integer, x numeric, y numeric, speed numeric, userid_input integer, objectid_input integer)
 RETURNS SETOF type_edges
 LANGUAGE plpgsql
AS $function$
	DECLARE
	r type_edges;
	distance numeric;
	id_vertex integer;
	excluded_class_id text;
	begin
	--The speed AND minutes input are considered as distance
	  distance=speed*minutes;
	  
	  SELECT variable_array::text
  	  INTO excluded_class_id 
      FROM variable_container v
      WHERE v.identifier = 'excluded_class_id_walking';

	  SELECT id INTO id_vertex
      FROM ways_userinput_vertices_pgr  v
--It is snapped to the closest vertex within 50 m. If no vertex is within 50m not calculation is started.
      WHERE ST_DWithin(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326), 250)
      ORDER BY ST_Distance(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326))
      limit 1;
      UPDATE starting_point_isochrones set geometry = v.geom FROM ways_userinput_vertices_pgr v 
      WHERE v.id = id_vertex AND starting_point_isochrones.objectid = objectid_input; 
	  For r IN SELECT *  FROM 
	--The function Pgr_DrivingDistance delivers the reached network 
	--In this case the routing is done on a modified table
			  (SELECT t1.seq, t1.id1 AS Node, t1.id2 AS Edge, t1.cost, t2.geom FROM PGR_DrivingDistance(
	--This routing is for pedestrians, thus some way_classes are excluded.  			
				'SELECT id::int4, source, target, length_m as cost FROM ways_userinput 
				WHERE not class_id = any(''' || excluded_class_id || ''') AND userid IS NULL OR userid='||userid_input,
	  		   id_vertex, 
		       distance, false, false) t1, ways_userinput t2
	           WHERE t1.id2 = t2.id) as route
	           LOOP
	  RETURN NEXT r;
	  
	  END LOOP;
	  RETURN;
	END ;
$function$



DELETE FROM isochrones

CREATE OR REPLACE FUNCTION public.network_modification(input_userid integer)
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
   cnt integer;
   count_bridges integer;
BEGIN
   
DELETE FROM ways_userinput WHERE userid = 133256;
DELETE FROM ways_userinput_vertices_pgr WHERE userid = 133256;
   
   
DROP TABLE IF EXISTS drawn_features, existing_network, intersection_existing_network, drawn_features_union, new_network, delete_extended_part, vertices_to_assign; 

CREATE TEMP TABLE drawn_features as
SELECT id,geom,class_id,userid, original_id  FROM ways_modified
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
FROM (SELECT DISTINCT * FROM intersection_points) x;




--Unions the input geometry so each linestring on the next step is split by the whole the geometries as a whole
--It is checked how many geometries are inserted by the user. If only one the can be no intersection between the inserted lines.


SELECT count(*) INTO cnt
FROM drawn_features;

IF cnt = 1 THEN
    CREATE TEMP TABLE drawn_features_union as
    SELECT geom
    FROM drawn_features;
ELSE
	    --Split_userinput is a funtion which needs userid as input
	CREATE TEMP TABLE drawn_features_union as
	SELECT st_union(split_userinput) as geom 
	FROM split_userinput();

END IF;

DROP TABLE drawn_features_union

CREATE TEMP TABLE drawn_features_union AS
SELECT ST_UNION(geom) geom
FROM drawn_features;

--Split the new lines WHERE they intersect with the new network
DROP TABLE IF EXISTS new_network;
CREATE TEMP TABLE new_network as
WITH x AS (
	SELECT ST_Union(geom) geom FROM (
	SELECT w.geom as geom 
	FROM ways_userinput w,drawn_features_union n 
	WHERE st_intersects(w.geom,n.geom)
	AND w.userid IS NULL
	UNION ALL 
	SELECT n.geom as geom 
	FROM ways_userinput w,drawn_features_union n 
	WHERE st_intersects(w.geom,n.geom)
	AND w.userid IS NULL) u
)--,
--y AS (
	SELECT st_collectionextract(ST_Intersection(x.geom,d.geom),1) geom
	FROM x, drawn_features_union d 
)
SELECT a.class_id,(ST_Dump(ST_Split(ST_Snap(a.geom, b.geom, 0.00005),b.geom))).geom as geom
FROM drawn_features a, y b
WHERE ST_DWithin(b.geom, a.geom, 0.00005);

SELECT st_union(geom) FROM
(
SELECT w.geom as geom 
FROM ways_userinput w,drawn_features_union n 
WHERE st_intersects(w.geom,n.geom)
AND w.userid IS NULL
UNION ALL 
SELECT n.geom as geom 
FROM ways_userinput w,drawn_features_union n 
WHERE st_intersects(w.geom,n.geom)
AND w.userid IS NULL
) x

DROP TABLE testtest;
CREATE TABLE testtest AS 
WITH x AS (
	SELECT ST_Union(geom) geom FROM (
	SELECT w.geom as geom 
	FROM ways_userinput w,drawn_features_union n 
	WHERE st_intersects(w.geom,n.geom)
	AND w.userid IS NULL
	UNION ALL 
	SELECT n.geom as geom 
	FROM ways_userinput w,drawn_features_union n 
	WHERE st_intersects(w.geom,n.geom)
	AND w.userid IS NULL) u
)--,
--y AS (
	SELECT st_collectionextract(ST_Intersection(x.geom,d.geom),1) geom
	FROM x, drawn_features_union d 




) i, drawn_features_union x 

ALTER TABLE new_network  add column source integer;
ALTER TABLE new_network  add column target integer;

DELETE FROM new_network
WHERE st_startpoint(geom) IN (SELECT * FROM delete_extended_part);
DELETE FROM new_network
WHERE st_endpoint(geom) IN (SELECT * FROM delete_extended_part);

/*It deletes all parts that are smaller then once centimeter*/
DELETE FROM new_network
WHERE st_length(geom::geography)*100 < 1;

/*Snaps network to unique intersection points in case of multiple very close intersections*/
DROP TABLE IF EXISTS x_y;
CREATE TEMP TABLE x_y AS
SELECT round(st_x(geom)::numeric,7) x,round(st_y(geom)::numeric,7) y, vertex_id,geom 
FROM intersection_existing_network;

DROP TABLE IF EXISTS vertices_to_snap;
CREATE TEMP TABLE vertices_to_snap as
SELECT DISTINCT x.vertex_id, concat(x::varchar,' ',y::varchar), i.geom
FROM  x_y x, intersection_existing_network i
WHERE x.vertex_id <> i.vertex_id
AND round(st_x(i.geom)::numeric,7) = x.x
AND round(st_y(i.geom)::numeric,7) = x.y;

DROP TABLE IF EXISTS vertices_to_keep;
CREATE TEMP TABLE vertices_to_keep AS
SELECT DISTINCT ON (concat) concat, vertex_id, geom 
FROM vertices_to_snap; 

UPDATE new_network SET geom = x.geom from
(
	SELECT t.gid, st_setpoint(t.geom,0,s.geom) geom
	FROM vertices_to_snap v, new_network t, vertices_to_keep s
	WHERE concat(round(substring(st_astext(t.geom), '[0-9. ]+ ')::numeric,7)::varchar,' ',
	round(substring(st_astext(t.geom), ' [0-9. ]+')::numeric,7)::varchar)
	= v.concat
	AND 
	concat(round(substring(st_astext(t.geom), '[0-9. ]+ ')::numeric,7)::varchar,' ',
	round(substring(st_astext(t.geom), ' [0-9. ]+')::numeric,7)::varchar)
	= s.concat
) x
WHERE new_network.gid = x.gid;
UPDATE new_network SET geom = x.geom FROM (
SELECT DISTINCT t.gid,st_setpoint(t.geom, st_npoints(t.geom)-1, s.geom) geom
	FROM vertices_to_snap v, new_network t, vertices_to_keep s
	WHERE concat(round(substring(substring(st_astext(t.geom), '[ 0-9.]+\)'),'[0-9.]+ ')::numeric,7)::varchar,' ',
	round(substring(substring(st_astext(t.geom), '[ 0-9.]+\)'),' [0-9.]+')::numeric,7)::varchar)
	= v.concat
	AND 
	concat(round(substring(substring(st_astext(t.geom), '[ 0-9.]+\)'),'[0-9.]+ ')::numeric,7)::varchar,' ',
	round(substring(substring(st_astext(t.geom), '[ 0-9.]+\)'),' [0-9.]+')::numeric,7)::varchar)
	= s.concat
) x
WHERE new_network.gid = x.gid;

/*Delete all intersection points that are not needed anymore*/
DELETE FROM intersection_existing_network
WHERE vertex_id IN (SELECT vertex_id FROM vertices_to_snap);
INSERT INTO intersection_existing_network
SELECT vertex_id, 133256, geom 
FROM vertices_to_keep;

DELETE FROM intersection_existing_network 
WHERE vertex_id IN
(SELECT vertex_id
FROM intersection_existing_network i, ways_userinput_vertices_pgr v
WHERE v.userid is null AND ST_AsText(i.geom) = ST_AsText(v.geom));


/*Update vertex_ids*/
CREATE TEMP TABLE placeholder_intersection_existing_network AS
SELECT (SELECT max(id) FROM ways_userinput_vertices_pgr) + row_number() over() as vertex_id, userid, geom
FROM intersection_existing_network;
DROP TABLE IF EXISTS intersection_existing_network;
ALTER TABLE placeholder_intersection_existing_network RENAME TO intersection_existing_network; 


--------------------------------EXISTING NETWORK----------------------------------------------------------

--All the lines FROM the existing network which intersect with the draw network are split, this
--is done as a new node now is added	
DROP TABLE IF EXISTS existing_network;
CREATE TABLE existing_network as 
WITH p_n as ( 
	SELECT DISTINCT w.id,w.class_id,w.source,w.target,w.geom
	FROM ways_userinput w, drawn_features i
	WHERE st_intersects(w.geom,i.geom)
	AND w.userid IS NULL
	AND w.id NOT IN (SELECT DISTINCT original_id FROM drawn_features where original_id is not null)
)
--It snaps approx. in a distance of 1 m
SELECT a.class_id,(ST_Dump(ST_Split(ST_Snap(a.geom, b.geom, 0.00001),b.geom))).geom as geom, source,target
FROM 
p_n a, (SELECT ST_Union(geom) geom from intersection_existing_network) b
WHERE ST_DWithin(b.geom, a.geom, 0.00001);


/*Set source and target of existing network*/
UPDATE existing_network set source = x.id 
FROM (
	SELECT v.id,v.geom 
	FROM ways_userinput_vertices_pgr v, existing_network i
	WHERE st_intersects(v.geom,ST_Buffer(i.geom::geography,0.001)::geometry)
	AND v.userid IS NULL
	UNION ALL
	SELECT vertex_id,geom FROM intersection_existing_network
	) x
WHERE st_startpoint(existing_network.geom) = x.geom;



UPDATE existing_network set target = x.id 
FROM (
	SELECT v.id,v.geom 
	FROM ways_userinput_vertices_pgr v, existing_network i
	WHERE st_intersects(v.geom,ST_Buffer(i.geom::geography,0.001)::geometry)
	AND v.userid IS NULL
	UNION ALL
	SELECT vertex_id,geom FROM intersection_existing_network
) x
WHERE st_endpoint(existing_network.geom) = x.geom;

/*Set source and target of new network*/
CREATE TEMP TABLE vertices_to_assign as
WITH start_end AS (
	SELECT ST_StartPoint(geom) geom
	FROM new_network
	UNION ALL
	SELECT ST_EndPoint(geom) geom
	FROM new_network
),
v as (
	SELECT v.id,v.geom 
	FROM ways_userinput_vertices_pgr v, new_network i
	WHERE st_intersects(v.geom,ST_Buffer(i.geom::geography,0.001)::geometry)
	AND v.userid IS NULL
	UNION ALL
	SELECT vertex_id,geom FROM intersection_existing_network
),
vertices_to_remove as
(
	SELECT s.geom 
	from start_end s, v 
	where ST_Intersects(v.geom,ST_Buffer(s.geom::geography,0.001)::geometry)
)
SELECT * FROM v 
UNION ALL 
SELECT (SELECT max(id) FROM v) + row_number() over() as id,geom FROM start_end 
WHERE geom not in (SELECT geom FROM vertices_to_remove); 
	
UPDATE new_network set source = v.id 
FROM vertices_to_assign v
WHERE ST_Intersects(ST_Buffer(ST_StartPoint(new_network.geom)::geography,0.001)::geometry,v.geom);

UPDATE new_network set target = v.id 
FROM vertices_to_assign v
WHERE ST_Intersects(ST_Buffer(ST_EndPoint(new_network.geom)::geography,0.001)::geometry,v.geom);

/*
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

*/


/*
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


DROP TABLE IF EXISTS test;
CREATE TABLE test AS 
SELECT * FROM new_network;
*/

/*

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

*/
----------------------------------------------------------------------------------------------------------------------
--INSERT NEW VERTICES AND WAYS INTO THE EXISTING TABLES
----------------------------------------------------------------------------------------------------------------------

INSERT INTO ways_userinput_vertices_pgr(id,geom,userid)
SELECT va.id::bigint,va.geom,133256 userid
FROM vertices_to_assign va
WHERE va.id >=(SELECT min(vertex_id) from intersection_existing_network); 

/*

insert INTO ways_userinput_vertices_pgr(id,geom,userid)
SELECT distinct *,133256 FROM (
SELECT source::bigint,st_startpoint(geom) FROM new_network
WHERE source not in (SELECT vertex_id FROM intersection_existing_network)
UNION ALL
SELECT target::bigint,st_endpoint(geom) FROM new_network
WHERE target not in (SELECT vertex_id FROM intersection_existing_network)) x;
*/
INSERT INTO ways_userinput(id,class_id,source,target,geom,userid)
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),class_id,source,target,geom,133256 FROM new_network;

INSERT INTO ways_userinput(id,class_id,source,target,geom,userid) 
SELECT (SELECT max(id) FROM ways_userinput) + row_nSELECT * FROM ways_modifiedumber() over(),class_id,source,target,geom,133256 FROM existing_network;

UPDATE ways_userinput 
set length_m = st_length(geom::geography)
WHERE length_m IS NULL;

--DELETE FROM ways_userinput WHERE source IS NULL OR target IS NULL;

---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------


END
$function$

SELECT * FROM ways_userinput

