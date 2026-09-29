<!-- mz-docs page: self-managed-deployments/materialize-crd-field-descriptions/v1 -->

# v1
Reference page on Materialize CRD Fields for the v1 API (v26.30+)
> **Note:** The `v1` CRD is available starting in v26.30. It is opt-in for the Helm chart
> and the default for the Terraform modules starting in v4.0.0. If you are on
> `v1alpha1` and want a simplified rollout behavior of `v1`, see [Adopting the v1
> CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/).
> For the `v1alpha1` field descriptions, see [CRD v1alpha1 field descriptions](/self-managed-deployments/materialize-crd-field-descriptions/v1alpha1/).

#### MaterializeSpec
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>backendSecretName</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The name of a secret containing <code>metadata_backend_url</code> and <code>persist_backend_url</code>.
It may also contain <code>external_login_password_mz_system</code>, which will be used as
the password for the <code>mz_system</code> user if <code>authenticatorKind</code> is <code>Password</code>.</p>

</td>
</tr>
<tr>
<td><code>environmentdImageRef</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The environmentd image to run.</p>

</td>
</tr>
<tr>
<td><code>authenticatorKind</code></td>
<td></td>
<td>
<em><strong>Enum</strong></em>

<p><p>How to authenticate with Materialize.</p>
<p>Valid values:</p>
<ul>
<li><code>Frontegg</code>:<br>  Authenticate users using Frontegg.</li>
<li><code>Password</code>:<br>  Authenticate users using internally stored password hashes.
The backend secret must contain external_login_password_mz_system.</li>
<li><code>Sasl</code>:<br>  Authenticate users using SASL.</li>
<li><code>Oidc</code>:<br>  Authenticate users using OIDC (JWT tokens).</li>
<li><code>None</code> (default):<br>  Do not authenticate users. Trust they are who they say they are without verification.</li>
</ul>
</p>

<p><strong>Default:</strong> <code>None</code></p></td>
</tr>
<tr>
<td><code>balancerdConfigmapName</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>The name of an externally managed ConfigMap in this namespace containing
balancerd dynamic configuration as a JSON object in <code>config.json</code>.
Changes to its contents are applied at runtime. Changing this reference
restarts balancerd pods but does not trigger an environmentd rollout.</p>

</td>
</tr>
<tr>
<td><code>balancerdExternalCertificateSpec</code></td>
<td></td>
<td>
<em><strong><a href='#materializecertspec'>MaterializeCertSpec</a></strong></em>

<p><p>The configuration for generating an x509 certificate using cert-manager for balancerd
to present to incoming connections.
The <code>dnsNames</code> and <code>issuerRef</code> fields are required.</p>
<p>This field is excluded from the rollout hash and changes will not trigger a rollout.</p>
</p>

</td>
</tr>
<tr>
<td><code>balancerdReplicas</code></td>
<td></td>
<td>
<em><strong>Integer</strong></em>

<p><p>Number of balancerd pods to create.</p>
<p>This field is excluded from the rollout hash and changes will not trigger a rollout.</p>
</p>

</td>
</tr>
<tr>
<td><code>balancerdResourceRequirements</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1resourcerequirements'>io.k8s.api.core.v1.ResourceRequirements</a></strong></em>

<p><p>Resource requirements for the balancerd pod.</p>
<p>This field is excluded from the rollout hash and changes will not trigger a rollout.</p>
</p>

</td>
</tr>
<tr>
<td><code>consoleExternalCertificateSpec</code></td>
<td></td>
<td>
<em><strong><a href='#materializecertspec'>MaterializeCertSpec</a></strong></em>

<p><p>The configuration for generating an x509 certificate using cert-manager for the console
to present to incoming connections.
The <code>dnsNames</code> and <code>issuerRef</code> fields are required.
Not yet implemented.</p>
<p>This field is excluded from the rollout hash and changes will not trigger a rollout.</p>
</p>

</td>
</tr>
<tr>
<td><code>consoleReplicas</code></td>
<td></td>
<td>
<em><strong>Integer</strong></em>

<p><p>Number of console pods to create.</p>
<p>This field is excluded from the rollout hash and changes will not trigger a rollout.</p>
</p>

</td>
</tr>
<tr>
<td><code>consoleResourceRequirements</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1resourcerequirements'>io.k8s.api.core.v1.ResourceRequirements</a></strong></em>

<p><p>Resource requirements for the console pod.</p>
<p>This field is excluded from the rollout hash and changes will not trigger a rollout.</p>
</p>

</td>
</tr>
<tr>
<td><code>enableRbac</code></td>
<td></td>
<td>
<em><strong>Bool</strong></em>

<p>Whether to enable role based access control. Defaults to false.</p>

</td>
</tr>
<tr>
<td><code>environmentId</code></td>
<td></td>
<td>
<em><strong>Uuid</strong></em>

<p>The value used by environmentd (via the &ndash;environment-id flag) to
uniquely identify this instance. Must be globally unique, and
is required if a license key is not provided.
NOTE: This value MUST NOT be changed in an existing instance,
since it affects things like the way data is stored in the persist
backend.</p>

<p><strong>Default:</strong> <code>00000000-0000-0000-0000-000000000000</code></p></td>
</tr>
<tr>
<td><code>environmentdConnectionRoleArn</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>If running in AWS, override the IAM role to use to support
the CREATE CONNECTION feature.</p>

</td>
</tr>
<tr>
<td><code>environmentdExtraArgs</code></td>
<td></td>
<td>
<em><strong>Array&lt;String&gt;</strong></em>

<p>Extra args to pass to the environmentd binary.</p>

</td>
</tr>
<tr>
<td><code>environmentdExtraEnv</code></td>
<td></td>
<td>
<em><strong>Array&lt;<a href='#iok8sapicorev1envvar'>io.k8s.api.core.v1.EnvVar</a>&gt;</strong></em>

<p>Extra environment variables to pass to the environmentd binary.</p>

</td>
</tr>
<tr>
<td><code>environmentdResourceRequirements</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1resourcerequirements'>io.k8s.api.core.v1.ResourceRequirements</a></strong></em>

<p>Resource requirements for the environmentd pod.</p>

</td>
</tr>
<tr>
<td><code>environmentdScratchVolumeStorageRequirement</code></td>
<td></td>
<td>
<em><strong>io.k8s.apimachinery.pkg.api.resource.Quantity</strong></em>

<p>Amount of disk to allocate, if a storage class is provided.</p>

</td>
</tr>
<tr>
<td><code>forcePromote</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p><p>If <code>forcePromote</code> is set to the same value as the <code>status.requestedRolloutHash</code>,
current rollout will skip waiting for clusters in the new
generation to rehydrate before promoting the new environmentd to
leader.</p>
<p>This field is excluded from the rollout hash and changes will not trigger a rollout.</p>
</p>

</td>
</tr>
<tr>
<td><code>forceRollout</code></td>
<td></td>
<td>
<em><strong>Uuid</strong></em>

<p>This value will force the controller to detect the spec as changed
even if no other changes happened. This can be used to force a rollout
to a new generation even without making any meaningful changes.</p>

<p><strong>Default:</strong> <code>00000000-0000-0000-0000-000000000000</code></p></td>
</tr>
<tr>
<td><code>internalCertificateSpec</code></td>
<td></td>
<td>
<em><strong><a href='#materializecertspec'>MaterializeCertSpec</a></strong></em>

<p>The cert-manager Issuer or ClusterIssuer to use for database internal communication.
The <code>issuerRef</code> field is required.
This currently is only used for environmentd, but will eventually support clusterd.
Not yet implemented.</p>

</td>
</tr>
<tr>
<td><code>podAnnotations</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Annotations to apply to the pods.</p>

</td>
</tr>
<tr>
<td><code>podLabels</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Labels to apply to the pods.</p>

</td>
</tr>
<tr>
<td><code>rolloutRequestTimeout</code></td>
<td></td>
<td>
<em><strong>RolloutRequestTimeout</strong></em>

<p><p>The maximum amount of time a rollout may remain in progress before
it is automatically cancelled.</p>
<p>While a rollout is in progress, the new generation of <code>environmentd</code>
runs in a read-only, un-promoted state and holds back compaction via
read holds. Leaving it in this state for too long can cause
incident-inducing load when it is eventually promoted, so the
operator cancels the rollout once this timeout is exceeded: the new
generation is torn down and the previously-active generation
continues serving. A new rollout can then be triggered by setting
<code>forceRollout</code> to a new value.</p>
<p>This does not apply to the <code>ImmediatelyPromoteCausingDowntime</code>
rollout strategy or to force-promoted rollouts, since by the time
those are in progress the old generation may already be gone.</p>
<p>The value is parsed as a human-readable duration, e.g. <code>24h</code>,
<code>90m</code>, or <code>1h 30m</code>. Defaults to [<code>DEFAULT_ROLLOUT_REQUEST_TIMEOUT</code>]
when omitted (the API server fills it in); an unparseable value also
falls back to that default.</p>
</p>

<p><strong>Default:</strong> <code>24h</code></p></td>
</tr>
<tr>
<td><code>rolloutStrategy</code></td>
<td></td>
<td>
<em><strong>Enum</strong></em>

<p><p>Rollout strategy to use when upgrading this Materialize instance.</p>
<p>Valid values:</p>
<ul>
<li>
<p><code>WaitUntilReady</code> (default):<br>  Create a new generation of pods, leaving the old generation around until the
new ones are ready to take over.
This minimizes downtime, and is what almost everyone should use.</p>
</li>
<li>
<p><code>ManuallyPromote</code>:<br>  Create a new generation of pods, leaving the old generation as the serving generation
until the user manually promotes the new generation.</p>
<p>When using <code>ManuallyPromote</code>, the new generation can be promoted at any
time, even if it has dataflows that are not fully caught up, by setting
<code>forcePromote</code> to the current rollout identifier: in <code>v1</code>, the value of
<code>status.requestedRolloutHash</code>; in <code>v1alpha1</code>, the <code>requestRollout</code> value
in the spec.</p>
<p>To minimize downtime, promotion should occur when the new generation
has caught up to the prior generation. To determine if the new
generation has caught up, consult the <code>UpToDate</code> condition in the
status of the Materialize Resource. If the condition&rsquo;s reason is
<code>ReadyToPromote</code> the new generation is ready to promote.</p>
> **Warning:** Do not leave new generations unpromoted indefinitely.
>   The new generation keeps open read holds which prevent compaction. Once promoted or
>   cancelled, those read holds are released. If left unpromoted for an extended time, this
>   data can build up, and can cause extreme deletion load on the metadata backend database
>   when finally promoted or cancelled.
>   To guard against this, a rollout that remains in progress longer
>   than `rolloutRequestTimeout` (default 24h) is automatically
>   cancelled.

</li>
<li>
<p><code>ImmediatelyPromoteCausingDowntime</code>:<br>  > **Warning:** THIS WILL CAUSE YOUR MATERIALIZE INSTANCE TO BE UNAVAILABLE FOR SOME TIME!!!
>   This strategy should ONLY be used by customers with physical hardware who do not have
>   enough hardware for the `WaitUntilReady` strategy. If you think you want this, please
>   consult with Materialize engineering to discuss your situation.
</p>
<p>Tear down the old generation of pods and promote the new generation of pods immediately,
without waiting for the new generation of pods to be ready.</p>
</li>
</ul>
</p>

<p><strong>Default:</strong> <code>WaitUntilReady</code></p></td>
</tr>
<tr>
<td><code>serviceAccountAnnotations</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p><p>Annotations to apply to the service account.</p>
<p>Annotations on service accounts are commonly used by cloud providers for IAM.
AWS uses &ldquo;eks.amazonaws.com/role-arn&rdquo;.
Azure uses &ldquo;azure.workload.identity/client-id&rdquo;, but
additionally requires &ldquo;azure.workload.identity/use&rdquo;: &ldquo;true&rdquo; on the pods.</p>
</p>

</td>
</tr>
<tr>
<td><code>serviceAccountLabels</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Labels to apply to the service account.</p>

</td>
</tr>
<tr>
<td><code>serviceAccountName</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Name of the kubernetes service account to use.
If not set, we will create one with the same name as this Materialize object.</p>

</td>
</tr>
<tr>
<td><code>systemParameterConfigmapName</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p><p>The name of a ConfigMap containing system parameters in JSON format.
The ConfigMap must contain a <code>system-params.json</code> key whose value
is a valid JSON object containing valid system parameters.</p>
<p>Run <code>SHOW ALL</code> in SQL to see a subset of configurable system parameters.</p>
<p>Example ConfigMap:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-yaml" data-lang="yaml"><span class="line"><span class="cl"><span class="nt">data</span><span class="p">:</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">system-params.json</span><span class="p">:</span><span class="w"> </span><span class="p">|</span><span class="sd">
</span></span></span><span class="line"><span class="cl"><span class="sd">    {
</span></span></span><span class="line"><span class="cl"><span class="sd">      &#34;max_connections&#34;: 1000
</span></span></span><span class="line"><span class="cl"><span class="sd">    }</span><span class="w">
</span></span></span></code></pre></div></p>

</td>
</tr>
</tbody>
</table>

#### MaterializeCertSpec
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>dnsNames</code></td>
<td></td>
<td>
<em><strong>Array&lt;String&gt;</strong></em>

<p>Additional DNS names the certificate will be valid for.</p>

</td>
</tr>
<tr>
<td><code>duration</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Duration the certificate will be requested for.
Value must be in units accepted by Go
<a href="https://golang.org/pkg/time/#ParseDuration" ><code>time.ParseDuration</code></a>.</p>

</td>
</tr>
<tr>
<td><code>issuerRef</code></td>
<td></td>
<td>
<em><strong><a href='#certificateissuerref'>CertificateIssuerRef</a></strong></em>

<p>Reference to an <code>Issuer</code> or <code>ClusterIssuer</code> that will generate the certificate.</p>

</td>
</tr>
<tr>
<td><code>privateKeyAlgorithm</code></td>
<td></td>
<td>
<em><strong>CertificatePrivateKeyAlgorithm</strong></em>

