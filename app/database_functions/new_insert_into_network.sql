DROP TABLE IF EXISTS drawn_features;
DROP TABLE IF EXISTS existing_network;
DROP TABLE IF EXISTS intersection_existing_network;

CREATE TEMP TABLE drawn_features as
SELECT id,geom,class_id,userid  FROM ways_modified
WHERE userid = 1154498;

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



--All Points WHERE the drawn geometry intersects the existing network are extracted (=new vertices)
CREATE TEMP TABLE intersection_existing_network as
SELECT (SELECT max(id) FROM ways_userinput_vertices_pgr) + row_number() over() as vertex_id,* 
FROM (
	
	SELECT w.id as ways_id,i.userid,st_intersection(i.geom,w.geom) as geom 
	FROM drawn_features i,ways_userinput w 
	WHERE st_intersects(i.geom,w.geom)
	AND w.userid IS NULL
	AND ST_geometrytype(st_intersection(i.geom,w.geom)) = 'ST_Point'
	UNION ALL
	SELECT w.id as ways_id,i.userid, (st_dump(st_intersection(i.geom,w.geom))).geom as geom 
	FROM drawn_features i,ways_userinput w
	WHERE ST_geometryType(st_intersection(i.geom,w.geom)) ='ST_MultiPoint'
	AND w.userid IS NULL
	AND st_intersects(i.geom,w.geom)
) x
;


----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
--------------------------------EXISTING NETWorK----------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------	
--All the lines FROM the existing network which intersect with the draw network are split, this
--is done as a new node now is added	

SELECT * FROM split_existing_network()


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



--Unions the input geometry so each linestring on the next step is split by the whole the geometries as a whole
--It is checked how many geometries are inserted by the user. If only one the can be no intersection between the inserted lines.


SELECT count(*) INTO cnt
FROM drawn_features


IF cnt = 1 THEN
    CREATE TEMP TABLE drawn_features_union as
    SELECT geometry as geom
    FROM drawn_features
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
CREATE TABLE xxx as

WITH two_intersections as(
	SELECT t.geom geom,i.vertex_id AS source, 0 target
	FROM (
		SELECT geom,st_startpoint(geom) _1
		FROM 
		(
			SELECT distinct t.* FROM testtest t,intersection_existing_network i
			WHERE source IS NULL AND target IS NULL
			AND st_intersects(i.geom,t.geom)) x
		) t,
		intersection_existing_network i
	--geometries are compared as text
	WHERE st_astext(i.geom) = st_astext(t._1)
),
update_1 as(
		--Afterwards the target is UPDATEd as well
	UPDATE two_intersections set target = x.target 
	FROM (
		SELECT t.geom geom,i.vertex_id as target
		FROM (
			SELECT geom, st_endpoint(geom) _2
			FROM 
			(
				SELECT distinct t.* FROM testtest t,intersection_existing_network i
				WHERE source IS NULL AND target IS NULL
				AND st_intersects(i.geom,t.geom)) x
			) t,intersection_existing_network i
	--geometries are compared as text
		WHERE st_astext(i.geom) = st_astext(t._2)
		)x
	WHERE two_intersections.geom = x.geom

) 
UPDATE new_network set source = two_intersections.source, target = two_intersections.target
FROM two_intersections
WHERE testtest.geom = two_intersections.geom;