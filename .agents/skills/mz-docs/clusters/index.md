# Clusters

Guidance for configuring and operating Materialize clusters.

Clusters provide the compute resources for running dataflows in Materialize.

- Learn about [clusters](/fundamentals/concepts/clusters/).
- Follow the [operational guidelines](/clusters/operational-guidelines/).
- Learn how to [optimize cluster size](/clusters/sizing/).
- [Optimize hydration requirements](/clusters/optimize-hydration-requirements/).
- Speed up hydration with [autoscaling](/clusters/autoscaling/).
- Understand [system clusters](/clusters/system-clusters/).
- [Troubleshoot clusters](/clusters/troubleshoot-clusters/).

## Pages in this section

- [Autoscaling for hydration](/clusters/autoscaling/index.md): Speed up cluster hydration with a temporary burst replica, monitor it, and know what to expect if the steady-size replica never catches up or the burst can't be provisioned.
- [M.1 to cc size mapping](/clusters/m1-cc-mapping/index.md): General mapping between cc and M.1 cluster sizes.
- [Operational guidelines](/clusters/operational-guidelines/index.md): General guidelines for production
- [Optimize hydration requirements](/clusters/optimize-hydration-requirements/index.md): Strategies to reduce the memory Materialize needs to hydrate objects, and to speed up or avoid hydration altogether.
- [Size clusters for hydration](/clusters/sizing/index.md): Measure the resources your cluster requires to hydrate, and optimize your cluster size accordingly
- [System clusters](/clusters/system-clusters/index.md): Reference page on system clusters
- [Troubleshoot clusters](/clusters/troubleshoot-clusters/index.md): Guides for diagnosing common cluster problems.
