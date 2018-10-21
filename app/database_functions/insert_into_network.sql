CREATE OR REPLACE FUNCTION public.insert_into_network(input_userid integer)
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
   cnt integer;
   count_bridges integer;
BEGIN
   
	delete FROM ways_userinput WHERE userid = input_userid;
	delete FROM ways_userinput_vertices_pgr WHERE userid = input_userid;
   
   
-----------------------------------------------------------------------------------
-----------------------------------------------------------------------------------
-----------------------------------------------------------------------------------

--Drop all the temporary tables
DROP TABLE IF EXISTS intersection_test;
DROP TABLE IF EXISTS dump_geometries;
DROP TABLE IF EXISTS test_multi;
DROP TABLE IF EXISTS user_input_network_union; 
DROP TABLE IF EXISTS test_modi;
DROP TABLE IF EXISTS pre_network;
DROP TABLE IF EXISTS vertices_not_intersection;
DROP TABLE IF EXISTS testtest;
DROP TABLE IF EXISTS new_test;
DROP TABLE IF EXISTS final;
DROP TABLE IF EXISTS xxx;
DROP TABLE IF EXISTS user_input_network;




CREATE TABLE user_input_network as
SELECT gid,geometry,userid  FROM input_network
WHERE userid = input_userid
AND way_type = 'Street';


--Extends drawn lines by a distance of approx. 1 meter
CREATE TABLE test_modi as 
SELECT u.gid,st_addpoint(u.geometry,end_point,-1) as geom
FROM
--Line is extended on the end_point part
(SELECT gid,st_translate(a,sin(azimuth) * newlength,cos(azimuth) * newlength) as end_point
FROM
	--Calculates a extended distance of the line
	(SELECT gid,a,b,st_azimuth(a,b) azimuth,st_distance(a,b) as length,
	(st_distance(a,b) + (st_distance(a,b)*(0.00000957046/st_distance(a,b)))) as newlength
	FROM
		-- Extracts the starting AND end point of each line
		(SELECT gid,st_startpoint(geometry) a,st_endpoint(geometry) b
		FROM user_input_network) x
	) y
) z,
user_input_network u
WHERE z.gid=u.gid;

--Does the same as above but extends on the side of the starting point AND UPDATEs the input geometry

UPDATE user_input_network set geometry = x.geom
FROM
(SELECT u.gid,st_addpoint(u.geom,start_point,0) geom
	FROM
	(SELECT gid,st_translate(a,sin(azimuth) * newlength,cos(azimuth) * newlength) as start_point
	FROM
	(SELECT gid,a,b,st_azimuth(a,b) azimuth,st_distance(a,b) as length,
	(st_distance(a,b) + (st_distance(a,b)*(0.00000957046/st_distance(a,b)))) as newlength
	FROM
		(SELECT gid,st_startpoint(geometry) b,st_endpoint(geometry) a
		FROM user_input_network) x) 
		y) 
	t,test_modi u
WHERE t.gid=u.gid) x
WHERE user_input_network.gid = x.gid;


--All Points WHERE the drawn geometry intersects the existing network are extracted (=new vertices)
CREATE TABLE intersection_test as
SELECT (SELECT max(id) FROM ways_userinput_vertices_pgr) + row_number() over() as vertex_id,* 
FROM (
	SELECT w.id as ways_id,u.userid,st_intersection(u.geometry,w.geom) as geom 
	FROM user_input_network u,ways_userinput w 
	WHERE st_intersects(u.geometry,w.geom)
	AND w.userid IS NULL
	AND ST_GeometryType(st_intersection(u.geometry,w.geom)) = 'ST_Point'
	UNION ALL
	SELECT w.id as ways_id,u.userid, (st_dump(st_intersection(u.geometry,w.geom))).geom as geom 
	FROM user_input_network u,ways_userinput w
	WHERE ST_GeometryType(st_intersection(u.geometry,w.geom)) ='ST_MultiPoint'
	AND w.userid IS NULL
	AND st_intersects(u.geometry,w.geom)) x;


----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
--------------------------------EXISTING NETWorK----------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------	
--All the lines FROM the existing network which intersect with the draw network are split, this
--is done as a new node now is added	
-----------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!-------------------------------
-----------Has to be replaced by a function-----------
perform * FROM split_existing_network();




CREATE TABLE dump_geometries as 
SELECT distinct * FROM pre_network;  

