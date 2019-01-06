CREATE OR REPLACE FUNCTION public.show_network(max_cost float,modus_input integer, userid_input integer)
 RETURNS TABLE(id bigint,node integer,cost NUMERIC,class_id integer, geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE
--Declares the output as type pg_isochrone

ways_table varchar(20) := 'ways';
sql_userid varchar(100):='';
excluded_class_id varchar(200);
excluded_ways_id text;
begin
  --depending on the modus the default OR the input table is used
  if modus_input = 2 OR modus_input = 4 then
  	ways_table = 'ways_userinput';
  	sql_userid = ' AND w.userid IS NULL OR w.userid ='||userid_input;
  
  END IF;
 
  RAISE NOTICE '%',sql_userid;
  
  SELECT array_append(array_agg(x.id),0::bigint)::text INTO excluded_ways_id FROM (
	SELECT Unnest(deleted_feature_ids) id FROM user_data u
	WHERE u.id = userid_input
	UNION ALL
	SELECT original_id modified
	FROM ways_modified 
	WHERE userid = userid_input AND original_id IS NOT null
  ) x;
 
  SELECT variable_array::varchar(200)
  INTO excluded_class_id 
  FROM variable_container v
  WHERE v.identifier = 'excluded_class_id_walking';
  return query execute '
  with xx AS (
		SELECT * FROM (		--Select all that share ways that share a node with the edges
			SELECT w.id, n.node, w.source, w.target, w.geom, coalesce(w.class_id,0) class_id, n.cost 
			FROM '||ways_table||' w, temp_edges n 
			WHERE w.source = n.node
			OR w.target = n.node '||sql_userid||
		') t 
		WHERE NOT t.class_id = ANY('''||excluded_class_id||''')
		and NOT t.id::int4 = any('''|| excluded_ways_id ||''') 
	),
	x AS (
		SELECT xx.*
		FROM xx, 
		(
			SELECT max(cost) AS cost, geom   
			FROM xx
			GROUP BY geom
			HAVING count(geom) > 1
			UNION ALL 
			SELECT max(cost) AS cost, geom   
			FROM xx 
			GROUP BY geom
			HAVING count(geom) = 1
		) t
		WHERE xx.geom = t.geom 
		AND xx.cost=t.cost
	),
	y AS ( --Select all that only share one node with the edges ==> these are lines touching at the borders
		SELECT count(*), SOURCE
		FROM 
		(	SELECT source FROM x
			UNION ALL
			SELECT target FROM x
		) x
		GROUP BY SOURCE 
		HAVING count(*) < 2
	),
	z AS ( -- Cut these touching lines depending on the value missing to reach isochrone calculation limit 
		SELECT x.id, x.node,'||max_cost||' AS cost, x.class_id, st_linesubstring(geom,1-('||max_cost||'-cost)/ST_length(geom::geography),1) geom 
		FROM x, y
		WHERE x.SOURCE = y.source 
		AND 1-('||max_cost||'-cost)/ST_length(geom::geography) BETWEEN 0 AND 1
		UNION ALL 
		SELECT id,x.node,'||max_cost||' AS cost, x.class_id, st_linesubstring(geom,0.0,('||max_cost||'-cost)/ST_length(geom::geography)) geom FROM x, y
		WHERE x.target = y.source 
		AND ('||max_cost||'-cost)/ST_length(geom::geography) BETWEEN 0 AND 1
	)
	SELECT DISTINCT x.id, x.node, x.cost, x.class_id, x.geom 
	FROM x 
	LEFT JOIN z ON x.id = z.id 
	WHERE z.id IS NULL
	UNION ALL 
	SELECT * FROM z
	UNION ALL
	SELECT * FROM (
		SELECT w.id, n.node, n.cost, w.class_id, w.geom 
		FROM '||ways_table||' w, temp_edges n 
		WHERE  w.source = n.node
		AND w.target = n.node
	) t 
	WHERE NOT t.class_id = ANY('''||excluded_class_id||''')';
--Workaround St_CollectionExtract AND filter all with length 0
  RETURN;
END ;
$function$
