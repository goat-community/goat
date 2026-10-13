{{/*
──── Garage (garage.enabled) ────────────────────────────────────────────────
A single-node S3 store in the release. Its names, and the S3 settings every
service reads: `global.s3`, with the keys left empty filled for Garage.
*/}}

{{- define "goat.garage.fullname" -}}
{{- include "goat.serviceFullname" (dict "context" . "component" "garage") -}}
{{- end }}

{{/* rpc-secret and admin-token. */}}
{{- define "goat.garage.secretName" -}}
{{- .Values.garage.existingSecret | default (printf "%s-garage" (include "goat.fullname" .)) -}}
{{- end }}

{{/* The S3 key pair the chart generates when global.s3.existingSecret is empty. */}}
{{- define "goat.garage.keySecretName" -}}
{{- printf "%s-garage-s3" (include "goat.fullname" .) -}}
{{- end }}

{{/*
The effective object storage settings, as YAML (read with fromYaml):
`global.s3`, and with garage.enabled every key left empty filled for the
bundled Garage. The public URLs default to the web app's host, where
garage.ingress (or the operator) routes /<bucket> to Garage's S3 API and
/<assets bucket> to its website endpoint. Param: root.
*/}}
{{- define "goat.s3.settings" -}}
{{- $s3 := deepCopy (.Values.global.s3 | default dict) -}}
{{- if .Values.garage.enabled -}}
{{- $web := include "goat.web.publicUrl" . | trimSuffix "/" -}}
{{- $bucket := $s3.bucket | default "goat-uploads" -}}
{{- $_ := set $s3 "bucket" $bucket -}}
{{- if not $s3.endpointUrl -}}
{{- $_ := set $s3 "endpointUrl" (printf "http://%s:3900" (include "goat.garage.fullname" .)) -}}
{{- $_ := set $s3 "forcePathStyle" true -}}
{{- end -}}
{{- $_ := set $s3 "provider" ($s3.provider | default "garage") -}}
{{- $_ := set $s3 "region" ($s3.region | default "garage") -}}
{{- if and (not $s3.publicEndpointUrl) $web -}}
{{- $_ := set $s3 "publicEndpointUrl" $web -}}
{{- end -}}
{{- if not $s3.existingSecret -}}
{{- $_ := set $s3 "existingSecret" (include "goat.garage.keySecretName" .) -}}
{{- $_ := set $s3 "existingSecretKeys" (dict "accessKeyId" "access-key-id" "secretAccessKey" "secret-access-key") -}}
{{- end -}}
{{- $assets := deepCopy ($s3.assets | default dict) -}}
{{- $_ := set $assets "bucket" ($assets.bucket | default "goat-assets") -}}
{{- if and (not $assets.publicUrl) $web -}}
{{- $_ := set $assets "publicUrl" (printf "%s/%s" $web $assets.bucket) -}}
{{- end -}}
{{- $_ := set $s3 "assets" $assets -}}
{{- end -}}
{{- toYaml $s3 -}}
{{- end }}
