DROP FUNCTION IF EXISTS update_accessibility_array;
CREATE OR REPLACE FUNCTION update_accessibility_array(arr_to_update int[][], arr_to_add int[][], arr_position integer)
RETURNS SETOF integer[][] AS
$$
	SELECT arr[1:(-1+arr_position)] + new_value || arr[arr_position+1:]
	FROM 
	(
		SELECT unnest_2d_1d(arr_to_update) arr, UNNEST(arr_to_add) new_value
	) x
$$
LANGUAGE sql immutable;
--SELECT update_accessibility_array(array[[1,2,3],[4,5,6]],ARRAY[[22],[34]],2)

CREATE OR REPLACE FUNCTION append_accessibility_array(arr_to_update int[][], arr_to_append int[][])
RETURNS SETOF integer[][] AS
$$
	SELECT ARRAY_AGG(arr1 || arr2)
	FROM 
	(
		SELECT unnest_2d_1d(arr_to_update) arr1, unnest_2d_1d(arr_to_append) arr2
	) x; 
$$
LANGUAGE sql immutable;

--SELECT append_accessibility_array(ARRAY[[1,2],[3,4]],ARRAY[[5,6],[7,8]] )