CREATE OR REPLACE FUNCTION clean_duplicated_pois(table_name text)
	RETURNS VOID
	LANGUAGE plpgsql
AS $function$
BEGIN
	DROP TABLE IF EXISTS pois_duplicated;
	CREATE TEMP TABLE pois_duplicated (id serial, gid integer, distance NUMERIC);
	ALTER TABLE pois_duplicated ADD PRIMARY KEY(id) ;
	
	EXECUTE 'INSERT INTO pois_duplicated 
			SELECT min(gid) as gid, distance 
			FROM (
				SELECT o.gid, ST_Distance(o.geom,p.geom) AS distance
				FROM '|| quote_ident(table_name) ||' o
				JOIN '|| quote_ident(table_name) ||' p
				ON ST_DWithin( o.geom::geography, p.geom::geography, select_from_variable_container_s('|| quote_literal('duplicated_lookup_radius') ||')::float)
				AND NOT ST_DWithin(o.geom, p.geom, 0)
			) x
			GROUP BY distance';
	
	EXECUTE 'DELETE FROM '||quote_ident(table_name)||' WHERE gid = ANY (SELECT id FROM pois_duplicated)';
END;
$function$;
