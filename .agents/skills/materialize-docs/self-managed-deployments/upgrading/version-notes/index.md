# Upgrade notes
Version-specific notes for upgrading Self-Managed Materialize.
Review the notes for your target version before upgrading. For the general
upgrade procedure, see the [upgrade
guides](/self-managed-deployments/upgrading/#upgrade-guides).

## Upgrading to `v26.30` and later versions

<p>v26.30.0 introduces support for a new version of the Materialize CRD, <code>v1</code>,
which provides simplified rollouts. Previously, Materialize only supported
<code>v1alpha1</code>; <code>v1alpha1</code> remains the default.</p>
<p>Upgrading to v26.30+ does <strong>not</strong> require adopting the <code>v1</code> CRD; adopting <code>v1</code>
is <strong>opt-in</strong>. You can upgrade as usual while continuing to use <code>v1alpha1</code>; your
existing instances will behave exactly as before. However, once you are on
v26.30+, we do recommend you schedule <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/" >adoption of
<code>v1</code></a> before the next
major release.</p>
<p>If using Materialize-provided TF modules, v3.1.1+ automatically handles the
<a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/#prerequisites" >prerequisites for adopting
<code>v1</code></a>.
It does not switch your instances to <code>v1</code>. To switch to <code>v1</code>, see <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/#switch-to-v1" >Switch to
<code>v1</code>
CRD</a>.</p>

## Upgrading to `v26.1` and later versions

<ul>
<li>To upgrade to <code>v26.1</code> or future versions, you must first upgrade to <code>v26.0</code></li>
</ul>

## Upgrading to `v26.0`

<ul>
<li>
<p>Upgrading to <code>v26.0.0</code> is a major version upgrade. To upgrade to <code>v26.0</code> from
<code>v25.2.X</code> or <code>v25.1</code>, you must first upgrade to <code>v25.2.16</code> and then upgrade to
<code>v26.0.0</code>.</p>
</li>
<li>
<p>For upgrades, the <code>inPlaceRollout</code> setting has been deprecated and will be
ignored. Instead, use the new setting <code>rolloutStrategy</code> to specify either:</p>
<ul>
<li><code>WaitUntilReady</code> (<em>Default</em>)</li>
<li><code>ImmediatelyPromoteCausingDowntime</code></li>
</ul>
<p>For more information, see
<a href="/self-managed-deployments/upgrading/#rollout-strategies" ><code>rolloutStrategy</code></a>.</p>
</li>
<li>
<p>New requirements were introduced for <a href="/releases/#license-key" >license keys</a>.
To upgrade, you will first need to add a license key to the <code>backendSecret</code>
used in the spec for your Materialize resource.</p>
<p>See <a href="/releases/#license-key" >License key</a> for details on getting your license
key.</p>
</li>
<li>
<p>Swap is now enabled by default. Swap reduces the memory required to
operate Materialize and improves cost efficiency. Upgrading to <code>v26.0</code>
requires some preparation to ensure Kubernetes nodes are labeled
and configured correctly. As such:</p>
<ul>
<li>
<p>If you are using the Materialize-provided Terraforms, upgrade to version
<code>v0.6.1</code> of the Terraform.</p>
</li>
<li>
<p>If you are <red><strong>not</strong></red> using a Materialize-provided Terraform, refer
to <a href="/self-managed-deployments/appendix/upgrade-to-swap/" >Prepare for swap and upgrade to v26.0</a>.</p>
</li>
</ul>
</li>
</ul>

## Upgrading between minor versions less than `v26`

- Prior to `v26`, you must upgrade at most one minor version at a time. For
  example, upgrading from `v25.1.5` to `v25.2.16` is permitted.
