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
drop table if exists intersection_test;
drop table if exists dump_geometries;
drop table if exists test_multi;
drop table if exists user_input_network_union; 
drop table if exists test_modi;
drop table if exists pre_network;
drop table if exists vertices_not_intersection;
drop table if exists testtest;
drop table if exists new_test;
drop table if exists final;
drop table if exists xxx;
drop table if exists user_input_network;




create table user_input_network as
select gid,geometry,userid  from input_network
where userid = input_userid
and way_type = 'Bridge'
limit 1;


--Extends drawn lines by a distance of approx. 1 meter
create table test_modi as 
select u.gid,st_addpoint(u.geometry,end_point,-1) as geom
from
--Line is extended on the end_point part
(select gid,st_translate(a,sin(azimuth) * newlength,cos(azimuth) * newlength) as end_point
from
	--Calculates a extended distance of the line
	(select gid,a,b,st_azimuth(a,b) azimuth,st_distance(a,b) as length,
	(st_distance(a,b) + (st_distance(a,b)*(0.00000957046/st_distance(a,b)))) as newlength
	from
		-- Extracts the starting and end point of each line
		(select gid,st_startpoint(geometry) a,st_endpoint(geometry) b
		from user_input_network) x
	) y
) z,
user_input_network u
where z.gid=u.gid;

--Does the same as above but extends on the side of the starting point and updates the input geometry

update user_input_network set geometry = x.geom
from
(select u.gid,st_addpoint(u.geom,start_point,0) geom
	from
	(select gid,st_translate(a,sin(azimuth) * newlength,cos(azimuth) * newlength) as start_point
	from
	(select gid,a,b,st_azimuth(a,b) azimuth,st_distance(a,b) as length,
	(st_distance(a,b) + (st_distance(a,b)*(0.00000957046/st_distance(a,b)))) as newlength
	from
		(select gid,st_startpoint(geometry) b,st_endpoint(geometry) a
		from user_input_network) x) 
		y) 
	t,test_modi u
where t.gid=u.gid) x
where user_input_network.gid = x.gid;


--All Points where the drawn geometry intersects the existing network are extracted (=new vertices)
create table intersection_test as
select (select max(id) from ways_userinput_vertices_pgr) + row_number() over() as vertex_id,* 
from (
	select w.id as ways_id,u.userid,st_intersection(u.geometry,w.geom) as geom 
	from user_input_network u,ways_userinput w 
	where st_intersects(u.geometry,w.geom)
	and w.userid is null or w.userid = input_userid
	and ST_GeometryType(st_intersection(u.geometry,w.geom)) = 'ST_Point'
	union all
	select w.id as ways_id,u.userid, (st_dump(st_intersection(u.geometry,w.geom))).geom as geom 
	from user_input_network u,ways_userinput w
	where ST_GeometryType(st_intersection(u.geometry,w.geom)) ='ST_MultiPoint'
	and w.userid is null or w.userid = input_userid
	and st_intersects(u.geometry,w.geom)) x;

	
delete from intersection_test where
ST_GeometryType(geom) <> 'ST_Point';	
	
delete from intersection_test where geom not in(
select * from (
select * from (select i.geom 
from intersection_test i,	
(select st_startpoint(geometry) geom from user_input_network) x
order by st_distance(i.geom,x.geom)
limit 1) x

union all 

select * from (select i.geom 
from intersection_test i,	
(select st_endpoint(geometry) geom from user_input_network) x
order by st_distance(i.geom,x.geom)
limit 1) x) z);


----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
--------------------------------EXISTING NETWORK----------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------	
--All the lines from the existing network which intersect with the draw network are split, this
--is done as a new node now is added	
-----------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!-------------------------------
-----------Has to be replaced by a function-----------
perform * from split_existing_network();

create table dump_geometries as 
select distinct * from pre_network;  

delete from dump_geometries where geom not in (
select d.geom from dump_geometries d, intersection_test i where st_intersects(d.geom,i.geom));

update dump_geometries set source = x.id 
from (
select v.id,v.geom 
from ways_userinput_vertices_pgr v, pre_network i
where st_intersects(v.geom,i.geom)
and v.userid is null
union all
select vertex_id,geom from intersection_test) x
where st_startpoint(dump_geometries.geom) = x.geom;


update dump_geometries set target = x.id 
from (
select v.id,v.geom 
from ways_userinput_vertices_pgr v, pre_network i
where st_intersects(v.geom,i.geom)
and v.userid is null
union all
select vertex_id,geom from intersection_test) x
where st_endpoint(dump_geometries.geom) = x.geom;


----------------------------------------------------------------------------------------------------------------------
--INSERT NEW VERTICES AND WAYS INTO THE EXISTING TABLES
----------------------------------------------------------------------------------------------------------------------


insert into ways_userinput_vertices_pgr(id,geom,userid)
select vertex_id::bigint,geom,input_userid from intersection_test;



insert into ways_userinput(id,source,target,geom,userid)
select (select max(id) from ways_userinput) + row_number() over(),
vertex_1.vertex_id,vertex_2.vertex_id,ST_MakeLine(vertex_1.geom,vertex_2.geom )geom,input_userid 
from (select * from intersection_test order by vertex_id asc limit 1) vertex_1,
(select * from intersection_test order by vertex_id desc limit 1) vertex_2;

insert into ways_userinput(id,source,target,geom,userid) 
select (select max(id) from ways_userinput) + row_number() over(),source,target,geom,input_userid from dump_geometries;

update ways_userinput 
set length_m = st_length(geom::geography)
where length_m is null
and userid = input_userid;



--------------------------------------------------------------------------------------------------------------------
--CLEAN 
--------------------------------------------------------------------------------------------------------------------

--Drop all the temporary tables
drop table if exists intersection_test;
--drop table if exists dump_geometries;
drop table if exists test_multi;
drop table if exists user_input_network_union; 
drop table if exists test_modi;
drop table if exists pre_network;
drop table if exists vertices_not_intersection;
--drop table if exists testtest;
drop table if exists new_test;
drop table if exists final;
drop table if exists xxx;
drop table if exists user_input_network;

---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------


END
$function$
