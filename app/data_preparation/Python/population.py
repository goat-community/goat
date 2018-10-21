x = """-- Preparing the tables
DROP TABLE IF EXISTS helping_table;

create table helping_table(
osm_id bigint,
street varchar(200),
housenumber varchar(100),
geom geometry,
origin varchar(20),
area float,
distance float);

--Inserts all the addresses which are derived from entrances, insert all the addresses which are directly-derived and not
--derived from entrances. insert all the addresses which are derived from buildings and not derived from entrances nor
--derived directly.
insert into helping_table
select x.osm_id,x.street,x.housenumber,x.geom,x.origin from
(select b.osm_id,b.street,b.housenumber,b.geom,b.origin  
from building_derived_addresses b, study_area m 
where st_within(b.geom,m.geom)  
and b.x not in 
(select x from entrances_derived_addresses b, study_area m 
where st_within(b.geom,m.geom) 
and m.gid='02.3.1') 
and b.x not in 
(select x from directly_derived_addresses b, study_area m 
where st_within(b.geom,m.geom) and m.gid='02.3.1')
and m.gid='02.3.1'
union all	
select b.osm_id,b.street,b.housenumber,b.geom,b.origin 
from directly_derived_addresses b, study_area m 
where st_within(b.geom,m.geom) 
and b.x not in 
(select x from entrances_derived_addresses b, study_area m
where m.gid='02.3.1')
and m.gid='02.3.1'
union all
select b.osm_id,b.street,b.housenumber,b.geom,b.origin 
from entrances_derived_addresses b,study_area m,buildings_residential x
where st_within(b.geom,m.geom)
and m.gid='02.3.1' 
and st_intersects(x.geom,b.geom)) x;

--All addresses which intersect with an building the area of the building is added to the address
UPDATE helping_table set area=b.area
from buildings_residential b 
where st_intersects(helping_table.geom,b.geom) ;


--For all addresses which are not directly lying on a building but close (12m) the closes building is UPDATEd
UPDATE helping_table set area=t.area 
from(
	--The area and the osm_id is selected from the created selection and the helping_table 
	select z.osm_id,z.street,z.housenumber,z.geom, b.area, st_distance(z.geom::geography, b.geom::geography) 
	from buildings_residential b, 
	study_area m,
	--
	(select k.* 
	from helping_table k
	where k.osm_id not in 
	--This part selects all osm_ids of addresses which are in the "Stadtbezirksteil" and are intersecting with any building
		(select k.osm_id from helping_table k, buildings_residential b 
		where st_intersects(k.geom,b.geom)) and origin <> 'building') z
	where  st_intersects(b.geom,m.geom) 
	---------------------------------------------------------------------------------------------------------------------	
		and m.gid='02.3.1'
		and st_distance(z.geom::geography, b.geom::geography) in(
		--This part calculates the distances of all building which are not yet assigned to an address
		--and select the minimun distance of each to an address and the area of the building is attached to the address
			select min(st_distance) from (			
				select x.*, b.area, st_distance(x.geom::geography, b.geom::geography) 
				from buildings_residential b, 
				study_area m,
					(select k.* 
					from helping_table k
					where k.osm_id not in 
					(select k.osm_id from helping_table k, buildings_residential b 
					where st_intersects(k.geom,b.geom)) and origin <> 'building') x
				where  st_intersects(b.geom,m.geom) 
				and m.gid='02.3.1' ) t
				-------------------------------------------------------------------------------------------------
				group by t.osm_id,t.street,t.geom, t.origin,t.housenumber
				having(min(st_distance)<12)
			)
	) t
where helping_table.osm_id=t.osm_id;

--For all addresses which are directly derived the area is added through the osm_id
UPDATE helping_table set area=b.area
from buildings_residential b
where helping_table.osm_id=b.osm_id;

--For building with various different addresses on it the area of each building has to be split between the different 
	--addresses 
UPDATE helping_table set area = helping_table.area/t.count from
	(select area,count(*) from helping_table h 
	where area in(
		--Only the areas are selected which are not null and not in the list of the doubled areas
		select area from helping_table h
		where area is not null
		and area not in(
			--All areas are selected which are given more than one time to the same address (e.g. two identical addresses on one building)	
			select x.area from(
				select *,concat(street,housenumber) from helping_table) x
			group by x.concat,x.area
			having count(*) > 1)
			-------------------------------------------------------------------------------------------
		group by area
		having count(*) > 1)
	group by area) t
where helping_table.area = t.area;



--The problem was that we have buildings which have more than twice the same address and which also 
--have different addresses on the same building (normally bigger buildings)
UPDATE helping_table set area = helping_table.area / z.count 
from (
--Now we have to count how often the area is existing, because we have to divide the area by this count
select y.area, count(y.*) from (
	--From all addresses only distict addresses are selected (doubled addresses are not selected)
	--which are on the list of those which appear more than once
	select distinct street,housenumber,area from helping_table 
	where area in(
		select t.area from ( 
			--All areas are select which appear more than once for a certain address
			select x.concat,x.area, count(*) from(
				select *,concat(street,housenumber) from helping_table
				) x
				group by x.concat,x.area
				having count(*) > 1
		) t
			--------------------------------------------------------------------------
			group by t.area
			having count(*)>1)
	) y
group by y.area) z
where helping_table.area  = z.area;

--All building which are not in a min distance of 12 m and are not intersecting with an address are assiciated
--with a address
UPDATE helping_table set area=helping_table.area+x.area 
from(
	select k.osm_id,k.street,k.housenumber,k.geom,k.origin,b.area,st_distance(b.geom::geography,k.geom::geography) 
	from buildings_residential b, study_area m,helping_table k
	where st_intersects(b.geom,m.geom)
	and m.gid='02.3.1'
	and b.gid not in
		(select gid 
		from buildings_residential b,helping_table k 
		where st_intersects(b.geom,k.geom))
		and st_distance(b.geom::geography,k.geom::geography) in
			(select min(st_distance(b.geom::geography,k.geom::geography)) 
			from buildings_residential b, study_area m,helping_table k
			where st_intersects(b.geom,m.geom)
			and m.gid='02.3.1'
			and b.gid not in
				(select gid 
				from buildings_residential b,helping_table k 
				where st_intersects(b.geom,k.geom))
				group by b.osm_id,b.area)) x
where helping_table.osm_id = x.osm_id;


insert into addresses_residential
select * from helping_table where area is not null;

 """



