CREATE OR REPLACE FUNCTION update_impedance(wid integer, interval_ float DEFAULT 10)
RETURNS SETOF void
LANGUAGE plpgsql
AS $function$
DECLARE 
	v_s_imp float;
	v_rs_imp float;
BEGIN
	SELECT ci.imp, ci.rs_imp
	INTO v_s_imp, v_rs_imp
	FROM get_slope_profile(wid,interval_), LATERAL compute_impedances(elevs, linkLength, interval_) ci;
	
	UPDATE ways SET s_imp = v_s_imp, rs_imp = v_rs_imp 
	WHERE id = wid;
END;
$function$;
--SELECT update_impedance(3,10);