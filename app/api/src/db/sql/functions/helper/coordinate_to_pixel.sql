CREATE OR REPLACE FUNCTION basic.coordinate_to_pixel(lat double precision, lon double precision, zoom integer)
 RETURNS integer[]
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
DECLARE
    invCos float;
    tan float;
    ln float;
    lon_pixel integer;
    lat_pixel integer;
    rds float;
BEGIN
    rds = (lat * pi()) / 180;
    invCos = 1 / cos(rds);
    tan = tan(rds);
    ln = ln(tan + invCos);
    lat_pixel = ((1 - (ln / pi())) * pow(2, zoom - 1) * 256);
    lon_pixel = ((lon + 180) / 360 * pow(2, zoom) * 256);
    RETURN ARRAY[lat_pixel, lon_pixel];
END
$function$
;
