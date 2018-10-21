CREATE OR REPLACE FUNCTION public.insert_into_network_bridge(input_userid integer)
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
   cnt integer;
BEGIN
   

   
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
AND way_type = 'Bridge'
limit 1;


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
	AND w.userid IS NULL OR w.userid = input_userid
	AND ST_GeometryType(st_intersection(u.geometry,w.geom)) = 'ST_Point'
	UNION ALL
	SELECT w.id as ways_id,u.userid, (st_dump(st_intersection(u.geometry,w.geom))).geom as geom 
	FROM user_input_network u,ways_userinput w
	WHERE ST_GeometryType(st_intersection(u.geometry,w.geom)) ='ST_MultiPoint'
	AND w.userid IS NULL OR w.userid = input_userid
	AND st_intersects(u.geometry,w.geom)) x;

	
delete FROM intersection_test WHERE
ST_GeometryType(geom) <> 'ST_Point';	
	
delete FROM intersection_test WHERE geom not in(
SELECT * FROM (
SELECT * FROM (SELECT i.geom 
FROM intersection_test i,	
(SELECT st_startpoint(geometry) geom FROM user_input_network) x
ORDER by st_distance(i.geom,x.geom)
limit 1) x

UNION ALL 

SELECT * FROM (SELECT i.geom 
FROM intersection_test i,	
(SELECT st_endpoint(geometry) geom FROM user_input_network) x
ORDER by st_distance(i.geom,x.geom)
limit 1) x) z);


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

delete FROM dump_geometries WHERE geom not in (
SELECT d.geom FROM dump_geometries d, intersection_test i WHERE st_intersects(d.geom,i.geom));

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


----------------------------------------------------------------------------------------------------------------------
--INSERT NEW VERTICES AND WAYS INTO THE EXISTING TABLES
----------------------------------------------------------------------------------------------------------------------


insert INTO ways_userinput_vertices_pgr(id,geom,userid)
SELECT vertex_id::bigint,geom,input_userid FROM intersection_test;



insert INTO ways_userinput(id,source,target,geom,userid)
SELECT (SELECT max(id) FROM ways_userinput) + row_number() over(),
vertex_1.vertex_id,vertex_2.vertex_id,ST_MakeLine(vertex_1.geom,vertex_2.geom )geom,input_userid 
FROM (SELECT * FROM intersection_test ORDER by vertex_id asc limit 1) vertex_1,
(SELECT * FROM intersection_test ORDER by vertex_id desc limit 1) vertex_2;

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
---------------------------------------------------------------------------------------------------------------------


END
$function$
