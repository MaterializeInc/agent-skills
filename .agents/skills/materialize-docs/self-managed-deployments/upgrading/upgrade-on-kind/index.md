# Upgrade on kind
Upgrade Materialize running locally on a kind cluster.
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
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl"><span class="nv">mz_version</span><span class="o">=</span>v26.37.0
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
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>--version v26.37.0 <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>-f upgrade-values.yaml <span class="se">\
</span></span></span><span class="line"><span class="cl"><span class="se"></span>--set observability.podMetrics.enabled<span class="o">=</span><span class="nb">true</span> <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>--set operator.args.installV1CRD<span class="o">=</span><span class="nb">true</span>
</span></span></code></pre></div></div>
<div class="tab-pane" title="CRD v1alpha1" id="upgrade-operator-kind-v1alpha1">
<p>If currently using <code>v1alpha1</code> (default):</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl">helm upgrade my-materialize-operator materialize/materialize-operator <span class="se">\
</span></span></span><span class="line"><span class="cl"><span class="se"></span>--namespace<span class="o">=</span>materialize <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>--version v26.37.0 <span class="se">\
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
          <td>Update the version to the new version. This should be the same as the operator version: <code>v26.37.0</code>. Updating this field automatically triggers a rollout.</td>
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
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">environmentdImageRef</span><span class="p">:</span><span class="w"> </span><span class="l">materialize/environmentd:v26.37.0</span><span class="w"> </span><span class="c"># Update version</span><span class="w">
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
          <td>Update the version to the new version. This should be the same as the operator version: <code>v26.37.0</code>.</td>
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
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">environmentdImageRef</span><span class="p">:</span><span class="w"> </span><span class="l">materialize/environmentd:v26.37.0</span><span class="w"> </span><span class="c"># Update version</span><span class="w">
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