<p>Optional algorithm to use for the private key. If not specified, a recommended default will be chosen.</p>

</td>
</tr>
<tr>
<td><code>privateKeySize</code></td>
<td></td>
<td>
<em><strong>Integer</strong></em>

<p>Optional size for the private key.</p>

</td>
</tr>
<tr>
<td><code>renewBefore</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Duration before expiration the certificate will be renewed.
Value must be in units accepted by Go
<a href="https://golang.org/pkg/time/#ParseDuration" ><code>time.ParseDuration</code></a>.</p>

</td>
</tr>
<tr>
<td><code>secretTemplate</code></td>
<td></td>
<td>
<em><strong><a href='#certificatesecrettemplate'>CertificateSecretTemplate</a></strong></em>

<p>Additional annotations and labels to include in the Certificate object.</p>

</td>
</tr>
</tbody>
</table>

#### CertificateSecretTemplate
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>annotations</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Annotations is a key value map to be copied to the target Kubernetes Secret.</p>

</td>
</tr>
<tr>
<td><code>labels</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Labels is a key value map to be copied to the target Kubernetes Secret.</p>

</td>
</tr>
</tbody>
</table>

#### CertificateIssuerRef
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name of the resource being referred to.</p>

</td>
</tr>
<tr>
<td><code>group</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Group of the resource being referred to.</p>

</td>
</tr>
<tr>
<td><code>kind</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Kind of the resource being referred to.</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ResourceRequirements
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>claims</code></td>
<td></td>
<td>
<em><strong>Array&lt;<a href='#iok8sapicorev1resourceclaim'>io.k8s.api.core.v1.ResourceClaim</a>&gt;</strong></em>

<p><p>Claims lists the names of resources, defined in spec.resourceClaims, that are used by this container.</p>
<p>This field depends on the DynamicResourceAllocation feature gate.</p>
<p>This field is immutable. It can only be set for containers.</p>
</p>

</td>
</tr>
<tr>
<td><code>limits</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, io.k8s.apimachinery.pkg.api.resource.Quantity&gt;</strong></em>

<p>Limits describes the maximum amount of compute resources allowed. More info: <a href="https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/" >https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/</a></p>

</td>
</tr>
<tr>
<td><code>requests</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, io.k8s.apimachinery.pkg.api.resource.Quantity&gt;</strong></em>

<p>Requests describes the minimum amount of compute resources required. If Requests is omitted for a container, it defaults to Limits if that is explicitly specified, otherwise to an implementation-defined value. Requests cannot exceed Limits. More info: <a href="https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/" >https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/</a></p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ResourceClaim
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name must match the name of one entry in pod.spec.resourceClaims of the Pod where this field is used. It makes that resource available inside a container.</p>

</td>
</tr>
<tr>
<td><code>request</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Request is the name chosen for a request in the referenced claim. If empty, everything from the claim is made available, otherwise only the result of this request.</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.EnvVar
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name of the environment variable. May consist of any printable ASCII characters except &lsquo;=&rsquo;.</p>

</td>
</tr>
<tr>
<td><code>value</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Variable references $(VAR_NAME) are expanded using the previously defined environment variables in the container and any service environment variables. If a variable cannot be resolved, the reference in the input string will be unchanged. Double $$ are reduced to a single $, which allows for escaping the $(VAR_NAME) syntax: i.e. &ldquo;$$(VAR_NAME)&rdquo; will produce the string literal &ldquo;$(VAR_NAME)&rdquo;. Escaped references will never be expanded, regardless of whether the variable exists or not. Defaults to &ldquo;&rdquo;.</p>

</td>
</tr>
<tr>
<td><code>valueFrom</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1envvarsource'>io.k8s.api.core.v1.EnvVarSource</a></strong></em>

<p>Source for the environment variable&rsquo;s value. Cannot be used if value is not empty.</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.EnvVarSource
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>configMapKeyRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1configmapkeyselector'>io.k8s.api.core.v1.ConfigMapKeySelector</a></strong></em>

<p>Selects a key of a ConfigMap.</p>

</td>
</tr>
<tr>
<td><code>fieldRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1objectfieldselector'>io.k8s.api.core.v1.ObjectFieldSelector</a></strong></em>

<p>Selects a field of the pod: supports metadata.name, metadata.namespace, <code>metadata.labels['&lt;KEY&gt;']</code>, <code>metadata.annotations['&lt;KEY&gt;']</code>, spec.nodeName, spec.serviceAccountName, status.hostIP, status.podIP, status.podIPs.</p>

</td>
</tr>
<tr>
<td><code>fileKeyRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1filekeyselector'>io.k8s.api.core.v1.FileKeySelector</a></strong></em>

<p>FileKeyRef selects a key of the env file. Requires the EnvFiles feature gate to be enabled.</p>

</td>
</tr>
<tr>
<td><code>resourceFieldRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1resourcefieldselector'>io.k8s.api.core.v1.ResourceFieldSelector</a></strong></em>

<p>Selects a resource of the container: only resources limits and requests (limits.cpu, limits.memory, limits.ephemeral-storage, requests.cpu, requests.memory and requests.ephemeral-storage) are currently supported.</p>

</td>
</tr>
<tr>
<td><code>secretKeyRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1secretkeyselector'>io.k8s.api.core.v1.SecretKeySelector</a></strong></em>

<p>Selects a key of a secret in the pod&rsquo;s namespace</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.SecretKeySelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>key</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The key of the secret to select from.  Must be a valid secret key.</p>

</td>
</tr>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name of the referent. This field is effectively required, but due to backwards compatibility is allowed to be empty. Instances of this type with an empty value here are almost certainly wrong. More info: <a href="https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names" >https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names</a></p>

</td>
</tr>
<tr>
<td><code>optional</code></td>
<td></td>
<td>
<em><strong>Bool</strong></em>

<p>Specify whether the Secret or its key must be defined</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ResourceFieldSelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>resource</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Required: resource to select</p>

</td>
</tr>
<tr>
<td><code>containerName</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Container name: required for volumes, optional for env vars</p>

</td>
</tr>
<tr>
<td><code>divisor</code></td>
<td></td>
<td>
<em><strong>io.k8s.apimachinery.pkg.api.resource.Quantity</strong></em>

<p>Specifies the output format of the exposed resources, defaults to &ldquo;1&rdquo;</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.FileKeySelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>key</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The key within the env file. An invalid key will prevent the pod from starting. The keys defined within a source may consist of any printable ASCII characters except &lsquo;=&rsquo;. During Alpha stage of the EnvFiles feature gate, the key size is limited to 128 characters.</p>

</td>
</tr>
<tr>
<td><code>path</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The path within the volume from which to select the file. Must be relative and may not contain the &lsquo;..&rsquo; path or start with &lsquo;..&rsquo;.</p>

</td>
</tr>
<tr>
<td><code>volumeName</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The name of the volume mount containing the env file.</p>

</td>
</tr>
<tr>
<td><code>optional</code></td>
<td></td>
<td>
<em><strong>Bool</strong></em>

<p><p>Specify whether the file or its key must be defined. If the file or key does not exist, then the env var is not published. If optional is set to true and the specified key does not exist, the environment variable will not be set in the Pod&rsquo;s containers.</p>
<p>If optional is set to false and the specified key does not exist, an error will be returned during Pod creation.</p>
</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ObjectFieldSelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>fieldPath</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Path of the field to select in the specified API version.</p>

</td>
</tr>
<tr>
<td><code>apiVersion</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Version of the schema the FieldPath is written in terms of, defaults to &ldquo;v1&rdquo;.</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ConfigMapKeySelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>key</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The key to select.</p>

</td>
</tr>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name of the referent. This field is effectively required, but due to backwards compatibility is allowed to be empty. Instances of this type with an empty value here are almost certainly wrong. More info: <a href="https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names" >https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names</a></p>

</td>
</tr>
<tr>
<td><code>optional</code></td>
<td></td>
<td>
<em><strong>Bool</strong></em>

<p>Specify whether the ConfigMap or its key must be defined</p>

</td>
</tr>
</tbody>
</table>


<!-- mz-docs page: self-managed-deployments/materialize-crd-field-descriptions/v1alpha1 -->

# v1alpha1
Reference page on Materialize CRD Fields for the v1alpha1 API (before v26.30)
> **Note:** `v1alpha1` is the default CRD version for the Helm chart. The Terraform
> modules default to `v1` starting in v4.0.0. With v1alpha1, rollouts require
> manually rotating a UUID. Starting in v26.30, the
> [v1](/self-managed-deployments/materialize-crd-field-descriptions/v1/) CRD is
> available and provides a simplified rollout behavior.
> To switch to `v1`, see [Adopting the v1
> CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/).

#### MaterializeSpec
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>backendSecretName</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The name of a secret containing <code>metadata_backend_url</code> and <code>persist_backend_url</code>.
It may also contain <code>external_login_password_mz_system</code>, which will be used as
the password for the <code>mz_system</code> user if <code>authenticatorKind</code> is <code>Password</code>,
<code>Sasl</code>, or <code>Oidc</code>.</p>

</td>
</tr>
<tr>
<td><code>environmentdImageRef</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The environmentd image to run.</p>

</td>
</tr>
<tr>
<td><code>authenticatorKind</code></td>
<td></td>
<td>
<em><strong>Enum</strong></em>

<p><p>How to authenticate with Materialize.</p>
<p>Valid values:</p>
<ul>
<li><code>Frontegg</code>:<br>  Authenticate users using Frontegg.</li>
<li><code>Password</code>:<br>  Authenticate users using internally stored password hashes.
The backend secret must contain external_login_password_mz_system.</li>
<li><code>Sasl</code>:<br>  Authenticate users using SASL.</li>
<li><code>Oidc</code>:<br>  Authenticate users using OIDC (JWT tokens).</li>
<li><code>None</code> (default):<br>  Do not authenticate users. Trust they are who they say they are without verification.</li>
</ul>
</p>

<p><strong>Default:</strong> <code>None</code></p></td>
</tr>
<tr>
<td><code>balancerdConfigmapName</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>The name of an externally managed ConfigMap in this namespace containing
balancerd dynamic configuration as a JSON object in <code>config.json</code>.
Changes to its contents are applied at runtime. Changing this reference
restarts balancerd pods but does not trigger an environmentd rollout.</p>

</td>
</tr>
<tr>
<td><code>balancerdExternalCertificateSpec</code></td>
<td></td>
<td>
<em><strong><a href='#materializecertspec'>MaterializeCertSpec</a></strong></em>

<p>The configuration for generating an x509 certificate using cert-manager for balancerd
to present to incoming connections.
The <code>dnsNames</code> and <code>issuerRef</code> fields are required.</p>

</td>
</tr>
<tr>
<td><code>balancerdReplicas</code></td>
<td></td>
<td>
<em><strong>Integer</strong></em>

<p>Number of balancerd pods to create.</p>

</td>
</tr>
<tr>
<td><code>balancerdResourceRequirements</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1resourcerequirements'>io.k8s.api.core.v1.ResourceRequirements</a></strong></em>

<p>Resource requirements for the balancerd pod.</p>

</td>
</tr>
<tr>
<td><code>consoleExternalCertificateSpec</code></td>
<td></td>
<td>
<em><strong><a href='#materializecertspec'>MaterializeCertSpec</a></strong></em>

<p>The configuration for generating an x509 certificate using cert-manager for the console
to present to incoming connections.
The <code>dnsNames</code> and <code>issuerRef</code> fields are required.
Not yet implemented.</p>

</td>
</tr>
<tr>
<td><code>consoleReplicas</code></td>
<td></td>
<td>
<em><strong>Integer</strong></em>

<p>Number of console pods to create.</p>

</td>
</tr>
<tr>
<td><code>consoleResourceRequirements</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1resourcerequirements'>io.k8s.api.core.v1.ResourceRequirements</a></strong></em>

<p>Resource requirements for the console pod.</p>

</td>
</tr>
<tr>
<td><code>enableRbac</code></td>
<td></td>
<td>
<em><strong>Bool</strong></em>

<p>Whether to enable role based access control. Defaults to false.</p>

</td>
</tr>
<tr>
<td><code>environmentId</code></td>
<td></td>
<td>
<em><strong>Uuid</strong></em>

<p>The value used by environmentd (via the &ndash;environment-id flag) to
uniquely identify this instance. Must be globally unique, and
is required if a license key is not provided.
NOTE: This value MUST NOT be changed in an existing instance,
since it affects things like the way data is stored in the persist
backend.</p>

<p><strong>Default:</strong> <code>00000000-0000-0000-0000-000000000000</code></p></td>
</tr>
<tr>
<td><code>environmentdConnectionRoleArn</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>If running in AWS, override the IAM role to use to support
the CREATE CONNECTION feature.</p>

</td>
</tr>
<tr>
<td><code>environmentdExtraArgs</code></td>
<td></td>
<td>
<em><strong>Array&lt;String&gt;</strong></em>

<p>Extra args to pass to the environmentd binary.</p>

</td>
</tr>
<tr>
<td><code>environmentdExtraEnv</code></td>
<td></td>
<td>
<em><strong>Array&lt;<a href='#iok8sapicorev1envvar'>io.k8s.api.core.v1.EnvVar</a>&gt;</strong></em>

<p>Extra environment variables to pass to the environmentd binary.</p>

</td>
</tr>
<tr>
<td><code>environmentdResourceRequirements</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1resourcerequirements'>io.k8s.api.core.v1.ResourceRequirements</a></strong></em>

<p>Resource requirements for the environmentd pod.</p>

</td>
</tr>
<tr>
<td><code>environmentdScratchVolumeStorageRequirement</code></td>
<td></td>
<td>
<em><strong>io.k8s.apimachinery.pkg.api.resource.Quantity</strong></em>

<p>Amount of disk to allocate, if a storage class is provided.</p>

</td>
</tr>
<tr>
<td><code>forcePromote</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>If <code>forcePromote</code> is set to the same value as <code>requestRollout</code>, the
current rollout will skip waiting for clusters in the new
generation to rehydrate before promoting the new environmentd to
leader.</p>

