CREATE OR REPLACE FUNCTION accidents_cyclists()
RETURNS TABLE (year text, month text, hours text, bicycle text, car text, pedestrians text, motorbike text, geom geometry) AS
$$
	SELECT ujahr as year, umonat as month, ustunde as hour, istrad as bicycle, 
    istpkw as car, istfuss as pedestrian, istkrad as motorbike, geom 
    FROM accidents 
    WHERE istrad='1';
$$
LANGUAGE sql;

COMMENT ON FUNCTION accidents_cyclists() 
IS '**FOR-API-FUNCTION** RETURNS col_names[year,month,hours,bicycle,car,pedestrians,motorbike,geom] **FOR-API-FUNCTION**';


