CREATE TYPE public.type_edges AS
(
	seq integer,
	node integer,
	edge integer,
	cost numeric,
	geom geometry
);

CREATE TYPE public.type_isochrone AS
(
	userid integer,
	id integer,
	step integer,
	geom geometry
);

CREATE TYPE public.type_isochrone_thematic AS
(
	gid integer,
	objectid integer,
	id integer,
	step integer,
	geom geometry,
	sum_pois text
);

CREATE TYPE public.type_catchment_vertices AS
(
	start_vertex integer,
	node integer,
	edge integer,
	cnt integer,
	cost numeric,
	geom geometry,
	objectid integer	
);


CREATE TYPE type_pois_multi_isochrones AS 
(
	gid integer, 
	objectid integer,
	coordinates NUMERIC[][],
	userid integer,
	step integer, 
	speed NUMERIC, 
	alphashape_parameter NUMERIC,
	modus integer, 
	parent_id integer, 
	population jsonb,
	geom geometry	
);


