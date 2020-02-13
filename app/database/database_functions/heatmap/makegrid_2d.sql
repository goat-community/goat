DROP FUNCTION IF EXISTS makegrid_2d;
CREATE OR REPLACE FUNCTION public.makegrid_2d(bound_polygon geometry, width_step integer, height_step integer)
 RETURNS geometry
 LANGUAGE plpgsql
AS $function$
DECLARE
  Xmin DOUBLE PRECISION;
  Xmax DOUBLE PRECISION;
  Ymax DOUBLE PRECISION;
  X DOUBLE PRECISION;
  Y DOUBLE PRECISION;
  NextX DOUBLE PRECISION;
  NextY DOUBLE PRECISION;
  CPoint public.geometry;
  sectors public.geometry[];
  i INTEGER;
  SRID INTEGER;
BEGIN
  Xmin := ST_XMin(bound_polygon);
  Xmax := ST_XMax(bound_polygon);
  Ymax := ST_YMax(bound_polygon);
  SRID := ST_SRID(bound_polygon);

  Y := ST_YMin(bound_polygon); --current sector's corner coordinate
  i := -1;
  <<yloop>>
  LOOP
    IF (Y > Ymax) THEN  
        EXIT;
    END IF;

    X := Xmin;
    <<xloop>>
    LOOP
      IF (X > Xmax) THEN
          EXIT;
      END IF;

      CPoint := ST_SetSRID(ST_MakePoint(X, Y), SRID);
      NextX := ST_X(ST_Project(CPoint, $2, radians(90))::geometry);
      NextY := ST_Y(ST_Project(CPoint, $3, radians(0))::geometry);

      i := i + 1;
      sectors[i] := ST_MakeEnvelope(X, Y, NextX, NextY, SRID);

      X := NextX;
    END LOOP xloop;
    CPoint := ST_SetSRID(ST_MakePoint(X, Y), SRID);
    NextY := ST_Y(ST_Project(CPoint, $3, radians(0))::geometry);
    Y := NextY;
  END LOOP yloop;

  RETURN ST_Collect(sectors);
END;
$function$

