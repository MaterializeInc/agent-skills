# Disaster recovery (Cloud)

Learn about various disaster recovery (DR) strategies for Materialize.

The following outlines various disaster recovery (DR) strategies for
Materialize.

## Level 1: Basic configuration (Intra-Region Recovery)

Because Materialize is deterministic and its infrastructure runs on a container
scheduler (AWS EKS), basic Materialize configuration provides intra-region
disaster recovery **as long as**:

- Materialize can spin up a new pod somewhere in the region, and

- S3 is available.

In such cases, your mean time to recovery is the **same as your compute
cluster's rehydration time**.

> **💡 Recommendation:** When running with the basic configuration, we recommend that you track your rehydration time to ensure that it is within an acceptable range for your business' risk tolerance. 

## Level 2:  Multi-replica clusters (High availability across AZs)

> **Note:** The hybrid strategy is available if your deployment uses a [three-tier or a
> two-tier architecture](/clusters/operational-guidelines/).

Materialize supports multi-replica clusters, allowing for distribution across
Availability Zones (AZs):

- For clusters sized **up to and including `3200cc`**, Materialize guarantees
  that all provisioned replicas in a cluster are distributed across the
  underlying cloud provider's availability zones.

- For clusters sized **above `3200cc`**, even distribution of replicas
  across availability zones **cannot** be guaranteed.

Multi-replica **compute clusters** and multi-replica **serving clusters**
(excluding sink clusters) with replicas distributed across AZs provide DR
resilience against: machine-level failures; rack and building-level outages; and
AZ level failures for those clusters:

- With multi-replica **compute clusters**, each replica performs the same work.

- With multi-replica **serving clusters** (excluding sink clusters), each
  replica processes the same queries.

As such, your compute and serving clusters will continue to serve up-to-date
data uninterrupted in the case of a replica failure.

> **💡 Cost and work capacity:** - For Cloud, each replica incurs cost, calculated as `cluster size * replication factor` per second. See [Usage & billing (Cloud)](/materialize-cloud/billing/) for more details. - Increasing the replication factor does **not** increase the cluster's work capacity. Replicas are exact copies of one another: each replica must do exactly the same work as all the other replicas of the cluster (i.e., maintain the same dataflows and process the same queries). To increase the capacity of a cluster, you must increase its size. 

If you require resilience beyond a single region, consider the Level 3 strategy.

## Level 3: A duplicate Materialize environment (Inter-region resilience)

> **Note:** The duplicate environment strategy assumes the use of Infrastructure-as-Code
> (IaC) practice for managing the environment. This ensures that catalog data,
> including your RBAC setup, is identical in the second environment.

For region-level fault tolerance, you can choose to have a second Materialize
environment in another region. With this strategy:

- You avoid complicated cross-regional communication.

- You avoid state dependency checks and verifications.

- And, because Materialize is deterministic, as long as your upstream sources
can also be accessed from the second region, the two Materialize environments
can guarantee the same results.

> **💡 No strict transactional consistency between environments:** This approach does <red>**not**</red> offer strict transactional consistency across regions. However, as long as both regions are caught up, the results should be within about a second of each other. 

The duplicate Materialize environment setup can be adapted into a more
cost-effective setup if your deployment uses a [three-tier or a two-tier
architecture](/clusters/operational-guidelines/). For details, see the [hybrid
variation](#hybrid-variation).

### Hybrid variation

> **Note:** - The hybrid strategy is available if your deployment uses a [three-tier or a
> two-tier architecture](/clusters/operational-guidelines/).
> - The duplicate environment strategy assumes the use of Infrastructure-as-Code
> (IaC) practice for managing the environment. This ensures that catalog data,
> including your RBAC setup, is identical in the second environment.

For a more cost-effective variation to the duplicate Materialize environment in
another region, you can choose a hybrid strategy where:

- Only the sources clusters are running in the second Materialize environment.

- The compute clusters are  provisioned **only** in the event of an incident.

When combined with a [multi-replica
approach](#level-2--multi-replica-clusters-high-availability-across-azs), you
have:

- Immediate failover during an AZ failure.

- Downtime equal to hydration time during intra-region failover.

## See also

- [Materialize DR
  characteristics](/materialize-cloud/disaster-recovery/recovery-characteristics)

## Pages in this section

- [Materialize Cloud DR characteristics](/materialize-cloud/disaster-recovery/recovery-characteristics/index.md): Reference on various failure modes and recovery characteristics of Materialize Cloud.