</td>
</tr>
<tr>
<td><code>forceRollout</code></td>
<td></td>
<td>
<em><strong>Uuid</strong></em>

<p>This value will be written to an annotation in the generated
environmentd statefulset, in order to force the controller to
detect the generated resources as changed even if no other changes
happened. This can be used to force a rollout to a new generation
even without making any meaningful changes, by setting it to the
same value as <code>requestRollout</code>.</p>

<p><strong>Default:</strong> <code>00000000-0000-0000-0000-000000000000</code></p></td>
</tr>
<tr>
<td><code>internalCertificateSpec</code></td>
<td></td>
<td>
<em><strong><a href='#materializecertspec'>MaterializeCertSpec</a></strong></em>

<p>The cert-manager Issuer or ClusterIssuer to use for database internal communication.
The <code>issuerRef</code> field is required.
This currently is only used for environmentd, but will eventually support clusterd.
Not yet implemented.</p>

</td>
</tr>
<tr>
<td><code>podAnnotations</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Annotations to apply to the pods.</p>

</td>
</tr>
<tr>
<td><code>podLabels</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Labels to apply to the pods.</p>

</td>
</tr>
<tr>
<td><code>requestRollout</code></td>
<td></td>
<td>
<em><strong>Uuid</strong></em>

<p><p>When changes are made to the environmentd resources (either via
modifying fields in the spec here or by deploying a new
orchestratord version which changes how resources are generated),
existing environmentd processes won&rsquo;t be automatically restarted.
In order to trigger a restart, the request_rollout field should be
set to a new (random) value. Once the rollout completes, the value
of <code>status.lastCompletedRolloutRequest</code> will be set to this value
to indicate completion.</p>
<p>Defaults to a random value in order to ensure that the first
generation rollout is automatically triggered.</p>
</p>

<p><strong>Default:</strong> <code>00000000-0000-0000-0000-000000000000</code></p></td>
</tr>
<tr>
<td><code>rolloutRequestTimeout</code></td>
<td></td>
<td>
<em><strong>RolloutRequestTimeout</strong></em>

<p><p>The maximum amount of time a rollout may remain in progress before
it is automatically cancelled.</p>
<p>While a rollout is in progress, the new generation of <code>environmentd</code>
runs in a read-only, un-promoted state and holds back compaction via
read holds. Leaving it in this state for too long can cause
incident-inducing load when it is eventually promoted, so the
operator cancels the rollout once this timeout is exceeded: the new
generation is torn down and the previously-active generation
continues serving. A new rollout can then be triggered by setting
<code>requestRollout</code> to a new value.</p>
<p>This does not apply to the <code>ImmediatelyPromoteCausingDowntime</code>
rollout strategy or to force-promoted rollouts, since by the time
those are in progress the old generation may already be gone.</p>
<p>The value is parsed as a human-readable duration, e.g. <code>24h</code>,
<code>90m</code>, or <code>1h 30m</code>. Defaults to [<code>DEFAULT_ROLLOUT_REQUEST_TIMEOUT</code>]
when omitted (the API server fills it in); an unparseable value also
falls back to that default.</p>
</p>

<p><strong>Default:</strong> <code>24h</code></p></td>
</tr>
<tr>
<td><code>rolloutStrategy</code></td>
<td></td>
<td>
<em><strong>Enum</strong></em>

<p><p>Rollout strategy to use when upgrading this Materialize instance.</p>
<p>Valid values:</p>
<ul>
<li>
<p><code>WaitUntilReady</code> (default):<br>  Create a new generation of pods, leaving the old generation around until the
new ones are ready to take over.
This minimizes downtime, and is what almost everyone should use.</p>
</li>
<li>
<p><code>ManuallyPromote</code>:<br>  Create a new generation of pods, leaving the old generation as the serving generation
until the user manually promotes the new generation.</p>
<p>When using <code>ManuallyPromote</code>, the new generation can be promoted at any
time, even if it has dataflows that are not fully caught up, by setting
<code>forcePromote</code> to the current rollout identifier: in <code>v1</code>, the value of
<code>status.requestedRolloutHash</code>; in <code>v1alpha1</code>, the <code>requestRollout</code> value
in the spec.</p>
<p>To minimize downtime, promotion should occur when the new generation
has caught up to the prior generation. To determine if the new
generation has caught up, consult the <code>UpToDate</code> condition in the
status of the Materialize Resource. If the condition&rsquo;s reason is
<code>ReadyToPromote</code> the new generation is ready to promote.</p>
> **Warning:** Do not leave new generations unpromoted indefinitely.
>   The new generation keeps open read holds which prevent compaction. Once promoted or
>   cancelled, those read holds are released. If left unpromoted for an extended time, this
>   data can build up, and can cause extreme deletion load on the metadata backend database
>   when finally promoted or cancelled.
>   To guard against this, a rollout that remains in progress longer
>   than `rolloutRequestTimeout` (default 24h) is automatically
>   cancelled.

</li>
<li>
<p><code>ImmediatelyPromoteCausingDowntime</code>:<br>  > **Warning:** THIS WILL CAUSE YOUR MATERIALIZE INSTANCE TO BE UNAVAILABLE FOR SOME TIME!!!
>   This strategy should ONLY be used by customers with physical hardware who do not have
>   enough hardware for the `WaitUntilReady` strategy. If you think you want this, please
>   consult with Materialize engineering to discuss your situation.
</p>
<p>Tear down the old generation of pods and promote the new generation of pods immediately,
without waiting for the new generation of pods to be ready.</p>
</li>
</ul>
</p>

<p><strong>Default:</strong> <code>WaitUntilReady</code></p></td>
</tr>
<tr>
<td><code>serviceAccountAnnotations</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p><p>Annotations to apply to the service account.</p>
<p>Annotations on service accounts are commonly used by cloud providers for IAM.
AWS uses &ldquo;eks.amazonaws.com/role-arn&rdquo;.
Azure uses &ldquo;azure.workload.identity/client-id&rdquo;, but
additionally requires &ldquo;azure.workload.identity/use&rdquo;: &ldquo;true&rdquo; on the pods.</p>
</p>

</td>
</tr>
<tr>
<td><code>serviceAccountLabels</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Labels to apply to the service account.</p>

</td>
</tr>
<tr>
<td><code>serviceAccountName</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Name of the kubernetes service account to use.
If not set, we will create one with the same name as this Materialize object.</p>

</td>
</tr>
<tr>
<td><code>systemParameterConfigmapName</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p><p>The name of a ConfigMap containing system parameters in JSON format.
The ConfigMap must contain a <code>system-params.json</code> key whose value
is a valid JSON object containing valid system parameters.</p>
<p>Run <code>SHOW ALL</code> in SQL to see a subset of configurable system parameters.</p>
<p>Example ConfigMap:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-yaml" data-lang="yaml"><span class="line"><span class="cl"><span class="nt">data</span><span class="p">:</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">system-params.json</span><span class="p">:</span><span class="w"> </span><span class="p">|</span><span class="sd">
</span></span></span><span class="line"><span class="cl"><span class="sd">    {
</span></span></span><span class="line"><span class="cl"><span class="sd">      &#34;max_connections&#34;: 1000
</span></span></span><span class="line"><span class="cl"><span class="sd">    }</span><span class="w">
</span></span></span></code></pre></div></p>

</td>
</tr>
</tbody>
</table>

#### MaterializeCertSpec
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>dnsNames</code></td>
<td></td>
<td>
<em><strong>Array&lt;String&gt;</strong></em>

<p>Additional DNS names the certificate will be valid for.</p>

</td>
</tr>
<tr>
<td><code>duration</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Duration the certificate will be requested for.
Value must be in units accepted by Go
<a href="https://golang.org/pkg/time/#ParseDuration" ><code>time.ParseDuration</code></a>.</p>

</td>
</tr>
<tr>
<td><code>issuerRef</code></td>
<td></td>
<td>
<em><strong><a href='#certificateissuerref'>CertificateIssuerRef</a></strong></em>

<p>Reference to an <code>Issuer</code> or <code>ClusterIssuer</code> that will generate the certificate.</p>

</td>
</tr>
<tr>
<td><code>privateKeyAlgorithm</code></td>
<td></td>
<td>
<em><strong>CertificatePrivateKeyAlgorithm</strong></em>

<p>Optional algorithm to use for the private key. If not specified, a recommended default will be chosen.</p>

</td>
</tr>
<tr>
<td><code>privateKeySize</code></td>
<td></td>
<td>
<em><strong>Integer</strong></em>

<p>Optional size for the private key.</p>

</td>
</tr>
<tr>
<td><code>renewBefore</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Duration before expiration the certificate will be renewed.
Value must be in units accepted by Go
<a href="https://golang.org/pkg/time/#ParseDuration" ><code>time.ParseDuration</code></a>.</p>

</td>
</tr>
<tr>
<td><code>secretTemplate</code></td>
<td></td>
<td>
<em><strong><a href='#certificatesecrettemplate'>CertificateSecretTemplate</a></strong></em>

<p>Additional annotations and labels to include in the Certificate object.</p>

</td>
</tr>
</tbody>
</table>

#### CertificateSecretTemplate
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>annotations</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Annotations is a key value map to be copied to the target Kubernetes Secret.</p>

</td>
</tr>
<tr>
<td><code>labels</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, String&gt;</strong></em>

<p>Labels is a key value map to be copied to the target Kubernetes Secret.</p>

</td>
</tr>
</tbody>
</table>

#### CertificateIssuerRef
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name of the resource being referred to.</p>

</td>
</tr>
<tr>
<td><code>group</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Group of the resource being referred to.</p>

</td>
</tr>
<tr>
<td><code>kind</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Kind of the resource being referred to.</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ResourceRequirements
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>claims</code></td>
<td></td>
<td>
<em><strong>Array&lt;<a href='#iok8sapicorev1resourceclaim'>io.k8s.api.core.v1.ResourceClaim</a>&gt;</strong></em>

<p><p>Claims lists the names of resources, defined in spec.resourceClaims, that are used by this container.</p>
<p>This field depends on the DynamicResourceAllocation feature gate.</p>
<p>This field is immutable. It can only be set for containers.</p>
</p>

</td>
</tr>
<tr>
<td><code>limits</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, io.k8s.apimachinery.pkg.api.resource.Quantity&gt;</strong></em>

<p>Limits describes the maximum amount of compute resources allowed. More info: <a href="https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/" >https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/</a></p>

</td>
</tr>
<tr>
<td><code>requests</code></td>
<td></td>
<td>
<em><strong>Map&lt;String, io.k8s.apimachinery.pkg.api.resource.Quantity&gt;</strong></em>

<p>Requests describes the minimum amount of compute resources required. If Requests is omitted for a container, it defaults to Limits if that is explicitly specified, otherwise to an implementation-defined value. Requests cannot exceed Limits. More info: <a href="https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/" >https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/</a></p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ResourceClaim
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name must match the name of one entry in pod.spec.resourceClaims of the Pod where this field is used. It makes that resource available inside a container.</p>

</td>
</tr>
<tr>
<td><code>request</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Request is the name chosen for a request in the referenced claim. If empty, everything from the claim is made available, otherwise only the result of this request.</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.EnvVar
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name of the environment variable. May consist of any printable ASCII characters except &lsquo;=&rsquo;.</p>

</td>
</tr>
<tr>
<td><code>value</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Variable references $(VAR_NAME) are expanded using the previously defined environment variables in the container and any service environment variables. If a variable cannot be resolved, the reference in the input string will be unchanged. Double $$ are reduced to a single $, which allows for escaping the $(VAR_NAME) syntax: i.e. &ldquo;$$(VAR_NAME)&rdquo; will produce the string literal &ldquo;$(VAR_NAME)&rdquo;. Escaped references will never be expanded, regardless of whether the variable exists or not. Defaults to &ldquo;&rdquo;.</p>

</td>
</tr>
<tr>
<td><code>valueFrom</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1envvarsource'>io.k8s.api.core.v1.EnvVarSource</a></strong></em>

<p>Source for the environment variable&rsquo;s value. Cannot be used if value is not empty.</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.EnvVarSource
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>configMapKeyRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1configmapkeyselector'>io.k8s.api.core.v1.ConfigMapKeySelector</a></strong></em>

<p>Selects a key of a ConfigMap.</p>

</td>
</tr>
<tr>
<td><code>fieldRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1objectfieldselector'>io.k8s.api.core.v1.ObjectFieldSelector</a></strong></em>

<p>Selects a field of the pod: supports metadata.name, metadata.namespace, <code>metadata.labels['&lt;KEY&gt;']</code>, <code>metadata.annotations['&lt;KEY&gt;']</code>, spec.nodeName, spec.serviceAccountName, status.hostIP, status.podIP, status.podIPs.</p>

</td>
</tr>
<tr>
<td><code>fileKeyRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1filekeyselector'>io.k8s.api.core.v1.FileKeySelector</a></strong></em>

<p>FileKeyRef selects a key of the env file. Requires the EnvFiles feature gate to be enabled.</p>

</td>
</tr>
<tr>
<td><code>resourceFieldRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1resourcefieldselector'>io.k8s.api.core.v1.ResourceFieldSelector</a></strong></em>

<p>Selects a resource of the container: only resources limits and requests (limits.cpu, limits.memory, limits.ephemeral-storage, requests.cpu, requests.memory and requests.ephemeral-storage) are currently supported.</p>

</td>
</tr>
<tr>
<td><code>secretKeyRef</code></td>
<td></td>
<td>
<em><strong><a href='#iok8sapicorev1secretkeyselector'>io.k8s.api.core.v1.SecretKeySelector</a></strong></em>

<p>Selects a key of a secret in the pod&rsquo;s namespace</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.SecretKeySelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>key</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The key of the secret to select from.  Must be a valid secret key.</p>

</td>
</tr>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name of the referent. This field is effectively required, but due to backwards compatibility is allowed to be empty. Instances of this type with an empty value here are almost certainly wrong. More info: <a href="https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names" >https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names</a></p>

</td>
</tr>
<tr>
<td><code>optional</code></td>
<td></td>
<td>
<em><strong>Bool</strong></em>

