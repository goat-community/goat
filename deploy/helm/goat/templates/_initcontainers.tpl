{{/*
One-time bootstrap, done as init containers on the Deployments that need it
(chart 0.5.0+). These replaced two post-install hooks (`ducklake-bootstrap`
and `windmill-db-bootstrap`): with `helm install --wait`, Helm holds
post-install hooks until every resource is Ready, while the pods that needed
those hooks could not go Ready until the hooks had run — a deadlock that
forced a multi-phase first install. An init container creates (or finds) its
own pod's dependency before the main container starts, so there is nothing to
order.

Both are idempotent and race-safe: several pods starting at once may all try
to create the same thing; the loser fails, retries, and finds it done.
*/}}

{{/*
DuckLake catalog init container for geoapi / processes.

Runs goatlib's own idempotent bootstrap (`python -m
goatlib.storage.ducklake_init`, GOAT v3.0.2+) in the component's OWN image —
DuckDB, goatlib and the DuckLake extensions are all baked in, so nothing is
downloaded at run time and the catalog is created in exactly the metadata
format the service will attach. It gets the same ConfigMap, Postgres
credentials, extraEnv and data mount as the main container, so the
DUCKLAKE_DATA_DIR / DUCKLAKE_CATALOG_SCHEMA it creates the catalog with are the
ones the service reads (both are emitted into the component's ConfigMap —
see geoapi/configmap.yaml).

The shell wrapper retries (Postgres may still be starting on a fresh install,
or a sibling pod may be racing it) except in two non-transient cases:
  - DuckLake catalog version mismatch: prints the migration guidance and fails.
  - the catalog exists but was created with a different DATA_PATH than this
    pod's DUCKLAKE_DATA_DIR (per-component DUCKLAKE_DATA_DIR overrides, a
    changed ducklakeBootstrap.dataDir, or a catalog adopted from elsewhere):
    goatlib's init ATTACHes without OVERRIDE_DATA_PATH and DuckDB refuses,
    while the services themselves attach WITH it and run fine. The catalog
    exists, which is all this init is for, so it prints a note and exits 0
    instead of crash-looping forever.
Failure output is passed through a password redaction first, because
DuckDB's attach errors print the full libpq DSN: the literal value of
$POSTGRES_PASSWORD is replaced wherever it appears (so a password with
spaces or quotes is caught too), then every whitespace-separated piece of it
of 3+ characters (libpq echoes the fragment it failed to parse), then any
remaining `password=...` token
(e.g. a password that differs from the env, from a DSN baked elsewhere).

Params: context (root), component ("geoapi" | "processes"), values (that
component's values block).
*/}}
{{- define "goat.ducklakeInit.container" -}}
{{- $root := .context -}}
{{- $v := .values -}}
{{- $ctx := dict "context" $root "component" .component -}}
- name: ducklake-init
  image: {{ include "goat.image" (dict "image" $v.image "global" $root.Values.global "root" $root) }}
  imagePullPolicy: {{ $v.image.pullPolicy }}
  {{- with $v.securityContext }}
  securityContext:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  command: ["sh", "-c"]
  args:
    - |
      attempt=1
      while :; do
        if out=$(python -m goatlib.storage.ducklake_init 2>&1); then
          echo "$out"
          exit 0
        fi
        # DuckDB's connection errors echo the libpq DSN, password included.
        # Replace the literal password first (catches any characters,
        # spaces and quotes included), then each whitespace-separated piece
        # of it (libpq quotes fragments of a password it cannot parse, e.g.
        # `missing "=" after "pa"ss"`), then any other password=... token.
        printf '%s\n' "$out" \
          | python -c 'import os,sys,functools; p=os.environ.get("POSTGRES_PASSWORD",""); ts=([p] if p else [])+[t for t in sorted(set(p.split()),key=len,reverse=True) if len(t)>=3]; sys.stdout.write(functools.reduce(lambda d,t: d.replace(t,"REDACTED"),ts,sys.stdin.read()))' \
          | sed -E 's/password=[^ "]*/password=REDACTED/g' >&2
        case "$out" in
          *"does not match existing data path"*)
            echo "" >&2
            echo "ducklake-init: the DuckLake catalog already exists, but was created with a" >&2
            echo "different data path than this pod's DUCKLAKE_DATA_DIR=${DUCKLAKE_DATA_DIR:-<unset>}." >&2
            echo "The services attach with OVERRIDE_DATA_PATH and will use this pod's" >&2
            echo "DUCKLAKE_DATA_DIR; the catalog exists, which is all this init needs." >&2
            echo "Continuing. Keep DUCKLAKE_DATA_DIR identical across geoapi, processes and" >&2
            echo "the windmill workers (ducklakeBootstrap.dataDir), or files written by one" >&2
            echo "will not be found by another." >&2
            exit 0
            ;;
          *[Cc]atalog\ version\ mismatch*)
            echo "" >&2
            echo "DuckLake catalog version mismatch: this catalog was created by an older" >&2
            echo "duckdb/DuckLake extension (metadata format 0.3) and this image's DuckDB" >&2
            echo "(format 1.0) refuses to attach it. This is a ONE-WAY migration and is not" >&2
            echo "done automatically. Follow docs/ducklake-15-upgrade.md in the main goat" >&2
            echo "repo (pause schedules, scale geoapi/processes/workers to 0, back up the" >&2
            echo "catalog schema, migrate with AUTOMATIC_MIGRATION=true from one pinned pod," >&2
            echo "VACUUM FULL, then roll the new images out)." >&2
            exit 1
            ;;
        esac
        if [ "$attempt" -ge 30 ]; then
          echo "ducklake-init: giving up after $attempt attempts" >&2
          exit 1
        fi
        echo "ducklake-init: attempt $attempt failed, retrying in 5s" >&2
        attempt=$((attempt + 1))
        sleep 5
      done
  envFrom:
    - configMapRef:
        name: {{ include "goat.serviceFullname" $ctx }}
  env:
    - name: POSTGRES_USER
      valueFrom:
        secretKeyRef:
          name: {{ include "goat.postgresql.secretName" $root }}
          key: {{ include "goat.postgresql.userKey" $root }}
    - name: POSTGRES_PASSWORD
      valueFrom:
        secretKeyRef:
          name: {{ include "goat.postgresql.secretName" $root }}
          key: {{ include "goat.postgresql.passwordKey" $root }}
    {{- with $v.extraEnv }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  {{- with $v.resources }}
  resources:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  {{- if or $root.Values.data.enabled $v.extraVolumeMounts }}
  {{- /* Same mounts as the main container: the data volume, plus the
       component's extraVolumeMounts (e.g. a Postgres CA certificate). The
       matching extraVolumes are already pod-level. */}}
  volumeMounts:
    {{- if $root.Values.data.enabled }}
    {{- include "goat.data.mounts.full" $root | nindent 4 }}
    {{- end }}
    {{- with $v.extraVolumeMounts }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  {{- end }}
{{- end }}

{{/*
Whether the windmill database init container is rendered: exactly when this
chart creates the windmill role/secret (chart-managed CNPG, windmill not
sharing goat's connection) — same gate as managed.roles in
postgresql/cluster.yaml and postgresql/windmill-cred-secret.yaml.
*/}}
{{- define "goat.windmillDbInit.enabled" -}}
{{- if and .Values.postgresql.cluster.enabled (not .Values.windmill.db.reuseGoatConnection) -}}
true
{{- end -}}
{{- end }}

{{/*
Windmill database init container for the windmill server and every worker.

The `windmill` database cannot be created by CNPG's postInitSQL (its owner,
`windmill_owner_user`, is a managed role and does not exist yet at initdb —
see postgresql/cluster.yaml), so it is created here, self-service, by that
role (CREATEDB via managed.roles). Uses the Postgres image the Cluster
already runs (`postgresql.cluster.image`, which ships psql) as its `postgres`
user (uid 26). Waits for Postgres and the role to be reachable, creates the
database only if missing (an "already exists" from a racing sibling counts as
success), then pins the owner's search_path in it (idempotent).

Params: the root context.
*/}}
{{- define "goat.windmillDbInit.container" -}}
{{- $image := .Values.postgresql.cluster.image -}}
{{- if not $image -}}
{{- fail "postgresql.cluster.image must be set: the windmill database init container runs psql from it (set windmill.db.reuseGoatConnection: true, or postgresql.cluster.enabled: false with windmill.db.external.*, to skip it)" -}}
{{- end -}}
- name: windmill-db-init
  image: {{ $image | quote }}
  imagePullPolicy: IfNotPresent
  securityContext:
    runAsUser: 26
    runAsNonRoot: true
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    capabilities:
      drop: ["ALL"]
    seccompProfile:
      type: RuntimeDefault
  command: ["sh", "-c"]
  args:
    - |
      set -u
      export PGDATABASE=postgres PGCONNECT_TIMEOUT=5
      attempt=1
      until psql -XtAc 'SELECT 1' >/dev/null 2>&1; do
        if [ "$attempt" -ge 60 ]; then
          echo "windmill-db-init: Postgres not reachable as $PGUSER after $attempt attempts" >&2
          psql -XtAc 'SELECT 1'
          exit 1
        fi
        echo "windmill-db-init: waiting for Postgres at $PGHOST:$PGPORT as $PGUSER ($attempt)"
        attempt=$((attempt + 1))
        sleep 5
      done
      exists() {
        [ "$(psql -XtA -v ON_ERROR_STOP=1 -v db="$WINDMILL_DB" <<'SQL'
      SELECT 1 FROM pg_database WHERE datname = :'db'
      SQL
      )" = "1" ]
      }
      if exists; then
        echo "windmill-db-init: database $WINDMILL_DB already exists"
      elif psql -Xq -v ON_ERROR_STOP=1 -v db="$WINDMILL_DB" -v owner="$PGUSER" <<'SQL'
      CREATE DATABASE :"db" OWNER :"owner"
      SQL
      then
        echo "windmill-db-init: created database $WINDMILL_DB, owner $PGUSER"
      elif exists; then
        echo "windmill-db-init: database $WINDMILL_DB was created concurrently"
      else
        exit 1
      fi
      psql -Xq -v ON_ERROR_STOP=1 -v db="$WINDMILL_DB" -v owner="$PGUSER" <<'SQL'
      ALTER ROLE :"owner" IN DATABASE :"db" SET search_path = public
      SQL
  env:
    - name: PGHOST
      value: {{ include "windmill.postgresql.host" . | quote }}
    - name: PGPORT
      value: {{ include "windmill.postgresql.port" . | quote }}
    - name: WINDMILL_DB
      value: {{ include "windmill.postgresql.database" . | quote }}
    - name: PGUSER
      valueFrom:
        secretKeyRef:
          name: {{ include "windmill.postgresql.secretName" . }}
          key: {{ include "windmill.postgresql.userKey" . }}
    - name: PGPASSWORD
      valueFrom:
        secretKeyRef:
          name: {{ include "windmill.postgresql.secretName" . }}
          key: {{ include "windmill.postgresql.passwordKey" . }}
{{- end }}
