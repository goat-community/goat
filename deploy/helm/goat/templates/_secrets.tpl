{{/*
Resolve the secret NAME holding the postgres user credentials.
- If postgresql.cluster.enabled: CNPG creates a "<cluster>-app" secret containing username + password keys.
- Else if postgresql.external.existingSecret is set: use that.
- Else: fail loudly at render time.

Returns the secret name (string). Caller is responsible for the keys.
*/}}
{{- define "goat.postgresql.secretName" -}}
{{- if .Values.postgresql.cluster.enabled -}}
{{- printf "%s-pg-app" (include "goat.fullname" .) -}}
{{- else if .Values.postgresql.external.existingSecret -}}
{{- .Values.postgresql.external.existingSecret -}}
{{- else -}}
{{- fail "postgresql.external.existingSecret is required when postgresql.cluster.enabled is false" -}}
{{- end -}}
{{- end -}}

{{/*
Key inside the postgres secret for the username.
- Bundled (CNPG): always "username"
- External: configurable via postgresql.external.existingSecretUserKey (default "username")
*/}}
{{- define "goat.postgresql.userKey" -}}
{{- if .Values.postgresql.cluster.enabled -}}
username
{{- else -}}
{{- default "username" .Values.postgresql.external.existingSecretUserKey -}}
{{- end -}}
{{- end -}}

{{/*
Key inside the postgres secret for the password.
*/}}
{{- define "goat.postgresql.passwordKey" -}}
{{- if .Values.postgresql.cluster.enabled -}}
password
{{- else -}}
{{- default "password" .Values.postgresql.external.existingSecretPasswordKey -}}
{{- end -}}
{{- end -}}

{{/*
Resolve the postgres HOST.
- Bundled: <release>-<chart>-pg-rw (CNPG service naming convention)
- External: postgresql.external.host
*/}}
{{- define "goat.postgresql.host" -}}
{{- if .Values.postgresql.cluster.enabled -}}
{{- printf "%s-pg-rw" (include "goat.fullname" .) -}}
{{- else -}}
{{- required "postgresql.external.host is required when postgresql.cluster.enabled is false" .Values.postgresql.external.host -}}
{{- end -}}
{{- end -}}

{{/*
Postgres database name. Same for bundled and external in v1.
*/}}
{{- define "goat.postgresql.database" -}}
{{- default "goat" .Values.postgresql.external.database -}}
{{- end -}}

{{/*
Postgres port.
*/}}
{{- define "goat.postgresql.port" -}}
{{- default 5432 .Values.postgresql.external.port | toString -}}
{{- end -}}

{{/*
Windmill database helpers.

Windmill is bootstrap-heavy: its server runs migrations that CREATE ROLE +
GRANT inside whichever database it points at. Running those against the
shared goat DB (as `windmill.db.reuseGoatConnection: true` does) is
disruptive — windmill writes ~100 tables in the goat user's default schema
and the migrations require role-creation privileges that the goat owner
typically does not have. The default in values.yaml is therefore false.

Resolution precedence (most-specific wins):
  1. `windmill.db.reuseGoatConnection: true`     → fall through to goat helpers
  2. `windmill.db.external.*` populated          → use those literal values
  3. `postgresql.cluster.enabled: true` (CNPG)   → auto-wire to chart-managed
     `<release>-pg-windmill-cred` secret + `<release>-pg-rw` service, with
     the windmill DB / roles provisioned by the CNPG Cluster template
  4. Otherwise                                   → fail at render time
*/}}

{{- define "windmill.postgresql.secretName" -}}
{{- if .Values.windmill.db.reuseGoatConnection -}}
{{- include "goat.postgresql.secretName" . -}}
{{- else if .Values.windmill.db.external.existingSecret -}}
{{- .Values.windmill.db.external.existingSecret -}}
{{- else if .Values.postgresql.cluster.enabled -}}
{{- printf "%s-pg-windmill-cred" (include "goat.fullname" .) -}}
{{- else -}}
{{- fail "windmill.db.external.existingSecret is required (or set postgresql.cluster.enabled: true to let the chart manage it)" -}}
{{- end -}}
{{- end -}}

{{- define "windmill.postgresql.userKey" -}}
{{- if .Values.windmill.db.reuseGoatConnection -}}
{{- include "goat.postgresql.userKey" . -}}
{{- else -}}
{{- default "username" .Values.windmill.db.external.existingSecretUserKey -}}
{{- end -}}
{{- end -}}

