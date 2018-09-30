--Create table ways_userinput and way_userinput_vertices_pgr

create table ways_userinput as
select * from ways;

create table ways_userinput_vertices_pgr as
select * from ways_vertices_pgr;

alter table ways rename column gid to id;
alter table ways_userinput rename column gid to id;
alter table ways_userinput add column userid int4;
alter table ways_userinput_vertices_pgr add column userid int4;


alter table ways rename column the_geom to geom;
alter table ways_vertices_pgr rename column the_geom to geom;
alter table ways alter column target type int4;
alter table ways alter column source type int4;
alter table ways_userinput rename column the_geom to geom;
alter table ways_userinput_vertices_pgr rename column the_geom to geom;
alter table ways_userinput alter column target type int4;
alter table ways_userinput alter column source type int4;

ALTER TABLE public.ways_userinput ADD CONSTRAINT ways_userinput_pkey PRIMARY KEY (id);
ALTER TABLE public.ways_userinput ADD CONSTRAINT ways_userinput_class_id_fkey FOREIGN KEY (class_id) REFERENCES osm_way_classes(class_id);
ALTER TABLE public.ways_userinput ADD CONSTRAINT ways_userinput_source_fkey FOREIGN KEY (source) REFERENCES ways_userinput_vertices_pgr(id);
ALTER TABLE public.ways_userinput ADD CONSTRAINT ways_userinput_target_fkey FOREIGN KEY (target) REFERENCES ways_userinput_vertices_pgr(id);
CREATE INDEX ways_userinput_index ON ways_userinput USING gist (geom);
CREATE INDEX ways_userinput_source_idx ON ways_userinput USING btree (source);
CREATE INDEX ways_userinput_target_idx ON ways_userinput USING btree (target);
CREATE INDEX ways_userinput_userid_idx ON ways_userinput USING btree (userid);


ALTER TABLE public.ways_userinput_vertices_pgr ADD CONSTRAINT ways_userinput_vertices_pgr_osm_id_key UNIQUE (osm_id);
ALTER TABLE public.ways_userinput_vertices_pgr ADD CONSTRAINT ways_userinput_vertices_pgr_pkey PRIMARY KEY (id);
CREATE INDEX ways_userinput_vertices_pgr_index ON ways_userinput_vertices_pgr USING gist (geom);
CREATE INDEX ways_userinput_vertices_pgr_osm_id_idx ON ways_userinput_vertices_pgr USING btree (osm_id);



insert into osm_way_classes(class_id,name) values(501,'secondary_use_sidepath');
insert into osm_way_classes(class_id,name) values(502,'secondary_link_use_sidepath');
insert into osm_way_classes(class_id,name) values(503,'tertiary_use_sidepath');
insert into osm_way_classes(class_id,name) values(504,'tertiary_link_use_sidepath');
insert into osm_way_classes(class_id,name) values(601,'foot_yes');

with links_to_update as (
select osm_id, o.class_id 
from planet_osm_line p, osm_way_classes o
where highway in('secondary','secondary_link','tertiary','tertiary_link')
and foot = 'use_sidepath'
and concat(highway,'_use_sidepath') = o.name
)
update ways set class_id = l.class_id
from links_to_update l
where ways.osm_id = l.osm_id;
update ways_userinput set class_id = w.class_id
from ways w 
where ways_userinput.osm_id = w.osm_id;


with links_to_update as (
select osm_id, o.class_id 
from planet_osm_line p, osm_way_classes o
where highway in('secondary','secondary_link','tertiary','tertiary_link')
and foot = 'use_sidepath'
and concat(highway,'_use_sidepath') = o.name
)
update ways set class_id = l.class_id
from links_to_update l
where ways.osm_id = l.osm_id;
update ways_userinput set class_id = w.class_id
from ways w 
where ways_userinput.osm_id = w.osm_id;


with links_to_update as (
select osm_id
from planet_osm_line p
where foot = 'yes'
)
update ways set class_id = 601
from links_to_update l
where ways.osm_id = l.osm_id;
update ways_userinput set class_id = w.class_id
from ways w 
where ways_userinput.osm_id = w.osm_id;


with links_to_update as (
select osm_id, o.class_id 
from planet_osm_line p, osm_way_classes o
where highway in('secondary','secondary_link','tertiary','tertiary_link')
and foot = 'use_sidepath'
and concat(highway,'_use_sidepath') = o.name
)
update ways set class_id = l.class_id
from links_to_update l
where ways.osm_id = l.osm_id;


with class_id as (
select unnest(variable_array) class_id
from variable_container 
where identifier = 'excluded_class_id_walking'
),
class_names as(
select c.class_id, o.name
from class_id c, osm_way_classes o
where c.class_id::integer = o.class_id
and c.class_id::integer < 500
),
links_to_update as(
select osm_id
from planet_osm_line p, class_names c
where p.highway = c.name
and foot = 'yes'
union all
select osm_id
from planet_osm_line p
where (tags -> 'sidewalk') is not null
and (tags -> 'sidewalk') <> 'no'
and (tags -> 'sidewalk') <> 'none'
)
update ways set class_id = 601
from links_to_update l
where ways.osm_id = l.osm_id;

update ways_userinput set class_id = w.class_id
from ways w 
where ways_userinput.osm_id = w.osm_id;
