"""The SQL behind the processes access check, kept free of settings imports.

core's authorization tests run this exact statement against a real database
(`customer.can` and the published-project table exist there), so this module
must stay importable without the processes configuration.
"""


def access_check_sql(schema: str) -> str:
    """One statement that returns the references the caller may NOT use.

    `$1` is the caller's user id (NULL when anonymous), `$2` a JSON array of
    `{"kind": ..., "id": ..., "action": ...}` with kind one of layer,
    layer_project, project, folder, bundle, template and action one of
    read, write. A layer is readable when any published project contains it,
    or when `can` grants it (which includes a catalog layer's public read).
    A `layer_project` reference is checked as a read of its layer. A
    reference whose id does not resolve is returned as denied.

    A tool puts its result in the folder of the project it runs in, which
    belongs to the project's owner. Writing there is allowed to whoever may
    edit a project the same request names and that lives in that folder,
    so an editor of a shared project can run tools in it.
    """
    return f"""
WITH refs AS (
    SELECT r->>'kind' AS kind, r->>'id' AS raw_id, r->>'action' AS action
      FROM jsonb_array_elements($2::jsonb) AS r
), resolved AS (
    SELECT kind, raw_id, action,
           CASE
               WHEN kind = 'layer_project' THEN (
                   SELECT lp.layer_id FROM {schema}.layer_project lp
                    WHERE raw_id ~ '^[0-9]{{1,18}}$' AND lp.id = raw_id::bigint
               )
               WHEN raw_id ~* '^[0-9a-f]{{8}}-?([0-9a-f]{{4}}-?){{3}}[0-9a-f]{{12}}$'
                   THEN raw_id::uuid
           END AS ref_id,
           CASE WHEN kind = 'layer_project' THEN 'layer' ELSE kind END AS checked_kind,
           CASE WHEN kind = 'layer_project' THEN 'read' ELSE action END AS checked_action
      FROM refs
)
SELECT kind, raw_id, action
  FROM resolved
 WHERE ref_id IS NULL
    OR NOT (
        (checked_kind = 'layer' AND checked_action = 'read' AND EXISTS (
            SELECT 1
              FROM {schema}.project_public pp
             WHERE pp.config->'layers'
                   @> jsonb_build_array(jsonb_build_object('layer_id', ref_id::text))
        ))
        OR COALESCE({schema}.can(checked_kind, ref_id, $1::uuid, checked_action), FALSE)
        OR (checked_kind = 'folder' AND checked_action = 'write' AND EXISTS (
            SELECT 1
              FROM resolved named
              JOIN {schema}.project p ON p.id = named.ref_id
             WHERE named.checked_kind = 'project'
               AND p.folder_id = resolved.ref_id
               AND COALESCE({schema}.can('project', p.id, $1::uuid, 'write'), FALSE)
        ))
    )
"""