{{- define "windmill.postgresql.passwordKey" -}}
{{- if .Values.windmill.db.reuseGoatConnection -}}
{{- include "goat.postgresql.passwordKey" . -}}
{{- else -}}
{{- default "password" .Values.windmill.db.external.existingSecretPasswordKey -}}
{{- end -}}
{{- end -}}

{{- define "windmill.postgresql.host" -}}
{{- if .Values.windmill.db.reuseGoatConnection -}}
{{- include "goat.postgresql.host" . -}}
{{- else if .Values.windmill.db.external.host -}}
{{- .Values.windmill.db.external.host -}}
{{- else if .Values.postgresql.cluster.enabled -}}
{{- printf "%s-pg-rw" (include "goat.fullname" .) -}}
{{- else -}}
{{- fail "windmill.db.external.host is required (or set postgresql.cluster.enabled: true)" -}}
{{- end -}}
{{- end -}}

{{- define "windmill.postgresql.port" -}}
{{- if .Values.windmill.db.reuseGoatConnection -}}
{{- include "goat.postgresql.port" . -}}
{{- else -}}
{{- default 5432 .Values.windmill.db.external.port | toString -}}
{{- end -}}
{{- end -}}

{{- define "windmill.postgresql.database" -}}
{{- if .Values.windmill.db.reuseGoatConnection -}}
{{- include "goat.postgresql.database" . -}}
{{- else -}}
{{- default "windmill" .Values.windmill.db.external.database -}}
{{- end -}}
{{- end -}}

{{/*
Redis — host. Bundled sub-chart service is <release>-redis-master.
*/}}
{{- define "goat.redis.host" -}}
{{- if .Values.redis.enabled -}}
{{- include "goat.serviceFullname" (dict "context" . "component" "redis") -}}
{{- else -}}
{{- required "redis.external.host is required when redis.enabled is false" .Values.redis.external.host -}}
{{- end -}}
{{- end }}

{{- define "goat.redis.port" -}}
{{- if .Values.redis.enabled -}}6379{{- else -}}{{- .Values.redis.external.port -}}{{- end -}}
{{- end }}

{{- define "goat.redis.database" -}}
{{- if .Values.redis.enabled -}}0{{- else -}}{{- .Values.redis.external.database -}}{{- end -}}
{{- end }}

{{/*
Redis — whether a password is in play at all.
*/}}
{{- define "goat.redis.authEnabled" -}}
{{- if .Values.redis.enabled -}}
{{- if .Values.redis.auth.enabled -}}true{{- end -}}
{{- else -}}
{{- if .Values.redis.external.existingSecret -}}true{{- end -}}
{{- end -}}
{{- end }}

{{/*
Redis — the Secret holding the password: redis.auth.existingSecret, else the
one the chart generates (templates/redis/secret.yaml).
*/}}
{{- define "goat.redis.secretName" -}}
{{- if .Values.redis.enabled -}}
{{- .Values.redis.auth.existingSecret | default (printf "%s-redis" (include "goat.fullname" .)) -}}
{{- else -}}
{{- .Values.redis.external.existingSecret -}}
{{- end -}}
{{- end }}

{{- define "goat.redis.passwordKey" -}}
{{- if .Values.redis.enabled -}}
{{- if .Values.redis.auth.existingSecret -}}{{- .Values.redis.auth.existingSecretPasswordKey | default "redis-password" -}}{{- else -}}redis-password{{- end -}}
{{- else -}}
{{- .Values.redis.external.existingSecretPasswordKey -}}
{{- end -}}
{{- end }}

{{/*
Redis — the URL itself. When a password is in play this emits a $(REDIS_PASSWORD)
reference, so the caller MUST emit a REDIS_PASSWORD env var BEFORE this one:
Kubernetes only substitutes $(VAR) against variables defined earlier in the list.
*/}}
{{- define "goat.redis.url" -}}
{{- if include "goat.redis.authEnabled" . -}}
{{- printf "redis://:$(REDIS_PASSWORD)@%s:%s/%s" (include "goat.redis.host" .) (include "goat.redis.port" .) (include "goat.redis.database" .) -}}
{{- else -}}
{{- printf "redis://%s:%s/%s" (include "goat.redis.host" .) (include "goat.redis.port" .) (include "goat.redis.database" .) -}}
{{- end -}}
{{- end }}
