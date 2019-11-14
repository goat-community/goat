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
	population jsonb NULL,
	geom geometry NULL,	
	CONSTRAINT multi_isochrones_pkey PRIMARY KEY (gid)
);


CREATE INDEX ON multi_isochrones USING gist (geom);
CREATE INDEX ON multi_isochrones USING btree(objectid,parent_id);

CREATE TABLE public.edges (
	seq int4 NULL,
	node int4 NULL,
	edge int4 NULL,
	cost numeric NULL,
	geom geometry NULL,
	objectid int4 NULL,
	id serial NOT NULL,
	class_id int4,
	CONSTRAINT edges_pkey PRIMARY KEY (id)
);
CREATE INDEX index_edges ON edges USING gist(geom);
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
distance float);

ALTER TABLE addresses_residential add column gid serial;
ALTER TABLE addresses_residential add primary key (gid);
CREATE INDEX index_addresses_residential ON addresses_residential USING GIST (geom);

CREATE TABLE study_area_union as
SELECT st_union(geom) geom FROM study_area;



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
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.ways_modified
    OWNER to goat;

-- Index: ways_modified_index

-- DROP INDEX public.ways_modified_index;

CREATE INDEX ways_modified_index
    ON public.ways_modified USING gist
    (geom)
    TABLESPACE pg_default;

-- Table: public.user_data

-- DROP TABLE public.user_data;


DROP SEQUENCE IF EXISTS user_data_id_seq;
CREATE SEQUENCE user_data_id_seq;

CREATE TABLE public.user_data
(
    id bigint NOT NULL DEFAULT nextval('user_data_id_seq'::regclass),
    name character varying COLLATE pg_catalog."default",
    surname character varying COLLATE pg_catalog."default",
    deleted_feature_ids bigint[],
    CONSTRAINT user_data_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.user_data
    OWNER to goat;


CREATE TABLE public.variable_container (
	identifier varchar(100) NOT NULL,
	variable_simple text NULL,
	variable_array text[] NULL,
	variable_object jsonb NULL,
	CONSTRAINT variable_container_pkey PRIMARY KEY (identifier)
);

INSERT INTO variable_container(identifier,variable_array) 
values('poi_categories',
'{"kindergarten","primary_school","secondary_school","bar","biergarten","cafe","pub","fast_food",
"ice_cream","restaurant","theatre","sum_population","cinema","library","night_club","recycling",
"car_sharing","bicycle_rental","charging_station","bus_station","tram_station","subway_station","railway_station","taxi",
"hairdresser","atm","bank","dentist","doctors","pharmacy","post_box","post_office","fuel",
"bakery","butcher","clothes","convenience","general","fashion","florist","greengrocer",
"kiosk","mall","shoes","sports","supermarket","health_food","discount_supermarket",
"hypermarket","international_supermarket","chemist","organic","marketplace",
"hotel","museum","hostel","guest_house","viewpoint","gallery","bus_stop",
"tram_stop","subway_entrance","rail_station"}');


INSERT INTO variable_container(identifier,variable_array) 
values('excluded_class_id_walking',
'{0,101,102,103,104,105,106,107,501,502,503,504,701,801}');

INSERT INTO variable_container(identifier,variable_array) 
values('categories_no_foot',
'{"use_sidepath","no"}');

INSERT INTO variable_container(identifier,variable_array) 
values('categories_sidewalk_no_foot',
'{"separate"}'); -- only for visualization

INSERT INTO variable_container(identifier,variable_simple) 
values('max_length_links',
'300');

INSERT INTO variable_container(identifier,variable_array)
values('custom_landuse_no_residents',
'{"AX_TagebauGrubeSteinbruch",
"AX_SportFreizeitUndErholungsflaeche",
"AX_FlaecheBesondererFunktionalerPraegung",
"AX_Halde",
"AX_Friedhof",
"AX_IndustrieUndGewerbeflaeche"}'
);

INSERT INTO variable_container(identifier,variable_array)
values('osm_landuse_no_residents',
'{"farmyard","quarry","industrial","retail","commercial","military","cemetery","landfill","allotments","recreation ground","railway"}'
);

--All buildings that can be potentially residential
INSERT INTO variable_container(identifier,variable_array)
values('building_types_potentially_residential',
'{"residential","yes","house","detached","terrace","apartments","home"}'
);
--All buildings that are definitely residential
INSERT INTO variable_container(identifier,variable_array)
values('building_types_residential',
'{"residential","detached","terrace","apartments","home"}'
);

INSERT INTO variable_container(identifier,variable_array)
values('tourism_no_residents',
'{"zoo"}'
);

INSERT INTO variable_container(identifier,variable_array)
values('amenity_no_residents',
'{"hospital","university","community_centre","school","kindergarten","recreation_ground","wood"}'
);

INSERT INTO variable_container(identifier,variable_simple)
values('default_building_levels',
'3'
);
INSERT INTO variable_container(identifier,variable_simple)
values('minimum_building_size_residential',
'54'
);

INSERT INTO variable_container(identifier,variable_simple)
values('census_minimum_number_new_buildings',
'1'
);
INSERT INTO variable_container(identifier,variable_simple)
values('average_gross_living_area',
'50'
);

INSERT INTO variable_container(identifier,variable_array)
values('chains_discount_supermarket',
'{"Aldi","Penny","Lidl","Netto","Norma"}'
);

INSERT INTO variable_container(identifier,variable_array)
values('chains_hypermarket',
'{"Hit","Real","Kaufland","V-Markt","Marktkauf"}'
);

INSERT INTO variable_container(identifier,variable_array)
values('chains_health_food',
'{"Vitalia","Reformhaus"}'
);

INSERT INTO variable_container(identifier,variable_array)
values('no_end_consumer_store',
'{"Hamberger","Metro"}'
);


INSERT INTO variable_container(identifier,variable_array)
values('operators_bicycle_rental',
'{"Münchner Verkehrs gesellschaft","Münchner Verkehrsgesellschaft","MVG"}'
);

INSERT INTO variable_container(identifier,variable_object) 
SELECT 'wheelchair', jsonb_build_object('smoothness_no', ARRAY['very_bad','horrible','very_horrible','impassable'],
						'smoothness_limited', ARRAY['bad'],
						'surface_no', ARRAY['ground','grass','sand','dirt','unhewn_cobblestone'],
						'highway_onstreet_yes', ARRAY['living_street'],
						'highway_onstreet_limited', ARRAY['residential']);

INSERT INTO variable_container(identifier,variable_object) 
SELECT 'lit', jsonb_build_object('highway_yes', ARRAY['living_street','residential','secondary','tertiary'],
						'highway_no', ARRAY['track'],
						'surface_no', ARRAY['ground', 'gravel', 'unpaved', 'grass']);
