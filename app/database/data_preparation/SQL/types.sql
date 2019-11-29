DROP TYPE IF EXISTS type_edges CASCADE;
CREATE TYPE public.type_edges AS
(
	seq integer,
	node integer,
	edge integer,
	cost numeric,
	geom geometry
);

DROP TYPE IF EXISTS type_isochrone CASCADE;
CREATE TYPE public.type_isochrone AS
(
	userid integer,
	id integer,
	step integer,
	geom geometry
);

DROP TYPE IF EXISTS type_isochrone_thematic CASCADE;
CREATE TYPE public.type_isochrone_thematic AS
(
	gid integer,
	objectid integer,
	id integer,
	step integer,
	geom geometry,
	sum_pois text
);

DROP TYPE IF EXISTS type_catchment_vertices CASCADE;
CREATE TYPE public.type_catchment_vertices AS
(
	start_vertex integer,
	node integer,
	edge integer,
	cnt integer,
	cost numeric,
	geom geometry,
	w_geom geometry,
	objectid integer	
);

DROP TYPE IF EXISTS type_catchment_vertices_multi CASCADE;
CREATE TYPE public.type_catchment_vertices_multi AS
(
	start_vertex integer,
	node integer,
	edge integer,
	cnt integer,
	cost numeric,
	geom geometry,
	objectid integer	
);

DROP TYPE IF EXISTS type_pois_multi_isochrones CASCADE;
CREATE TYPE type_pois_multi_isochrones AS 
(
	gid integer, 
	objectid integer,
	coordinates NUMERIC[][],
	userid integer,
	step integer, 
	routing_profile text,
	speed NUMERIC, 
	alphashape_parameter NUMERIC,
	modus integer, 
	parent_id integer, 
	population jsonb,
	geom geometry	
);
DROP TYPE IF EXISTS type_isochrones_api CASCADE;
CREATE TYPE type_isochrones_api AS
(
	gid integer, 
	objectid integer, 
	coordinates NUMERIC[],
	step integer,
	speed NUMERIC,
	shape_precision NUMERIC,
	modus integer,
	parent_id integer,
	sum_pois jsonb, 
	geom geometry,
  	starting_point text
);
DROP TYPE IF EXISTS type_fetch_ways_routing CASCADE;
CREATE TYPE type_fetch_ways_routing AS
(
	id integer, 
	SOURCE integer, 
	target integer, 
	cost float,
	geom geometry
);
DROP TYPE IF EXISTS type_catchment_vertices_single CASCADE;
CREATE TYPE public.type_catchment_vertices_single AS
(
	start_vertex integer,
	node integer,
	edge integer,
	cost numeric,
	geom geometry,
	w_geom geometry,
	objectid integer	
);
DROP TYPE IF EXISTS pois_visualization CASCADE;
CREATE TYPE public.pois_visualization AS
(
	name text, 
	osm_id bigint, 
	opening_hours text, 
	orgin_geometry text, 
	geom geometry, 
	status text
);
