# Install on GCP
Deploy the advanced SSO stack on GCP with Materialize.
This guide walks through the
[`gcp/examples/enterprise`](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/gcp/examples/enterprise)
example in the [Materialize Terraform
repository](https://github.com/MaterializeInc/materialize-terraform-self-managed),
which extends the base [Install on
GCP](/self-managed-deployments/installation/install-on-gcp/) walkthrough with
the advanced SSO stack on GKE.

If Materialize is already running, see [Add to an existing
installation](/self-managed-deployments/sso/advanced/existing-installation/)
instead.

Self-managed Materialize requires: a Kubernetes (v1.31+) cluster; PostgreSQL as
a metadata database; blob storage; and a license key.
 This example layers the
Ory stack (Kratos, Hydra, the selfservice UI, and optional Polis) on top so
that the Materialize Console authenticates users through OIDC, with SAML and
SCIM available when Polis is enabled. The example wires these modules
together as a reference; the individual modules are designed to be composed
into your own Terraform rather than used only through the example.

> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

## What Gets Created

This example provisions everything from the base [Install on
GCP](/self-managed-deployments/installation/install-on-gcp/) guide, plus the
additions below.

### Networking

| Resource | Description |
|----------|-------------|
| Public Hostnames | Six browser-facing hostnames (Hydra, Kratos, the selfservice UI, optional Polis, the Materialize Console, balancerd). DNS records are created by you after `terraform apply`. |
| LoadBalancer Services | One per browser-facing service in the `ory` and `materialize-environment` namespaces. Backed by GCP network load balancers. |

### Database

| Resource | Description |
|----------|-------------|
| Ory Cloud SQL for PostgreSQL | Separate instance from the Materialize backend. PostgreSQL 18, `db-f1-micro` tier, private IP only. |
| Databases | `kratos`, `hydra`, plus `polis` when `enable_polis = true`. Cloud SQL supports multiple databases on a single instance, so all three Ory components share this instance. |
| User | `oryadmin` with auto-generated password. |

### Kubernetes Add-ons

| Resource | Description |
|----------|-------------|
| Ory Kratos | Helm release in the `ory` namespace. Identity management: login, registration, recovery, account flows. |
| Ory Hydra | Helm release in the `ory` namespace. OAuth2 / OIDC provider that the Materialize Console trusts. Hydra Maester is enabled. |
| Ory Selfservice UI | Helm release in the `ory` namespace. Renders the Kratos login, consent, and recovery pages. |
| Ory Polis (optional) | Helm release in the `ory` namespace when `enable_polis = true`. SAML-to-OIDC bridge plus SCIM endpoint. |
| Polis TLS termination (optional) | Polis serves plain HTTP internally. The Polis chart runs a TLS-terminating sidecar that presents HTTPS on the public port, using the cert-manager certificate mounted into it. |
| cert-manager `ClusterIssuer` | Defaults to the in-cluster self-signed issuer. Override via `cert_issuer_ref` to plug in a real one (corporate CA, Let's Encrypt, etc.). |

### Materialize

| Resource | Description |
|----------|-------------|
| Materialize Instance | Configured for OIDC sign-in against the Hydra issuer URL. The browser-facing console hostname is registered as the OAuth2 redirect URI. |

## GCP-Specific Requirements

Cross-cutting requirements (license key with the `ory` entitlement, DNS
hostnames, cert-manager strategy, required tools) are covered on the shared
[Prerequisites](/self-managed-deployments/sso/advanced/prerequisites/)
page. This section only lists the GCP-specific bits.

A Google account with permission to enable the required APIs on your project and to create:

- GKE clusters and node pools
- Cloud SQL instances and VPC peering
- Cloud Storage buckets
- VPC networks, subnets, Cloud Router, Cloud NAT
- Service accounts and IAM bindings

## Getting Started: Advanced SSO Example

> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

> **Tip:** * The `examples/enterprise` example, used in this tutorial, is provided for illustration and to help you get started. In practice, we recommend instantiating these modules within your own Terraform code rather than relying on the example configuration directly.

### Step 1: Set Up the Environment

1. Open a terminal window.

1. Clone the Materialize Terraform repository and go to the
   `gcp/examples/enterprise` directory:

   ```bash
   git clone https://github.com/MaterializeInc/materialize-terraform-self-managed.git
   cd materialize-terraform-self-managed/gcp/examples/enterprise
   ```

1. Authenticate with Google Cloud and select your project:

   ```bash
   gcloud auth application-default login
   gcloud config set project <your-project-id>
   ```

### Step 2: Configure Terraform Variables

1. Create a `terraform.tfvars` file with the required variables:

   - `project_id`: GCP project ID
   - `region`: GCP region (defaults to `us-central1`)
   - `name_prefix`: Prefix for all resource names
   - `license_key`: Materialize license key JWT with the `ory` entitlement
   - `k8s_apiserver_authorized_networks`: CIDRs allowed to reach the GKE master endpoint (required, no default)
   - `ory_hydra_fqdn`, `ory_ui_fqdn`, `ory_kratos_fqdn`, `materialize_console_fqdn`, `materialize_balancerd_fqdn`: Hostnames for the browser-facing services
   - `internal_load_balancer`: Defaults to `true`, which gives every load balancer a private address. Set it to `false` to reach the endpoints from outside the VPC. SCIM from a cloud IdP such as Okta requires this, because the IdP must reach Polis
   - `ingress_cidr_blocks`: CIDRs allowed to reach the load balancers when `internal_load_balancer = false` (defaults to `0.0.0.0/0`, tighten for production)
   - `labels`: Map of labels to apply to resources

   ```hcl
   project_id  = "my-gcp-project-id"
   region      = "us-central1"
   name_prefix = "mz-enterprise"
   license_key = "your-materialize-license-key"

   k8s_apiserver_authorized_networks = [
     {
       cidr_block   = "0.0.0.0/0"   # tighten for production
       display_name = "lab"
     },
   ]

   ory_hydra_fqdn             = "hydra.example.com"
   ory_ui_fqdn                = "auth.example.com"
   ory_kratos_fqdn            = "kratos.example.com"
   materialize_console_fqdn   = "console.example.com"
   materialize_balancerd_fqdn = "balancerd.example.com"

   labels = {
     environment = "demo"
   }
   ```

1. To enable Polis (SAML and SCIM):

```hcl
enable_polis   = true
ory_polis_fqdn = "polis.example.com"
```

1. To bring your own cert-manager `ClusterIssuer` for the browser-facing TLS certs (Hydra, Kratos, the selfservice UI, Polis, the Materialize console, and balancerd):

```hcl
cert_issuer_ref = {
  name = "letsencrypt-prod"
  kind = "ClusterIssuer"
}
```

If you want a Let's Encrypt issuer signed via DNS-01, the example's README ships a starter `letsencrypt.tf` snippet for Cloudflare, Route 53, Azure DNS, and Google Cloud DNS. Drop it next to `main.tf`, set your DNS provider API token, and point `cert_issuer_ref` at it.

1. To federate logins through one or more upstream OIDC providers (Okta, Google Workspace, Auth0, Entra), add an `upstream_identity_providers` list. Each entry renders as a "Sign in with ..." button on the selfservice UI:

```hcl
upstream_identity_providers = [
  {
    id            = "okta"
    provider      = "generic"
    client_id     = "<from your IdP>"
    client_secret = "<from your IdP>"
    issuer_url    = "https://your-org.okta.com"
    scope         = ["openid", "email", "profile"]
    label         = "Sign in with Okta"
  },
]
```

Register the redirect URI `https://<ory_kratos_fqdn>/self-service/methods/oidc/callback/<id>` at the upstream IdP. See [Configure identity providers](/self-managed-deployments/sso/advanced/identity-providers/) for SAML and SCIM setup once the stack is up.

### Step 3: Apply the Terraform

1. Initialize the Terraform directory:

   ```bash
   terraform init
   ```

1. Apply the Terraform configuration:

   ```bash
   terraform apply
   ```

   Expect 30 to 45 minutes for the full apply. The slowest parts are GKE
   provisioning, the two Cloud SQL instances, and the Materialize instance
   reaching ready.

1. Configure `kubectl` against the new cluster:

   ```bash
   gcloud container clusters get-credentials \
     $(terraform output -raw gke_cluster_name) \
     --region $(terraform output -raw gke_cluster_location)
   ```

### Step 4: Create DNS Records

After `terraform apply`, read the load balancer addresses from the Terraform outputs:

```bash
# Ory endpoints (all clouds)
terraform output ory_lb_addresses

# Console and balancerd, Azure and GCP
terraform output console_load_balancer_ip
terraform output balancerd_load_balancer_ip

# Console and balancerd, AWS (one NLB hostname serves both)
terraform output nlb_dns_name
```

Create DNS records pointing the browser-facing hostnames at those addresses: an A record for an IP (Azure, GCP), a CNAME for a hostname (AWS):

| Hostname | Address |
|----------|---------|
| `hydra.example.com` | `ory_lb_addresses.hydra` |
| `kratos.example.com` | `ory_lb_addresses.kratos` |
| `auth.example.com` | `ory_lb_addresses.ui` |
| `polis.example.com` | `ory_lb_addresses.polis` (only when `enable_polis = true`) |
| `console.example.com` | `console_load_balancer_ip` (Azure, GCP) or `nlb_dns_name` (AWS) |
| `balancerd.example.com` | `balancerd_load_balancer_ip` (Azure, GCP) or `nlb_dns_name` (AWS) |

cert-manager issues TLS certs as soon as DNS resolves. Wait for all Certificates to report `READY=True`:

```bash
kubectl get certificate -A -w
```

The first certificate issuance typically takes 1 to 3 minutes per cert when using ACME (Let's Encrypt DNS-01); in-cluster self-signed certs issue near-instantly.

### Step 5: Verify the Deployment

Smoke-test each browser-facing endpoint. These commands assume a publicly trusted issuer (`cert_issuer_ref` set). With the default self-signed issuer, fetch its CA first and pass `--cacert ca.crt` to each `curl`:

```bash
kubectl -n cert-manager get secret <name_prefix>-root-ca -o jsonpath='{.data.ca\.crt}' | base64 -d > ca.crt
```

```bash
# Hydra OIDC discovery (issuer should match ory_hydra_fqdn)
curl -fsSL https://hydra.example.com/.well-known/openid-configuration | jq .issuer

# Kratos health
curl -fsSL https://kratos.example.com/health/ready

# Selfservice UI health
curl -fsSL https://auth.example.com/health/alive

# Polis health (only when enable_polis = true)
curl -fsSL https://polis.example.com/api/health

# Materialize console (expect HTTP 200)
curl -fsSL -o /dev/null -w "%{http_code}\n" https://console.example.com
```

Then sign in end to end, which is what proves SSO works:

1. Open `https://console.example.com`. You are redirected to the selfservice UI at `auth.example.com`, with one button per `upstream_identity_providers` entry and per `saml_providers` entry. Each button's text comes from that entry's `label`; see [Configure identity providers](/self-managed-deployments/sso/advanced/identity-providers/).
2. Sign in through one of them. You should land back in the Console as that user.
3. Run `SELECT current_user;`. It should return the user's email.

If you haven't configured an identity provider yet, see
[Configure identity
providers](/self-managed-deployments/sso/advanced/identity-providers/).

## Customizing Your Deployment

You can override module inputs independently. For details on the per-cloud
modules, see the [top-level
README](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main)
and the [GCP-specific
README](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/gcp).

Notes specific to GCP:

- **Shared Cloud SQL instance for Ory**: Cloud SQL supports multiple databases
  on a single instance, so Kratos, Hydra, and optional Polis share one
  `db-f1-micro` instance with separate databases. (AWS, in contrast,
  provisions one RDS instance per Ory component.)
- **GKE master access**: `k8s_apiserver_authorized_networks` has no default.
  Production deployments should pin a tight allowlist instead of `0.0.0.0/0`.
- **Egress to the OEL proxy**: GKE nodes need outbound access to
  `ory.registry.cloud.materialize.com` and `storage.googleapis.com`. The proxy
  returns HTTP 307 redirects to signed GCS URLs for blob layers, which the
  kubelet follows directly. Adjust your VPC firewall and Cloud NAT egress
  rules accordingly.
- **Node pools**: Default `e2-standard-8` for the generic pool;
  `n2-highmem-8` with one local SSD for the Materialize pool. Override via the
  `generic_nodepool` and `materialize_nodepool` variables.

## Cleanup

```bash
terraform destroy
```

> **Note:** `terraform destroy` can hang on the `ory` namespace because the `OAuth2Client` CRD has a Hydra Maester finalizer that is not always cleared before Maester itself is torn down. If the destroy stalls on the namespace, patch the finalizer off:
> ```bash
> kubectl patch oauth2client materialize-oauth2-client -n ory \
>   --type=json -p='[{"op":"remove","path":"/metadata/finalizers"}]'
> ```
> Then re-run `terraform destroy`. A cleaner fix is tracked upstream.

## See Also

- [Configure identity providers](/self-managed-deployments/sso/advanced/identity-providers/)
- [Operations](/self-managed-deployments/sso/advanced/operations/)
- [Troubleshooting](/self-managed-deployments/sso/advanced/troubleshooting/)
- [Install on GCP (base Materialize stack)](/self-managed-deployments/installation/install-on-gcp/)
