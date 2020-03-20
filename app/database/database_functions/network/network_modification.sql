DROP FUNCTION IF EXISTS network_modification;
CREATE OR REPLACE FUNCTION public.network_modification(input_userid integer)
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
   cnt integer;
   count_bridges integer;
BEGIN
   
DELETE FROM ways_userinput WHERE userid = input_userid;
DELETE FROM ways_userinput_vertices_pgr WHERE userid = input_userid; 
DROP TABLE IF EXISTS drawn_features, existing_network, intersection_existing_network, drawn_features_union, new_network, delete_extended_part, vertices_to_assign; 

--Update ways_modified status column "1 == added"
UPDATE ways_modified SET status = 1 WHERE userid = input_userid;


CREATE TEMP TABLE drawn_features as
SELECT id,geom,class_id,userid, original_id, type  FROM ways_modified
WHERE userid = input_userid;



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
FROM extend_both_parts b, ways_userinput w
WHERE drawn_features.id = b.id;


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

--Split the new lines WHERE they intersect with the new network
DROP TABLE IF EXISTS new_network;
CREATE TEMP TABLE new_network as
SELECT row_number() over() as gid,NULL AS class_id, NULL AS type, NULL AS mother_id, geom 
FROM(
	SELECT DISTINCT (st_dump(ST_CollectionExtract(st_split(x.geom,i.geom),2))).geom as geom
	FROM 
	(SELECT st_union(w.geom) as geom 
	FROM ways_userinput w,drawn_features_union n 
	WHERE st_intersects(w.geom,n.geom)
	AND w.userid IS NULL) i,
	drawn_features_union x) t 
WHERE st_length(geom::geography) <> 0;

/*It deletes all parts that are smaller then once centimeter*/
DELETE FROM new_network
WHERE st_length(geom::geography)*100 < 1;

/*It takes the class_id from way_modified. For splitting the network a union is done accordingly the class_id can not be kept.
 The following query creating a little buffer for the intersection as the line to line intersection was not working as expected. */
WITH y as (
	SELECT geom,st_buffer(geom::geography,0.01)::geometry buffer, class_id, type, id AS mother_id
	FROM ways_modified
	WHERE userid = input_userid
),
z as(
	SELECT x.geom, y.class_id, x.gid, y.type, y.mother_id, ST_length(ST_intersection(y.buffer,x.geom)::geography)--st_intersection(st_buffer(d.geom,0.0000001),x.geom), st_length(st_intersection(st_buffer(d.geom,0.0000001),x.geom))
	FROM y, new_network x
	WHERE st_intersects(y.buffer,x.geom)
	AND  ST_length(ST_intersection(y.buffer,x.geom)::geography) > 0.1
),
zz as(
	SELECT DISTINCT z.class_id,z.gid, z.type, z.mother_id FROM z,
	(
		SELECT gid, max(st_length) st_length
		FROM z
		GROUP BY gid
	) m
	WHERE z.gid = m.gid 
	AND z.st_length = m.st_length
)
UPDATE new_network SET class_id = zz.class_id, type = zz.type, mother_id = zz.mother_id
FROM zz 
WHERE new_network.gid = zz.gid;

/*Use the not unsplit geometry in case of a bridge or underpass*/
UPDATE new_network SET geom = m.geom
FROM ways_modified m 
WHERE new_network.type = 'bridge'
AND new_network.mother_id = m.id::varchar;

DROP TABLE IF EXISTS new_network_temp;
CREATE TEMP TABLE new_network_temp AS 
SELECT DISTINCT ON (geom) geom, gid, class_id, type  
FROM new_network;
DROP TABLE new_network;
ALTER TABLE new_network_temp RENAME TO new_network;


ALTER TABLE new_network  add column source integer;
ALTER TABLE new_network  add column target integer;
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
SELECT vertex_id, input_userid, geom 
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
SELECT a.id AS original_id, a.class_id,(ST_Dump(ST_Split(ST_Snap(a.geom, b.geom, 0.00001),b.geom))).geom as geom, source,target
FROM 
p_n a, (SELECT ST_Union(geom) geom from intersection_existing_network) b
WHERE ST_DWithin(b.geom, a.geom, 0.00001);


/*Set source and target of existing network*/
UPDATE existing_network set source = x.id 
FROM (

	SELECT v.id,v.geom 
	FROM ways_userinput_vertices_pgr v, existing_network i
	WHERE v.geom && ST_Buffer(i.geom::geography,0.001)::geometry
	AND v.userid IS NULL
	
	
	UNION ALL
	SELECT vertex_id,geom FROM intersection_existing_network
	) x
WHERE st_startpoint(existing_network.geom) = x.geom;


UPDATE existing_network set target = x.id 
FROM (
	SELECT v.id,v.geom 
	FROM ways_userinput_vertices_pgr v, existing_network i
	WHERE v.geom && ST_Buffer(i.geom::geography,0.001)::geometry
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
	WHERE v.geom && ST_Buffer(i.geom::geography,0.001)::geometry
	AND v.userid IS NULL
	UNION ALL
	SELECT vertex_id,geom FROM intersection_existing_network
),
vertices_to_remove as
(
	SELECT s.geom 
	FROM start_end s, v 
	WHERE v.geom && ST_Buffer(s.geom::geography,0.001)::geometry
)
SELECT * FROM v 
UNION ALL 
SELECT (SELECT max(id) FROM v) + row_number() over() as id,geom FROM start_end 
WHERE geom not in (SELECT geom FROM vertices_to_remove); 
	
UPDATE new_network set source = v.id 
FROM vertices_to_assign v
WHERE ST_Buffer(ST_StartPoint(new_network.geom)::geography,0.001)::geometry && v.geom;

UPDATE new_network set target = v.id 
FROM vertices_to_assign v
WHERE ST_Buffer(ST_EndPoint(new_network.geom)::geography,0.001)::geometry && v.geom;


----------------------------------------------------------------------------------------------------------------------
--INSERT NEW VERTICES AND WAYS INTO THE EXISTING TABLES
----------------------------------------------------------------------------------------------------------------------

INSERT INTO ways_userinput_vertices_pgr(id,geom,userid)
SELECT va.id::bigint,va.geom,input_userid userid
FROM vertices_to_assign va
WHERE va.id >=(SELECT min(vertex_id) from intersection_existing_network); 

INSERT INTO ways_userinput(id,class_id,source,target,geom,userid)
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),coalesce(class_id::integer,100),source,target,geom,input_userid FROM new_network;

INSERT INTO ways_userinput(id,class_id,source,target,geom,userid, original_id) 
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),coalesce(class_id::integer,100),source,target,geom,input_userid, original_id FROM existing_network;

UPDATE ways_userinput 
set length_m = st_length(geom::geography)
WHERE length_m IS NULL;

---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------

END
$function$