preparation = """DROP TABLE IF EXISTS addresses_residential;
create table addresses_residential(
osm_id bigint,
street varchar(200),
housenumber varchar(100),
geom geometry,
origin varchar(20),
area float,
population integer,
distance float);"""


index_keys ="""ALTER TABLE addresses_residential add column gid serial;
ALTER TABLE addresses_residential add primary key (gid);
CREATE INDEX index_addresses_residential ON addresses_residential USING GIST (geom);"""

calculate_population ="""DROP TABLE IF EXISTS concat_address;

select distinct row_number() over() as id,concat(street,housenumber),area,geom 
into concat_address 
from addresses_residential;

ALTER TABLE concat_address add primary key (id );
CREATE INDEX index_concat_address ON concat_address USING GIST (geom);

ALTER TABLE addresses_residential add column gid_administrative_boundary varchar(20);

with area_built_up as (

	select gid,sum(a.area) as sum_pop, m.area, m.geom 
	from study_area m,concat_address a
	where st_within(a.geom,m.geom)
	group by gid
)
UPDATE addresses_residential set population = x.sum_pop*(addresses_residential.area/x.area),
gid_administrative_boundary=x.gid
from area_built_up x
where st_within(addresses_residential.geom,x.geom);

DROP TABLE IF EXISTS concat_address;

"""


import psycopg2
from psycopg2 import sql
con=psycopg2.connect(dbname='goat', host='localhost', port = 5432, user='goat',password='earlmanigault')
cursor=con.cursor()

cursor.execute(preparation)

vi_nummer = 'select distinct gid from study_area'
cursor.execute(vi_nummer)
vi_nummer = cursor.fetchall()

for i in vi_nummer:
    main_sql = x.replace('02.3.1',str(i[0]))
    cursor.execute(main_sql)
    print(i[0])

    
    con.commit()

cursor.execute(index_keys)
cursor.execute(calculate_population)
con.commit()    
con.close()

