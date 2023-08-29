apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - argocd.yaml
  - external-secrets-operator.yaml