<p>Specify whether the Secret or its key must be defined</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ResourceFieldSelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>resource</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Required: resource to select</p>

</td>
</tr>
<tr>
<td><code>containerName</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Container name: required for volumes, optional for env vars</p>

</td>
</tr>
<tr>
<td><code>divisor</code></td>
<td></td>
<td>
<em><strong>io.k8s.apimachinery.pkg.api.resource.Quantity</strong></em>

<p>Specifies the output format of the exposed resources, defaults to &ldquo;1&rdquo;</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.FileKeySelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>key</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The key within the env file. An invalid key will prevent the pod from starting. The keys defined within a source may consist of any printable ASCII characters except &lsquo;=&rsquo;. During Alpha stage of the EnvFiles feature gate, the key size is limited to 128 characters.</p>

</td>
</tr>
<tr>
<td><code>path</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The path within the volume from which to select the file. Must be relative and may not contain the &lsquo;..&rsquo; path or start with &lsquo;..&rsquo;.</p>

</td>
</tr>
<tr>
<td><code>volumeName</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The name of the volume mount containing the env file.</p>

</td>
</tr>
<tr>
<td><code>optional</code></td>
<td></td>
<td>
<em><strong>Bool</strong></em>

<p><p>Specify whether the file or its key must be defined. If the file or key does not exist, then the env var is not published. If optional is set to true and the specified key does not exist, the environment variable will not be set in the Pod&rsquo;s containers.</p>
<p>If optional is set to false and the specified key does not exist, an error will be returned during Pod creation.</p>
</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ObjectFieldSelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>fieldPath</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Path of the field to select in the specified API version.</p>

</td>
</tr>
<tr>
<td><code>apiVersion</code></td>
<td></td>
<td>
<em><strong>String</strong></em>

<p>Version of the schema the FieldPath is written in terms of, defaults to &ldquo;v1&rdquo;.</p>

</td>
</tr>
</tbody>
</table>

#### io.k8s.api.core.v1.ConfigMapKeySelector
<table>
<thead>
<tr>
<th>Field Name</th>
<th>Required</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>key</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>The key to select.</p>

</td>
</tr>
<tr>
<td><code>name</code></td>
<td>✅</td>
<td>
<em><strong>String</strong></em>

<p>Name of the referent. This field is effectively required, but due to backwards compatibility is allowed to be empty. Instances of this type with an empty value here are almost certainly wrong. More info: <a href="https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names" >https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names</a></p>

</td>
</tr>
<tr>
<td><code>optional</code></td>
<td></td>
<td>
<em><strong>Bool</strong></em>

<p>Specify whether the ConfigMap or its key must be defined</p>

</td>
</tr>
</tbody>
</table>


<!-- mz-docs page: self-managed-deployments/operator-configuration -->

# Materialize Operator Configuration
Configuration reference for the Materialize Operator Helm chart
## Configure the Materialize operator

To configure the Materialize operator, you can:

- Use a configuration YAML file (e.g., `values.yaml`) that specifies the
  configuration values and then install the chart with the `-f` flag:

  ```shell
  # Assumes you have added the Materialize operator Helm chart repository
  helm install my-materialize-operator materialize/materialize-operator \
     -f /path/to/your/config/values.yaml
  ```

- Specify each parameter using the `--set key=value[,key=value]` argument to
  `helm install`. For example:

  ```shell
  # Assumes you have added the Materialize operator Helm chart repository
  helm install my-materialize-operator materialize/materialize-operator  \
    --set observability.podMetrics.enabled=true
  ```

<table>
<thead>
<tr>
<th>Parameter</th>
<th>Default</th>

</tr>
</thead>
<tbody>

