# Upgrading

Upgrading Self-Managed Materialize.

Materialize releases new Self-Managed versions per the schedule outlined in [Release schedule](/releases/schedule/#self-managed-release-schedule).

## General rules for upgrading

<p>When upgrading:</p>
<ul>
<li>
<p><strong>Always</strong> check the <a href="/self-managed-deployments/upgrading/version-notes/" >version-specific upgrade
notes</a> for your target
version:</p>
<ul>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v2630-and-later-versions" >Upgrading to <code>v26.30</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v261-and-later-versions" >Upgrading to <code>v26.1</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v260" >Upgrading to <code>v26.0</code></a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-between-minor-versions-less-than-v26" >Upgrading between minor versions less than <code>v26</code></a></li>
</ul>
</li>
<li>
**Always** upgrade the Materialize Operator **before**
upgrading the Materialize instances.

</li>
</ul>

> **Note:** For major version upgrades, you can **only** upgrade **one** major version
> at a time. For example, upgrades from **v26**.1.0 to **v27**.3.0 is
> permitted but **v26**.1.0 to **v28**.0.0 is not.

## Upgrade guides

The following upgrade guides are available as examples:

#### Upgrade using Helm Commands

|  Guide         | Description  |
| ------------- | -------|
| [Upgrade on Kind](/self-managed-deployments/upgrading/upgrade-on-kind/) | Uses standard Helm commands to upgrade Materialize on a Kind cluster in Docker.

<h4 id="upgrade-using-terraform-modules">Upgrade using Terraform Modules</h4>
> **Tip:** The Terraform modules are provided as examples. They are not required for
> upgrading Materialize.

<table>
  <thead>
      <tr>
          <th>Guide</th>
          <th>Description</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td><a href="/self-managed-deployments/upgrading/upgrade-on-aws/" >Upgrade on AWS (Terraform)</a></td>
          <td>Uses Terraform module to deploy Materialize to AWS Elastic Kubernetes Service (EKS).</td>
      </tr>
      <tr>
          <td><a href="/self-managed-deployments/upgrading/upgrade-on-azure/" >Upgrade on Azure (Terraform)</a></td>
          <td>Uses Terraform module to deploy Materialize to Azure Kubernetes Service (AKS).</td>
      </tr>
      <tr>
          <td><a href="/self-managed-deployments/upgrading/upgrade-on-gcp/" >Upgrade on GCP (Terraform)</a></td>
          <td>Uses Terraform module to deploy Materialize to Google Kubernetes Engine (GKE).</td>
      </tr>
  </tbody>
</table>

## Upgrading the Helm Chart and Materialize Operator

> **Important:** When upgrading Materialize, always upgrade the Helm Chart and Materialize
> Operator first.

### Update the Helm Chart repository

To update your Materialize Helm Chart repository:

```shell
helm repo update materialize
```

View the available chart versions:

```shell
helm search repo materialize/materialize-operator --versions
```

### Upgrade your Materialize Operator

The Materialize Kubernetes Operator is deployed via Helm and can be updated
through standard `helm upgrade` command:

```mzsql
helm upgrade -n <namespace> <release-name> materialize/materialize-operator \
  --version <new_version> \
  -f <your-custom-values.yml>

```

| Syntax element | Description |
| --- | --- |
| `<namespace>` | The namespace where the Operator is running. (e.g., `materialize`)  |
| `<release-name>` | The release name. You can use `helm list -n <namespace>` to find your release name.  |
| `<new_version>` | The upgrade version.  |
| `<your-custom-values.yml>` | The name of your customization file, if using. If you are configuring using `--set key=value` options, include them as well.  |

You can use `helm list` to find your release name. For example, if your Operator
is running in the namespace `materialize`, run `helm list`:

```shell
helm list -n materialize
```

Retrieve the name associated with the `materialize-operator` **CHART**; for
example, `my-demo` in the following helm list:

```none
NAME    	  NAMESPACE  	REVISION	UPDATED                             	STATUS  	CHART                                          APP VERSION
my-demo	materialize	1      2025-12-08 11:39:50.185976 -0500 EST	deployed	materialize-operator-v26.1.0    v26.1.0
```

Then, to upgrade:

```shell
helm upgrade -n materialize my-demo materialize/operator \
  -f my-values.yaml \
  --version v26.36.0
```

## Upgrading Materialize Instances

After upgrading the operator, upgrade each Materialize instance to the
operator's **App Version** by updating its `environmentdImageRef`. For
step-by-step instructions, use the [upgrade guide](#upgrade-guides) for your
environment (Kind, AWS, Azure, or GCP). This section explains how instance
rollouts work.

## Rollout configuration

Materialize supports two CRD API versions: `v1alpha1` and `v1` (available
starting in v26.30). The Helm chart defaults to `v1alpha1`. The Terraform
modules default to `v1` starting in v4.0.0.

How you trigger a rollout depends on the CRD API version of your instances.

> **Tip:** To migrate a `v1alpha1` instance to `v1`, see
> [Adopting the v1 CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/).

**v1alpha1:**

Specify a new `UUID` value for `requestRollout` to roll out changes to the
Materialize instance.

> **Note:** `requestRollout` without the `forceRollout` field only rolls out if changes exist
> to the Materialize instance. To roll out even if there are no changes to the
> instance, use it with `forceRollout`.

```shell
# Only rolls out if there are changes
kubectl patch materialize <instance-name> \
  -n <materialize-instance-namespace> \
  --type='merge' \
  -p "{\"spec\": {\"requestRollout\": \"$(uuidgen)\"}}"
```

To force a rollout even when there are no other changes, set a new `forceRollout`
UUID alongside `requestRollout`:

```shell
kubectl patch materialize <instance-name> \
  -n <materialize-instance-namespace> \
  --type='merge' \
  -p "{\"spec\": {\"requestRollout\": \"$(uuidgen)\", \"forceRollout\": \"$(uuidgen)\"}}"
```

**v1:**

With v1, updating the spec automatically triggers a rollout and there is no
`requestRollout` field. For details on the underlying mechanism, see [How it
works](/self-managed-deployments/upgrading/adopting-the-v1-crd/#how-the-switchover-works).

To trigger a rollout even when there are no other changes to the instance,
specify a new `UUID` value for `forceRollout`. That is:

- Set it in your manifest:

  ```yaml
  spec:
    forceRollout: <new-uuid>  # e.g. the output of `uuidgen`
  ```

- Then reapply.

  ```shell
  kubectl apply -f materialize.yaml
  ```

## Rollout strategies

Rollout strategies control how Materialize transitions from the current
generation to a new generation during an upgrade. The behavior follows your
`rolloutStrategy` setting.

### *WaitUntilReady* — ***Default***

`WaitUntilReady` creates a new generation of pods and automatically promotes them
as soon as they catch up to the old generation and become `ReadyToPromote`.
Because both generations run simultaneously until the promotion, this strategy
temporarily doubles the required resources to run Materialize.

> **Note:** While the new generation waits to become `ReadyToPromote`, it runs in a
> read-only, un-promoted state and holds back compaction. To prevent it from
> sitting in this state indefinitely (which can cause incident-inducing load when
> it is eventually promoted), the rollout is bounded by the `rolloutRequestTimeout`
> field in the Materialize spec, which defaults to `24h`.
> If the new generation does not become `ReadyToPromote` within
> `rolloutRequestTimeout`, the operator cancels the rollout: the new generation is
> torn down and the previously-active generation continues serving. You can then
> trigger a new rollout (in v1, set a new `forceRollout`; in v1alpha1, set a new
> `requestRollout`).

### *ImmediatelyPromoteCausingDowntime*

> **Warning:** Using the `ImmediatelyPromoteCausingDowntime` rollout flag will cause downtime.

`ImmediatelyPromoteCausingDowntime` tears down the prior generation and
immediately promotes the new generation without waiting for it to hydrate. This
causes downtime until the new generation has hydrated. However, it does not
require additional resources.

### *ManuallyPromote*

`ManuallyPromote` allows you to choose when to promote the new generation. This
means you can time the promotion for periods when load is low, minimizing the
impact of potential downtime for any clients connected to Materialize. This
strategy temporarily doubles the required resources to run Materialize.

To minimize downtime, wait until the new generation has fully hydrated and caught
up to the prior generation before promoting. To check hydration status, inspect
the `UpToDate` condition in the Materialize resource status. When hydration
completes, the condition will be `ReadyToPromote`.

To promote, update the `forcePromote` field to match the current rollout
identifier (in v1, the `status.requestedRolloutHash`; in v1alpha1, the
`requestRollout` UUID in the spec). If you need to promote before hydration
completes, you can set `forcePromote` immediately, but clients may experience
downtime.

> **Warning:** Leaving a new generation unpromoted for over 6 hours may cause downtime.

**Do not leave new generations unpromoted indefinitely**. They should either be
promoted or canceled. New generations open a read hold on the metadata database
that prevents compaction. This hold is only released when the generation is
promoted or canceled. If left open too long, promoting or canceling can trigger a
spike in deletion load on the metadata database, potentially causing downtime. It
is not recommended to leave generations unpromoted for over 6 hours.

### *inPlaceRollout* — ***Deprecated*** (v1alpha1 only)

The setting is ignored.

## Verifying the upgrade

After initiating the rollout, you can monitor the status field of the Materialize
custom resource to check on the upgrade.

```shell
# Watch the status of your Materialize environment
kubectl get materialize -n materialize-environment -w

# Check the logs of the operator
kubectl logs -l app.kubernetes.io/name=materialize-operator -n materialize
```

## Cancelling the upgrade

You may want to cancel an in-progress rollout if the upgrade has failed (for
example, new pods are not healthy). Before cancelling, verify that the upgrade has
not already completed by checking that the deploy generation (found via
`status.activeGeneration`) is still the one from before the upgrade. Once an
upgrade has already happened, you cannot revert using this method.

**v1alpha1:**

To cancel an in-progress rollout and revert to the last completed rollout state,
revert both `requestRollout` and `environmentdImageRef` back to the values from
the last completed rollout. Reverting `environmentdImageRef` alongside
`requestRollout` keeps the spec aligned with what is actually running, so a later
rollout doesn't accidentally pick up the previously attempted upgrade image.

First, retrieve the last completed rollout request ID and the matching
environmentd image ref from your Materialize CR:

```shell
kubectl get materialize <instance-name> -n materialize-environment \
  -o jsonpath='{.status.lastCompletedRolloutRequest} {.status.lastCompletedRolloutEnvironmentdImageRef}'
```

Then set both fields back to these values in a single patch:

```shell
kubectl patch materialize <instance-name> \
  -n materialize-environment \
  --type='merge' \
  -p "{\"spec\": {\"requestRollout\": \"<lastCompletedRolloutRequest-value>\", \"environmentdImageRef\": \"<lastCompletedRolloutEnvironmentdImageRef-value>\"}}"
```

**v1:**

To cancel an in-progress rollout and revert to the last completed rollout state,
reapply the Materialize resource with the spec it had before the rollout (notably
the previous `environmentdImageRef`). Because v1 derives the rollout from the
spec hash, restoring the previous spec produces the previous hash and returns the
instance to the last completed state.

```shell
kubectl apply -f previous_materialize_configuration.yaml
```

## See also

- [Version-specific upgrade
  notes](/self-managed-deployments/upgrading/version-notes/)

- [Adopting the v1
  CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/)

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)

- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)

- [Troubleshooting](/self-managed-deployments/troubleshooting/)

---

## Adopting the v1 CRD

This page describes the Materialize CRD API versions and how to adopt `v1` for
your Materialize instances.

## CRD API versions

Starting in v26.30, Materialize introduces support for a new version of the
Materialize CRD, `v1`, which provides simplified rollouts. Previously,
Materialize only supported `v1alpha1`. The Helm chart still defaults to
`v1alpha1`, while the [Terraform
modules](https://github.com/MaterializeInc/materialize-terraform-self-managed)
default to `v1` starting in v4.0.0.

- **v1alpha1** (Helm chart default) uses a two-step rollout: first stage the spec
  change, then trigger a rollout with a new `requestRollout` UUID.

  ```yaml
  apiVersion: materialize.cloud/v1alpha1
  kind: Materialize
  metadata:
    name: 12345678-1234-1234-1234-123456789012
    namespace: materialize-environment
  spec:
    environmentdImageRef: materialize/environmentd:v26.30.1
    requestRollout: 22222222-2222-2222-2222-222222222222  # ← MUST set a new UUID every upgrade
  # forceRollout: 33333333-3333-3333-3333-333333333333   # ← for forced rollouts
    rolloutStrategy: WaitUntilReady
    backendSecretName: materialize-backend
  ```
- **v1** rolls out automatically when spec fields change, removing the
  need to manually set a `requestRollout` UUID.

  ```yaml
  apiVersion: materialize.cloud/v1
  kind: Materialize
  metadata:
    name: 12345678-1234-1234-1234-123456789012
    namespace: materialize-environment
  spec:
    environmentdImageRef: materialize/environmentd:v26.30.1  # ← just change this
  # forceRollout: 33333333-3333-3333-3333-333333333333       # ← only for forced rollouts
    rolloutStrategy: WaitUntilReady
    backendSecretName: materialize-backend
  ```

When using the Helm chart, adopting `v1` is **opt-in** for now. When using the
Terraform modules, `crd_version` defaults to `v1` starting in v4.0.0. Upgrading
the operator to v26.30+ does not change your existing `v1alpha1` CRs or their
behavior; you can continue using `v1alpha1` until the next major release.

> **Important:** In the next major release, all Materialize CRs will be force upgraded to `v1`.
> You will still be able to apply `v1alpha1` CRs, but they will be auto-converted
> to `v1` and use the `v1` rollout behavior. We recommend opting in to `v1` at
> your convenience to migrate on your own schedule before the upgrade is
> mandatory. With the new change, the `requestRollout` field will be removed,
> along with all previously deprecated fields.

## Prerequisites

- First, set up infrastructure requirements (needed by conversion webhooks to
  allow for graceful migration from `v1alpha1` to `v1`)
  - Install `cert-manager` (or provide your own certificate).
  - Allow internal network ingress on port `8001`.

- Next, enable the `v1` CRD by setting the Helm value
  `operator.args.installV1CRD=true`. Enabling the `v1` CRD does not roll out
  your existing instances; they continue to use `v1alpha1`.

For instructions on completing the prerequisites, select the tab that matches
your deployment method:

**Terraform:**

If you are using the [Terraform
modules](https://github.com/MaterializeInc/materialize-terraform-self-managed),
the required infrastructure changes (cert-manager and network ingress) and
enabling of `v1` CRD will be handled for you automatically starting in TF
modules (**v3.1.1 or greater**). Starting in TF modules **v4.0.0**, the
`materialize-instance` module also defaults `crd_version` to `v1`.

- If you have already upgraded your TF modules to **v3.1.1 or greater**, the
  prerequisites are handled automatically.

- If you are on earlier TF modules, use the same [procedure to perform version
  upgrades](/self-managed-deployments/upgrading/#upgrade-using-terraform-modules)
  to upgrade to **v3.1.1 or greater**; i.e., update each module's `source` to
  point to the new release tag (v3.1.1 or greater), then run `terraform init &&
  terraform plan && terraform apply`.

  This will also upgrade your Materialize version to that associated with that
  TF release tag.

  - [Upgrade on AWS](/self-managed-deployments/upgrading/upgrade-on-aws/)
  - [Upgrade on Azure](/self-managed-deployments/upgrading/upgrade-on-azure/)
  - [Upgrade on GCP](/self-managed-deployments/upgrading/upgrade-on-gcp/)

**Manual:**

If you are not using our Terraform modules, you **must** complete the following
steps before enabling the `v1` CRD:

**1. Install cert-manager**

The conversion webhook requires a TLS certificate.
The Helm chart defaults to using [cert-manager](https://cert-manager.io/)
to automatically create and manage this certificate. cert-manager must be
installed **before** enabling the `v1` CRD.

If you prefer to provide your own certificate instead of using cert-manager,
set the following Helm values:
- `operator.certificate.source`: `secret`
- `operator.certificate.secretName`: the name of the Kubernetes Secret
  containing `ca.crt`, `tls.crt`, and `tls.key` entries.

**2. Allow network access to the webhook port**

The conversion webhooks require the Kubernetes API server to reach the
`orchestratord` pod on port `8001`. If your cluster enforces network policies
or cloud-level firewall rules, you must allow ingress traffic on TCP port
`8001` from the API server to pods with the label
`app.kubernetes.io/name: materialize-operator`.

**Kubernetes NetworkPolicy:** Add a policy that allows ingress from the
Kubernetes API server on port `8001` to the `materialize-operator` pods in the
namespace where the operator is deployed:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-server-ingress-to-conversion-webhook
  namespace: materialize  # the namespace where the operator runs
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: materialize-operator
  policyTypes:
    - Ingress
  ingress:
    - ports:
        - protocol: TCP
          port: 8001
```

**Cloud firewall rules (e.g., AWS security groups, GCP firewall rules):**
Ensure the node security group or firewall allows inbound TCP traffic on
port `8001` from the Kubernetes control plane. For example, on AWS, add an
ingress rule to the EKS node security group allowing port `8001` from the
cluster security group. On GCP with private clusters, add a firewall rule
allowing port `8001` from the GKE control plane CIDR.

For a complete example of the required changes across AWS, Azure, and GCP,
see [this pull request](https://github.com/MaterializeInc/materialize-terraform-self-managed/pull/160).

**3. Enable the v1 CRD**

Once the prerequisites above are in place, set the following Helm value when
installing or upgrading the operator:

```yaml
operator:
  args:
    installV1CRD: true
```

This installs the `v1` version of the Materialize CRD and the conversion
webhook that converts between `v1` and `v1alpha1`.

## Switch to `v1`

After you have fulfilled the pre-requisites (Materialize v26.30+, set up
infrastructure requirements, enabled `v1` CRD), you can submit a `v1` CR to
adopt `v1`.

> **Important:** Schedule `v1` adoption during a window where a rollout is acceptable.

### How the switchover works

When you submit a `v1` CR, the operator's conversion webhook automatically
converts it to `v1alpha1` for storage. During conversion, the webhook computes a
SHA256 hash of a subset of the spec fields and derives a deterministic
`requestRollout` UUID from it. The hash covers the fields that affect the
running `environmentd` (for example, `environmentdImageRef`,
`environmentdExtraArgs`, `environmentdExtraEnv`, resource requirements,
`podAnnotations`, `podLabels`, `authenticatorKind`, `enableRbac`,
`rolloutStrategy`, and `forceRollout`). It excludes fields that do not require a
rollout, such as `balancerd`/`console` resource requirements and replica counts.

> **Important:** Schedule `v1` adoption during a window where a rollout is acceptable. Adopting
> `v1` on an existing `v1alpha1` instance typically triggers a rollout. The
> derived `requestRollout` is computed from the spec hash and will not match the
> `requestRollout` you previously set by hand, so the instance rolls out once even
> if nothing else in the spec changed.

**Terraform:**

If you are managing your Materialize instance with the [Materialize Terraform
modules](https://github.com/MaterializeInc/materialize-terraform-self-managed),
set:

```hcl
crd_version     = "v1"
request_rollout = null
```

Starting in Terraform module version v4.0.0, `crd_version` defaults to `v1`,
so you can also omit it.

**Once on v1, an unchanged spec will not trigger a rollout.** Reapplying the
same spec produces the same hash and the same derived `requestRollout`. Changing
a hashed spec field produces a new value and triggers a rollout automatically.

**Manual:**

To adopt v1 for an existing instance, apply your CR with `apiVersion:
materialize.cloud/v1` and remove the `requestRollout` field:

```shell
kubectl apply -f - <<EOF
apiVersion: materialize.cloud/v1
kind: Materialize
metadata:
  name: <instance-name>
  namespace: <materialize-instance-namespace>
spec:
  environmentdImageRef: <current-image-ref>
  backendSecretName: <backend-secret-name>
  # ... other spec fields (copy from your existing CR, removing requestRollout)
EOF
```

**Once on v1, an unchanged spec will not trigger a rollout.** Reapplying the
same spec produces the same hash and the same derived `requestRollout`. Changing
a hashed spec field produces a new value and triggers a rollout automatically.

## Returning to the v1alpha1 behavior

You can go back to the `v1alpha1` rollout behavior at any time by applying your
CR with `apiVersion: materialize.cloud/v1alpha1` and an explicit
`requestRollout` UUID. With the Terraform modules, set `crd_version =
"v1alpha1"` explicitly (required starting in v4.0.0, where `crd_version`
defaults to `v1`) and set `request_rollout` to a new UUID.

---

## Upgrade notes

Review the notes for your target version before upgrading. For the general
upgrade procedure, see the [upgrade
guides](/self-managed-deployments/upgrading/#upgrade-guides).

## Upgrading to `v26.33` and later versions

Starting in v26.33, Self-Managed deployments that use a **PostgreSQL metadata
database** can configure Materialize to run its internal consensus queries using
`READ COMMITTED` instead of `SERIALIZABLE` transaction isolation.

> **Note:** The transaction isolation levels discussed in this section refer to those of the
> PostgreSQL metadata database, not Materialize's [client transaction isolation
> levels](/reference/isolation-level/).

The consensus queries are designed to be linearizable under `READ COMMITTED`.
`READ COMMITTED` also improves metadata write throughput by avoiding the
serialization-failure retries that `SERIALIZABLE` incurs under contention.

To use `READ COMMITTED` with a PostgreSQL metadata database, enable the
`persist_pg_consensus_read_committed` parameter. The parameter is **disabled by
default**.

> **Warning:** - Do not use with non-PostgreSQL metadata databases; Materialize will refuse to
>   run consensus queries when the parameter is enabled for other metadata databases.
> - You must be on v26.33+ before enabling the parameter.

**Recommendation**: After your entire environment has finished upgrading to
v26.33 or later, enable the parameter on PostgreSQL-backed deployments by
adding it to your [system parameters
ConfigMap](/self-managed-deployments/configuration-system-parameters/):

```json
{
  "persist_pg_consensus_read_committed": true
}
```

or with [`ALTER SYSTEM SET`](/sql/alter-system-set/) (as a superuser):

```sql
ALTER SYSTEM SET persist_pg_consensus_read_committed = true;
```

## Upgrading to `v26.30` and later versions

v26.30.0 introduces support for a new version of the Materialize CRD, `v1`,
which provides simplified rollouts. Previously, Materialize only supported
`v1alpha1`; `v1alpha1` remains the default.

Upgrading to v26.30+ does **not** require adopting the `v1` CRD; adopting `v1`
is **opt-in**. You can upgrade as usual while continuing to use `v1alpha1`; your
existing instances will behave exactly as before. However, once you are on
v26.30+, we do recommend you schedule [adoption of
`v1`](/self-managed-deployments/upgrading/adopting-the-v1-crd/) before the next
major release.

If using Materialize-provided TF modules, v3.1.1+ automatically handles the
[prerequisites for adopting
`v1`](/self-managed-deployments/upgrading/adopting-the-v1-crd/#prerequisites).
It does not switch your instances to `v1`. To switch to `v1`, see [Switch to
`v1`
CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/#switch-to-v1).

## Upgrading to `v26.1` and later versions

- To upgrade to `v26.1` or future versions, you must first upgrade to `v26.0`

## Upgrading to `v26.0`

- Upgrading to `v26.0.0` is a major version upgrade. To upgrade to `v26.0` from
  `v25.2.X` or `v25.1`, you must first upgrade to `v25.2.16` and then upgrade to
  `v26.0.0`.

- For upgrades, the `inPlaceRollout` setting has been deprecated and will be
  ignored. Instead, use the new setting `rolloutStrategy` to specify either:
  - `WaitUntilReady` (*Default*)
  - `ImmediatelyPromoteCausingDowntime`

  For more information, see
  [`rolloutStrategy`](/self-managed-deployments/upgrading/#rollout-strategies).

- New requirements were introduced for [license keys](/releases/#license-key).
  To upgrade, you will first need to add a license key to the `backendSecret`
  used in the spec for your Materialize resource.

  See [License key](/releases/#license-key) for details on getting your license
  key.

- Swap is now enabled by default. Swap reduces the memory required to
  operate Materialize and improves cost efficiency. Upgrading to `v26.0`
  requires some preparation to ensure Kubernetes nodes are labeled
  and configured correctly. As such:

  - If you are using the Materialize-provided Terraforms, upgrade to version
    `v0.6.1` of the Terraform.

  - If you are <red>**not**</red> using a Materialize-provided Terraform, refer
    to [Prepare for swap and upgrade to v26.0](/self-managed-deployments/appendix/upgrade-to-swap/).

## Upgrading between minor versions less than `v26`

- Prior to `v26`, you must upgrade at most one minor version at a time. For
  example, upgrading from `v25.1.5` to `v25.2.16` is permitted.

---

## Upgrade on AWS

The following tutorial upgrades your Materialize deployment running on AWS
Elastic Kubernetes Service (EKS). The tutorial assumes you have installed the
example on [Install on
AWS](/self-managed-deployments/installation/install-on-aws/).

## Upgrade guidelines

<p>When upgrading:</p>
<ul>
<li>
<p><strong>Always</strong> check the <a href="/self-managed-deployments/upgrading/version-notes/" >version-specific upgrade
notes</a> for your target
version:</p>
<ul>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v2630-and-later-versions" >Upgrading to <code>v26.30</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v261-and-later-versions" >Upgrading to <code>v26.1</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v260" >Upgrading to <code>v26.0</code></a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-between-minor-versions-less-than-v26" >Upgrading between minor versions less than <code>v26</code></a></li>
</ul>
</li>
<li>
**Always** upgrade the Materialize Operator **before**
upgrading the Materialize instances.

</li>
</ul>

> **Note:** For major version upgrades, you can **only** upgrade **one** major version
> at a time. For example, upgrades from **v26**.1.0 to **v27**.3.0 is
> permitted but **v26**.1.0 to **v28**.0.0 is not.

> **Note:** Downgrading is not supported.

## Prerequisites

### Required Tools

- [Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- [kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html)

## Upgrade process

> **Important:** The following procedure performs a rolling upgrade, where both the old and new Materialize instances are running before the old instances are removed. When performing a rolling upgrade, ensure you have enough resources to support having both the old and new Materialize instances running.

### Step 1: Update TF module source version

Update each module's `source` to point to the desired release tag, substituting
`<RELEASE_TAG>` in the code block below with your tag version:

> **Important:** The following code block is not comprehensive. Only the core modules and their
> dependency chain are shown below.
> If your configuration includes additional modules (networking, storage,
> database, node pools, etc.) provided by Materialize, **update those to the same
> release tag as well**.

```hcl
module "eks" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//aws/modules/eks?ref=<RELEASE_TAG>"
  # ... your existing configuration ...
}

module "cert_manager" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//kubernetes/modules/cert-manager?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.eks]
}

module "operator" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//aws/modules/operator?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.cert_manager]
}

module "materialize_instance" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//kubernetes/modules/materialize-instance?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.operator]
}

# Update the source of any additional Materialize-provided modules to the same release tag
```

### Step 2: Explicitly request rollout if using v1alpha1

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

> **Important:** Starting in Terraform module version v4.0.0, `crd_version` defaults to
> `v1`. If your instance uses `v1alpha1` and you are upgrading to module
> version v4.0.0 or greater, set `crd_version = "v1alpha1"` explicitly to
> stay on `v1alpha1`. Otherwise, applying migrates the instance to `v1` and
> triggers a rollout. See [Adopting the v1
> CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/).

To check the CRD version of the Materialize manifest that was applied, run
the following:

```sh
terraform state show 'module.materialize_instance.kubectl_manifest.materialize_instance' \
  | grep -iE 'api_?version|kind'
```

- If you are using `v1`, skip to the [Apply the updated TF
  step](#step-3-apply-the-updated-tf).
- **If you are using `v1alpha1`**, you need to update your `terraform.tfvars`
file to set the `request_rollout` variable to a new UUID value, substituting
the example value in the code block below with a UUID you generate (for
example, with `uuidgen`):

```hcl
# ...
# ...
request_rollout = "DBB4FCEC-1837-44F6-9CF2-3894678DD8D5" # ONLY for v1alpha1
```

### Step 3: Apply the updated TF

1. Initialize the Terraform directory to download the required providers
    and modules:

    ```bash
    terraform init
    ```

1. Review the execution plan before applying. In particular, check for any
  resources Terraform plans to destroy and recreate (shown as `-/+` in the
  plan), especially stateful resources such as your cluster, storage, and
  database:

    ```bash
    terraform plan
    ```

1. After reviewing the plan, apply the Terraform configuration.

    ```bash
    terraform apply
    ```

### Step 4: Verify the upgrade

Configure `kubectl` to connect to your EKS cluster, replacing `<your-region>`
with the region of your cluster (found in your `terraform.tfvars`; e.g.,
`us-east-1`):

```bash
# aws eks update-kubeconfig --name <your-eks-cluster-name> --region <your-region>
aws eks update-kubeconfig --name $(terraform output -raw eks_cluster_name) --region <your-region>
```

> **Note:** `terraform apply` returns once the Materialize custom resource is updated.
> The Operator then rolls out the new generation asynchronously, so the new
> `environmentd` pods may take a few minutes to become ready.

<ol>
<li>
<p>Check the status of the <code>materialize</code> namespace:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize get all
</span></span></code></pre></div></li>
<li>
<p>Check the status of the <code>materialize-environment</code> namespace:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment get all
</span></span></code></pre></div></li>
<li>
<p>Once a new <code>environmentd</code> is up (may take a few minutes), confirm the
running <code>environmentd</code> version matches the version you upgraded to. Check
the <code>Image</code> field in the pod description.</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment describe pod -l <span class="nv">app</span><span class="o">=</span>environmentd
</span></span></code></pre></div></li>
</ol>
<p>If you run into an error during the upgrade, refer to the
<a href="/self-managed-deployments/troubleshooting/" >Troubleshooting</a>.</p>

## See also

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)
- [Troubleshooting](/self-managed-deployments/troubleshooting/)

---

## Upgrade on Azure

The following tutorial upgrades your Materialize deployment running on Azure
Kubernetes Service (AKS). The tutorial assumes you have installed the
example on [Install on
Azure](/self-managed-deployments/installation/install-on-azure/).

## Upgrade guidelines

<p>When upgrading:</p>
<ul>
<li>
<p><strong>Always</strong> check the <a href="/self-managed-deployments/upgrading/version-notes/" >version-specific upgrade
notes</a> for your target
version:</p>
<ul>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v2630-and-later-versions" >Upgrading to <code>v26.30</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v261-and-later-versions" >Upgrading to <code>v26.1</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v260" >Upgrading to <code>v26.0</code></a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-between-minor-versions-less-than-v26" >Upgrading between minor versions less than <code>v26</code></a></li>
</ul>
</li>
<li>
**Always** upgrade the Materialize Operator **before**
upgrading the Materialize instances.

</li>
</ul>

> **Note:** For major version upgrades, you can **only** upgrade **one** major version
> at a time. For example, upgrades from **v26**.1.0 to **v27**.3.0 is
> permitted but **v26**.1.0 to **v28**.0.0 is not.

> **Note:** Downgrading is not supported.

## Prerequisites

### Required Tools

- [Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Upgrade process

> **Important:** The following procedure performs a rolling upgrade, where both the old and new Materialize instances are running before the old instances are removed. When performing a rolling upgrade, ensure you have enough resources to support having both the old and new Materialize instances running.

### Step 1: Update TF module source version

Update each module's `source` to point to the desired release tag, substituting
`<RELEASE_TAG>` in the code block below with your tag version:

> **Important:** The following code block is not comprehensive. Only the core modules and their
> dependency chain are shown below.
> If your configuration includes additional modules (networking, storage,
> database, node pools, etc.) provided by Materialize, **update those to the same
> release tag as well**.

```hcl
module "aks" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//azure/modules/aks?ref=<RELEASE_TAG>"
  # ... your existing configuration ...
}

