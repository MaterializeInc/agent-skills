# Upgrade notes
Version-specific notes for upgrading Self-Managed Materialize.
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