<tr>
<td><a href='#balancerdaffinity'><code>balancerd.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#balancerddefaultresourceslimits'><code>balancerd.defaultResources.limits</code></a></td>
<td>
<code>{&quot;memory&quot;:&quot;256Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#balancerddefaultresourcesrequests'><code>balancerd.defaultResources.requests</code></a></td>
<td>
<code>{&quot;cpu&quot;:&quot;500m&quot;,&quot;memory&quot;:&quot;256Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#balancerdenabled'><code>balancerd.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#balancerdnodeselector'><code>balancerd.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#balancerdtolerations'><code>balancerd.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdaffinity'><code>clusterd.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdnodeselector'><code>clusterd.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdpriorityclassname'><code>clusterd.priorityClassName</code></a></td>
<td>
<code>nil</code>
</td>
</tr>

<tr>
<td><a href='#clusterdscratchfsnodeselector'><code>clusterd.scratchfsNodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdswapnodeselector'><code>clusterd.swapNodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdtolerations'><code>clusterd.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#consoleaffinity'><code>console.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#consoledefaultresourceslimits'><code>console.defaultResources.limits</code></a></td>
<td>
<code>{&quot;memory&quot;:&quot;256Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#consoledefaultresourcesrequests'><code>console.defaultResources.requests</code></a></td>
<td>
<code>{&quot;cpu&quot;:&quot;500m&quot;,&quot;memory&quot;:&quot;256Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#consoleenabled'><code>console.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#consoleimagetagmapoverride'><code>console.imageTagMapOverride</code></a></td>
<td>
<code>{}</code>
</td>
</tr>

<tr>
<td><a href='#consolenodeselector'><code>console.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#consoletolerations'><code>console.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#environmentdaffinity'><code>environmentd.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#environmentddefaultresourceslimits'><code>environmentd.defaultResources.limits</code></a></td>
<td>
<code>{&quot;memory&quot;:&quot;4Gi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#environmentddefaultresourcesrequests'><code>environmentd.defaultResources.requests</code></a></td>
<td>
<code>{&quot;cpu&quot;:&quot;1&quot;,&quot;memory&quot;:&quot;4095Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#environmentdnodeselector'><code>environmentd.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#environmentdpriorityclassname'><code>environmentd.priorityClassName</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#environmentdtolerations'><code>environmentd.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#networkpoliciesegresscidrs'><code>networkPolicies.egress.cidrs</code></a></td>
<td>
<code>[&quot;0.0.0.0/0&quot;]</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesegressenabled'><code>networkPolicies.egress.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesenabled'><code>networkPolicies.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesingresscidrs'><code>networkPolicies.ingress.cidrs</code></a></td>
<td>
<code>[&quot;0.0.0.0/0&quot;]</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesingressenabled'><code>networkPolicies.ingress.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesinternalenabled'><code>networkPolicies.internal.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#observabilityenabled'><code>observability.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#observabilitypodmetricsenabled'><code>observability.podMetrics.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#observabilityprometheusscrapeannotationsenabled'><code>observability.prometheus.scrapeAnnotations.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#operatoradditionalmaterializecrdcolumns'><code>operator.additionalMaterializeCRDColumns</code></a></td>
<td>
<code>{}</code>
</td>
</tr>

<tr>
<td><a href='#operatoraffinity'><code>operator.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#operatorargsenableinternalstatementlogging'><code>operator.args.enableInternalStatementLogging</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#operatorargsenablelicensekeychecks'><code>operator.args.enableLicenseKeyChecks</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#operatorargsinstallv1crd'><code>operator.args.installV1CRD</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#operatorargsstartuplogfilter'><code>operator.args.startupLogFilter</code></a></td>
<td>
<code>&quot;INFO,mz_orchestratord=TRACE&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorargsstatementloggingmaxsamplerate'><code>operator.args.statementLoggingMaxSampleRate</code></a></td>
<td>
<code>0.99</code>
</td>
</tr>

<tr>
<td><a href='#operatorargsstatementloggingtargetdatarate'><code>operator.args.statementLoggingTargetDataRate</code></a></td>
<td>
<code>nil</code>
</td>
</tr>

<tr>
<td><a href='#operatorargswebhookcertreloadinterval'><code>operator.args.webhookCertReloadInterval</code></a></td>
<td>
<code>nil</code>
</td>
</tr>

<tr>
<td><a href='#operatorcertificatecaduration'><code>operator.certificate.caDuration</code></a></td>
<td>
<code>&quot;87600h&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcertificatecarenewbefore'><code>operator.certificate.caRenewBefore</code></a></td>
<td>
<code>&quot;8760h&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcertificatesecretname'><code>operator.certificate.secretName</code></a></td>
<td>
<code>nil</code>
</td>
</tr>

<tr>
<td><a href='#operatorcertificatesource'><code>operator.certificate.source</code></a></td>
<td>
<code>&quot;cert-manager&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersawsaccountid'><code>operator.cloudProvider.providers.aws.accountID</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersawsenabled'><code>operator.cloudProvider.providers.aws.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersawsiamrolesconnection'><code>operator.cloudProvider.providers.aws.iam.roles.connection</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersawsiamrolesenvironment'><code>operator.cloudProvider.providers.aws.iam.roles.environment</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcp'><code>operator.cloudProvider.providers.gcp</code></a></td>
<td>
<code>{&quot;enabled&quot;:false,&quot;nodeUpgradeRolloutTrigger&quot;:{&quot;clusterLocation&quot;:&quot;&quot;,&quot;clusterName&quot;:&quot;&quot;,&quot;enabled&quot;:false,&quot;notificationSubscription&quot;:&quot;&quot;,&quot;watchedNodePools&quot;:[]}}</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcpnodeupgraderollouttriggerclusterlocation'><code>operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.clusterLocation</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcpnodeupgraderollouttriggerclustername'><code>operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.clusterName</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcpnodeupgraderollouttriggernotificationsubscription'><code>operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.notificationSubscription</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcpnodeupgraderollouttriggerwatchednodepools'><code>operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.watchedNodePools</code></a></td>
<td>
<code>[]</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderregion'><code>operator.cloudProvider.region</code></a></td>
<td>
<code>&quot;kind&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudprovidertype'><code>operator.cloudProvider.type</code></a></td>
<td>
<code>&quot;local&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultreplicationfactoranalytics'><code>operator.clusters.defaultReplicationFactor.analytics</code></a></td>
<td>
<code>0</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultreplicationfactorprobe'><code>operator.clusters.defaultReplicationFactor.probe</code></a></td>
<td>
<code>0</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultreplicationfactorsupport'><code>operator.clusters.defaultReplicationFactor.support</code></a></td>
<td>
<code>0</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultreplicationfactorsystem'><code>operator.clusters.defaultReplicationFactor.system</code></a></td>
<td>
<code>0</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizesanalytics'><code>operator.clusters.defaultSizes.analytics</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizescatalogserver'><code>operator.clusters.defaultSizes.catalogServer</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizesdefault'><code>operator.clusters.defaultSizes.default</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizesprobe'><code>operator.clusters.defaultSizes.probe</code></a></td>
<td>
<code>&quot;mz_probe&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizessupport'><code>operator.clusters.defaultSizes.support</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizessystem'><code>operator.clusters.defaultSizes.system</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersswap_enabled'><code>operator.clusters.swap_enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#operatorimagepullpolicy'><code>operator.image.pullPolicy</code></a></td>
<td>
<code>&quot;IfNotPresent&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorimagerepository'><code>operator.image.repository</code></a></td>
<td>
<code>&quot;materialize/orchestratord&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorimagetag'><code>operator.image.tag</code></a></td>
<td>
<code>&quot;v26.43.0&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatornodeselector'><code>operator.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#operatorpoddisruptionbudgetenabled'><code>operator.podDisruptionBudget.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#operatorpoddisruptionbudgetmaxunavailable'><code>operator.podDisruptionBudget.maxUnavailable</code></a></td>
<td>
<code>1</code>
</td>
</tr>

<tr>
<td><a href='#operatorreplicas'><code>operator.replicas</code></a></td>
<td>
<code>2</code>
</td>
</tr>

<tr>
<td><a href='#operatorresourceslimits'><code>operator.resources.limits</code></a></td>
<td>
<code>{&quot;memory&quot;:&quot;512Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#operatorresourcesrequests'><code>operator.resources.requests</code></a></td>
<td>
<code>{&quot;cpu&quot;:&quot;100m&quot;,&quot;memory&quot;:&quot;512Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#operatorsecretscontroller'><code>operator.secretsController</code></a></td>
<td>
<code>&quot;kubernetes&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatortolerations'><code>operator.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#rbaccreate'><code>rbac.create</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#schedulername'><code>schedulerName</code></a></td>
<td>
<code>nil</code>
</td>
</tr>

<tr>
<td><a href='#serviceaccountannotations'><code>serviceAccount.annotations</code></a></td>
<td>
<code>{}</code>
</td>
</tr>

<tr>
<td><a href='#serviceaccountcreate'><code>serviceAccount.create</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#serviceaccountname'><code>serviceAccount.name</code></a></td>
<td>
<code>&quot;orchestratord&quot;</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassallowvolumeexpansion'><code>storage.storageClass.allowVolumeExpansion</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclasscreate'><code>storage.storageClass.create</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassname'><code>storage.storageClass.name</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassparameters'><code>storage.storageClass.parameters</code></a></td>
<td>
<code>{&quot;fsType&quot;:&quot;ext4&quot;,&quot;storage&quot;:&quot;lvm&quot;,&quot;volgroup&quot;:&quot;instance-store-vg&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassprovisioner'><code>storage.storageClass.provisioner</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassreclaimpolicy'><code>storage.storageClass.reclaimPolicy</code></a></td>
<td>
<code>&quot;Delete&quot;</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassvolumebindingmode'><code>storage.storageClass.volumeBindingMode</code></a></td>
<td>
<code>&quot;WaitForFirstConsumer&quot;</code>
</td>
</tr>

<tr>
<td><a href='#telemetryenabled'><code>telemetry.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#telemetrysegmentapikey'><code>telemetry.segmentApiKey</code></a></td>
<td>
<code>&quot;hMWi3sZ17KFMjn2sPWo9UJGpOQqiba4A&quot;</code>
</td>
</tr>

<tr>
<td><a href='#telemetrysegmentclientside'><code>telemetry.segmentClientSide</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#tlsdefaultcertificatespecs'><code>tls.defaultCertificateSpecs</code></a></td>
<td>
<code>{}</code>
</td>
</tr>

</tbody>
</table>

## Parameters

### `balancerd` parameters

#### balancerd.affinity

**Default**: 

Affinity to use for balancerd pods spawned by the operator

#### balancerd.defaultResources.limits

**Default**: <code>{&quot;memory&quot;:&quot;256Mi&quot;}</code>

Default resource limits for balancerd&rsquo;s CPU and memory if not set in the Materialize CR

#### balancerd.defaultResources.requests

**Default**: <code>{&quot;cpu&quot;:&quot;500m&quot;,&quot;memory&quot;:&quot;256Mi&quot;}</code>

Default resources requested for balancerd&rsquo;s CPU and memory if not set in the Materialize CR

#### balancerd.enabled

**Default**: <code>true</code>

Flag to indicate whether to create balancerd pods for the environments

#### balancerd.nodeSelector

**Default**: 

Node selector to use for balancerd pods spawned by the operator

#### balancerd.tolerations

**Default**: 

Tolerations to use for balancerd pods spawned by the operator

### `clusterd` parameters

#### clusterd.affinity

**Default**: 

Affinity to use for clusterd pods spawned by the operator

#### clusterd.nodeSelector

**Default**: 

Node selector to use for all clusterd pods spawned by the operator

#### clusterd.priorityClassName

**Default**: <code>nil</code>

PriorityClass to use for clusterd pods spawned by the operator. The PriorityClass must already exist. Kubernetes rejects a pod that names one it cannot resolve, so a typo here stops these pods being created at all.

#### clusterd.scratchfsNodeSelector

**Default**: 

Additional node selector to use for clusterd pods when using an LVM scratch disk. This will be merged with the values in <code>nodeSelector</code>.

#### clusterd.swapNodeSelector

**Default**: 

Additional node selector to use for clusterd pods when using swap. This will be merged with the values in <code>nodeSelector</code>.

#### clusterd.tolerations

**Default**: 

Tolerations to use for clusterd pods spawned by the operator

### `console` parameters

#### console.affinity

**Default**: 

Affinity to use for console pods spawned by the operator

#### console.defaultResources.limits

**Default**: <code>{&quot;memory&quot;:&quot;256Mi&quot;}</code>

Default resource limits for the console&rsquo;s CPU and memory if not set in the Materialize CR

#### console.defaultResources.requests

**Default**: <code>{&quot;cpu&quot;:&quot;500m&quot;,&quot;memory&quot;:&quot;256Mi&quot;}</code>

Default resources requested for the console&rsquo;s CPU and memory if not set in the Materialize CR

#### console.enabled

**Default**: <code>true</code>

Flag to indicate whether to create console pods for the environments

#### console.imageTagMapOverride

**Default**: <code>{}</code>

Override the mapping of environmentd versions to console versions

#### console.nodeSelector

**Default**: 

Node selector to use for console pods spawned by the operator

#### console.tolerations

**Default**: 

Tolerations to use for console pods spawned by the operator

### `environmentd` parameters

#### environmentd.affinity

**Default**: 

Affinity to use for environmentd pods spawned by the operator

#### environmentd.defaultResources.limits

**Default**: <code>{&quot;memory&quot;:&quot;4Gi&quot;}</code>

Default resource limits for environmentd&rsquo;s CPU and memory if not set in the Materialize CR

#### environmentd.defaultResources.requests

**Default**: <code>{&quot;cpu&quot;:&quot;1&quot;,&quot;memory&quot;:&quot;4095Mi&quot;}</code>

Default resources requested for environmentd&rsquo;s CPU and memory if not set in the Materialize CR

#### environmentd.nodeSelector

**Default**: 

Node selector to use for environmentd pods spawned by the operator

#### environmentd.priorityClassName

**Default**: <code>&quot;&quot;</code>

PriorityClass to use for environmentd pods spawned by the operator. The PriorityClass must already exist. Kubernetes rejects a pod that names one it cannot resolve, so a typo here stops these pods being created at all.

#### environmentd.tolerations

**Default**: 

Tolerations to use for environmentd pods spawned by the operator

### `networkPolicies` parameters

#### networkPolicies.egress.cidrs

**Default**: <code>[&quot;0.0.0.0/0&quot;]</code>

CIDR blocks to allow egress to

#### networkPolicies.egress.enabled

**Default**: <code>false</code>

Whether to enable egress network policies to sources and sinks

#### networkPolicies.enabled

**Default**: <code>false</code>

Whether to enable network policies for securing communication between pods

#### networkPolicies.ingress.cidrs

**Default**: <code>[&quot;0.0.0.0/0&quot;]</code>

CIDR blocks to allow ingress from

#### networkPolicies.ingress.enabled

**Default**: <code>false</code>

Whether to enable ingress network policies to the SQL and HTTP interfaces on environmentd and balancerd

#### networkPolicies.internal.enabled

**Default**: <code>false</code>

Whether to enable network policies for internal communication between Materialize pods

### `observability` parameters

#### observability.enabled

**Default**: <code>true</code>

Whether to enable observability features

#### observability.podMetrics.enabled

**Default**: <code>false</code>

Whether to enable the pod metrics scraper which populates the Environment Overview Monitoring tab in the web console (requires metrics-server to be installed)

#### observability.prometheus.scrapeAnnotations.enabled

**Default**: <code>true</code>

Whether to annotate pods with common keys used for prometheus scraping.

### `operator` parameters

#### operator.additionalMaterializeCRDColumns

**Default**: <code>{}</code>

Additional columns to display when printing the Materialize CRD in table format.

#### operator.affinity

**Default**: 

Affinity to use for the operator pod

#### operator.args.enableInternalStatementLogging

**Default**: <code>true</code>

#### operator.args.enableLicenseKeyChecks

**Default**: <code>false</code>

#### operator.args.installV1CRD

**Default**: <code>false</code>

Whether to install the v1 version of the Materialize CRD and the conversion webhook that converts between v1 and v1alpha1. When false, only the v1alpha1 CRD version is installed and no webhook serving certificate or service is created.

#### operator.args.startupLogFilter

**Default**: <code>&quot;INFO,mz_orchestratord=TRACE&quot;</code>

Log filtering settings for startup logs

#### operator.args.statementLoggingMaxSampleRate

**Default**: <code>0.99</code>

Caps the fraction of statements recorded in query history, via environmentd&rsquo;s <code>statement_logging_max_sample_rate</code>. This is the rate Materialize Cloud runs at. Sampling costs CPU on environmentd, but the volume written is bounded by <code>statementLoggingTargetDataRate</code> rather than by this, so lowering this gives up query history completeness without lowering the ceiling on what statement logging stores. Set it to <code>0</code> to disable statement logging entirely, or to <code>null</code> to inherit environmentd&rsquo;s default.

#### operator.args.statementLoggingTargetDataRate

**Default**: <code>nil</code>

Caps the sustained volume statement logging writes, in bytes per second, via environmentd&rsquo;s <code>statement_logging_target_data_rate</code>. This is what actually bounds how fast query history grows, and the recorded history is retained for the lifetime of the environment, so lower it on environments with limited storage. Must be greater than 0. Set it to <code>null</code> to inherit environmentd&rsquo;s default of 2071 bytes per second, which is the rate Materialize Cloud runs at.

#### operator.args.webhookCertReloadInterval

**Default**: <code>nil</code>

How often orchestratord reloads its webhook TLS certificate from disk and, when the CA changes, refreshes the conversion webhook&rsquo;s CA bundle. Must be shorter than the certificate&rsquo;s lifetime. Accepts a humantime duration (e.g. &ldquo;1h&rdquo;, &ldquo;30m&rdquo;). Leave null to use the binary default. Only used if <code>installV1CRD</code> is true.

#### operator.certificate.caDuration

**Default**: <code>&quot;87600h&quot;</code>

Lifetime of the root CA that signs the webhook serving certificate, when <code>source</code> is &ldquo;cert-manager&rdquo;. The serving certificate is signed by this CA, so the CA outlives individual serving-certificate rotations.

#### operator.certificate.caRenewBefore

**Default**: <code>&quot;8760h&quot;</code>

How long before the root CA expires to renew it. Must be less than <code>caDuration</code>.

#### operator.certificate.secretName

**Default**: <code>nil</code>

Name of a secret in the operator&rsquo;s namespace containing ca.crt, tls.crt, and tls.key entries. Only used if <code>source</code> is &ldquo;secret&rdquo;.

#### operator.certificate.source

**Default**: <code>&quot;cert-manager&quot;</code>

Where to obtain the certificate for orchestratord. Valid values are &lsquo;cert-manager&rsquo; and &lsquo;secret&rsquo;. Only used if <code>operator.args.installV1CRD</code> is true.

#### operator.cloudProvider.providers.aws.accountID

**Default**: <code>&quot;&quot;</code>

When using AWS, accountID is required

#### operator.cloudProvider.providers.aws.enabled

**Default**: <code>false</code>

#### operator.cloudProvider.providers.aws.iam.roles.connection

**Default**: <code>&quot;&quot;</code>

ARN for CREATE CONNECTION feature

#### operator.cloudProvider.providers.aws.iam.roles.environment

**Default**: <code>&quot;&quot;</code>

ARN of the IAM role for environmentd

#### operator.cloudProvider.providers.gcp

**Default**: <code>{&quot;enabled&quot;:false,&quot;nodeUpgradeRolloutTrigger&quot;:{&quot;clusterLocation&quot;:&quot;&quot;,&quot;clusterName&quot;:&quot;&quot;,&quot;enabled&quot;:false,&quot;notificationSubscription&quot;:&quot;&quot;,&quot;watchedNodePools&quot;:[]}}</code>

GCP Configuration

#### operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.clusterLocation

**Default**: <code>&quot;&quot;</code>

The location (region or zone) of the GKE cluster.

#### operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.clusterName

**Default**: <code>&quot;&quot;</code>

The name of the GKE cluster.

#### operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.notificationSubscription

**Default**: <code>&quot;&quot;</code>

The Pub/Sub subscription receiving GKE cluster notifications for this cluster, in <code>projects/{project}/subscriptions/{subscription}</code> form. The cluster must be configured to publish upgrade notifications to the corresponding topic, and the operator&rsquo;s service account must be able to subscribe to it and to read the cluster&rsquo;s node pools.

#### operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.watchedNodePools

**Default**: <code>[]</code>

The node pools to watch. An empty list watches all node pools.

#### operator.cloudProvider.region

**Default**: <code>&quot;kind&quot;</code>

Common cloud provider settings

#### operator.cloudProvider.type

**Default**: <code>&quot;local&quot;</code>

Specifies cloud provider. Valid values are &lsquo;aws&rsquo;, &lsquo;gcp&rsquo;, &lsquo;azure&rsquo; , &lsquo;generic&rsquo;, or &rsquo;local&rsquo;

#### operator.clusters.defaultReplicationFactor.analytics

**Default**: <code>0</code>

#### operator.clusters.defaultReplicationFactor.probe

**Default**: <code>0</code>

#### operator.clusters.defaultReplicationFactor.support

**Default**: <code>0</code>

#### operator.clusters.defaultReplicationFactor.system

**Default**: <code>0</code>

#### operator.clusters.defaultSizes.analytics

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.defaultSizes.catalogServer

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.defaultSizes.default

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.defaultSizes.probe

**Default**: <code>&quot;mz_probe&quot;</code>

#### operator.clusters.defaultSizes.support

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.defaultSizes.system

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.swap_enabled

**Default**: <code>true</code>

Configure sizes such that the pod QoS class is not Guaranteed, as is required for swap to be enabled. Disk doesn&rsquo;t make much sense with swap, as swap performs better than lgalloc, so it also gets disabled.

#### operator.image.pullPolicy

**Default**: <code>&quot;IfNotPresent&quot;</code>

Policy for pulling the image: &ldquo;IfNotPresent&rdquo; avoids unnecessary re-pulling of images

#### operator.image.repository

**Default**: <code>&quot;materialize/orchestratord&quot;</code>

The Docker repository for the operator image

#### operator.image.tag

**Default**: <code>&quot;v26.43.0&quot;</code>

The tag/version of the operator image to be used

#### operator.nodeSelector

**Default**: 

Node selector to use for the operator pod

#### operator.podDisruptionBudget.enabled

**Default**: <code>true</code>

Whether to create a PodDisruptionBudget for the operator. Only created when <code>replicas</code> is greater than 1, since a budget over a single replica either blocks node drains or protects nothing.

#### operator.podDisruptionBudget.maxUnavailable

**Default**: <code>1</code>

Maximum number of operator pods that may be unavailable at once during voluntary disruptions. Expressed as a maximum rather than a minimum so that node drains are never blocked outright, they are only serialized.

#### operator.replicas

**Default**: <code>2</code>

Number of operator replicas. The operator uses leader election so that only one replica reconciles at a time. Running more than one replica avoids downtime of the CRD conversion webhook during rollouts and node drains.

#### operator.resources.limits

**Default**: <code>{&quot;memory&quot;:&quot;512Mi&quot;}</code>

Resource limits for the operator&rsquo;s CPU and memory

#### operator.resources.requests

**Default**: <code>{&quot;cpu&quot;:&quot;100m&quot;,&quot;memory&quot;:&quot;512Mi&quot;}</code>

Resources requested by the operator for CPU and memory

#### operator.secretsController

**Default**: <code>&quot;kubernetes&quot;</code>

Which secrets controller to use for storing secrets. Valid values are &lsquo;kubernetes&rsquo; and &lsquo;aws-secrets-manager&rsquo;. Setting &lsquo;aws-secrets-manager&rsquo; requires a configured AWS cloud provider and IAM role for the environment with Secrets Manager permissions.

#### operator.tolerations

**Default**: 

Tolerations to use for the operator pod

### `rbac` parameters

#### rbac.create

**Default**: <code>true</code>

Whether to create necessary RBAC roles and bindings

### `schedulerName` parameters

#### schedulerName

**Default**: <code>nil</code>

Optionally use a non-default kubernetes scheduler.

### `serviceAccount` parameters

#### serviceAccount.annotations

**Default**: <code>{}</code>

Annotations to add to the service account, e.g. <code>iam.gke.io/gcp-service-account</code> to link it to a GCP service account via workload identity.

#### serviceAccount.create

**Default**: <code>true</code>

Whether to create a new service account for the operator

#### serviceAccount.name

**Default**: <code>&quot;orchestratord&quot;</code>

The name of the service account to be created

### `storage` parameters

#### storage.storageClass.allowVolumeExpansion

**Default**: <code>false</code>

#### storage.storageClass.create

**Default**: <code>false</code>

Set to false to use an existing StorageClass instead. Refer to the <a href="https://kubernetes.io/docs/concepts/storage/storage-classes/" >Kubernetes StorageClass documentation</a>

#### storage.storageClass.name

**Default**: <code>&quot;&quot;</code>

Name of the StorageClass to create/use: eg &ldquo;openebs-lvm-instance-store-ext4&rdquo;

#### storage.storageClass.parameters

**Default**: <code>{&quot;fsType&quot;:&quot;ext4&quot;,&quot;storage&quot;:&quot;lvm&quot;,&quot;volgroup&quot;:&quot;instance-store-vg&quot;}</code>

Parameters for the CSI driver

#### storage.storageClass.provisioner

**Default**: <code>&quot;&quot;</code>

CSI driver to use, eg &ldquo;local.csi.openebs.io&rdquo;

#### storage.storageClass.reclaimPolicy

**Default**: <code>&quot;Delete&quot;</code>

#### storage.storageClass.volumeBindingMode

**Default**: <code>&quot;WaitForFirstConsumer&quot;</code>

### `telemetry` parameters

#### telemetry.enabled

**Default**: <code>true</code>

#### telemetry.segmentApiKey

**Default**: <code>&quot;hMWi3sZ17KFMjn2sPWo9UJGpOQqiba4A&quot;</code>

#### telemetry.segmentClientSide

**Default**: <code>true</code>

### `tls` parameters

#### tls.defaultCertificateSpecs

**Default**: <code>{}</code>

## See also

- [Installation](/installation/)
- [Troubleshooting](/installation/troubleshooting/)

<!-- mz-docs page: self-managed-deployments/query-history -->

# Query History
How query history and statement logging are configured in self-managed Materialize deployments
The Materialize Console includes a **Query History** view, under its
[**Monitoring**](/developer-tools/console/monitoring/) section, that lists a sample of the SQL
statements recently issued to your Materialize instance, along with their
duration, status, and the cluster that ran them. Query history is available in
self-managed deployments and is enabled by default in Materialize operator chart
v26.40.0 and later. Earlier chart versions disabled statement logging outright,
and the Query History view stays empty on them.

Query history is backed by *statement logging*: Materialize records a randomly
sampled fraction of statement executions into the system catalog, most visibly
[`mz_recent_activity_log`](/sql/system-catalog/mz_internal/#mz_recent_activity_log),
which covers the last 24 hours. Sampling means the view is a representative
sample of your workload rather than a complete audit log. For a complete record
of DDL, use
[`mz_audit_events`](/sql/system-catalog/mz_catalog/#mz_audit_events)
instead.

To see query history in the Console, connect as a Materialize *superuser* or as
a user granted the [`mz_monitor`
role](/security/appendix/appendix-built-in-roles/#system-catalog-roles).

## Configure statement logging

Two system parameters bound how much query history you collect:

| Parameter | Default | Bounds |
|-----------|---------|--------|
| `statement_logging_max_sample_rate` | `0.99` (set by the chart) | The fraction of executions considered for logging. |
| `statement_logging_target_data_rate` | 2071 (`environmentd`'s own) | The sustained bytes per second written. |

> **Tip:** The Materialize operator Helm chart exposes each parameter as:
> - `operator.args.statementLoggingMaxSampleRate`, which it sets to `0.99`, and
> - `operator.args.statementLoggingTargetDataRate`, which it leaves unset so
> `environmentd`'s default applies.

Statement logging is therefore on by default, sampling nearly every statement up
to that byte rate.

A session can request its own rate with `SET statement_logging_sample_rate`. The
rate that applies to a statement is the smaller of the session's rate and the
system cap, so lowering the cap reduces logging for every session regardless of
what individual sessions ask for.

Sampling is not the only limit, and it is not the one that bounds volume.
Materialize also throttles statement logging to the target byte rate and drops
sampled executions that would exceed it. So a sample rate of `1.0` does not
guarantee every statement is recorded, and on a busy instance the byte rate is
what determines how much history you actually accumulate.

The two parameters are not interchangeable. Lower the data rate to hold storage
growth down. Lowering the sample rate instead makes query history less
representative without lowering the ceiling on what statement logging stores,
because the byte rate is already the binding limit.

> **Note:** The chart also enables `enableInternalStatementLogging`, which logs statements
> run by Materialize's internal users: `mz_system`, `mz_support`, and
> `mz_analytics`. This covers both Materialize's own activity, such as the
> Console's catalog queries, and any session you open as one of those users, and
> it counts toward the cost described below.
> Statements from your own users are always subject to sampling and are unaffected
> by this setting. Logging in through the Console as a normal user is sampled at
> the rates above either way.

Either parameter can be set through the Helm chart or as a system parameter, and
those two paths interact, so read the note on precedence below before picking
one.

### Using the Helm chart

Set either value when installing or upgrading the operator. For example, to
halve how fast query history grows:

```shell
helm upgrade my-materialize-operator materialize/materialize-operator \
  --set operator.args.statementLoggingTargetDataRate=1035
```

Or, in your `values.yaml`:

```yaml
operator:
  args:
    statementLoggingMaxSampleRate: 0.99
    statementLoggingTargetDataRate: 1035
```

Setting `statementLoggingMaxSampleRate` to `0` disables statement logging
entirely. Already-logged statements remain visible until they age out of the
24-hour window. Setting either value to `null` inherits `environmentd`'s own
default, `0.99` for the sample rate and 2071 bytes per second for the data rate.
The data rate must be greater than 0.

The operator passes these values to `environmentd` as the *defaults* for
`statement_logging_max_sample_rate` and
`statement_logging_target_data_rate`, so they only take effect when
`environmentd` restarts. Upgrading the operator does not by itself roll out your Materialize
instances: you also need to request a rollout, as described in [modifying the
custom
resource](/self-managed-deployments/#modifying-the-custom-resource). For the
full list of chart values, see [Materialize Operator
Configuration](/self-managed-deployments/operator-configuration/).

### Using system parameters

Because the chart values are only defaults, you can override either at runtime
without a rollout, through the `system-params.json` ConfigMap described in
[Configuring System
Parameters](/self-managed-deployments/configuration-system-parameters/):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mz-system-params
  namespace: materialize-environment
data:
  system-params.json: |
    {
      "statement_logging_target_data_rate": 1035
    }
```

Or with [`ALTER SYSTEM SET`](/sql/alter-system-set/), connected as the
`mz_system` user:

```mzsql
ALTER SYSTEM SET statement_logging_target_data_rate = 1035;
```

> **Warning:** Setting either parameter to `0` this way turns off statement logging for the
> whole instance, and the Console's Query History view stops recording new
> statements. A sample rate of `0` logs nothing, and a target data rate of `0`
> throttles every statement. Unlike the Helm chart values, these take effect
> immediately and without a rollout, so it is easy to disable query history
> without meaning to.
> The Helm chart rejects a target data rate of `0`, but `ALTER SYSTEM SET` does
> not, so this is the path where that mistake is possible. Setting the target data
> rate to `NULL` is the opposite hazard: it removes throttling altogether rather
> than restoring the default of 2071, leaving nothing to bound how fast query
> history grows.
> To stop logging only your own statements, use `SET
> statement_logging_sample_rate` in your session instead.

> **Note:** A value set through the ConfigMap or `ALTER SYSTEM SET` is stored in the catalog
> and takes precedence over the Helm chart value, which is only a default. While
> such an override is in place, editing the corresponding chart value has no
> effect.
> To go back to the chart-provided value, first remove the parameter from the
> ConfigMap, then run [`ALTER SYSTEM
> RESET`](/sql/alter-system-reset/) for it. Removing it from the ConfigMap alone is
> not enough, because the last synced value remains in the catalog. Resetting it
> while it is still in the ConfigMap is also not enough, because the sync loop
> reapplies it.

To check the values currently in effect:

```mzsql
SHOW statement_logging_max_sample_rate;
SHOW statement_logging_target_data_rate;
```

## Cost of statement logging

Statement logging has two distinct costs, and each is governed by a different
parameter:

- **CPU on `environmentd`**, governed by the sample rate. Every logged execution
  is prepared and written by the control plane, so the overhead scales with your
  statement throughput, not with your data volume. Instances serving many short
  queries pay the most.

- **Storage**, governed by the target data rate. Logged statements, including
  their SQL text, consume space in your blob storage and metadata backend.
  Although `mz_recent_activity_log` only surfaces the last 24 hours, the
  underlying statement history collections are never truncated, so their
  footprint grows for the lifetime of the instance.

That second point is the one to plan around: query history is not a fixed-size
buffer, and its growth rate is set by `statement_logging_target_data_rate`. On
an instance with limited storage, lower that parameter. Reach for the sample
rate only when you want to reduce `environmentd` CPU overhead, and expect less
representative history in exchange.

## See also

- [Console monitoring](/developer-tools/console/monitoring/)
- [`mz_internal` statement logging
  relations](/sql/system-catalog/mz_internal/#mz_recent_activity_log)
- [`ALTER SYSTEM SET`](/sql/alter-system-set/)
- [`ALTER SYSTEM RESET`](/sql/alter-system-reset/)
- [Configuring System
  Parameters](/self-managed-deployments/configuration-system-parameters/)
- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)

<!-- mz-docs page: self-managed-deployments/release-versions -->

# Self-managed release versions
## V26 releases

| Materialize Operator | orchestratord version | environmentd version | Release date | Notes |
| --- | --- | --- | --- | --- |
| v26.43 | v26.43 | v26.43 | 2026-09-24 | See <a href="/releases/#v26430" >v26.43 release notes</a> |
| v26.42 | v26.42 | v26.42 | 2026-09-18 | See <a href="/releases/#v26420" >v26.42 release notes</a> |
| v26.41 | v26.41 | v26.41 | 2026-09-11 | See <a href="/releases/#v26410" >v26.41 release notes</a> |
| v26.40.2 | v26.40.2 | v26.40.2 | 2026-09-08 | See <a href="/releases/#v26402" >v26.40.2 release notes</a> |
| v26.40 | v26.40 | v26.40 | 2026-09-03 | See <a href="/releases/#v26400" >v26.40 release notes</a> |
| v26.39 | v26.39 | v26.39 | 2026-08-27 | See <a href="/releases/#v26390" >v26.39 release notes</a> |
| v26.38.2 | v26.38.2 | v26.38.2 | 2026-08-25 | See <a href="/releases/#v26382" >v26.38.2 release notes</a> |
| v26.38 | v26.38 | v26.38 | 2026-08-20 | See <a href="/releases/#v26382" >v26.38 release notes</a> |
| v26.37 | v26.37 | v26.37 | 2026-08-13 | See <a href="/releases/#v26370" >v26.37 release notes</a> |
| v26.36 | v26.36 | v26.36 | 2026-08-07 | See <a href="/releases/#v26360" >v26.36 release notes</a> |
| v26.35 | v26.35 | v26.35 | 2026-07-30 | See <a href="/releases/#v26350" >v26.35 release notes</a> |
| v26.34.1 | v26.34.1 | v26.34.1 | 2026-07-24 | See <a href="/releases/#v26341" >v26.34.1 release notes</a> |
| v26.34 | v26.34 | v26.34 | 2026-07-21 | See <a href="/releases/#v26340" >v26.34 release notes</a> |
| v26.33 | v26.33 | v26.33 | 2026-07-17 | See <a href="/releases/#v26330" >v26.33 release notes</a> |
| v26.32 | v26.32 | v26.32 | 2026-07-10 | See <a href="/releases/#v26320" >v26.32 release notes</a> |
| v26.31.2 | v26.31.2 | v26.31.2 | 2026-07-08 | See <a href="/releases/#v26312" >v26.31.2 release notes</a> |
| v26.31 | v26.31 | v26.31 | 2026-07-03 | See <a href="/releases/#v26310" >v26.31 release notes</a> |
| v26.30.1 | v26.30.1 | v26.30.1 | 2026-06-26 | See <a href="/releases/#v26301" >v26.30.1 release notes</a> |
| v26.29 | v26.29 | v26.29 | 2026-06-19 | See <a href="/releases/#v26290" >v26.29 release notes</a> |
| v26.28 | v26.28 | v26.28 | 2026-06-12 | See <a href="/releases/#v26280" >v26.28 release notes</a> |
| v26.27 | v26.27 | v26.27 | 2026-06-05 | See <a href="/releases/#v26270" >v26.27 release notes</a> |
| v26.26 | v26.26 | v26.26 | 2026-05-29 | See <a href="/releases/#v26260" >v26.26 release notes</a> |
| v26.24.3 | v26.24.3 | v26.24.3 | 2026-05-20 | See <a href="/releases/#v26243" >v26.24.3 release notes</a> |
| v26.24.2 | v26.24.2 | v26.24.2 | 2026-05-18 | See <a href="/releases/#v26242" >v26.24.2 release notes</a> |
| v26.24.1 | v26.24.1 | v26.24.1 | 2026-05-15 | See <a href="/releases/#v26241" >v26.24.1 release notes</a> |
| v26.24.0 | v26.24.0 | v26.24.0 | 2026-05-15 | See <a href="/releases/#v26241" >v26.24.1 release notes</a> |
| v26.22.0 | v26.22.0 | v26.22.0 | 2026-05-01 | See <a href="/releases/#v26220" >v26.22.0 release notes</a> |
| v26.20.2 | v26.20.2 | v26.20.2 | 2026-04-18 | See <a href="/releases/#v26202" >v26.20.2 release notes</a> |
| v26.20.0 | v26.20.0 | v26.20.0 | 2026-04-17 |  |
| v26.19.0 | v26.19.0 | v26.19.0 | 2026-04-10 | See <a href="/releases/#v26190" >v26.19.0 release notes</a> |
| v26.18.0 | v26.18.0 | v26.18.0 | 2026-04-03 | See <a href="/releases/#v26180" >v26.18.0 release notes</a> |
| v26.17.1 | v26.17.1 | v26.17.1 | 2026-03-27 |  |
| v26.17.0 | v26.17.0 | v26.17.0 | 2026-03-27 | See <a href="/releases/#v26170" >v26.17.0 release notes</a> |
| v26.16.0 | v26.16.0 | v26.16.0 | 2026-03-20 | See <a href="/releases/#v26160" >v26.16.0 release notes</a> |
| v26.15.0 | v26.15.0 | v26.15.0 | 2026-03-13 |  |
| v26.15.0 | v26.15.0 | v26.15.0 | 2026-03-13 | See <a href="/releases/#v26150" >v26.15.0 release notes</a> |
| v26.14.1 | v26.14.1 | v26.14.1 | 2026-03-06 | See <a href="/releases/#v26141" >v26.14 release notes</a> |
| v26.14.0 | v26.14.0 | v26.14.0 | 2026-03-06 |  |
| v26.13.0 | v26.13.0 | v26.13.0 | 2026-02-27 | See <a href="/releases/#v26130" >v26.13.0 release notes</a> |
| v26.12.1 | v26.12.1 | v26.12.1 | 2026-02-20 |  |
| v26.12.0 | v26.12.0 | v26.12.0 | 2026-02-20 | See <a href="/releases/#v26120" >v26.12.0 release notes</a> |
| v26.11.0 | v26.11.0 | v26.11.0 | 2026-02-13 | See <a href="/releases/#v26110" >v26.11.0 release notes</a> |
| v26.10.2 | v26.10.2 | v26.10.2 | 2026-02-09 |  |
| v26.10.1 | v26.10.1 | v26.10.1 | 2026-02-06 | See <a href="/releases/#v26101" >v26.10.1 release notes</a> |
| v26.9.0 | v26.9.0 | v26.9.0 | 2026-01-30 | See <a href="/releases/#v2690" >v26.9.0 release notes</a> |
| v26.8.0 | v26.8.0 | v26.8.0 | 2026-01-23 | See <a href="/releases/#v2680" >v26.8.0 release notes</a> |
| v26.7.0 | v26.7.0 | v26.7.0 | 2026-01-16 | See <a href="/releases/#v2670" >v26.7.0 release notes</a> |
| v26.6.0 | v26.6.0 | v26.6.0 | 2026-01-12 | See <a href="/releases/#v2660" >v26.6.0 release notes</a> |
| v26.5.1 | v26.5.1 | v26.5.1 | 2025-12-23 | See <a href="/releases/#v2651" >v26.5.1 release notes</a> |
| v26.5.0 | v26.5.0 | v26.5.0 | 2025-12-23 | Do not use. |
| v26.4.0 | v26.4.0 | v26.4.0 | 2025-12-17 | See <a href="/releases/#v2640" >v26.4.0 release notes</a>. |
| v26.3.0 | v26.3.0 | v26.3.0 | 2025-12-12 | See <a href="/releases/#v2630" >v26.3.0 release notes</a>. |
| v26.2.0 | v26.2.0 | v26.2.0 | 2025-12-09 | See <a href="/releases/#v2620" >v26.2.0 release notes</a>. |
| v26.1.0 | v26.1.0 | v26.1.0 | 2025-11-26 | See <a href="/releases/#v2610" >v26.1.0 release notes</a>. |
| v26.0.0 | v26.0.0 | v26.0.0 | 2025-11-18 | See <a href="/releases/#self-managed-v2600" >v26.0.0 release notes</a> |

<!-- mz-docs page: self-managed-deployments/troubleshooting -->

# Troubleshooting
## Troubleshooting Kubernetes

To check the status of the Materialize operator:

```shell
kubectl -n materialize get all
```

If you encounter issues with the Materialize operator,

- Check the operator logs, using the label selector:

  ```shell
  kubectl -n materialize logs -l app.kubernetes.io/name=materialize-operator
  ```

- Check the log of a specific object (pod/deployment/etc) running in
  your namespace:

  ```shell
  kubectl -n materialize logs <type>/<name>
  ```

  In case of a container restart, to get the logs for previous instance, include
  the `--previous` flag.

- Check the events for the operator pod:

  - You can use `kubectl describe`, substituting your pod name for `<pod-name>`:

    ```shell
    kubectl -n materialize describe pod/<pod-name>
    ```

  - You can use `kubectl get events`, substituting your pod name for
    `<pod-name>`:

    ```shell
    kubectl -n materialize get events --sort-by=.metadata.creationTimestamp --field-selector involvedObject.name=<pod-name>
    ```

### Materialize deployment

- To check the status of your Materialize deployment, run:

  ```shell
  kubectl  -n materialize-environment get all
  ```

- To check the log of a specific object (pod/deployment/etc) running in your
  namespace:

  ```shell
  kubectl -n materialize-environment logs <type>/<name>
  ```

  In case of a container restart, to get the logs for previous instance, include
  the `--previous` flag.

- To describe an object, you can use `kubectl describe`:

  ```shell
  kubectl -n materialize-environment describe <type>/<name>
  ```

For additional `kubectl` commands, see [kubectl Quick reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/).

## Troubleshooting Console unresponsiveness

If you experience long loading screens or unresponsiveness in the Materialize
Console, it may be that the size of the `mz_catalog_server` cluster (where the
majority of the Console's queries are run) is insufficient (default size is
`25cc`).

To increase the cluster's size, you can follow the following steps:

1. Login as the `mz_system` user in order to update `mz_catalog_server`.

   1. To login as `mz_system` you'll need the internal-sql port found in the
      `environmentd` pod (`6877` by default). You can port forward via `kubectl
      port-forward svc/mzXXXXXXXXXX 6877:6877 -n materialize-environment`.

   1. Connect using a pgwire compatible client (e.g., `psql`) and connect using
      the port and user `mz_system`. For example:

       ```
       psql -h localhost -p 6877 --user mz_system
       ```

3. Run the following [ALTER CLUSTER](/sql/alter-cluster/#resizing) statement
   to change the cluster size to `50cc`:

    ```mzsql
    ALTER CLUSTER mz_catalog_server SET (SIZE = '50cc');
    ```

4. Verify your changes via `SHOW CLUSTERS;`

   ```mzsql
   show clusters;
   ```

   Resizing a cluster is a graceful reconfiguration: Materialize brings up a
   replica at the new size, waits for it to hydrate, and only then retires the
   old one. Until that finishes, `SHOW CLUSTERS` reports the old size, and
   briefly both. Re-run the statement until it settles. The replacement replica
   also gets a fresh name, so the resized cluster reports `r2` rather than `r1`.

   The output should include the `mz_catalog_server` cluster with a size of `50cc`:

   ```none
          name        | replicas  | comment
    -------------------+-----------+---------
    mz_analytics      |           |
    mz_catalog_server | r2 (50cc) |
    mz_probe          |           |
    mz_support        |           |
    mz_system         |           |
    quickstart        | r1 (25cc) |
    (6 rows)
    ```

<!-- mz-docs page: self-managed-deployments/upgrading -->

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
  --version v26.43.0
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

<!-- mz-docs page: self-managed-deployments/upgrading/adopting-the-v1-crd -->

# Adopting the v1 CRD
Adopt the v1 Materialize CRD API version for Self-Managed Materialize.
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

<!-- mz-docs page: self-managed-deployments/upgrading/upgrade-on-aws -->

# Upgrade on AWS
Upgrade Materialize on AWS using the Terraform module.
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

### Step 1: Update the Materialize Terraform Modules source version

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

- If you are using `v1`, skip to the [Apply the updated Terraform
  step](#step-3-apply-the-updated-terraform).
- **If you are using `v1alpha1`**, you need to update your `terraform.tfvars`
file to set the `request_rollout` variable to a new UUID value, substituting
the example value in the code block below with a UUID you generate (for
example, with `uuidgen`):

```hcl
# ...
# ...
request_rollout = "DBB4FCEC-1837-44F6-9CF2-3894678DD8D5" # ONLY for v1alpha1
```

### Step 3: Apply the updated Terraform

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

## Enable the monitoring stack

The Terraform modules can install a monitoring stack — Grafana, Thanos, Loki,
Grafana Alloy, and Alertmanager — alongside your deployment, with the
Materialize dashboards pre-installed. You can turn it on during an upgrade, in
the same `terraform apply` as the version bump.

The stack below arrived in **v10.0.0** of the Materialize Terraform Modules,
replacing the earlier single Prometheus and Grafana. **v10.1.0** then added
durable state for Grafana and a load balancer to reach it on.

> **Warning:** Starting with **v11.0.0** of the Materialize Terraform Modules,
> `enable_observability` defaults to `true`. Bumping `ref=<RELEASE_TAG>` to
> v11.0.0 or later therefore installs the whole stack, and its billable
> supporting resources, on a deployment that never set the variable. Set
> `enable_observability = false` in the same change if you do not want it.

> **Warning:** `kubernetes/modules/prometheus` and `kubernetes/modules/grafana` were **removed**
> in v10.0.0, not deprecated in place. If your configuration references either
> directly, that reference breaks — pin the previous major until you have
> migrated.
> If you were running the old stack, upgrading **destroys** its Helm releases and
> PersistentVolumeClaims. Up to 15 days of local Prometheus data goes with them,
> along with anything hand-created in the old Grafana. There is no backfill. See
> [How to upgrade from previous versions of the Materialize Terraform
> Modules](/observability/self-managed/grafana/#how-to-upgrade-from-previous-versions-of-the-materialize-terraform-modules).

### If you use the example configuration

Nothing is required starting with v11.0.0 of the Materialize Terraform
Modules, where the variable defaults to `true`. To be explicit, or on an
earlier release, set the following in your `terraform.tfvars`:

```hcl
enable_observability = true
```

### If you instantiate the modules yourself

1. Add the `alekc/kubectl` provider to your `versions.tf`. The monitoring module
   uses it for the `TargetGroupBinding` that attaches the Grafana load balancer
   to the Grafana Service:

   ```hcl
   kubectl = {
     source  = "alekc/kubectl"
     version = "2.4.1"
   }
   ```

1. Add the `monitoring` module, using the same release tag as the rest of your
   modules:

   ```hcl
   module "monitoring" {
     source = "github.com/MaterializeInc/materialize-terraform-self-managed//aws/modules/monitoring?ref=<RELEASE_TAG>"

     name_prefix = var.name_prefix
     region      = var.aws_region

     namespace = "monitoring"
     # The operator module already creates this namespace.
     create_namespace = false

     oidc_provider_arn       = module.eks.oidc_provider_arn
     cluster_oidc_issuer_url = module.eks.cluster_oidc_issuer_url

     storage_class = module.ebs_csi_driver.storage_class_name

     materialize_instance_namespace = "materialize-environment"
     materialize_operator_namespace = "materialize"

     # Grafana's own state. Omit to leave Grafana on SQLite.
     grafana_database = {
       vpc_id                    = module.networking.vpc_id
       subnet_ids                = module.networking.private_subnet_ids
       cluster_name              = module.eks.cluster_name
       cluster_security_group_id = module.eks.cluster_security_group_id
       node_security_group_id    = module.eks.node_security_group_id
     }

     # Reach Grafana without port forwarding. Omit to keep it on ClusterIP.
     grafana_load_balancer = {
       vpc_id                 = module.networking.vpc_id
       subnet_ids             = module.networking.private_subnet_ids
       node_security_group_id = module.eks.node_security_group_id
       ingress_cidr_blocks    = var.ingress_cidr_blocks
     }

     depends_on = [module.operator]
   }
   ```

1. Turn on the operator's scrape annotations so its pods are collected:

   ```hcl
   module "operator" {
     # ...
     helm_values = {
       observability = {
         enabled = true
         prometheus = {
           scrapeAnnotations = {
             enabled = true
           }
         }
       }
     }
   }
   ```

### What this creates

Applying the above adds S3 buckets for metrics and logs, and — from
Materialize Terraform Modules v10.1.0 — a `db.t4g.micro` RDS instance for
Grafana's own state and an internal NLB to reach Grafana on. The database and
the load balancer are both billable.

> **Warning:** The Grafana load balancer terminates no TLS, and Grafana has no identity
> provider until you configure one. Keep it internal until both are addressed. A
> public load balancer whose allowlist is still `0.0.0.0/0` is refused at plan
> time for Grafana specifically.

> **Note:** The monitoring stack runs several components: Loki, Thanos, Grafana,
> Alertmanager, kube-state-metrics, and two Alloy roles. Your generic node pool
> may need to grow before the apply can schedule all of them.

For accessing Grafana, pointing the stack at a database you already run, sizing
profiles, and retention, see
[Grafana](/observability/self-managed/grafana/). For what the stack stores and
the backends it can forward to, see [How logs and metrics are
stored](/observability/self-managed/storage/).

## See also

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)
- [Troubleshooting](/self-managed-deployments/troubleshooting/)

<!-- mz-docs page: self-managed-deployments/upgrading/upgrade-on-azure -->

# Upgrade on Azure
Upgrade Materialize on Azure using the Terraform module.
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

### Step 1: Update the Materialize Terraform Modules source version

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

- If you are using `v1`, skip to the [Apply the updated Terraform
  step](#step-3-apply-the-updated-terraform).
- **If you are using `v1alpha1`**, you need to update your `terraform.tfvars`
file to set the `request_rollout` variable to a new UUID value, substituting
the example value in the code block below with a UUID you generate (for
example, with `uuidgen`):

```hcl
# ...
# ...
request_rollout = "DBB4FCEC-1837-44F6-9CF2-3894678DD8D5" # ONLY for v1alpha1
```

### Step 3: Apply the updated Terraform

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

## Enable the monitoring stack

The Terraform modules can install a monitoring stack — Grafana, Thanos, Loki,
Grafana Alloy, and Alertmanager — alongside your deployment, with the
Materialize dashboards pre-installed. You can turn it on during an upgrade, in
the same `terraform apply` as the version bump.

The stack below arrived in **v10.0.0** of the Materialize Terraform Modules,
replacing the earlier single Prometheus and Grafana. **v10.1.0** then added
durable state for Grafana and a load balancer to reach it on.

> **Warning:** Starting with **v11.0.0** of the Materialize Terraform Modules,
> `enable_observability` defaults to `true`. Bumping `ref=<RELEASE_TAG>` to
> v11.0.0 or later therefore installs the whole stack, and its billable
> supporting resources, on a deployment that never set the variable. Set
> `enable_observability = false` in the same change if you do not want it.

> **Warning:** `kubernetes/modules/prometheus` and `kubernetes/modules/grafana` were **removed**
> in v10.0.0, not deprecated in place. If your configuration references either
> directly, that reference breaks — pin the previous major until you have
> migrated.
> If you were running the old stack, upgrading **destroys** its Helm releases and
> PersistentVolumeClaims. Up to 15 days of local Prometheus data goes with them,
> along with anything hand-created in the old Grafana. There is no backfill. See
> [How to upgrade from previous versions of the Materialize Terraform
> Modules](/observability/self-managed/grafana/#how-to-upgrade-from-previous-versions-of-the-materialize-terraform-modules).

### If you use the example configuration

Nothing is required starting with v11.0.0 of the Materialize Terraform
Modules, where the variable defaults to `true`. To be explicit, or on an
earlier release, set the following in your `terraform.tfvars`:

```hcl
enable_observability = true
```

### If you instantiate the modules yourself

1. Add the `monitoring` module, using the same release tag as the rest of your
   modules:

   ```hcl
   module "monitoring" {
     source = "github.com/MaterializeInc/materialize-terraform-self-managed//azure/modules/monitoring?ref=<RELEASE_TAG>"

     prefix              = var.name_prefix
     resource_group_name = azurerm_resource_group.materialize.name
     location            = var.location

     namespace = "monitoring"
     # The operator module already creates this namespace.
     create_namespace = false

     oidc_issuer_url = module.aks.cluster_oidc_issuer_url

     materialize_instance_namespace = "materialize-environment"
     materialize_operator_namespace = "materialize"

     # Grafana's own state. Omit to leave Grafana on SQLite.
     grafana_database = {
       subnet_id           = module.networking.postgres_subnet_id
       private_dns_zone_id = module.networking.private_dns_zone_id
     }

     # Reach Grafana without port forwarding. Omit to keep it on ClusterIP.
     grafana_load_balancer = {
       ingress_cidr_blocks = var.ingress_cidr_blocks
     }

     tags = var.tags

     depends_on = [module.operator]
   }
   ```

1. Turn on the operator's scrape annotations so its pods are collected:

   ```hcl
   module "operator" {
     # ...
     helm_values = {
       observability = {
         enabled = true
         prometheus = {
           scrapeAnnotations = {
             enabled = true
           }
         }
       }
     }
   }
   ```

### What this creates

Applying the above adds blob containers for metrics and logs, and — from
Materialize Terraform Modules v10.1.0 — a `B_Standard_B1ms` PostgreSQL
Flexible Server for Grafana's own state and an internal load balancer to reach
Grafana on. The database and the load balancer are both billable.

> **Warning:** The Grafana load balancer terminates no TLS, and Grafana has no identity
> provider until you configure one. Keep it internal until both are addressed. A
> public load balancer whose allowlist is still `0.0.0.0/0` is refused at plan
> time for Grafana specifically.

> **Note:** The monitoring stack runs several components: Loki, Thanos, Grafana,
> Alertmanager, kube-state-metrics, and two Alloy roles. Your generic node pool
> may need to grow before the apply can schedule all of them.

For accessing Grafana, pointing the stack at a database you already run, sizing
profiles, and retention, see
[Grafana](/observability/self-managed/grafana/). For what the stack stores and
the backends it can forward to, see [How logs and metrics are
stored](/observability/self-managed/storage/).

## See also

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)
- [Troubleshooting](/self-managed-deployments/troubleshooting/)

<!-- mz-docs page: self-managed-deployments/upgrading/upgrade-on-gcp -->

# Upgrade on GCP
Upgrade Materialize on GCP using the Terraform module.
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

### Step 1: Update the Materialize Terraform Modules source version

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

- If you are using `v1`, skip to the [Apply the updated Terraform
  step](#step-3-apply-the-updated-terraform).
- **If you are using `v1alpha1`**, you need to update your `terraform.tfvars`
file to set the `request_rollout` variable to a new UUID value, substituting
the example value in the code block below with a UUID you generate (for
example, with `uuidgen`):

```hcl
# ...
# ...
request_rollout = "DBB4FCEC-1837-44F6-9CF2-3894678DD8D5" # ONLY for v1alpha1
```

### Step 3: Apply the updated Terraform

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

## Enable the monitoring stack

The Terraform modules can install a monitoring stack — Grafana, Thanos, Loki,
Grafana Alloy, and Alertmanager — alongside your deployment, with the
Materialize dashboards pre-installed. You can turn it on during an upgrade, in
the same `terraform apply` as the version bump.

The stack below arrived in **v10.0.0** of the Materialize Terraform Modules,
replacing the earlier single Prometheus and Grafana. **v10.1.0** then added
durable state for Grafana and a load balancer to reach it on.

> **Warning:** Starting with **v11.0.0** of the Materialize Terraform Modules,
> `enable_observability` defaults to `true`. Bumping `ref=<RELEASE_TAG>` to
> v11.0.0 or later therefore installs the whole stack, and its billable
> supporting resources, on a deployment that never set the variable. Set
> `enable_observability = false` in the same change if you do not want it.

> **Warning:** `kubernetes/modules/prometheus` and `kubernetes/modules/grafana` were **removed**
> in v10.0.0, not deprecated in place. If your configuration references either
> directly, that reference breaks — pin the previous major until you have
> migrated.
> If you were running the old stack, upgrading **destroys** its Helm releases and
> PersistentVolumeClaims. Up to 15 days of local Prometheus data goes with them,
> along with anything hand-created in the old Grafana. There is no backfill. See
> [How to upgrade from previous versions of the Materialize Terraform
> Modules](/observability/self-managed/grafana/#how-to-upgrade-from-previous-versions-of-the-materialize-terraform-modules).

### If you use the example configuration

Nothing is required starting with v11.0.0 of the Materialize Terraform
Modules, where the variable defaults to `true`. To be explicit, or on an
earlier release, set the following in your `terraform.tfvars`:

```hcl
enable_observability = true
```

### If you instantiate the modules yourself

1. Add the `monitoring` module, using the same release tag as the rest of your
   modules:

   ```hcl
   module "monitoring" {
     source = "github.com/MaterializeInc/materialize-terraform-self-managed//gcp/modules/monitoring?ref=<RELEASE_TAG>"

     prefix     = var.name_prefix
     project_id = var.project_id
     region     = var.region

     namespace = "monitoring"
     # The operator module already creates this namespace.
     create_namespace = false

     materialize_instance_namespace = "materialize-environment"
     materialize_operator_namespace = "materialize"

     # Grafana's own state. Omit to leave Grafana on SQLite.
     grafana_database = {
       network_id = module.networking.network_id
     }

     # Reach Grafana without port forwarding. Omit to keep it on ClusterIP.
     grafana_load_balancer = {
       ingress_cidr_blocks = var.ingress_cidr_blocks
     }

     depends_on = [module.operator]
   }
   ```

1. Turn on the operator's scrape annotations so its pods are collected:

   ```hcl
   module "operator" {
     # ...
     helm_values = {
       observability = {
         enabled = true
         prometheus = {
           scrapeAnnotations = {
             enabled = true
           }
         }
       }
     }
   }
   ```

### What this creates

Applying the above adds Cloud Storage buckets for metrics and logs, and — from
Materialize Terraform Modules v10.1.0 — a `db-f1-micro` Cloud SQL instance for
Grafana's own state and an internal load balancer to reach Grafana on. The
database and the load balancer are both billable.

> **Warning:** The Grafana load balancer terminates no TLS, and Grafana has no identity
> provider until you configure one. Keep it internal until both are addressed. A
> public load balancer whose allowlist is still `0.0.0.0/0` is refused at plan
> time for Grafana specifically.

> **Note:** The monitoring stack runs several components: Loki, Thanos, Grafana,
> Alertmanager, kube-state-metrics, and two Alloy roles. Your generic node pool
> may need to grow before the apply can schedule all of them.

For accessing Grafana, pointing the stack at a database you already run, sizing
profiles, and retention, see
[Grafana](/observability/self-managed/grafana/). For what the stack stores and
the backends it can forward to, see [How logs and metrics are
stored](/observability/self-managed/storage/).

## See also

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)
- [Troubleshooting](/self-managed-deployments/troubleshooting/)

<!-- mz-docs page: self-managed-deployments/upgrading/upgrade-on-kind -->

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
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl"><span class="nv">mz_version</span><span class="o">=</span>v26.43.0
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
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>--version v26.43.0 <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>-f upgrade-values.yaml <span class="se">\
</span></span></span><span class="line"><span class="cl"><span class="se"></span>--set observability.podMetrics.enabled<span class="o">=</span><span class="nb">true</span> <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>--set operator.args.installV1CRD<span class="o">=</span><span class="nb">true</span>
</span></span></code></pre></div></div>
<div class="tab-pane" title="CRD v1alpha1" id="upgrade-operator-kind-v1alpha1">
<p>If currently using <code>v1alpha1</code> (default):</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-shell" data-lang="shell"><span class="line"><span class="cl">helm upgrade my-materialize-operator materialize/materialize-operator <span class="se">\
</span></span></span><span class="line"><span class="cl"><span class="se"></span>--namespace<span class="o">=</span>materialize <span class="se">\
</span></span></span><span class="line hl"><span class="cl"><span class="se"></span>--version v26.43.0 <span class="se">\
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
          <td>Update the version to the new version. This should be the same as the operator version: <code>v26.43.0</code>. Updating this field automatically triggers a rollout.</td>
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
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">environmentdImageRef</span><span class="p">:</span><span class="w"> </span><span class="l">materialize/environmentd:v26.43.0</span><span class="w"> </span><span class="c"># Update version</span><span class="w">
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
          <td>Update the version to the new version. This should be the same as the operator version: <code>v26.43.0</code>.</td>
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
</span></span></span><span class="line"><span class="cl"><span class="w">  </span><span class="nt">environmentdImageRef</span><span class="p">:</span><span class="w"> </span><span class="l">materialize/environmentd:v26.43.0</span><span class="w"> </span><span class="c"># Update version</span><span class="w">
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

<!-- mz-docs page: self-managed-deployments/upgrading/version-notes -->

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
> levels](/serve-results/isolation-level/).

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

<!-- mz-docs page: self-managed-deployments/usage -->

# Usage (Self-Managed)
Overview of the resource usage for Self-Managed Materialize.
## Compute

In Materialize, [clusters](/fundamentals/concepts/clusters/) are pools of compute resources
(CPU, memory, and scratch disk space) for running your workloads, such as
maintaining up-to-date results while also providing strong [consistency
guarantees](/serve-results/isolation-level/).

> **Note:** In Materialize,various [system clusters](/sql/system-clusters/) are
> pre-installed to improve the user experience as well as support system
> administration tasks.

You must provision at least one cluster to power your workloads. You can then
use the cluster to create the objects ([indexes](/fundamentals/concepts/indexes/) and
[materialized views](/fundamentals/concepts/views/#materialized-views)) that provide
always-fresh results. In Materialize, both indexes and materialized views are
incrementally maintained when Materialize ingests new data. That is, Materialize
performs work on writes such that no work is performed when reading from these
objects.

The cluster size for a workload will depend on the workload's compute and
storage requirements.

Clusters are always "on", and you can adjust the [replication
factor](/sql/create-cluster/#replication-factor) for
fault tolerance. See [Compute usage factors](#compute-usage-factors) for more
information on increasing a cluster's replication factor.

## Compute usage factors

Factors that contribute to compute usage include:

| Cost factor | Details       |
|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Replication factor for a cluster](/sql/create-cluster/#replication-factor). | Each replica of a cluster provisions a new pool of compute resources to perform exactly the same work on exactly the same data. That is, replicas are redundant copies of the cluster's workload, not shards: each replica processes the full workload. |
| [Indexes](/fundamentals/concepts/indexes/) and [materialized views](/fundamentals/concepts/views) | As data changes (insert/update/delete), [indexes](/fundamentals/concepts/indexes/) and [materialized views](/fundamentals/concepts/views) perform incremental updates to provide up-to-date results. |
| [Sources](/fundamentals/concepts/sources/) |• Sources that use upsert logic (i.e., [`ENVELOPE UPSERT`](/sql/create-sink/kafka/) or [`ENVELOPE DEBEZIUM` Kafka sources](/sql/create-sink/kafka/)) can lead to high memory and disk utilization.<br>• Other sources consume a negligible amount of resources in steady state. |
| [`SELECT`s](/sql/select/) and [`SUBSCRIBE`s](/sql/subscribe/)  |• [`SELECT`s](/sql/select/) and [`SUBSCRIBE`s](/sql/subscribe/) that do not use indexes and materialized views perform work. <br>• [`SELECT`s](/sql/select/) and [`SUBSCRIBE`s](/sql/subscribe/) that use indexes and materialized views access already-computed results.|
| [Sinks](/fundamentals/concepts/sinks/) | Only small CPU/memory costs.|

## Storage

In Materialize, storage is roughly proportional to the size of your source
datasets plus the size of any materialized views, with some overhead from
uncompacted data and system metrics.

Most data in Materialize is continually compacted, with the exception of
[append-only sources](/sql/create-source/kafka/#append-only-envelope). As such, the
total state stored in Materialize tends to grow at a rate that is more similar
to OLTP databases than cloud data warehouses.

