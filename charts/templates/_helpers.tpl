{{- define "helm-chart-repo.fullname" -}}
{{ include "helm-chart-repo.name" . }}-{{ .Release.Name }}
{{- end }}

{{- define "helm-chart-repo.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "helm-chart-repo.labels" -}}
app.kubernetes.io/name: {{ include "helm-chart-repo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "helm-chart-repo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "helm-chart-repo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

