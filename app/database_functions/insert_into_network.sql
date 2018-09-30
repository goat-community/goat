CREATE OR REPLACE FUNCTION public.insert_into_network(input_userid integer)
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
   cnt integer;
   count_bridges integer;
BEGIN
   
	delete from ways_userinput where userid = input_userid;
	delete from ways_userinput_vertices_pgr where userid = input_userid;
   
   
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
and way_type = 'Street';


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
	and w.userid is null
	and ST_GeometryType(st_intersection(u.geometry,w.geom)) = 'ST_Point'
	union all
	select w.id as ways_id,u.userid, (st_dump(st_intersection(u.geometry,w.geom))).geom as geom 
	from user_input_network u,ways_userinput w
	where ST_GeometryType(st_intersection(u.geometry,w.geom)) ='ST_MultiPoint'
	and w.userid is null
	and st_intersects(u.geometry,w.geom)) x;


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

----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
--------------------------------NEW NETWORK----------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------	
	
	

--Unions the input geometry so each linestring on the next step is split by the whole the geometries as a whole
--It is checked how many geometries are inserted by the user. If only one the can be no intersection between the inserted lines.


SELECT count(*) INTO cnt
  FROM input_network
  WHERE userid = input_userid and way_type = 'Street';

IF cnt = 1 THEN
    create table user_input_network_union as
    select geometry as geom
    from input_network
    where userid = input_userid and way_type = 'Street';

ELSE

	    --Split_userinput is a funtion which needs userid as input
	create table user_input_network_union as
	select st_union(split_userinput) as geom 
	from split_userinput(input_userid);

END IF;
	--Split the new lines where they intersect with the new network
	create table testtest as
	select row_number() over() as gid,geom 
	from(
		select (st_dump(ST_CollectionExtract(st_split(x.geom,i.geom),2))).geom as geom
		from 
		(select st_union(w.geom) as geom 
		from ways_userinput w,user_input_network_union n 
		where st_intersects(w.geom,n.geom)
		and w.userid is null) i,
		user_input_network_union x) t 
	where st_length(geom::geography) <> 0;
 	





--For each line the start and endpoint is created and saved 
create table final as
select distinct t.geom geom ,_1,_2,i.geom point,vertex_id
	from (select geom,st_startpoint(geom) _1, st_endpoint(geom) _2
	from testtest) t,
	intersection_test i
where st_astext(i.geom) = st_astext(t._1)
or st_astext(i.geom) = st_astext(t._2);


alter table testtest add column source integer;
alter table testtest add column target integer;


--All new edges which have one intersecting point with the already existing network are selected 
--and the corresponding vertex is selected
update testtest set source = x.vertex_id 
from (
select geom, vertex_id,_2 point from final where geom  
in(
	select t.geom geom 
	from (select geom,st_startpoint(geom) _1, st_endpoint(geom) _2
	from testtest) t,
	intersection_test i
	where st_astext(i.geom) = st_astext(t._1)
	or st_astext(i.geom) = st_astext(t._2)
	group by t.geom
	having count(*) = 1)
and _1 = point) x
where testtest.geom = x.geom;

update testtest set target = x.vertex_id 
from(
select geom, vertex_id,_1 as point from final where geom  
in(
	select t.geom geom 
	from (select geom,st_startpoint(geom) _1, st_endpoint(geom) _2
	from testtest) t,
	intersection_test i
	where st_astext(i.geom) = st_astext(t._1)
	or st_astext(i.geom) = st_astext(t._2)
	group by t.geom
	having count(*) = 1)
and _2 = point) x
where testtest.geom = x.geom;


-- All lines, which have two intersection points with the existing network are assigned with vertices

--First the source vertext is assign and put into a new preliminary table 
create table xxx as
select t.geom geom,i.vertex_id as source
from (select geom,st_startpoint(geom) _1
	from 
	(select distinct t.* from testtest t,intersection_test i
	where source is null and target is null
	and st_intersects(i.geom,t.geom)) x
	) t,
	intersection_test i
--geometries are compared as text
	where st_astext(i.geom) = st_astext(t._1);

			
alter table xxx add column target integer;

--Afterwards the target is updated as well
update xxx set target = x.target 
from (select t.geom geom,i.vertex_id as target
from (select geom, st_endpoint(geom) _2
	from 
	(select distinct t.* from testtest t,intersection_test i
	where source is null and target is null
	and st_intersects(i.geom,t.geom)) x
	) t,
	intersection_test i
--geometries are compared as text
	where st_astext(i.geom) = st_astext(t._2))x
where xxx.geom = x.geom;



update testtest set source = xxx.source, target = xxx.target
from xxx
where testtest.geom = xxx.geom;


--All new lines which are not interseting with the already existing network are getting new vertices as well
create table vertices_not_intersection as
select y.st_startpoint as vertex,
--Select the max vertex_id so far
(select max(max) from (
select max(source) from testtest
union all 
select max(target) from testtest) x) + row_number() over() as vertex_id
---------------------------------------------------------
from 
--Selects distinct vertices 
	(select distinct *
	from (
		select st_startpoint(geom),source 
		from testtest
		where source is null
		union all
		select st_endpoint(geom),target 
		from testtest
		where target is null) x
	) y;
	
update testtest set source = v.vertex_id
from vertices_not_intersection v
where st_startpoint(geom) = v.vertex;

update testtest set target = v.vertex_id
from vertices_not_intersection v
where st_endpoint(geom) = v.vertex;

--Delte those where source and target are so close to each other that they are identical 
delete from testtest 
where source=target;


----------------------------------------------------------------------------------------------------------------------
--INSERT NEW VERTICES AND WAYS INTO THE EXISTING TABLES
----------------------------------------------------------------------------------------------------------------------


insert into ways_userinput_vertices_pgr(id,geom,userid)
select vertex_id::bigint,geom,input_userid from intersection_test;

insert into ways_userinput_vertices_pgr(id,geom,userid)
select distinct *,input_userid from (
select source::bigint,st_startpoint(geom) from testtest
where source not in (select vertex_id from intersection_test)
union all
select target::bigint,st_endpoint(geom) from testtest
where target not in (select vertex_id from intersection_test)) x;

insert into ways_userinput(id,source,target,geom,userid)
select (select max(id) from ways_userinput) + row_number() over(),source,target,geom,input_userid from testtest;

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
SELECT count(*) INTO count_bridges
  FROM input_network
  WHERE userid = input_userid and way_type = 'Bridge';

IF count_bridges = 1 THEN
perform insert_into_network_bridge(input_userid);
END IF;

delete from ways_userinput where source is null or target is null;

---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------


END
$function$
