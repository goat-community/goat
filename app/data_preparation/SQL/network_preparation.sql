--CREATE TABLE ways_userinput AND way_userinput_vertices_pgr

CREATE TABLE ways_userinput as
SELECT * FROM ways;

CREATE TABLE ways_userinput_vertices_pgr as
SELECT * FROM ways_vertices_pgr;

ALTER TABLE ways rename column gid to id;
ALTER TABLE ways_userinput rename column gid to id;
ALTER TABLE ways_userinput add column userid int4;
ALTER TABLE ways_userinput_vertices_pgr add column userid int4;


ALTER TABLE ways rename column the_geom to geom;
ALTER TABLE ways_vertices_pgr rename column the_geom to geom;
ALTER TABLE ways alter column target type int4;
ALTER TABLE ways alter column source type int4;
ALTER TABLE ways_userinput rename column the_geom to geom;
ALTER TABLE ways_userinput_vertices_pgr rename column the_geom to geom;
ALTER TABLE ways_userinput alter column target type int4;
ALTER TABLE ways_userinput alter column source type int4;

ALTER TABLE public.ways_userinput ADD CONSTRAINT ways_userinput_pkey PRIMARY KEY (id);
ALTER TABLE public.ways_userinput ADD CONSTRAINT ways_userinput_class_id_fkey ForEIGN KEY (class_id) REFERENCES osm_way_classes(class_id);
ALTER TABLE public.ways_userinput ADD CONSTRAINT ways_userinput_source_fkey ForEIGN KEY (source) REFERENCES ways_userinput_vertices_pgr(id);
ALTER TABLE public.ways_userinput ADD CONSTRAINT ways_userinput_target_fkey ForEIGN KEY (target) REFERENCES ways_userinput_vertices_pgr(id);
CREATE INDEX ways_userinput_index ON ways_userinput USING gist (geom);
CREATE INDEX ways_userinput_source_idx ON ways_userinput USING btree (source);
CREATE INDEX ways_userinput_target_idx ON ways_userinput USING btree (target);
CREATE INDEX ways_userinput_userid_idx ON ways_userinput USING btree (userid);


ALTER TABLE public.ways_userinput_vertices_pgr ADD CONSTRAINT ways_userinput_vertices_pgr_osm_id_key UNIQUE (osm_id);
ALTER TABLE public.ways_userinput_vertices_pgr ADD CONSTRAINT ways_userinput_vertices_pgr_pkey PRIMARY KEY (id);
CREATE INDEX ways_userinput_vertices_pgr_index ON ways_userinput_vertices_pgr USING gist (geom);
CREATE INDEX ways_userinput_vertices_pgr_osm_id_idx ON ways_userinput_vertices_pgr USING btree (osm_id);



insert INTO osm_way_classes(class_id,name) values(501,'secondary_use_sidepath');
insert INTO osm_way_classes(class_id,name) values(502,'secondary_link_use_sidepath');
insert INTO osm_way_classes(class_id,name) values(503,'tertiary_use_sidepath');
insert INTO osm_way_classes(class_id,name) values(504,'tertiary_link_use_sidepath');
insert INTO osm_way_classes(class_id,name) values(601,'foot_yes');

with links_to_UPDATE as (
SELECT osm_id, o.class_id 
FROM planet_osm_line p, osm_way_classes o
WHERE highway in('secondary','secondary_link','tertiary','tertiary_link')
AND foot = 'use_sidepath'
AND concat(highway,'_use_sidepath') = o.name
)
UPDATE ways set class_id = l.class_id
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;
UPDATE ways_userinput set class_id = w.class_id
FROM ways w 
WHERE ways_userinput.osm_id = w.osm_id;


with links_to_UPDATE as (
SELECT osm_id, o.class_id 
FROM planet_osm_line p, osm_way_classes o
WHERE highway in('secondary','secondary_link','tertiary','tertiary_link')
AND foot = 'use_sidepath'
AND concat(highway,'_use_sidepath') = o.name
)
UPDATE ways set class_id = l.class_id
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;
UPDATE ways_userinput set class_id = w.class_id
FROM ways w 
WHERE ways_userinput.osm_id = w.osm_id;


with links_to_UPDATE as (
SELECT osm_id
FROM planet_osm_line p
WHERE foot = 'yes'
)
UPDATE ways set class_id = 601
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;
UPDATE ways_userinput set class_id = w.class_id
FROM ways w 
WHERE ways_userinput.osm_id = w.osm_id;


with links_to_UPDATE as (
SELECT osm_id, o.class_id 
FROM planet_osm_line p, osm_way_classes o
WHERE highway in('secondary','secondary_link','tertiary','tertiary_link')
AND foot = 'use_sidepath'
AND concat(highway,'_use_sidepath') = o.name
)
UPDATE ways set class_id = l.class_id
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;


with class_id as (
SELECT unnest(variable_array) class_id
FROM variable_container 
WHERE identifier = 'excluded_class_id_walking'
),
class_names as(
SELECT c.class_id, o.name
FROM class_id c, osm_way_classes o
WHERE c.class_id::integer = o.class_id
AND c.class_id::integer < 500
),
links_to_UPDATE as(
SELECT osm_id
FROM planet_osm_line p, class_names c
WHERE p.highway = c.name
AND foot = 'yes'
UNION ALL
SELECT osm_id
FROM planet_osm_line p
WHERE (tags -> 'sidewalk') IS NOT NULL
AND (tags -> 'sidewalk') <> 'no'
AND (tags -> 'sidewalk') <> 'none'
)
UPDATE ways set class_id = 601
FROM links_to_UPDATE l
WHERE ways.osm_id = l.osm_id;

UPDATE ways_userinput set class_id = w.class_id
FROM ways w 
WHERE ways_userinput.osm_id = w.osm_id;
