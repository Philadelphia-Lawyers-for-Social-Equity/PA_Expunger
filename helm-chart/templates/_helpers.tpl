{{- define "pa-expunger.allowedHosts" -}}
{{- /* Start with the list of extra hosts from values.yaml */ -}}
{{- $hosts := .Values.backend.allowedHosts.extra | default list | deepCopy -}}
{{- /* Add the internal Kubernetes service names */ -}}
{{- $hosts = append $hosts (printf "%s-backend-svc" .Release.Name) -}}
{{- $hosts = append $hosts (printf "%s-backend-svc.%s.svc.cluster.local" .Release.Name .Release.Namespace) -}}
{{- /* Add the public hostname. Routing lives outside this chart, so this is the only
       source of the externally-facing name. Omitting it means Django rejects every
       request from the outside world with a 400. */ -}}
{{- if .Values.publicHostname -}}
{{- $hosts = append $hosts .Values.publicHostname -}}
{{- end -}}
{{- /* Join the list into a comma-separated string, removing duplicates */ -}}
{{- $hosts | uniq | join "," -}}
{{- end -}}

{{/*
Construct the public origin the app is served from.
Precedence: apiUrlOverride, then publicHostname.
*/}}
{{- define "pa-expunger.backendApiUrl" -}}
{{- if .Values.apiUrlOverride -}}
{{- /* An explicit origin wins: use it when the public origin is not simply
       https://<publicHostname>, e.g. a CDN in front or a non-standard port. */ -}}
{{- .Values.apiUrlOverride -}}
{{- else if .Values.publicHostname -}}
{{- printf "https://%s" .Values.publicHostname -}}
{{- else -}}
{{- /* Failing loudly beats rendering an empty BACKEND_API_URL: prod.py would leave
       CSRF_TRUSTED_ORIGINS empty and every admin/session POST would 403 in a way
       that only shows up once someone tries to log in. */ -}}
{{- fail "FATAL: no public origin configured. Set publicHostname (or apiUrlOverride). When testing against a port-forward rather than a real hostname, set publicHostname to localhost." -}}
{{- end -}}
{{- end -}}

{{/*
Returns the appropriate backend secret name based on the context.
If secrets.create is true (local testing), it uses the local dummy secret name.
Otherwise, it uses the production secret name from values.
*/}}
{{- define "pa-expunger.backendSecretName" -}}
{{- ternary .Values.secrets.backendSecretName .Values.backend.existingSecret .Values.secrets.create -}}
{{- end -}}

{{/*
As in the above function, returns the appropriate postgres secret name based on the context.
*/}}
{{- define "pa-expunger.postgresSecretName" -}}
{{- ternary .Values.secrets.postgresSecretName .Values.postgres.existingSecret .Values.secrets.create -}}
{{- end -}}

{{/*
The database host. This chart runs no database of its own. The environment supplies one,
the same way it supplies routing. In the sandbox that is the shared CloudNativePG cluster;
locally it is local-test/postgres.yaml.

Fails the render rather than defaulting, because an unset DB_HOST surfaces as a confusing
connection error inside a running pod instead of a build failure.
*/}}
{{- define "pa-expunger.dbHost" -}}
{{- if .Values.externalDatabase.host -}}
{{- .Values.externalDatabase.host -}}
{{- else -}}
{{- fail "FATAL: no database host configured. Set externalDatabase.host, e.g. shared-cluster-rw.cloudnative-pg.svc.cluster.local in the sandbox, or pa-expunger-local-postgres when testing against local-test/postgres.yaml." -}}
{{- end -}}
{{- end -}}
