{{- define "push-to-helm-repo.fullname" -}}
{{ include "push-to-helm-repo.name" . }}-{{ .Release.Name }}
{{- end }}

{{- define "push-to-helm-repo.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "push-to-helm-repo.labels" -}}
app.kubernetes.io/name: {{ include "push-to-helm-repo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "push-to-helm-repo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "push-to-helm-repo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

