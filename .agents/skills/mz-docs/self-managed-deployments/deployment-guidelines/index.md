# Deployment guidelines

Self-managed Materialize requires: a Kubernetes (v1.31+) cluster; PostgreSQL as
a metadata database; blob storage; and a license key.

## Available deployment guidelines

The following guides outline recommended configurations for deploying Materialize across different cloud environments.

- [AWS Deployment
  Guidelines](/self-managed-deployments/deployment-guidelines/aws-deployment-guidelines/)
- [Azure Deployment
  Guidelines](/self-managed-deployments/deployment-guidelines/azure-deployment-guidelines/)
- [GCP Deployment
  Guidelines](/self-managed-deployments/deployment-guidelines/gcp-deployment-guidelines/)

## Pages in this section

- [AWS deployment guidelines](/self-managed-deployments/deployment-guidelines/aws-deployment-guidelines/index.md): General guidelines when deploying Self-Managed Materialize on AWS.
- [Azure deployment guidelines](/self-managed-deployments/deployment-guidelines/azure-deployment-guidelines/index.md): General guidelines when deploying Self-Managed Materialize on Azure.
- [GCP deployment guidelines](/self-managed-deployments/deployment-guidelines/gcp-deployment-guidelines/index.md): General guidelines when deploying Self-Managed Materialize on GCP.
- [GKE node pool upgrades](/self-managed-deployments/deployment-guidelines/gke-node-pool-upgrades/index.md): Configure graceful Materialize rollouts when GKE upgrades the node pools underneath it.
- [Resize node pools](/self-managed-deployments/deployment-guidelines/resize-node-pools/index.md): Safely change the VM type of a node pool in a Self-Managed Materialize deployment.
