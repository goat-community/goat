CREATE TABLE public.user_data
(
  	userid bigserial,
	username TEXT,
	pw TEXT, 
    CONSTRAINT user_data_pkey PRIMARY KEY (userid)
);

CREATE TABLE public.scenarios
(
  	scenario_id bigserial,
	scenario_name text,
	userid bigint,
	deleted_ways bigint[] DEFAULT '{}',
	deleted_pois bigint[] DEFAULT '{}',
	deleted_buildings bigint[] DEFAULT '{}',
    CONSTRAINT scenarios_pkey PRIMARY KEY (scenario_id),
    CONSTRAINT scenario_fkey FOREIGN KEY (userid)
    REFERENCES user_data(userid) ON DELETE CASCADE
);

CREATE TABLE public.isochrones (
	userid int4 NULL,
	scenario_id int4 NULL,
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
	cost float NULL,
	start_cost float NULL,
	end_cost float NULL,
	geom geometry NULL,
	objectid int4 NULL,
	id serial NOT NULL,
	CONSTRAINT edges_pkey PRIMARY KEY (id)
);

CREATE INDEX ON edges USING btree(objectid,cost);

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
	distance float
);

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
    gid bigserial,
    geom geometry(LineString,4326),
    way_type text,
	surface text,
	wheelchair text,
	lit text,
	street_category text,
	foot text,
	bicycle text,
    scenario_id integer,
    original_id integer,
	status bigint,
    CONSTRAINT ways_modified_id_pkey PRIMARY KEY (gid),
    CONSTRAINT ways_modified_fkey FOREIGN KEY (scenario_id)
    REFERENCES scenarios(scenario_id) ON DELETE CASCADE
);

CREATE INDEX ways_modified_index ON public.ways_modified USING gist(geom);

CREATE TABLE public.pois_modified (
	gid serial,
	name text NULL,
	amenity text NOT NULL,
	opening_hours text NULL,
	geom geometry(POINT, 4326) NULL,
	scenario_id int4,
	original_id int4 NULL,
	wheelchair text,
	CONSTRAINT pois_modified_id_pkey PRIMARY KEY (gid),
    CONSTRAINT pois_modified_fkey FOREIGN KEY (scenario_id)
    REFERENCES scenarios(scenario_id) ON DELETE CASCADE
);

CREATE INDEX ON pois_modified USING gist(geom);

CREATE TABLE buildings_modified
(
	gid serial,
	building TEXT NOT NULL,
	building_levels numeric NOT NULL,
	building_levels_residential numeric NOT NULL,
	gross_floor_area integer,
	population NUMERIC,
	geom geometry NULL,
	scenario_id integer NOT NULL,
	original_id integer,
	CONSTRAINT buildings_modified_gid_pkey PRIMARY KEY(gid),
    CONSTRAINT buildings_modified_fkey FOREIGN KEY (scenario_id)
    REFERENCES scenarios(scenario_id) ON DELETE CASCADE
);

CREATE INDEX ON buildings_modified USING GIST(geom);

CREATE TABLE population_modified
(
	gid serial,
	building_gid integer,
	population numeric,
	geom geometry(POINT, 4326) NULL,
	scenario_id integer,
	CONSTRAINT population_modified_gid_pkey PRIMARY KEY(gid),
    CONSTRAINT population_modified_fkey FOREIGN KEY (scenario_id)
    REFERENCES scenarios(scenario_id) ON DELETE CASCADE
);

CREATE INDEX ON population_modified USING GIST(geom);
