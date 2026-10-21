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
  --version v26.46.1
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

## Pages in this section

- [Adopting the v1 CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/index.md): Adopt the v1 Materialize CRD API version for Self-Managed Materialize.
- [Upgrade notes](/self-managed-deployments/upgrading/version-notes/index.md): Version-specific notes for upgrading Self-Managed Materialize.
- [Upgrade on AWS](/self-managed-deployments/upgrading/upgrade-on-aws/index.md): Upgrade Materialize on AWS using the Terraform module.
- [Upgrade on Azure](/self-managed-deployments/upgrading/upgrade-on-azure/index.md): Upgrade Materialize on Azure using the Terraform module.
- [Upgrade on GCP](/self-managed-deployments/upgrading/upgrade-on-gcp/index.md): Upgrade Materialize on GCP using the Terraform module.
- [Upgrade on kind](/self-managed-deployments/upgrading/upgrade-on-kind/index.md): Upgrade Materialize running locally on a kind cluster.