UPDATE dump_geometries set source = x.id 
FROM (
SELECT v.id,v.geom 
FROM ways_userinput_vertices_pgr v, pre_network i
WHERE st_intersects(v.geom,i.geom)
AND v.userid IS NULL
UNION ALL
SELECT vertex_id,geom FROM intersection_test) x
WHERE st_startpoint(dump_geometries.geom) = x.geom;


UPDATE dump_geometries set target = x.id 
FROM (
SELECT v.id,v.geom 
FROM ways_userinput_vertices_pgr v, pre_network i
WHERE st_intersects(v.geom,i.geom)
AND v.userid IS NULL
UNION ALL
SELECT vertex_id,geom FROM intersection_test) x
WHERE st_endpoint(dump_geometries.geom) = x.geom;

----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
--------------------------------NEW NETWorK----------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------	
	
	

--Unions the input geometry so each linestring on the next step is split by the whole the geometries as a whole
--It is checked how many geometries are inserted by the user. If only one the can be no intersection between the inserted lines.


SELECT count(*) INTO cnt
  FROM input_network
  WHERE userid = input_userid AND way_type = 'Street';

IF cnt = 1 THEN
    CREATE TABLE user_input_network_union as
    SELECT geometry as geom
    FROM input_network
    WHERE userid = input_userid AND way_type = 'Street';

ELSE

	    --Split_userinput is a funtion which needs userid as input
	CREATE TABLE user_input_network_union as
	SELECT st_union(split_userinput) as geom 
	FROM split_userinput(input_userid);

END IF;
	--Split the new lines WHERE they intersect with the new network
	CREATE TABLE testtest as
	SELECT row_number() over() as gid,geom 
	FROM(
		SELECT (st_dump(ST_CollectionExtract(st_split(x.geom,i.geom),2))).geom as geom
		FROM 
		(SELECT st_union(w.geom) as geom 
		FROM ways_userinput w,user_input_network_union n 
		WHERE st_intersects(w.geom,n.geom)
		AND w.userid IS NULL) i,
		user_input_network_union x) t 
	WHERE st_length(geom::geography) <> 0;
 	





--For each line the start AND endpoint is created AND saved 
CREATE TABLE final as
SELECT distinct t.geom geom ,_1,_2,i.geom point,vertex_id
	FROM (SELECT geom,st_startpoint(geom) _1, st_endpoint(geom) _2
	FROM testtest) t,
	intersection_test i
WHERE st_astext(i.geom) = st_astext(t._1)
OR st_astext(i.geom) = st_astext(t._2);


ALTER TABLE testtest add column source integer;
ALTER TABLE testtest add column target integer;


--All new edges which have one intersecting point with the already existing network are SELECTed 
--AND the corresponding vertex is SELECTed
UPDATE testtest set source = x.vertex_id 
FROM (
SELECT geom, vertex_id,_2 point FROM final WHERE geom  
in(
	SELECT t.geom geom 
	FROM (SELECT geom,st_startpoint(geom) _1, st_endpoint(geom) _2
	FROM testtest) t,
	intersection_test i
	WHERE st_astext(i.geom) = st_astext(t._1)
	OR st_astext(i.geom) = st_astext(t._2)
	GROUP BY t.geom
	having count(*) = 1)
AND _1 = point) x
WHERE testtest.geom = x.geom;

UPDATE testtest set target = x.vertex_id 
FROM(
SELECT geom, vertex_id,_1 as point FROM final WHERE geom  
in(
	SELECT t.geom geom 
	FROM (SELECT geom,st_startpoint(geom) _1, st_endpoint(geom) _2
	FROM testtest) t,
	intersection_test i
	WHERE st_astext(i.geom) = st_astext(t._1)
	OR st_astext(i.geom) = st_astext(t._2)
	GROUP BY t.geom
	having count(*) = 1)
AND _2 = point) x
WHERE testtest.geom = x.geom;


-- All lines, which have two intersection points with the existing network are assigned with vertices

--First the source vertext is assign AND put INTO a new preliminary table 
CREATE TABLE xxx as
SELECT t.geom geom,i.vertex_id as source
FROM (SELECT geom,st_startpoint(geom) _1
	FROM 
	(SELECT distinct t.* FROM testtest t,intersection_test i
	WHERE source IS NULL AND target IS NULL
	AND st_intersects(i.geom,t.geom)) x
	) t,
	intersection_test i
