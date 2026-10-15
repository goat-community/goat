-- Privileges of a database role of the assistant's own. Not needed when the
-- assistant connects as GOAT's database owner, as the Docker Compose bundle,
-- the Helm chart and Plan4Better's clusters do.
--
-- Run as the database owner after core's migration (alembic upgrade head) and
-- initial_data, with goat_assistant replaced by the role's name. Check the
-- result with `python -m assistant.dbcheck` in the assistant's environment.
-- Keep the table list equal to assistant.dbcheck.CUSTOMER_READS (a test does).

GRANT USAGE ON SCHEMA assistant TO goat_assistant;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA assistant TO goat_assistant;
-- Tables later migrations add, created by the owner who runs this file.
ALTER DEFAULT PRIVILEGES IN SCHEMA assistant
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO goat_assistant;

-- customer.can and the other authz functions are plain SQL functions: they
-- read these tables with the caller's privileges.
GRANT USAGE ON SCHEMA customer TO goat_assistant;
GRANT SELECT ON
  customer.bundle, customer.bundle_layer, customer.folder, customer.layer,
  customer.layer_project, customer.organization, customer.permission,
  customer.project, customer.resource, customer.resource_grant,
  customer.resource_permission, customer.role, customer.role_permission,
  customer.space, customer.team, customer.template, customer."user",
  customer.user_role, customer.user_team
  TO goat_assistant;
-- EXECUTE on every function of the schema is deliberate: authz functions that
-- later migrations add need no change to this file.
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA customer TO goat_assistant;