module "cert_manager" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//kubernetes/modules/cert-manager?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.aks]
}

module "operator" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//azure/modules/operator?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.cert_manager]
}

module "materialize_instance" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//kubernetes/modules/materialize-instance?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.operator]
}

# Update the source of any additional Materialize-provided modules to the same release tag
```

### Step 2: Explicitly request rollout if using v1alpha1

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

> **Important:** Starting in Terraform module version v4.0.0, `crd_version` defaults to
> `v1`. If your instance uses `v1alpha1` and you are upgrading to module
> version v4.0.0 or greater, set `crd_version = "v1alpha1"` explicitly to
> stay on `v1alpha1`. Otherwise, applying migrates the instance to `v1` and
> triggers a rollout. See [Adopting the v1
> CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/).

To check the CRD version of the Materialize manifest that was applied, run
the following:

```sh
terraform state show 'module.materialize_instance.kubectl_manifest.materialize_instance' \
  | grep -iE 'api_?version|kind'
```

- If you are using `v1`, skip to the [Apply the updated TF
  step](#step-3-apply-the-updated-tf).
- **If you are using `v1alpha1`**, you need to update your `terraform.tfvars`
file to set the `request_rollout` variable to a new UUID value, substituting
the example value in the code block below with a UUID you generate (for
example, with `uuidgen`):

```hcl
# ...
# ...
request_rollout = "DBB4FCEC-1837-44F6-9CF2-3894678DD8D5" # ONLY for v1alpha1
```

### Step 3: Apply the updated TF

1. Initialize the Terraform directory to download the required providers
    and modules:

    ```bash
    terraform init
    ```

1. Review the execution plan before applying. In particular, check for any
  resources Terraform plans to destroy and recreate (shown as `-/+` in the
  plan), especially stateful resources such as your cluster, storage, and
  database:

    ```bash
    terraform plan
    ```

1. After reviewing the plan, apply the Terraform configuration.

    ```bash
    terraform apply
    ```

### Step 4: Verify the upgrade

Configure `kubectl` to connect to your AKS cluster:

```bash
# az aks get-credentials --resource-group <your-resource-group-name> --name <your-aks-cluster-name>
az aks get-credentials --resource-group $(terraform output -raw resource_group_name) --name $(terraform output -raw aks_cluster_name)
```

> **Note:** `terraform apply` returns once the Materialize custom resource is updated.
> The Operator then rolls out the new generation asynchronously, so the new
> `environmentd` pods may take a few minutes to become ready.

<ol>
<li>
<p>Check the status of the <code>materialize</code> namespace:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize get all
</span></span></code></pre></div></li>
<li>
<p>Check the status of the <code>materialize-environment</code> namespace:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment get all
</span></span></code></pre></div></li>
<li>
<p>Once a new <code>environmentd</code> is up (may take a few minutes), confirm the
running <code>environmentd</code> version matches the version you upgraded to. Check
the <code>Image</code> field in the pod description.</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment describe pod -l <span class="nv">app</span><span class="o">=</span>environmentd
</span></span></code></pre></div></li>
</ol>
<p>If you run into an error during the upgrade, refer to the
<a href="/self-managed-deployments/troubleshooting/" >Troubleshooting</a>.</p>

## See also

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)
- [Troubleshooting](/self-managed-deployments/troubleshooting/)

---

## Upgrade on GCP

The following tutorial upgrades your Materialize deployment running on Google
Kubernetes Engine (GKE). The tutorial assumes you have installed the
example on [Install on
GCP](/self-managed-deployments/installation/install-on-gcp/).

## Upgrade guidelines

<p>When upgrading:</p>
<ul>
<li>
<p><strong>Always</strong> check the <a href="/self-managed-deployments/upgrading/version-notes/" >version-specific upgrade
notes</a> for your target
version:</p>
<ul>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v2630-and-later-versions" >Upgrading to <code>v26.30</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v261-and-later-versions" >Upgrading to <code>v26.1</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v260" >Upgrading to <code>v26.0</code></a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-between-minor-versions-less-than-v26" >Upgrading between minor versions less than <code>v26</code></a></li>
</ul>
</li>
<li>
**Always** upgrade the Materialize Operator **before**
upgrading the Materialize instances.

</li>
</ul>

> **Note:** For major version upgrades, you can **only** upgrade **one** major version
> at a time. For example, upgrades from **v26**.1.0 to **v27**.3.0 is
> permitted but **v26**.1.0 to **v28**.0.0 is not.

> **Note:** Downgrading is not supported.

## Prerequisites

### Required Tools

- [Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Upgrade process

> **Important:** The following procedure performs a rolling upgrade, where both the old and new Materialize instances are running before the old instances are removed. When performing a rolling upgrade, ensure you have enough resources to support having both the old and new Materialize instances running.

### Step 1: Update TF module source version

Update each module's `source` to point to the desired release tag, substituting
`<RELEASE_TAG>` in the code block below with your tag version:

> **Important:** The following code block is not comprehensive. Only the core modules and their
> dependency chain are shown below.
> If your configuration includes additional modules (networking, storage,
> database, node pools, etc.) provided by Materialize, **update those to the same
> release tag as well**.

```hcl
module "gke" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//gcp/modules/gke?ref=<RELEASE_TAG>"
  # ... your existing configuration ...
}

