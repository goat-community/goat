apiVersion: v1
kind: Namespace
metadata:
  name: external-secrets
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: external-secrets
  namespace: kube-system
spec:
  repo: https://charts.external-secrets.io
  chart: external-secrets
  targetNamespace: external-secrets
