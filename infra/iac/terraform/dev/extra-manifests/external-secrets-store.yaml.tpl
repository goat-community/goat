apiVersion: v1
kind: Namespace
metadata:
  name: external-secrets
---
apiVersion: v1
kind: Secret
metadata:
  name: base-secrets
  namespace: external-secrets
type: Opaque
data:
  aws-access-key: ${aws_access_key}
  aws-secret-key: ${aws_secret_key}
---
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: cluster-secret-store
spec:
  provider:
    aws:
      service: SecretsManager
      region: ${aws_region}
      auth:
        secretRef:
          accessKeyIDSecretRef: 
            name: base-secrets
            key: aws-access-key
            namespace: external-secrets
          secretAccessKeySecretRef:
            name: base-secrets
            key: aws-secret-key
            namespace: external-secrets