--geometries are compared as text
	WHERE st_astext(i.geom) = st_astext(t._1);

			
ALTER TABLE xxx add column target integer;

--Afterwards the target is UPDATEd as well
UPDATE xxx set target = x.target 
FROM (SELECT t.geom geom,i.vertex_id as target
FROM (SELECT geom, st_endpoint(geom) _2
	FROM 
	(SELECT distinct t.* FROM testtest t,intersection_test i
	WHERE source IS NULL AND target IS NULL
	AND st_intersects(i.geom,t.geom)) x
	) t,
	intersection_test i
--geometries are compared as text
	WHERE st_astext(i.geom) = st_astext(t._2))x
WHERE xxx.geom = x.geom;



UPDATE testtest set source = xxx.source, target = xxx.target
FROM xxx
WHERE testtest.geom = xxx.geom;


--All new lines which are not interseting with the already existing network are getting new vertices as well
CREATE TABLE vertices_not_intersection as
SELECT y.st_startpoint as vertex,
--SELECT the max vertex_id so far
(SELECT max(max) FROM (
SELECT max(source) FROM testtest
UNION ALL 
SELECT max(target) FROM testtest) x) + row_number() over() as vertex_id
---------------------------------------------------------
FROM 
--SELECTs distinct vertices 
	(SELECT distinct *
	FROM (
		SELECT st_startpoint(geom),source 
		FROM testtest
		WHERE source IS NULL
		UNION ALL
		SELECT st_endpoint(geom),target 
		FROM testtest
		WHERE target IS NULL) x
	) y;
	
UPDATE testtest set source = v.vertex_id
FROM vertices_not_intersection v
WHERE st_startpoint(geom) = v.vertex;

UPDATE testtest set target = v.vertex_id
FROM vertices_not_intersection v
WHERE st_endpoint(geom) = v.vertex;

--Delte those WHERE source AND target are so close to each other that they are identical 
delete FROM testtest 
WHERE source=target;


----------------------------------------------------------------------------------------------------------------------
--INSERT NEW VERTICES AND WAYS INTO THE EXISTING TABLES
----------------------------------------------------------------------------------------------------------------------


insert INTO ways_userinput_vertices_pgr(id,geom,userid)
SELECT vertex_id::bigint,geom,input_userid FROM intersection_test;

insert INTO ways_userinput_vertices_pgr(id,geom,userid)
SELECT distinct *,input_userid FROM (
SELECT source::bigint,st_startpoint(geom) FROM testtest
WHERE source not in (SELECT vertex_id FROM intersection_test)
UNION ALL
SELECT target::bigint,st_endpoint(geom) FROM testtest
WHERE target not in (SELECT vertex_id FROM intersection_test)) x;

insert INTO ways_userinput(id,source,target,geom,userid)
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),source,target,geom,input_userid FROM testtest;

insert INTO ways_userinput(id,source,target,geom,userid) 
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),source,target,geom,input_userid FROM dump_geometries;

UPDATE ways_userinput 
set length_m = st_length(geom::geography)
WHERE length_m IS NULL
AND userid = input_userid;

--------------------------------------------------------------------------------------------------------------------
--CLEAN 
--------------------------------------------------------------------------------------------------------------------

--Drop all the temporary tables
DROP TABLE IF EXISTS intersection_test;
--DROP TABLE IF EXISTS dump_geometries;
DROP TABLE IF EXISTS test_multi;
DROP TABLE IF EXISTS user_input_network_union; 
DROP TABLE IF EXISTS test_modi;
DROP TABLE IF EXISTS pre_network;
DROP TABLE IF EXISTS vertices_not_intersection;
--DROP TABLE IF EXISTS testtest;
DROP TABLE IF EXISTS new_test;
DROP TABLE IF EXISTS final;
DROP TABLE IF EXISTS xxx;
DROP TABLE IF EXISTS user_input_network;

---------------------------------------------------------------------------------------------------------------------
SELECT count(*) INTO count_bridges
  FROM input_network
  WHERE userid = input_userid AND way_type = 'Bridge';

IF count_bridges = 1 THEN
perform insert_into_network_bridge(input_userid);
END IF;

delete FROM ways_userinput WHERE source IS NULL OR target IS NULL;

---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------


END
$function$
