
/*This function is used if the intersection with a landuse table results in one building intersecting both residential and not-residential 
category.*/
DROP FUNCTION IF EXISTS derive_dominant_class;
CREATE OR REPLACE FUNCTION derive_dominant_class(bgid integer, categorization integer[], landuse_gids integer[], landuse_table TEXT)
 RETURNS integer
AS $$
DECLARE
   bgeom geometry := (SELECT geom FROM buildings WHERE gid = bgid);
   dominant_class integer;
BEGIN
	IF landuse_table = 'landuse' THEN 
		SELECT CASE WHEN ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom)))/ST_AREA(bgeom) > 0.5 THEN cat ELSE 2 END AS cat
		INTO dominant_class
		FROM (SELECT UNNEST(categorization) cat, UNNEST(landuse_gids) gid) c, landuse_subdivide l 
		WHERE l.gid = c.gid
		GROUP BY cat 
		ORDER BY ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom))) 
		DESC
		LIMIT 1;
	ELSEIF landuse_table = 'landuse_additional' THEN 
		SELECT CASE WHEN ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom)))/ST_AREA(bgeom) > 0.5 THEN cat ELSE 2 END AS cat
		INTO dominant_class
		FROM (SELECT UNNEST(categorization) cat, UNNEST(landuse_gids) gid) c, landuse_additional_subdivide l 
		WHERE l.gid = c.gid
		GROUP BY cat 
		ORDER BY ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom)))
		DESC
		LIMIT 1;
	ELSEIF landuse_table = 'landuse_osm' THEN 
		SELECT CASE WHEN ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom)))/ST_AREA(bgeom) > 0.5 THEN cat ELSE 2 END AS cat
		INTO dominant_class
		FROM (SELECT UNNEST(categorization) cat, UNNEST(landuse_gids) gid) c, landuse_osm_subdivide l 
		WHERE l.gid = c.gid
		GROUP BY cat 
		ORDER BY ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom))) 
		DESC
		LIMIT 1;
	ELSE 
		RAISE NOTICE 'No valid landuse table was selected.';
	END IF; 

	RETURN dominant_class;
END
$$ LANGUAGE plpgsql;
