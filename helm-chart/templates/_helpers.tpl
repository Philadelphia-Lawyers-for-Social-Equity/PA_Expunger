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
The backend pod's environment, shared by the app container and the wait-for-migrations
init container in deployment.yaml so the gate always checks the database the app uses.
*/}}
{{- define "pa-expunger.backendEnv" -}}
- name: DB_HOST
  value: {{ include "pa-expunger.dbHost" . }}
- name: DJANGO_LOG_LEVEL
  value: {{ .Values.backend.config.DJANGO_LOG_LEVEL | quote }}
- name: DJANGO_ALLOWED_HOSTS
  value: {{ include "pa-expunger.allowedHosts" . | quote }}
- name: BACKEND_API_URL
  value: {{ include "pa-expunger.backendApiUrl" . | quote }}
- name: HELM_APP_VERSION
  value: {{ .Chart.AppVersion | quote }}
# Deliberately not set on the migration Job: its name is keyed on its template
# revision, the image tag and bootstrapRevision only, so a chart version bump changing none
# would change an existing Job's immutable pod template and fail the apply.
- name: HELM_CHART_VERSION
  value: {{ .Chart.Version | quote }}
- name: DB_USER
  valueFrom:
    secretKeyRef:
      key: POSTGRES_USER
      name: {{ include "pa-expunger.postgresSecretName" . | quote }}
- name: DB_NAME
  valueFrom:
    secretKeyRef:
      key: POSTGRES_DB
      name: {{ include "pa-expunger.postgresSecretName" . | quote }}
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      key: POSTGRES_PASSWORD
      name: {{ include "pa-expunger.postgresSecretName" . | quote }}
- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP
# Only DJANGO_SECRET_KEY, not the whole backend secret: SUPERUSER_USERNAME/
# SUPERUSER_PASSWORD live in that secret too, for ensure_superuser in the
# migration Job, and the app itself has no use for them. Keeping envFrom here
# would put the admin password in every app pod's environment for no reason.
- name: DJANGO_SECRET_KEY
  valueFrom:
    secretKeyRef:
      key: DJANGO_SECRET_KEY
      name: {{ include "pa-expunger.backendSecretName" . | quote }}
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
locally it is k8s-e2e-test/postgres.yaml.

Fails the render rather than defaulting, because an unset DB_HOST surfaces as a confusing
connection error inside a running pod instead of a build failure.
*/}}
{{- define "pa-expunger.dbHost" -}}
{{- if .Values.externalDatabase.host -}}
{{- .Values.externalDatabase.host -}}
{{- else -}}
{{- fail "FATAL: no database host configured. Set externalDatabase.host, e.g. shared-cluster-rw.cloudnative-pg.svc.cluster.local in the sandbox, or pa-expunger-local-postgres when testing against k8s-e2e-test/postgres.yaml." -}}
{{- end -}}
{{- end -}}
