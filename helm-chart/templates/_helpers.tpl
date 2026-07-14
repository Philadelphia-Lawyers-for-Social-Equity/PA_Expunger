{{/*
Expand the name of the chart.
*/}}
{{- define "pa-expunger.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "pa-expunger.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "pa-expunger.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "pa-expunger.labels" -}}
helm.sh/chart: {{ include "pa-expunger.chart" . }}
{{ include "pa-expunger.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "pa-expunger.selectorLabels" -}}
app.kubernetes.io/name: {{ include "pa-expunger.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "pa-expunger.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "pa-expunger.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "pa-expunger.allowedHosts" -}}
{{- /* Start with the list of extra hosts from values.yaml */ -}}
{{- $hosts := .Values.backend.allowedHosts.extra | default list | deepCopy -}}
{{- /* Add the internal Kubernetes service names */ -}}
{{- $hosts = append $hosts (printf "%s-backend-svc" .Release.Name) -}}
{{- $hosts = append $hosts (printf "%s-backend-svc.%s.svc.cluster.local" .Release.Name .Release.Namespace) -}}
{{- /* Add all hosts defined in the ingress section */ -}}
{{- range .Values.ingress.hosts -}}
{{- $hosts = append $hosts .host -}}
{{- end -}}
{{- /* Join the list into a comma-separated string, removing duplicates */ -}}
{{- $hosts | uniq | join "," -}}
{{- end -}}

{{/*
Construct the backend API host from the first ingress host
*/}}
{{- define "pa-expunger.backendApiUrl" -}}
{{- if .Values.apiUrlOverride }}
{{- /* If an explicit apiUrl is provided (and is not an empty string), use it. */ -}}
{{- .Values.apiUrlOverride -}}
{{- else if and .Values.ingress.enabled .Values.ingress.hosts }}
{{- /* Otherwise, if ingress hosts exist, derive the URL from the first one. */ -}}
{{- $host := first .Values.ingress.hosts -}}
{{- printf "https://%s" $host.host -}}
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
