# Materialize Cloud

Guidance for operating Materialize Cloud.

## Overview

Materialize Cloud is the fully managed service for Materialize. It lets you
build real-time data products without deploying or managing database
infrastructure. Materialize operates the underlying service, so your team can
focus on ingesting data, defining transformations, and serving fresh results.

To get started, [sign up for a free trial](https://materialize.com/register/)
and try the [Quickstart](/get-started/quickstart/).

## Guides

- Learn about [free trials](/materialize-cloud/free-trials/).
- Understand [usage and billing](/materialize-cloud/billing/).
- Plan for [disaster recovery](/materialize-cloud/disaster-recovery/).

---

## Customer responsibility model (Cloud)

The Materialize Cloud platform is built with a **shared responsibility model**
to ensure the highest levels of data integrity, availability, and resilience.
This page outlines the specific responsibilities of customers to manage their
data and connectivity effectively. Understanding and fulfilling these
responsibilities is critical to leveraging the full potential of the platform.

### Backup

As part of the Materialize Cloud's shared responsibility model, customers are
tasked with maintaining backups of their original data. While Materialize
provides robust data processing capabilities, ensuring that you have a
comprehensive backup strategy is crucial. This includes:

- **Regular backups**. Implementing regular backup schedules that align with
    your data recovery and business continuity plans.

- **Data integrity**. Verifying the integrity of backups to ensure data is
    complete and accurate, enabling effective recovery if needed.

- **Secure storage**. Utilizing secure and reliable storage solutions to protect
    your backups from unauthorized access and potential data loss scenarios.

Materialize maintains backups of core system state and ingested data to ensure
timely recovery in the event of an outage. The data of record is expected to be
maintained in upstream customer systems.

### Recovery

Responsibility for recovery from data connectivity issues rests with the
customer. In the event of an outage or disruption, customers are expected to:

- **Connection recovery**. Re-establish connections to the Materialize platform
    promptly to minimize downtime.

- **Data resynchronization**. In cases where data streaming is interrupted,
    ensure mechanisms are in place to resynchronize any missing data once
    connectivity is restored.

- **Monitoring and alerts**. Implement monitoring solutions to quickly detect
    and respond to connectivity issues.

### Availability

While we strive to provide high-availability, customers play a vital role in
managing their end of the connection to maintain uninterrupted availability.
This includes:

- **Redundant connectivity**. Establishing redundant network paths to
    Materialize can help avoid single points of failure.

- **Load balancing**. Utilizing load balancers to distribute traffic efficiently
    and enhance resilience.

- **Disaster recovery planning**. Incorporating our service into your broader
    disaster recovery plan to ensure business continuity.

### Account management

Tenant accounts and account permissions are set by the customer using native
[access control](/manage/access-control/) features.
2FA, SSO, and password requirements are configurable and highly recommended.

### Data accuracy

Materialize is the data processor and our customers are the data controllers.
Data accuracy and completeness is fully controlled by platform users.

### Data governance

Materialize customers have full responsibility for responding to customer data
privacy and governance requests. For details, see our [Privacy Policy](https://materialize.com/privacy-policy/).

## Responsibility Matrix

| Area | Materialize Responsibilities | Customer Responsibilities |
|------|----------------------------|-------------------------|
| Infrastructure | - Platform maintenance and updates<br>- System availability<br>- Core service reliability | - Client-side infrastructure<br>- Network connectivity<br>- Load balancing configuration |
| Backups | - Core system state<br>- Ingested data | - Source data backups<br>- Integrity and security of source data backups |
| Connection Recovery |  | - Re-establish dropped connections<br>- Data resynchronization<br>- Monitoring and alerting on connection failure<br>- Client-side disaster recovery |
| Availability | - Core service availability<br>- Core platform disaster recovery | - Redundant connectivity<br>- Load balancing configuration<br>- Disaster recovery of customer-owned infrastructure |
| Account Management and Authorization | - Tenant account creation | - Create and manage users within your organization's account<br>- Configure and maintain SSO integration<br>- Enable and configure MFA<br>- Configure role based access control (RBAC)<br>- Audit and monitor user activity |
| Data | - Data processing integrity and correctness | - Data accuracy and quality<br>- Data privacy compliance<br>- Data governance<br>- Data retention policies |
| Security | - Platform security<br>- Enforce customer configured authorization controls<br>- Security patches & vulnerability management | - Account security<br>- Access management<br>- Authentication configuration |
| Monitoring | - Platform health monitoring<br>- System performance metrics | - Connection monitoring<br> |
## Conclusion

Adhering to these responsibilities ensures that your data is protected, and
Materialize is utilized effectively. If you have any questions or need further
clarification on your responsibilities, please [contact support](/support).

---

## Disaster recovery (Cloud)

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

---

## Free Trials

When you [sign up for Materialize Cloud](https://materialize.com/register/), you
get a free trial account so you can explore the product and start building! This
page answers some frequently asked questions about free trials.

> **Tip:** For help getting started with your data or other questions about Materialize, you can schedule a [free guided trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

### What are the limits of a free trial?

In Materialize, [clusters](/fundamentals/concepts/clusters/) are the pools of
compute resources for running your workloads. The size and replication factor
of each cluster determines its [credit usage](/sql/create-cluster/#credit-usage).

During your free trial, the credit consumption rate across all clusters in a
region cannot exceed 4 credits per hour at any point in time. This limit should
accommodate most trial scenarios.

For example, let's say you have 3 clusters in a region:

Cluster     | Size      | Replication factor | Credits per hour
------------|-----------|--------------------|-----------------
`ingest`    | `50cc`    | 1                  | 0.5
`compute`   | `50cc`    | 2                  | 1 (0.5 each)
`quickstart`| `25cc`    | 1                  | 0.25

In this case, your credit consumption rate would be 1.75 credits per hour, which
is under the rate limit of 4 credits per hour.

### How long does a free trial last?

7 days. If you need additional time, please [chat with our team](https://materialize.com/convert-account/?utm_campaign=General&utm_source=documentation).

To continue using Materialize, you can upgrade to a paid, [On Demand
plan](https://materialize.com/pdfs/on-demand-terms.pdf) from the billing section
of the [Materialize console](/developer-tools/console/). Otherwise,
Materialize will delete your resources and data at the end of the trial period.

### How do I monitor my credit consumption rate?

To see your current credit consumption rate, measured in credits per hour, run
the following query against Materialize:

```mzsql
SELECT sum(s.credits_per_hour) AS credit_consumption_rate
  FROM mz_cluster_replicas r
  JOIN mz_cluster_replica_sizes s ON r.size = s.size;
```

For example, if you start your free trial by following the [getting started guide](/get-started/quickstart),
or if you otherwise only use the pre-installed `quickstart` cluster
(`25cc`), you will end up consuming `.25` credit per hour:

```nofmt
 credit_consumption_rate
-------------------------
                     .25
(1 row)
```

### Can I go over the credit rate limit?

No, you cannot go over the rate limit of 4 credits per hour at any time during
your free trial. If you try to add a replica that puts you over the limit,
Materialize will return an error similar to:

```nofmt
Error: creating cluster replica would violate max_credit_consumption_rate limit (desired: 6, limit: 4, current: 3)
Hint: Drop an existing cluster replica or contact support to request a limit increase.
```

If you need additional resources during your trial, [chat with our team](http://materialize.com/convert-account/?utm_campaign=General&utm_source=documentation).

### How do I get help during my trial?

If you have questions about Materialize or need support, reach out to us in our
[Community Slack](https://materialize.com/s/chat).

---

## Usage & billing (Cloud)

Materialize determines billing based on your compute and storage usage.
Materialize bills per second based on the [cluster(s)](/fundamentals/concepts/clusters/) you
provision for your workloads. Each cluster is a pool of resources (CPU, memory,
and scratch disk space) that must stay up and running to continually provide you
with always-fresh results. For pricing details, see [Pricing](https://materialize.com/pricing/).

## Compute

In Materialize, [clusters](/fundamentals/concepts/clusters/) are pools of compute resources
(CPU, memory, and scratch disk space) for running your workloads, such as
maintaining up-to-date results while also providing strong [consistency
guarantees](/serve-results/isolation-level/). The credit usage for a cluster is
measured at a one second granularity.

> **Note:** When you enable a Materialize region, various [system
> clusters](/sql/system-clusters/) are pre-installed to improve the user
> experience as well as support system administration tasks. Except for the
> default `quickstart` cluster, you are <red>not billed</red> for these system clusters.

You must provision at least one cluster to power your workloads. You can then
use the cluster to create the objects ([indexes](/fundamentals/concepts/indexes/) and
[materialized views](/fundamentals/concepts/views/#materialized-views)) that provide
always-fresh results. In Materialize, both indexes and materialized views are
incrementally maintained when Materialize ingests new data. That is, Materialize
performs work on writes such that no work is performed when reading from these
objects.

The cluster size for a workload will depend on the workload's compute and
storage requirements. To help users select the correct cluster size for their
workload, Materialize uses cluster size names that are based on the compute
credit spend, specifically, "centicredits" or `cc` (1/100th of a compute credit). For
example, the `25cc` cluster size is equivalent to 0.25 compute credits/hour; the
`200cc` cluster size is equivalent to 2 compute credits/hour. Larger clusters
can process data faster and handle larger data volumes.

> **Note:** You can resize a cluster to respond to changes in your workload. See [Sizing
> your clusters](/sql/alter-cluster/#resizing).

Clusters are always "on", and you can adjust the [replication factor](/sql/create-cluster/#replication-factor)
for fault tolerance.

Each replica of a cluster provisions a new pool of compute resources to perform exactly the same work on exactly the same data. That is, replicas are redundant copies of the cluster's workload, not shards: each replica processes the full workload.

See [Compute cost factors](#compute-cost-factors) for more information on the
cost of increasing a cluster's replication factor.

### Compute cost factors

The credit usage for a cluster is measured at a one second granularity. Factors
that contribute to compute usage include:

| Cost factor | Details       |
|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Replication factor for a cluster](/sql/create-cluster/#replication-factor). | Cost is calculated (at one second granularity) as cluster [`SIZE`](/sql/create-cluster/#available-sizes) * [`REPLICATION FACTOR`](/sql/create-cluster/#replication-factor). |
| [Indexes](/fundamentals/concepts/indexes/) and [materialized views](/fundamentals/concepts/views) | As data changes (insert/update/delete), [indexes](/fundamentals/concepts/indexes/) and [materialized views](/fundamentals/concepts/views) perform incremental updates to provide up-to-date results. |
| [Sources](/fundamentals/concepts/sources/) |• Sources that use upsert logic (i.e., [`ENVELOPE UPSERT`](/sql/create-sink/kafka/#upsert) or [`ENVELOPE DEBEZIUM` Kafka sources](/sql/create-sink/kafka/#debezium)) can lead to high memory and disk utilization.<br>• Other sources consume a negligible amount of resources in steady state. |
| [`SELECT`s](/sql/select/) and [`SUBSCRIBE`s](/sql/subscribe/)  |• [`SELECT`s](/sql/select/) and [`SUBSCRIBE`s](/sql/subscribe/) that do not use indexes and materialized views perform work. <br>• [`SELECT`s](/sql/select/) and [`SUBSCRIBE`s](/sql/subscribe/) that use indexes and materialized views access already-computed results.|
| [Sinks](/fundamentals/concepts/sinks/) | Only small CPU/memory costs.|

## Storage

In Materialize, storage is roughly proportional to the size of your source
datasets plus the size of any materialized views, with some overhead from
uncompacted data and system metrics.

Materialize uses cheap, scalable object storage for its storage layer
(Amazon S3), and primarily passes the cost through to the customer.

Most data in Materialize is continually compacted, with the exception of
[append-only sources](/sql/create-source/kafka/). As such, the
total state stored in Materialize tends to grow at a rate that is more similar
to OLTP databases than cloud data warehouses.

## Invoices

> **Note:** Accessing usage and billing information in Materialize
> requires **administrator** privileges.

From the [Materialize console](/developer-tools/console/) (`Admin` >
`Usage & Billing`), administrators can access their invoice. The invoice
provides Compute and Storage usage and cost information.

## On Demand

Materialize Cloud administrators can sign up for an [On Demand
plan](https://materialize.com/pdfs/on-demand-terms.pdf) from the billing section
of the [Materialize console](/developer-tools/console/). Pricing is
usage-based and is billed on a monthly basis. Invoices will be sent to the
account email and paid via the card on file on the first of the month. If you
have questions about billing or are interested in converting to an annual
enterprise contract, please [contact us](https://materialize.com/docs/support/)
to discuss further.

If you'd like to cancel your On Demand account with Materialize, please email
cancellations@materialize.com to terminate services per the On Demand [Terms and
Conditions](https://materialize.com/pdfs/on-demand-terms.pdf).

## Additional references

- [Pricing](https://materialize.com/pricing/)

- [How Materialize can lower the cost of freshness for data teams](https://materialize.com/promotions/cost-of-freshness/?utm_campaign=General&utm_source=documentation)

<style>
redb { color: Red; font-weight: 500; }
</style>

