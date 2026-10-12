CREATE OR REPLACE FUNCTION customer.authorization(
    user_id UUID,
    requested_resource TEXT,
    requested_path TEXT, 
    requested_method TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    extracted_params JSONB;
    layer_ids UUID[];
    project_ids UUID[];
    team_ids UUID;
    organization_id UUID;
    requested_team_id UUID;
    rec_resource RECORD;
    rec_user RECORD;
    rec_organization RECORD; 
    rec_role RECORD;
    total_quota_column TEXT;
    used_quota_column TEXT;
    rec_organization_json JSONB;
BEGIN
    /*Extract the parameters to check from query params and path*/
    extracted_params := customer.extract_params_request(requested_resource, requested_path);

    /*Get layer_ids, project_ids, team_ids and organization_id*/
    --Check if layer_id in params if layer_ids use it
    IF extracted_params -> 'layer_id' IS NOT NULL THEN
        layer_ids := (
            SELECT ARRAY_AGG(val::UUID)
            FROM (SELECT jsonb_array_elements_text(extracted_params -> 'layer_id') AS val) x
        );
    ELSEIF extracted_params -> 'layer_ids' IS NOT NULL THEN
        layer_ids := (
            SELECT ARRAY_AGG(val::UUID)
            FROM (SELECT jsonb_array_elements_text(extracted_params -> 'layer_ids') AS val) x
        );
    END IF;

    project_ids := (
        SELECT ARRAY_AGG(val::UUID)
    	FROM (SELECT jsonb_array_elements_text(extracted_params -> 'project_id') AS val) x
	);
    team_ids := (extracted_params -> 'team_ids' )::TEXT::UUID[];
    -- Each extracted value is a one-element JSON array; JSON arrays are
    -- 0-indexed, and ->> unquotes the string for the cast.
    organization_id := (extracted_params -> 'organization_id' ->> 0)::UUID;
    requested_team_id := (extracted_params -> 'team_id' ->> 0)::UUID;

    /*Get resource into a record*/
    rec_resource := customer.check_resource(requested_resource, requested_path, requested_method);

    /*Get user into a record*/
    rec_user := customer.check_user(user_id, rec_resource);
    
    /*Get organization into a record*/
    rec_organization := customer.check_organization(rec_user, rec_resource, organization_id);

    /*A team in the path must belong to the user's organization*/
    IF requested_team_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
            FROM customer.team t
            WHERE t.id = requested_team_id
            AND t.organization_id = rec_user.organization_id
        ) THEN
            RAISE EXCEPTION 'Team from request params does not belong to organization from user';
        END IF;
    END IF;

    /*Check team*/
    IF team_ids IS NOT NULL THEN
        PERFORM customer.check_team(rec_user.id, team_ids, rec_resource.id);
    END IF;
    
    /*Check if user has access to the layers*/
    IF layer_ids IS NOT NULL THEN
        PERFORM customer.check_layer(rec_resource.id, rec_user.id, rec_user.organization_id, layer_ids);
    END IF;

    /*Check if user has access to the projects*/
    IF project_ids IS NOT NULL THEN
        PERFORM customer.check_project(rec_resource.id, rec_user.id, rec_user.organization_id, project_ids);
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
