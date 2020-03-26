CREATE TABLE public.isochrones (
	userid int4 NULL,
	id int4 NULL,
	step int4 NULL,
	geom geometry NULL,
	gid serial NOT NULL,
	speed numeric NULL,
	concavity numeric NULL,
	modus varchar(20) NULL,
	objectid int4 NULL,
	parent_id int4 NULL,
	population int4 NULL,
	pois text NULL, 
	sum_pois_time text NULL,
	sum_pois text NULL,
	starting_point text NULL,
	CONSTRAINT isochrones_pkey PRIMARY KEY (gid)
);
CREATE INDEX index_isochrones ON isochrones USING gist (geom);
CREATE INDEX ON isochrones USING btree(objectid,parent_id);

CREATE TABLE public.multi_isochrones (
	gid serial NOT NULL,
	objectid int4 NULL,
	coordinates numeric[][],
	userid int4 NULL,
	id int4 NULL,
	step int4 NULL,
	speed numeric NULL,
	alphashape_parameter numeric NULL,
	modus integer NULL,
	parent_id int4 NULL,
	routing_profile TEXT,
	population jsonb NULL,
	geom geometry NULL,	
	CONSTRAINT multi_isochrones_pkey PRIMARY KEY (gid)
);


CREATE INDEX ON multi_isochrones USING gist (geom);
CREATE INDEX ON multi_isochrones USING btree(objectid,parent_id);

CREATE UNLOGGED TABLE public.edges (
	edge integer NULL,
	node integer NULL,
	cost numeric NULL,
	geom geometry NULL,
	v_geom geometry NULL,
	objectid int4 NULL,
	id serial NOT NULL,
	CONSTRAINT edges_pkey PRIMARY KEY (id)
);
--CREATE INDEX index_edges ON edges USING gist(geom);
CREATE INDEX ON edges USING btree(objectid,cost);

/*
CREATE UNLOGGED TABLE public.edges_multi (
	edge integer NULL,
	node integer NULL,
	min_cost numeric NULL,
	geom geometry NULL,
	v_geom geometry NULL,
	objectid int4 NULL,
	node_cost_1 jsonb,
	node_cost_2 jsonb,
	id serial NOT NULL,
	CONSTRAINT edges_multi_pkey PRIMARY KEY (id)
);
--CREATE INDEX index_edges ON edges USING gist(geom);
CREATE INDEX ON edges_multi USING btree(objectid,min_cost);
*/
CREATE UNLOGGED TABLE public.edges_multi (
	edge integer NULL,
	node integer NULL,
	min_cost numeric NULL,
	geom geometry NULL,
	v_geom geometry NULL,
	objectid integer NULL,
	duplicates integer[],
	combi_ids integer[],
	combi_costs float[],
	id serial NOT NULL,
	CONSTRAINT edges_multi_pkey PRIMARY KEY (id)
);
--CREATE INDEX index_edges ON edges USING gist(geom);
CREATE INDEX ON edges_multi USING btree(objectid,min_cost);
CREATE INDEX ON edges_multi USING GIN(duplicates);

CREATE UNLOGGED TABLE edges_multi_extrapolated(
	edge integer,
	node integer,
	cost numeric,
	geom geometry,
	v_geom geometry,
	id_calc integer, 
	objectid integer,
	id serial,
	CONSTRAINT edges_multi_extrapolated_pkey PRIMARY KEY(id)
);
CREATE INDEX ON edges_multi_extrapolated USING btree(objectid,id_calc,cost);

CREATE TABLE public.starting_point_isochrones (
	gid serial,
	userid int4 NOT NULL,
	geom geometry,
	objectid int4 NOT NULL,
	number_calculation int4,
	CONSTRAINT starting_point_isochrones_pkey PRIMARY KEY (gid)
);
CREATE INDEX ON starting_point_isochrones USING gist(geom);

CREATE TABLE addresses_residential(
osm_id bigint,
street varchar(200),
housenumber varchar(100),
geom geometry,
origin varchar(20),
area float,
population integer,
distance float);

ALTER TABLE addresses_residential add column gid serial;
ALTER TABLE addresses_residential add primary key (gid);
CREATE INDEX index_addresses_residential ON addresses_residential USING GIST (geom);

CREATE TABLE study_area_union as
SELECT ST_Collect(ST_MakePolygon(geom)) As geom
FROM 
(
   SELECT ST_ExteriorRing((ST_Dump(st_union(geom))).geom) As geom
   FROM study_area
) s;

-- Table: public.ways_modified

-- DROP TABLE public.ways_modified;

CREATE TABLE public.ways_modified
(
    id bigint NOT NULL,
    class_id integer,
    geom geometry(LineString,4326),
    userid integer,
    original_id integer,
	type varchar(20),
	status bigint,
    CONSTRAINT ways_modified_id_pkey PRIMARY KEY (id)
);

CREATE INDEX ways_modified_index ON public.ways_modified USING gist(geom);

CREATE TABLE public.pois_modified (
	id serial,
	name text NULL,
	amenity text NOT NULL,
	opening_hours text NULL,
	geom geometry(POINT, 4326) NULL,
	userid int4 NULL,
	original_id int4 NULL,
	wheelchair text,
	CONSTRAINT pois_modified_id_pkey PRIMARY KEY (id)
);

CREATE INDEX ON pois_modified USING gist(geom);


DROP SEQUENCE IF EXISTS user_data_id_seq;
CREATE SEQUENCE user_data_id_seq;

CREATE TABLE public.user_data
(
    id bigint NOT NULL DEFAULT nextval('user_data_id_seq'::regclass),
    name character varying COLLATE pg_catalog."default",
    surname character varying COLLATE pg_catalog."default",
    deleted_feature_ids bigint[],
	userid bigint,
	layer_name varchar(100),
    CONSTRAINT user_data_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.user_data
    OWNER to goat;