module "cert_manager" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//kubernetes/modules/cert-manager?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.gke]
}

module "operator" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//gcp/modules/operator?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.cert_manager]
}

module "materialize_instance" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//kubernetes/modules/materialize-instance?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.operator]
}

# Update the source of any additional Materialize-provided modules to the same release tag
```

### Step 2: Explicitly request rollout if using v1alpha1

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

> **Important:** Starting in Terraform module version v4.0.0, `crd_version` defaults to
> `v1`. If your instance uses `v1alpha1` and you are upgrading to module
> version v4.0.0 or greater, set `crd_version = "v1alpha1"` explicitly to
> stay on `v1alpha1`. Otherwise, applying migrates the instance to `v1` and
> triggers a rollout. See [Adopting the v1
> CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/).

To check the CRD version of the Materialize manifest that was applied, run
the following:

```sh
terraform state show 'module.materialize_instance.kubectl_manifest.materialize_instance' \
  | grep -iE 'api_?version|kind'
```

- If you are using `v1`, skip to the [Apply the updated TF
  step](#step-3-apply-the-updated-tf).
- **If you are using `v1alpha1`**, you need to update your `terraform.tfvars`
file to set the `request_rollout` variable to a new UUID value, substituting
the example value in the code block below with a UUID you generate (for
example, with `uuidgen`):

```hcl
# ...
# ...
request_rollout = "DBB4FCEC-1837-44F6-9CF2-3894678DD8D5" # ONLY for v1alpha1
```

### Step 3: Apply the updated TF

1. Initialize the Terraform directory to download the required providers
    and modules:

    ```bash
    terraform init
    ```

1. Review the execution plan before applying. In particular, check for any
  resources Terraform plans to destroy and recreate (shown as `-/+` in the
  plan), especially stateful resources such as your cluster, storage, and
  database:

    ```bash
    terraform plan
    ```

1. After reviewing the plan, apply the Terraform configuration.

    ```bash
    terraform apply
    ```

### Step 4: Verify the upgrade

Configure `kubectl` to connect to your GKE cluster, replacing `<your-project-id>`
with your GCP project ID:

```bash
# gcloud container clusters get-credentials <your-gke-cluster-name> --region <your-region> --project <your-project-id>
gcloud container clusters get-credentials $(terraform output -raw gke_cluster_name) \
 --region $(terraform output -raw gke_cluster_location) \
 --project <your-project-id>
