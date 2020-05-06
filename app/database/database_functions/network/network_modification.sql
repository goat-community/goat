
DROP FUNCTION IF EXISTS network_modification;
CREATE OR REPLACE FUNCTION public.network_modification(userid_input integer)
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
   cnt integer;
   count_bridges integer;
BEGIN

DELETE FROM ways_userinput WHERE userid = userid_input;
DELETE FROM ways_userinput_vertices_pgr WHERE userid = userid_input; 
DROP TABLE IF EXISTS drawn_features, existing_network, intersection_existing_network, drawn_features_union, new_network, delete_extended_part, vertices_to_assign; 

--Update ways_modified status column "1 == added"
UPDATE ways_modified SET status = 1 WHERE userid = userid_input;

CREATE TEMP TABLE drawn_features as
SELECT id, extend_line(geom, 0.00001) AS geom, way_type, surface, wheelchair, street_category, userid, original_id 
FROM ways_modified
WHERE userid = userid_input;

/*Intersects with the existing network and creates a table with new vertices.*/

DROP TABLE IF EXISTS pre_intersection_points;
CREATE TEMP TABLE pre_intersection_points AS 
SELECT st_intersection(d.geom,w.geom) AS geom, d.geom AS d_geom
FROM drawn_features d, ways_userinput w 
WHERE ST_INtersects(d.geom,w.geom);

DROP TABLE IF EXISTS intersection_existing_network;
CREATE TEMP TABLE intersection_existing_network AS 
SELECT (SELECT max(id) FROM ways_userinput_vertices_pgr) + row_number() over() as vertex_id, userid_input userid, geom, d_geom 
FROM (SELECT DISTINCT (ST_DUMPpoints(geom)).geom AS geom, d_geom FROM pre_intersection_points) x;

ALTER TABLE intersection_existing_network ADD COLUMN gid serial;
ALTER TABLE intersection_existing_network ADD PRIMARY key(gid);

DROP TABLE IF EXISTS split_drawn_features;

/*Split network with itself*/
SELECT count(*) INTO cnt
FROM drawn_features
LIMIT 2;

IF cnt = 1 THEN
    CREATE TEMP TABLE split_drawn_features as
    SELECT geom, way_type, surface, wheelchair, street_category, userid, original_id  
	FROM drawn_features;
ELSE 
	CREATE TEMP TABLE split_drawn_features AS
	SELECT split_by_drawn_lines(id::integer,geom) AS geom, way_type, surface, wheelchair, street_category, userid, original_id  
	FROM drawn_features;
	--WHERE way_type <> 'bridge';

END IF;

/*Split new network with existing network*/
DROP TABLE IF EXISTS new_network;
CREATE TEMP TABLE new_network AS
WITH union_existing_network AS 
(
	SELECT ST_UNION(w.geom) AS geom 	
	FROM ways_userinput w, split_drawn_features d 
	WHERE ST_INtersects(d.geom,w.geom)
),
dump AS (
	SELECT ST_DUMP(ST_CollectionExtract(ST_SPLIT(d.geom,w.geom),2)) AS geom,  
	way_type, surface, wheelchair, street_category, userid, original_id  
	FROM split_drawn_features d, union_existing_network w
) 
SELECT (geom).geom, way_type, surface, wheelchair, street_category, userid, original_id
FROM dump; 

ALTER TABLE new_network ADD COLUMN gid serial;

/*It deletes all parts that are smaller then once centimeter*/
DELETE FROM new_network
WHERE st_length(geom) < 0.000001;
/*
INSERT INTO new_network 
SELECT geom, way_type, surface, wheelchair, street_category, userid, original_id 
FROM drawn_features
WHERE way_type = 'bridge';
*/
ALTER TABLE new_network ADD COLUMN source integer;
ALTER TABLE new_network ADD COLUMN target integer;

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
SELECT vertex_id, userid_input, geom 
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
--is done as a new node now is added. This here has to be refactored as the code above!	
DROP TABLE IF EXISTS existing_network;
CREATE TEMP TABLE existing_network as 
WITH p_n as ( 
	SELECT DISTINCT w.id,w.class_id,w.source,w.target,w.geom, lit_classified, wheelchair_classified, impedance_surface
	FROM ways_userinput w, drawn_features i
	WHERE st_intersects(w.geom,i.geom)
	AND w.userid IS NULL
	AND w.id NOT IN (SELECT DISTINCT original_id FROM drawn_features where original_id is not null)
),
dump AS (
	SELECT a.id AS original_id, a.class_id,ST_Dump(ST_Split(a.geom, b.geom)) as dump, source,target,
	lit_classified, wheelchair_classified, impedance_surface
	FROM 
	p_n a, (SELECT ST_Union(geom) geom from drawn_features) b
	WHERE ST_DWithin(b.geom, a.geom, 0.00001)
)
SELECT original_id, class_id, (dump).geom, source,target, lit_classified, wheelchair_classified, impedance_surface
FROM dump;


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
SELECT va.id::bigint,va.geom,userid_input userid
FROM vertices_to_assign va
WHERE va.id >=(SELECT min(vertex_id) from intersection_existing_network); 

INSERT INTO ways_userinput(id,class_id,source,target,surface,wheelchair_classified,geom,userid)
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),100,source,target,surface,wheelchair,geom,userid_input FROM new_network;

INSERT INTO ways_userinput(id,class_id,source,target,wheelchair_classified, lit_classified,impedance_surface, geom,userid, original_id) 
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),100,source,target,wheelchair_classified, lit_classified,impedance_surface,geom,userid_input, original_id FROM existing_network;

UPDATE ways_userinput 
set length_m = st_length(geom::geography)
WHERE length_m IS NULL;
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------

END
$function$