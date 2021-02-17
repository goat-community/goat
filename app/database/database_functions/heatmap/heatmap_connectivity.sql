DROP FUNCTION IF EXISTS heatmap_connectivity;
CREATE OR REPLACE FUNCTION public.heatmap_connectivity(modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(grid_id integer, percentile_area_isochrone smallint, area_isochrone float, geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE
	borders_quintiles numeric[]; 
BEGIN
	
	IF modus_input IN ('default','comparison') THEN   
		DROP TABLE IF EXISTS grids_default; 
		CREATE TEMP TABLE grids_default AS 
		SELECT g.grid_id, g.percentile_area_isochrone, g.area_isochrone, g.geom  
		FROM grid_heatmap g;	
	END IF; 

	IF modus_input IN ('scenario','comparison') THEN  
		SELECT array_agg(border)
		INTO borders_quintiles
		FROM 
		(
			SELECT min(x.area_isochrone) border
			FROM 
			(
				SELECT ntile(5) over (order by g.area_isochrone) AS percentile_area_isochrone, g.area_isochrone
				FROM grid_heatmap g
			) x 
			GROUP BY x.percentile_area_isochrone
			ORDER BY x.percentile_area_isochrone
		) b;
		
		DROP TABLE IF EXISTS grids_scenario;
		CREATE TEMP TABLE grids_scenario AS 
		WITH grids_to_classify AS 
		(	
			SELECT a.grid_id, 
			CASE WHEN COALESCE(a.area_isochrone,0) = 0 THEN 0
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[1] AND COALESCE(a.area_isochrone,0) < borders_quintiles[2] THEN 1
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[2] AND COALESCE(a.area_isochrone,0) < borders_quintiles[3] THEN 2
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[3] AND COALESCE(a.area_isochrone,0) < borders_quintiles[4] THEN 3
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[4] AND COALESCE(a.area_isochrone,0) < borders_quintiles[5] THEN 4
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[5] THEN 5
			END AS percentile_area_isochrone, a.area_isochrone
			FROM area_isochrones_scenario a
			WHERE scenario_id = scenario_id_input
		)
		SELECT g.grid_id, 
		CASE WHEN c.percentile_area_isochrone IS NULL THEN g.percentile_area_isochrone::SMALLINT ELSE c.percentile_area_isochrone::SMALLINT 
		END AS percentile_area_isochrone, 
		CASE WHEN c.area_isochrone IS NULL THEN g.area_isochrone ELSE c.area_isochrone END AS area_isochrone, g.geom
		FROM grid_heatmap g
		LEFT JOIN grids_to_classify c
		ON g.grid_id = c.grid_id; 
	END IF;
	
	IF modus_input = 'comparison' THEN 

		ALTER TABLE grids_default ADD PRIMARY KEY(grid_id);
		ALTER TABLE grids_scenario ADD PRIMARY KEY(grid_id);
		
		DROP TABLE IF EXISTS grids_comparison;
		CREATE TEMP TABLE grids_comparison AS 
		SELECT d.grid_id, (s.percentile_area_isochrone - d.percentile_area_isochrone) AS percentile_area_isochrone, 
		COALESCE(s.area_isochrone - d.area_isochrone, 0) AS area_isochrone, d.geom
		FROM grids_default d, grids_scenario s 
		WHERE d.grid_id = s.grid_id;
	
	END IF;
	
	IF modus_input = 'default' THEN 
		RETURN query 
		SELECT * FROM grids_default;
	ELSEIF modus_input = 'scenario' THEN 
		RETURN query 
		SELECT * FROM grids_scenario;
	ELSEIF modus_input = 'comparison' THEN 
		RETURN query 
		SELECT * FROM grids_comparison;
	END IF; 
END
$function$;

/*SELECT * FROM heatmap_connectivity('scenario',2)*/

DROP FUNCTION IF EXISTS heatmap_connectivity;
CREATE OR REPLACE FUNCTION public.heatmap_connectivity(modus_input text DEFAULT 'default', scenario_id_input integer DEFAULT 0)
 RETURNS TABLE(grid_id integer, percentile_area_isochrone smallint, area_isochrone float, geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE
	borders_quintiles numeric[]; 
BEGIN
	
	IF modus_input IN ('default','comparison') THEN   
		DROP TABLE IF EXISTS grids_default; 
		CREATE TEMP TABLE grids_default AS 
		SELECT g.grid_id, g.percentile_area_isochrone, g.area_isochrone, g.geom  
		FROM grid_heatmap g;	
	END IF; 

	IF modus_input IN ('scenario','comparison') THEN  
		SELECT array_agg(border)
		INTO borders_quintiles
		FROM 
		(
			SELECT min(x.area_isochrone) border
			FROM 
			(
				SELECT ntile(5) over (order by g.area_isochrone) AS percentile_area_isochrone, g.area_isochrone
				FROM grid_heatmap g
				WHERE g.percentile_area_isochrone <> 0
			) x 
			GROUP BY x.percentile_area_isochrone
			ORDER BY x.percentile_area_isochrone
		) b;
		
		DROP TABLE IF EXISTS grids_scenario;
		CREATE TEMP TABLE grids_scenario AS 
		WITH grids_to_classify AS 
		(	
			SELECT a.grid_id, 
			CASE WHEN COALESCE(a.area_isochrone,0) = 0 THEN 0
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[1] AND COALESCE(a.area_isochrone,0) < borders_quintiles[2] THEN 1
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[2] AND COALESCE(a.area_isochrone,0) < borders_quintiles[3] THEN 2
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[3] AND COALESCE(a.area_isochrone,0) < borders_quintiles[4] THEN 3
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[4] AND COALESCE(a.area_isochrone,0) < borders_quintiles[5] THEN 4
			WHEN COALESCE(a.area_isochrone,0) >= borders_quintiles[5] THEN 5
			END AS percentile_area_isochrone, a.area_isochrone
			FROM area_isochrones_scenario a
			WHERE scenario_id = scenario_id_input
		)
		SELECT g.grid_id, 
		CASE WHEN c.percentile_area_isochrone IS NULL THEN g.percentile_area_isochrone::SMALLINT ELSE c.percentile_area_isochrone::SMALLINT 
		END AS percentile_area_isochrone, 
		CASE WHEN c.area_isochrone IS NULL THEN g.area_isochrone ELSE c.area_isochrone END AS area_isochrone, g.geom
		FROM grid_heatmap g
		LEFT JOIN grids_to_classify c
		ON g.grid_id = c.grid_id; 
	END IF;
	
	IF modus_input = 'comparison' THEN 

		ALTER TABLE grids_default ADD PRIMARY KEY(grid_id);
		ALTER TABLE grids_scenario ADD PRIMARY KEY(grid_id);
		
		DROP TABLE IF EXISTS grids_comparison;
		CREATE TEMP TABLE grids_comparison AS 
		SELECT d.grid_id, (s.percentile_area_isochrone - d.percentile_area_isochrone) AS percentile_area_isochrone, 
		COALESCE(s.area_isochrone - d.area_isochrone, 0) AS area_isochrone, d.geom
		FROM grids_default d, grids_scenario s 
		WHERE d.grid_id = s.grid_id;
	
	END IF;
	
	IF modus_input = 'default' THEN 
		RETURN query 
		SELECT * FROM grids_default;
	ELSEIF modus_input = 'scenario' THEN 
		RETURN query 
		SELECT * FROM grids_scenario;
	ELSEIF modus_input = 'comparison' THEN 
		RETURN query 
		SELECT * FROM grids_comparison;
	END IF; 
END
$function$;

/*SELECT * FROM heatmap_connectivity('scenario',2)*/

