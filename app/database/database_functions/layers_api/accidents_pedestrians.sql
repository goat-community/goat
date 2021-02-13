CREATE OR REPLACE FUNCTION accidents_pedestrians()
RETURNS TABLE (year text, month text, hours text, bicycle text, car text, pedestrians text, motorbike text, geom geometry) AS
$$
	SELECT ujahr AS year, umonat AS month, ustunde AS hour, istrad AS bicycle, 
    istpkw AS car, istfuss AS pedestrian, istkrad AS motorbike, geom 
    FROM accidents WHERE istfuss='1';
$$
LANGUAGE sql;

COMMENT ON FUNCTION accidents_pedestrians() 
IS '**FOR-API-FUNCTION** RETURNS col_names[year,month,hours,bicycle,car,pedestrians,motorbike,geom] **FOR-API-FUNCTION**';