```

> **Note:** `terraform apply` returns once the Materialize custom resource is updated.
> The Operator then rolls out the new generation asynchronously, so the new
> `environmentd` pods may take a few minutes to become ready.

<ol>
<li>
<p>Check the status of the <code>materialize</code> namespace:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize get all
</span></span></code></pre></div></li>
<li>
<p>Check the status of the <code>materialize-environment</code> namespace:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment get all
</span></span></code></pre></div></li>
<li>
<p>Once a new <code>environmentd</code> is up (may take a few minutes), confirm the
running <code>environmentd</code> version matches the version you upgraded to. Check
the <code>Image</code> field in the pod description.</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment describe pod -l <span class="nv">app</span><span class="o">=</span>environmentd
</span></span></code></pre></div></li>
</ol>
<p>If you run into an error during the upgrade, refer to the
<a href="/self-managed-deployments/troubleshooting/" >Troubleshooting</a>.</p>

## See also

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)
- [Troubleshooting](/self-managed-deployments/troubleshooting/)

---

## Upgrade on kind

To upgrade your Materialize instances, first choose a new operator version and upgrade the Materialize operator. Then, upgrade your Materialize instances to the same version. The following tutorial upgrades your Materialize deployment running locally on a [`kind`](https://kind.sigs.k8s.io/)
cluster.

The tutorial assumes you have installed Materialize on `kind` using the
instructions on [Install locally on
kind](/self-managed-deployments/installation/install-on-local-kind/).

> **Important:** When performing major version upgrades, you can upgrade only one major version
> at a time. For example, upgrades from **v26**.1.0 to **v27**.2.0 is permitted
> but **v26**.1.0 to **v28**.0.0 is not. Skipping major versions or downgrading is
> not supported. To upgrade from v25.2 to v26.0, you must [upgrade first to v25.2.16+](https://materialize.com/docs/self-managed/v25.2/release-notes/#v25216).

## Prerequisites

### Helm 3.2.0+

If you don't have Helm version 3.2.0+ installed, install. For details, see the
[Helm documentation](https://helm.sh/docs/intro/install/).

### `kubectl`

This tutorial uses `kubectl`. To install, refer to the [`kubectl`
documentation](https://kubernetes.io/docs/tasks/tools/).

For help with `kubectl` commands, see [kubectl Quick
reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/).

### License key

Starting in v26.0, Materialize requires a license key. If your existing
deployment does not have a license key configured, contact [Materialize support](https://materialize.com/docs/support/).

## Upgrade

> **Important:** The following procedure performs a rolling upgrade, where both the old and new
> Materialize instances are running before the old instances are removed.
> When performing a rolling upgrade, ensure you have enough resources to support
> having both the old and new Materialize instances running.

<ol>
<li>
<p>Open a Terminal window.</p>
</li>
<li>
<p>Go to your Materialize working directory.</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl"><span class="nb">cd</span> my-local-mz
</span></span></code></pre></div></li>
<li>
<p>Upgrade the Materialize Helm chart.</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl">helm repo update materialize
</span></span></code></pre></div></li>
<li>
<p>Get the sample configuration files for the new version.</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl"><span class="nv">mz_version</span><span class="o">=</span>v26.36.0
</span></span><span class="line"><span class="cl">
</span></span><span class="line"><span class="cl">curl -o upgrade-values.yaml https://raw.githubusercontent.com/MaterializeInc/materialize/refs/tags/<span class="nv">$mz_version</span>/misc/helm-charts/operator/values.yaml
</span></span></code></pre></div><p>If you have previously modified the <code>sample-values.yaml</code> file for your
deployment, include the changes into the <code>upgrade-values.yaml</code> file.</p>
</li>
<li>
<p>Check the CRD version (<code>v1alpha1</code> or, available starting
in Materialize v26.30, <code>v1</code>) being used for your Materialize instance.
To determine which CRD version is in use, run the following command,
   replacing <instance-name> with your instance name. For the
   `sample-materialize.yaml` used in this example, the instance name is
   `12345678-1234-1234-1234-123456789012`:

   ```sh
   kubectl get materialize <instance-name> -n materialize-environment \
     -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}' \
   | python3 -c 'import sys,json; print(json.load(sys.stdin)["apiVersion"])'
   ```
</p>
</li>
<li>
<p>Upgrade the Materialize Operator, specifying the new version and the updated
configuration file. Include any additional configurations that you specify
for your deployment.</p>
<p>Select the tab for your Materialize CRD API version (<code>v1alpha1</code> or,
available starting in Materialize v26.30, <code>v1</code>) your deployment
<strong>currently</strong> uses. This step does not cover <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/" >migrating from <code>v1alpha1</code>
to <code>v1</code> (including setting up
prerequisites)</a>.</p>
<div class="code-tabs">
<ul class="nav-tabs"></ul>
<div class="tab-content">
<div class="tab-pane" title="CRD v1" id="upgrade-operator-kind-v1">
<p>If currently using <code>v1</code> (available starting in Materialize v26.30):</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl">helm upgrade my-materialize-operator materialize/materialize-operator <span class="se">\
</span></span></span><span class="line"><span class="cl"><span class="se"></span>--namespace<span class="o">=</span>materialize <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>--version v26.36.0 <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>-f upgrade-values.yaml <span class="se">\
</span></span></span><span class="line"><span class="cl"><span class="se"></span>--set observability.podMetrics.enabled<span class="o">=</span><span class="nb">true</span> <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>--set operator.args.installV1CRD<span class="o">=</span><span class="nb">true</span>
</span></span></code></pre></div></div>
<div class="tab-pane" title="CRD v1alpha1" id="upgrade-operator-kind-v1alpha1">
<p>If currently using <code>v1alpha1</code> (default):</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl">helm upgrade my-materialize-operator materialize/materialize-operator <span class="se">\
</span></span></span><span class="line"><span class="cl"><span class="se"></span>--namespace<span class="o">=</span>materialize <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>--version v26.36.0 <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>-f upgrade-values.yaml <span class="se">\
</span></span></span><span class="line"><span class="cl"><span class="se"></span>--set observability.podMetrics.enabled<span class="o">=</span><span class="nb">true</span>
</span></span></code></pre></div></div>
</div>
</div>
</li>
<li>
<p>Verify that the operator is running:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize get all
</span></span></code></pre></div><p>Verify the operator upgrade by checking its events:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize describe pod -l app.kubernetes.io/name<span class="o">=</span>materialize-operator
</span></span></code></pre></div></li>
<li>
<p>As of v26.0, Self-Managed Materialize requires a license key. If your
deployment has not been configured with a license key:</p>
<p>a. Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>.</p>
<p>b. Once you have your license key, run the following command to add it to the <code>materialize-backend</code> secret:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment patch secret materialize-backend -p <span class="s1">&#39;{&#34;stringData&#34;:{&#34;license_key&#34;:&#34;&lt;your license key goes here&gt;&#34;}}&#39;</span> --type<span class="o">=</span>merge
</span></span></code></pre></div></li>
<li>
<p>Create a new <code>upgrade-materialize.yaml</code> file, updating the following fields:</p>
<p>Select the tab for the CRD API version your deployment currently uses. This
step does not cover <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/" >migrating from <code>v1alpha1</code> to <code>v1</code></a>. (The <code>v1</code> CRD
API version is available starting in Materialize v26.30.)</p>
<div class="code-tabs">
<ul class="nav-tabs"></ul>
<div class="tab-content">
<div class="tab-pane" title="CRD v1" id="local-kind-v1">
<p>If using <code>v1</code>, update the following fields:</p>
<table>
  <thead>
      <tr>
          <th>Field</th>
          <th>Description</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td><code>environmentdImageRef</code></td>
          <td>Update the version to the new version. This should be the same as the operator version: <code>v26.36.0</code>. Updating this field automatically triggers a rollout.</td>
      </tr>
      <tr>
          <td><code>forceRollout</code></td>
          <td><strong>Optional.</strong> Set to a new UUID (can be generated with <code>uuidgen</code>) only to force a rollout when no other changes exist.</td>
      </tr>
  </tbody>
</table>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-yaml" data-lang="yaml"><span class="line"><span class="cl"><span class="nt">apiVersion</span><span class="p">:</span><span class="w"> </span><span class="l">materialize.cloud/v1</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w"></span><span class="nt">kind</span><span class="p">:</span><span class="w"> </span><span class="l">Materialize</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w"></span><span class="nt">metadata</span><span class="p">:</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">name</span><span class="p">:</span><span class="w"> </span><span class="m">12345678-1234-1234-1234-123456789012</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">namespace</span><span class="p">:</span><span class="w"> </span><span class="l">materialize-environment</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w"></span><span class="nt">spec</span><span class="p">:</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">environmentdImageRef</span><span class="p">:</span><span class="w"> </span><span class="l">materialize/environmentd:v26.36.0</span><span class="w"> </span><span class="c"># Update version</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="c"># forceRollout: 33333333-3333-3333-3333-333333333333    # For forced rollouts</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">rolloutStrategy</span><span class="p">:</span><span class="w"> </span><span class="l">WaitUntilReady                        </span><span class="w"> </span><span class="c"># The mechanism to use when rolling out the new version.</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">backendSecretName</span><span class="p">:</span><span class="w"> </span><span class="l">materialize-backend</span><span class="w">
</span></span></span></code></pre></div></div>
<div class="tab-pane" title="CRD v1alpha1" id="local-kind-v1alpha1">
<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
   chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
   With <code>v1alpha1</code>, instance rollouts require manually rotating a
   UUID.</p>
<p>If using <code>v1alpha1</code>, update the following fields:</p>
<table>
  <thead>
      <tr>
          <th>Field</th>
          <th>Description</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td><code>environmentdImageRef</code></td>
          <td>Update the version to the new version. This should be the same as the operator version: <code>v26.36.0</code>.</td>
      </tr>
      <tr>
          <td><code>requestRollout</code> or <code>forceRollout</code></td>
          <td>Enter a new UUID. Can be generated with <code>uuidgen</code>. <br> <ul><li><code>requestRollout</code> triggers a rollout only if changes exist. </li><li><code>forceRollout</code> triggers a rollout even if no changes exist.</li></ul></td>
      </tr>
  </tbody>
</table>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-yaml" data-lang="yaml"><span class="line"><span class="cl"><span class="nt">apiVersion</span><span class="p">:</span><span class="w"> </span><span class="l">materialize.cloud/v1alpha1</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w"></span><span class="nt">kind</span><span class="p">:</span><span class="w"> </span><span class="l">Materialize</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w"></span><span class="nt">metadata</span><span class="p">:</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">name</span><span class="p">:</span><span class="w"> </span><span class="m">12345678-1234-1234-1234-123456789012</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">namespace</span><span class="p">:</span><span class="w"> </span><span class="l">materialize-environment</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w"></span><span class="nt">spec</span><span class="p">:</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">environmentdImageRef</span><span class="p">:</span><span class="w"> </span><span class="l">materialize/environmentd:v26.36.0</span><span class="w"> </span><span class="c"># Update version</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">requestRollout</span><span class="p">:</span><span class="w"> </span><span class="m">22222222-2222-2222-2222-222222222222</span><span class="w">    </span><span class="c"># Enter a new UUID</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w"></span><span class="c"># forceRollout: 33333333-3333-3333-3333-333333333333    # For forced rollouts</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">rolloutStrategy</span><span class="p">:</span><span class="w"> </span><span class="l">WaitUntilReady                        </span><span class="w"> </span><span class="c"># The mechanism to use when rolling out the new version.</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">backendSecretName</span><span class="p">:</span><span class="w"> </span><span class="l">materialize-backend</span><span class="w">
</span></span></span></code></pre></div></div>
</div>
</div>
</li>
<li>
<p>Apply the upgrade-materialize.yaml file to your Materialize instance:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl">kubectl apply -f upgrade-materialize.yaml
</span></span></code></pre></div></li>
<li>
<p>Verify that the components are running after the upgrade:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment get all
</span></span></code></pre></div><p>Verify upgrade by checking the <code>balancerd</code> events:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment describe pod -l <span class="nv">app</span><span class="o">=</span>balancerd
</span></span></code></pre></div><p>The <strong>Events</strong> section should list that the new version of the <code>balancerd</code>
have been pulled.</p>
<p>Verify the upgrade by checking the <code>environmentd</code> events:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment describe pod -l <span class="nv">app</span><span class="o">=</span>environmentd
</span></span></code></pre></div><p>The <strong>Events</strong> section should list that the new version of the <code>environmentd</code>
have been pulled.</p>
</li>
<li>
<p>Open the Materialize Console. The Console should display the new version.</p>
</li>
</ol>

## See also

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Troubleshooting](/self-managed-deployments/troubleshooting/)

