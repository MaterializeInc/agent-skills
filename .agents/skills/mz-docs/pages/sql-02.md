<!-- mz-docs page: sql/create-connection -->

# CREATE CONNECTION
`CREATE CONNECTION` describes how to connect and authenticate to an external system in Materialize
[//]: # "TODO: This page could be broken up."

A connection describes how to connect and authenticate to an external system you
want Materialize to read from or write to. Once created, a connection
is **reusable** across multiple [`CREATE SOURCE`](/sql/create-source) and
[`CREATE SINK`](/sql/create-sink) statements.

To use credentials that contain sensitive information (like passwords and SSL
keys) in a connection, you must first [create secrets](/sql/create-secret) to
securely store each credential in Materialize's secret management system.
Credentials that are generally not sensitive (like usernames and SSL
certificates) can be specified as plain `text`, or also stored as secrets.

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

## Source and sink connections

### AWS

An Amazon Web Services (AWS) connection provides Materialize with access to an
Identity and Access Management (IAM) user or role in your AWS account. You can
use AWS connections to perform [bulk exports to Amazon S3](/serve-results/s3/),
perform [authentication with an Amazon MSK cluster](#kafka-aws-connection),
perform [authentication with an Amazon RDS MySQL database](#mysql-aws-connection),
or [authenticate to an AWS Glue Schema Registry](#aws-glue-schema-registry).

```mzsql
CREATE CONNECTION <connection_name> TO AWS (
    ENDPOINT = '<endpoint>',
    REGION = '<region>',
    ACCESS KEY ID = { '<access_key_id>' | SECRET <secret_name> },
    SECRET ACCESS KEY = SECRET <secret_name>,
    SESSION TOKEN = { '<session_token>' | SECRET <secret_name> },
    ASSUME ROLE ARN = '<role_arn>',
    ASSUME ROLE SESSION NAME = '<session_name>'
)
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `ENDPOINT` | *Value:* `text`  *Advanced.* Override the default AWS endpoint URL. Allows targeting S3-compatible services like MinIO.  |
| `REGION` | *Value:* `text`  *For Materialize Cloud only* The AWS region to connect to. Defaults to the current Materialize region.  |
| `ACCESS KEY ID` | *Value:* secret or `text`  The access key ID to connect with. Triggers credentials-based authentication.  **Warning!** Use of credentials-based authentication is deprecated. AWS strongly encourages the use of role assumption-based authentication instead.  |
| `SECRET ACCESS KEY` | *Value:* secret  The secret access key corresponding to the specified access key ID.  Required and only valid when `ACCESS KEY ID` is specified.  |
| `SESSION TOKEN` | *Value:* secret or `text`  The session token corresponding to the specified access key ID.  Only valid when `ACCESS KEY ID` is specified.  |
| `ASSUME ROLE ARN` | *Value:* `text`  The Amazon Resource Name (ARN) of the IAM role to assume. Triggers role assumption-based authentication.  |
| `ASSUME ROLE SESSION NAME` | *Value:* `text`  The session name to use when assuming the role.  Only valid when `ASSUME ROLE ARN` is specified.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `VALIDATE` \| `boolean` \| Whether [connection validation](#connection-validation) should be performed on connection creation. Default: `false`. \|  |

#### Permissions {#aws-permissions}

> **Warning:** Failing to constrain the external ID in your role trust policy will allow
> other Materialize customers to assume your role and use AWS privileges you
> have granted the role!

When using role assumption-based authentication, you must configure a [trust
policy] on the IAM role that permits Materialize to assume the role.

Materialize always uses the following IAM principal to assume the role:

```
arn:aws:iam::664411391173:role/MaterializeConnection
```

Materialize additionally generates an [external ID] which uniquely identifies
your AWS connection across all Materialize regions. To ensure that other
Materialize customers cannot assume your role, your IAM trust policy **must**
constrain access to only the external ID that Materialize generates for the
connection:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::664411391173:role/MaterializeConnection"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "<EXTERNAL ID FOR CONNECTION>"
                }
            }
        }
    ]
}
```

You can retrieve the external ID for the connection, as well as an example trust
policy, by querying the
[`mz_internal.mz_aws_connections`](/sql/system-catalog/mz_internal/#mz_aws_connections)
table:

```mzsql
SELECT id, external_id, example_trust_policy FROM mz_internal.mz_aws_connections;
```

#### Examples {#aws-examples}

**Role assumption:**

In this example, we have created the following IAM role for Materialize to
assume:

<table>
<tr>
<th>Name</th>
<th>AWS account ID</th>
<th>Trust policy</th>
<tr>
<td><code>WarehouseExport</code></td>
<td>000000000000</td>
<td>

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::000000000000:role/MaterializeConnection"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "mz_00000000-0000-0000-0000-000000000000_u0"
                }
            }
        }
    ]
}
```

</td>
</tr>
</table>

To create an AWS connection that will assume the `WarehouseExport` role:

```mzsql
CREATE CONNECTION aws_role_assumption TO AWS (
    ASSUME ROLE ARN = 'arn:aws:iam::000000000000:role/WarehouseExport',
    REGION = 'us-east-1'
);
```

**Credentials:**
> **Warning:** Use of credentials-based authentication is deprecated.  AWS strongly encourages
> the use of role assumption-based authentication instead.

To create an AWS connection that uses static access key credentials:

```mzsql
CREATE SECRET aws_secret_access_key AS '...';
CREATE CONNECTION aws_credentials TO AWS (
    ACCESS KEY ID = 'ASIAV2KIV5LPTG6HGXG6',
    SECRET ACCESS KEY = SECRET aws_secret_access_key
);
```

### S3 compatible object storage
You can use an AWS connection to perform bulk exports ([`COPY TO`](/sql/copy-to)) and bulk imports ([`COPY FROM`](/sql/copy-from)) with any S3 compatible object
storage service, such as Google Cloud Storage, Cloudflare R2, or MinIO. While connecting to S3
compatible object storage, you need to provide static access key credentials, specify the endpoint,
and the region.

To create a connection that uses static access key credentials:

```mzsql
CREATE SECRET secret_access_key AS '...';
CREATE CONNECTION gcs_connection TO AWS (
    ACCESS KEY ID = 'ASIAV2KIV5LPTG6HGXG6',
    SECRET ACCESS KEY = SECRET secret_access_key,
    ENDPOINT = 'https://storage.googleapis.com',
    REGION = 'us'
);
```

If you are exporting to Google Cloud Storage using [Iceberg sinks](/sql/create-sink/iceberg), use a [GCP connection](#gcp).

### GCP

You can use a GCP connection to export data to
[Lakehouse/BigLake](https://docs.cloud.google.com/lakehouse/docs/lakehouse-iceberg-rest-catalog)
via [Iceberg sinks](/sql/create-sink/iceberg).

The GCP connection uses a [GCP service account key
(JSON)](https://docs.cloud.google.com/iam/docs/keys-create-delete) to
authenticate. Create a [GCP service
account](https://docs.cloud.google.com/iam/docs/service-account-overview) for
Materialize to use and generate a [service account
key](https://docs.cloud.google.com/iam/docs/keys-create-delete) in JSON format.
Base64-encode the entire JSON key (e.g., `base64 < sa_key.json`) and decode it
in the `CREATE SECRET` statement, as shown below. This avoids escaping quotes
and newlines in the SQL string literal.

#### Syntax {#gcp-syntax}

```mzsql
-- Create the secret with the service account key.
-- Base64-encode the entire JSON service account key (e.g., base64 < sa_key.json)
-- And decode it in the CREATE SECRET statement.
CREATE SECRET <secret_name> AS decode('<sa_key_json_base64>', 'base64');

CREATE CONNECTION <connection_name> TO GCP (
    SERVICE ACCOUNT KEY = SECRET <secret_name>
)
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `SECRET <secret_name>` | Secret containing the [GCP service account key](https://docs.cloud.google.com/iam/docs/keys-create-delete) (JSON).  To create the secret, first base64-encode the entire JSON service account key and then decode it in the `CREATE SECRET` statement. This avoids escaping quotes and newlines in the SQL string literal.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `VALIDATE` \| `boolean` \| Whether [connection validation](#connection-validation) should be performed on connection creation. Default: `false`. \|  |

### Kafka

A Kafka connection establishes a link to a [Kafka] cluster. You can use Kafka
connections to create [sources](/sql/create-source/kafka) and [sinks](/sql/create-sink/kafka/).

#### Syntax {#kafka-syntax}

```mzsql
CREATE CONNECTION <connection_name> TO KAFKA (
    BROKER '<broker>' | BROKERS ('<broker1>', '<broker2>', ...),
    SECURITY PROTOCOL = { 'PLAINTEXT' | 'SSL' | 'SASL_PLAINTEXT' | 'SASL_SSL' },
    SASL MECHANISMS = { 'PLAIN' | 'SCRAM-SHA-256' | 'SCRAM-SHA-512' },
    SASL USERNAME = { '<username>' | SECRET <secret_name> },
    SASL PASSWORD = SECRET <secret_name>,
    SSL CERTIFICATE AUTHORITY = { '<pem>' | SECRET <secret_name> },
    SSL CERTIFICATE = { '<pem>' | SECRET <secret_name> },
    SSL KEY = SECRET <secret_name>,
    SSH TUNNEL = <ssh_connection_name>,
    AWS CONNECTION = <aws_connection_name>,
    AWS PRIVATELINK <privatelink_connection_name> (PORT <port>),
    PROGRESS TOPIC = '<topic_name>',
    PROGRESS TOPIC REPLICATION FACTOR = <int>
)
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `BROKER` / `BROKERS` | *Value:* `text` / `text[]`  The Kafka bootstrap server(s). Exactly one of `BROKER`, `BROKERS`, or `AWS PRIVATELINK` must be specified.  |
| `SECURITY PROTOCOL` | *Value:* `text`  The security protocol to use: `PLAINTEXT`, `SSL`, `SASL_PLAINTEXT`, or `SASL_SSL`.  Defaults to `SASL_SSL` if any `SASL ...` options are specified or if the `AWS CONNECTION` option is specified, otherwise defaults to `SSL`.  |
| `SASL MECHANISMS` | *Value:* `text`  The SASL mechanism to use for authentication: `PLAIN`, `SCRAM-SHA-256`, or `SCRAM-SHA-512`. Despite the name, this option only allows a single mechanism to be specified.  Required if the security protocol is `SASL_PLAINTEXT` or `SASL_SSL`. Cannot be specified if `AWS CONNECTION` is specified.  |
| `SASL USERNAME` / `SASL PASSWORD` | *Value:* secret or `text` / secret  Your SASL credentials.  Required and only valid when the security protocol is `SASL_PLAINTEXT` or `SASL_SSL`.  |
| `SSL CERTIFICATE AUTHORITY` | *Value:* secret or `text`  The certificate authority (CA) certificate in PEM format. Used to validate the brokers' TLS certificates. If unspecified, uses the system's default CA certificates.  Only valid when the security protocol is `SSL` or `SASL_SSL`.  |
| `SSL CERTIFICATE` / `SSL KEY` | *Value:* secret or `text` / secret  Your TLS certificate and key in PEM format for SSL client authentication. If unspecified, no client authentication is performed.  Only valid when the security protocol is `SSL` or `SASL_SSL`.  |
| `SSH TUNNEL` | *Value:* object name  The name of an [SSH tunnel connection](#ssh-tunnel) to route network traffic through by default.  |
| `AWS CONNECTION` | <a name="kafka-aws-connection"></a> *Value:* object name  The name of an [AWS connection](#aws) to use when performing IAM authentication with an Amazon MSK cluster.  Only valid if the security protocol is `SASL_PLAINTEXT` or `SASL_SSL`.  |
| `AWS PRIVATELINK` | *Value:* object name  The name of an [AWS PrivateLink connection](#aws-privatelink) to route network traffic through.  Exactly one of `BROKER`, `BROKERS`, or `AWS PRIVATELINK` must be specified.  |
| `PROGRESS TOPIC` | *Value:* `text`  The name of a topic that Kafka sinks can use to track internal consistency metadata.  Default: `_materialize-progress-{REGION ID}-{CONNECTION ID}`.  |
| `PROGRESS TOPIC REPLICATION FACTOR` | *Value:* `int`  The replication factor to use when creating the progress topic (if the Kafka topic does not already exist).  Default: Broker's default.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `VALIDATE` \| `boolean` \| Whether [connection validation](#connection-validation) should be performed on connection creation. Default: `true`. \|  |

To connect to a Kafka cluster with multiple bootstrap servers, use the `BROKERS`
option:

```mzsql
CREATE CONNECTION kafka_connection TO KAFKA (
    BROKERS ('broker1:9092', 'broker2:9092')
);
```

#### Security protocol examples {#kafka-auth}

**PLAINTEXT:**
> **Warning:** It is insecure to use the `PLAINTEXT` security protocol unless
> you are using a [network security connection](#network-security-connections)
> to tunnel into a private network, as shown below.

```mzsql
CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'unique-jellyfish-0000.prd.cloud.redpanda.com:9092',
    SECURITY PROTOCOL = 'PLAINTEXT',
    SSH TUNNEL ssh_connection
);
```

**SSL:**
With both TLS encryption and TLS client authentication:
```mzsql
CREATE SECRET kafka_ssl_cert AS '-----BEGIN CERTIFICATE----- ...';
CREATE SECRET kafka_ssl_key AS '-----BEGIN PRIVATE KEY----- ...';
CREATE SECRET ca_cert AS '-----BEGIN CERTIFICATE----- ...';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'rp-f00000bar.cloud.redpanda.com:30365',
    SECURITY PROTOCOL = 'SSL'
    SSL CERTIFICATE = SECRET kafka_ssl_cert,
    SSL KEY = SECRET kafka_ssl_key,
    -- Specifying a certificate authority is only required if your cluster's
    -- certificates are not issued by a CA trusted by the Mozilla root store.
    SSL CERTIFICATE AUTHORITY = SECRET ca_cert
);
```

With only TLS encryption:
> **Warning:** It is insecure to use TLS encryption with no authentication unless
> you are using a [network security connection](#network-security-connections)
> to tunnel into a private network as shown below.

```mzsql
CREATE SECRET ca_cert AS '-----BEGIN CERTIFICATE----- ...';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER = 'rp-f00000bar.cloud.redpanda.com:30365',
    SECURITY PROTOCOL = 'SSL',
    SSH TUNNEL ssh_connection,
    -- Specifying a certificate authority is only required if your cluster's
    -- certificates are not issued by a CA trusted by the Mozilla root store.
    SSL CERTIFICATE AUTHORITY = SECRET ca_cert
);
```

**SASL_PLAINTEXT:**
> **Warning:** It is insecure to use the `SASL_PLAINTEXT` security protocol unless
> you are using a [network security connection](#network-security-connections)
> to tunnel into a private network, as shown below.

```mzsql
CREATE SECRET kafka_password AS '...';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9092',
    SECURITY PROTOCOL = 'SASL_PLAINTEXT',
    SASL MECHANISMS = 'SCRAM-SHA-256', -- or `PLAIN` or `SCRAM-SHA-512`
    SASL USERNAME = 'foo',
    SASL PASSWORD = SECRET kafka_password,
    SSH TUNNEL ssh_connection
);
```

**SASL_SSL:**
```mzsql
CREATE SECRET kafka_password AS '...';
CREATE SECRET ca_cert AS '-----BEGIN CERTIFICATE----- ...';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9092',
    SECURITY PROTOCOL = 'SASL_SSL',
    SASL MECHANISMS = 'SCRAM-SHA-256', -- or `PLAIN` or `SCRAM-SHA-512`
    SASL USERNAME = 'foo',
    SASL PASSWORD = SECRET kafka_password,
    -- Specifying a certificate authority is only required if your cluster's
    -- certificates are not issued by a CA trusted by the Mozilla root store.
    SSL CERTIFICATE AUTHORITY = SECRET ca_cert
);
```

**AWS IAM:**

```mzsql
CREATE CONNECTION aws_msk TO AWS (
    ASSUME ROLE ARN = 'arn:aws:iam::000000000000:role/MaterializeMSK',
    REGION = 'us-east-1'
);

CREATE CONNECTION kafka_msk TO KAFKA (
    BROKER 'msk.mycorp.com:9092',
    SECURITY PROTOCOL = 'SASL_SSL',
    AWS CONNECTION = aws_msk
);
```

#### Network security {#kafka-network-security}

If your Kafka broker is not exposed to the public internet, you can tunnel the
connection through an AWS PrivateLink service (Materialize Cloud) or an
SSH bastion host.

**AWS PrivateLink (Materialize Cloud):**

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

Depending on the hosted service you are connecting to, you might need to specify
a PrivateLink connection and [per-availability-zone routing rules for brokers](#kafka-privatelinks) (e.g. Confluent Cloud),
a PrivateLink connection [per advertised broker](#kafka-privatelink-syntax) (e.g. Amazon MSK),
or a single [default PrivateLink connection](#kafka-privatelink-default) (e.g. Redpanda Cloud).

##### Dynamic broker discovery {#kafka-privatelinks}

Confluent Cloud does not require listing every broker individually.
Instead, include a static broker address for the initial connection
alongside wildcard `MATCHING` rules for routing dynamically discovered
brokers through PrivateLink.

```mzsql
CREATE CONNECTION <connection_name> TO KAFKA (
    BROKERS (
        '<broker_address>' USING AWS PRIVATELINK <privatelink_connection>,
        MATCHING '<pattern1>' USING AWS PRIVATELINK <privatelink_connection1> (
            PORT <port1>,
            AVAILABILITY ZONE = '<az_id1>'
        ),
        MATCHING '<pattern2>' USING AWS PRIVATELINK <privatelink_connection2>
    ),
    ...
);

```

| Syntax element | Description |
| --- | --- |
| `'<broker_address>' USING AWS PRIVATELINK ...` | A static broker address used for bootstrapping the initial connection to the Kafka cluster. At least one static broker is required when using `MATCHING` rules. The broker is routed through the specified AWS PrivateLink connection.  |
| `MATCHING '<pattern>' USING AWS PRIVATELINK <connection_name>` | Routes brokers whose advertised `host:port` matches `<pattern>` through the named AWS PrivateLink connection. A pattern may begin with `*` to match any prefix. A pattern may end with `*` to match any suffix. All other characters in the pattern are matched literally. Rules are evaluated in order. The first matching rule wins. If no rule matches, Materialize will attempt to connect to the broker directly, without tunneling.  |
| `AVAILABILITY ZONE` | *Value:* `text`. Optional.  The ID of the availability zone of the AWS PrivateLink service in which the broker is accessible. If omitted, traffic routes through the default PrivateLink endpoint, which distributes across all configured availability zones. Specify this only when you need to pin brokers to specific AZs.  |
| `PORT` | *Value:* `integer`. Optional.  The port of the AWS PrivateLink service to connect to. Defaults to the broker's port.  |

The static broker address is used to bootstrap the initial connection to
Kafka. It does not require an `AVAILABILITY ZONE` — Materialize will
attempt all configured availability zones to find it.

After bootstrapping, Kafka returns the addresses of all brokers in the
cluster. The `MATCHING` rules route these discovered brokers through the
correct AZ-specific PrivateLink endpoint based on their advertised
hostname.

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
    SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
    AVAILABILITY ZONES ('use1-az1', 'use1-az4')
);

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKERS (
        'lkc-xxx.domyyy.us-east-1.aws.confluent.cloud:9092'
            USING AWS PRIVATELINK privatelink_svc,
        MATCHING '*.use1-az1.*' USING AWS PRIVATELINK privatelink_svc (AVAILABILITY ZONE = 'use1-az1'),
        MATCHING '*.use1-az4.*' USING AWS PRIVATELINK privatelink_svc (AVAILABILITY ZONE = 'use1-az4')
    )
);
```

##### Broker connection syntax {#kafka-privatelink-syntax}

> **Warning:** If your Kafka cluster advertises brokers that are not specified
> in the `BROKERS` clause, Materialize will attempt to connect to
> those brokers without any tunneling.

```mzsql
CREATE CONNECTION <connection_name> TO KAFKA (
    BROKERS (
        '<broker1>:<port1>' USING <tunnel_option>,
        '<broker2>:<port2>' USING <tunnel_option>
    ),
    ...
);

```

| Syntax element | Description |
| --- | --- |
| `<broker>:<port>` | The hostname and port of each Kafka broker.  |
| `USING <tunnel_option>` | Specifies how to connect to each broker (e.g., via AWS PrivateLink or SSH tunnel).  |

##### `kafka_broker`

```mzsql
'<broker>:<port>' USING AWS PRIVATELINK <connection_name> (
    AVAILABILITY ZONE = '<az_id>',
    PORT = <port>
)

```

| Syntax element | Description |
| --- | --- |
| `AWS PRIVATELINK <connection_name>` | The name of an AWS PrivateLink connection through which network traffic for this broker should be routed.  |
| `AVAILABILITY ZONE` | The ID of the availability zone of the AWS PrivateLink service in which the broker is accessible.  |
| `PORT` | The port of the AWS PrivateLink service to connect to.  |

The `USING` clause specifies that Materialize Cloud should connect to the
designated broker via an AWS PrivateLink service. Brokers do not need to be
configured the same way, but the clause must be individually attached to each
broker that you want to connect to via the tunnel.

##### Broker connection options {#kafka-privatelink-options}

Field                                   | Value            | Required | Description
----------------------------------------|------------------|:--------:|-------------------------------
`AWS PRIVATELINK`                       | object name      | ✓        | The name of an [AWS PrivateLink connection](#aws-privatelink) through which network traffic for this broker should be routed.
`AVAILABILITY ZONE`                     | `text`           |          | The ID of the availability zone of the AWS PrivateLink service in which the broker is accessible.
`PORT`                                  | `integer`        |          | The port of the AWS PrivateLink service to connect to. Defaults to the broker's port.

##### Example {#kafka-privatelink-example}

Suppose you have the following infrastructure:

  * A Kafka cluster consisting of two brokers named `broker1` and `broker2`,
    both listening on port 9092.

  * A Network Load Balancer that forwards port 9092 to `broker1:9092` and port
    9093 to `broker2:9092`.

  * A PrivateLink endpoint service attached to the load balancer.

You can create a connection to this Kafka broker in Materialize like so:

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
    SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
    AVAILABILITY ZONES ('use1-az1', 'use1-az4')
);

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKERS (
        'broker1:9092' USING AWS PRIVATELINK privatelink_svc,
        'broker2:9092' USING AWS PRIVATELINK privatelink_svc (PORT 9093)
    )
);
```

##### Default connections {#kafka-privatelink-default}

[Redpanda Cloud](/ingest-data/redpanda/redpanda-cloud/) does not require
listing every broker individually. In this case, you should specify a
PrivateLink connection and the port of the bootstrap server instead.

##### Default connection syntax {#kafka-privatelink-default-syntax}

```mzsql
CREATE CONNECTION <connection_name> TO KAFKA (
    AWS PRIVATELINK <privatelink_connection_name> (PORT <port>),
    ...
);

```

| Syntax element | Description |
| --- | --- |
| `AWS PRIVATELINK <privatelink_connection_name>` | *Value:* object name. Required.  The name of an AWS PrivateLink connection through which network traffic should be routed.  |
| `PORT` | *Value:* `integer`  The port of the AWS PrivateLink service to connect to. Defaults to the broker's port.  |

##### Example {#kafka-privatelink-default-example}

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
    SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
    AVAILABILITY ZONES ('use1-az1')
);

CREATE CONNECTION kafka_connection TO KAFKA (
    AWS PRIVATELINK (PORT 30292)
    SECURITY PROTOCOL = 'SASL_PLAINTEXT',
    SASL MECHANISMS = 'SCRAM-SHA-256',
    SASL USERNAME = 'foo',
    SASL PASSWORD = SECRET red_panda_password
);
```

For step-by-step instructions on creating AWS PrivateLink connections and
configuring an AWS PrivateLink service to accept connections from Materialize,
check [this guide](/ops/network-security/privatelink/).

**SSH tunnel:**

##### Syntax {#kafka-ssh-syntax}

> **Warning:** If you do not specify a default `SSH TUNNEL` and your Kafka
> cluster advertises brokers that are not listed in the `BROKERS` clause,
> Materialize will attempt to connect to those brokers without any tunneling.

```mzsql
CREATE CONNECTION <connection_name> TO KAFKA (
    BROKERS (
        '<broker1>:<port1>' USING <tunnel_option>,
        '<broker2>:<port2>' USING <tunnel_option>
    ),
    ...
);

```

| Syntax element | Description |
| --- | --- |
| `<broker>:<port>` | The hostname and port of each Kafka broker.  |
| `USING <tunnel_option>` | Specifies how to connect to each broker (e.g., via AWS PrivateLink or SSH tunnel).  |

##### `kafka_broker`

```mzsql
'<broker>:<port>' USING SSH TUNNEL <connection_name>

```

| Syntax element | Description |
| --- | --- |
| `SSH TUNNEL <connection_name>` | The name of an SSH tunnel connection through which network traffic for this broker should be routed.  |

The `USING` clause specifies that Materialize should connect to the designated
broker via an SSH bastion server. Brokers do not need to be configured the same
way, but the clause must be individually attached to each broker that you want
to connect to via the tunnel.

##### Example {#kafka-ssh-example}

Using a default SSH tunnel:

```mzsql
CREATE CONNECTION ssh_connection TO SSH TUNNEL (
    HOST '<SSH_BASTION_HOST>',
    USER '<SSH_BASTION_USER>',
    PORT <SSH_BASTION_PORT>
);

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'broker1:9092',
    SSH TUNNEL ssh_connection
);
```

Using different SSH tunnels for each broker, with a default for brokers that are
not listed:

```mzsql
CREATE CONNECTION ssh1 TO SSH TUNNEL (HOST 'ssh1', ...);
CREATE CONNECTION ssh2 TO SSH TUNNEL (HOST 'ssh2', ...);

CREATE CONNECTION kafka_connection TO KAFKA (
BROKERS (
    'broker1:9092' USING SSH TUNNEL ssh1,
    'broker2:9092' USING SSH TUNNEL ssh2
    )
    SSH TUNNEL ssh_1
);
```

For step-by-step instructions on creating SSH tunnel connections and configuring
an SSH bastion server to accept connections from Materialize, check [this guide](/ops/network-security/ssh-tunnel/).

### Confluent Schema Registry

A Confluent Schema Registry connection establishes a link to a [Confluent Schema
Registry] server. You can use Confluent Schema Registry connections in the
`FORMAT` clause of [`CREATE SOURCE`] and [`CREATE SINK`] statements.

#### Syntax {#csr-syntax}

```mzsql
CREATE CONNECTION <connection_name> TO CONFLUENT SCHEMA REGISTRY (
    URL '<url>',
    USERNAME = { '<username>' | SECRET <secret_name> },
    PASSWORD = SECRET <secret_name>,
    SSL CERTIFICATE = { '<pem>' | SECRET <secret_name> },
    SSL KEY = SECRET <secret_name>,
    SSL CERTIFICATE AUTHORITY = { '<pem>' | SECRET <secret_name> },
    AWS PRIVATELINK <privatelink_connection_name>,
    SSH TUNNEL <ssh_connection_name>
)
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `URL` | *Value:* `text`. Required.  The schema registry URL.  |
| `USERNAME` / `PASSWORD` | *Value:* secret or `text` / secret  Credentials for basic HTTP authentication. `PASSWORD` is required and only valid if `USERNAME` is specified.  |
| `SSL CERTIFICATE` / `SSL KEY` | *Value:* secret or `text` / secret  Your TLS certificate and key in PEM format for TLS client authentication. If unspecified, no TLS client authentication is performed.  Only respected if the URL uses the `https` protocol.  |
| `SSL CERTIFICATE AUTHORITY` | *Value:* secret or `text`  The certificate authority (CA) certificate in PEM format. Used to validate the server's TLS certificate. If unspecified, uses the system's default CA certificates.  Only respected if the URL uses the `https` protocol.  |
| `AWS PRIVATELINK` | *Value:* object name  The name of an [AWS PrivateLink connection](#aws-privatelink) to route network traffic through.  |
| `SSH TUNNEL` | *Value:* object name  The name of an [SSH tunnel connection](#ssh-tunnel) to route network traffic through.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `VALIDATE` \| `boolean` \| Whether [connection validation](#connection-validation) should be performed on connection creation. Default: `true`. \|  |

#### Examples {#csr-example}

Using username and password authentication with TLS encryption:

```mzsql
CREATE SECRET csr_password AS '...';
CREATE SECRET ca_cert AS '-----BEGIN CERTIFICATE----- ...';

CREATE CONNECTION csr_basic TO CONFLUENT SCHEMA REGISTRY (
    URL 'https://rp-f00000bar.cloud.redpanda.com:30993',
    USERNAME = 'foo',
    PASSWORD = SECRET csr_password
    -- Specifying a certificate authority is only required if your cluster's
    -- certificates are not issued by a CA trusted by the Mozilla root store.
    SSL CERTIFICATE AUTHORITY = SECRET ca_cert
);
```

Using TLS for encryption and authentication:

```mzsql
CREATE SECRET csr_ssl_cert AS '-----BEGIN CERTIFICATE----- ...';
CREATE SECRET csr_ssl_key AS '-----BEGIN PRIVATE KEY----- ...';
CREATE SECRET ca_cert AS '-----BEGIN CERTIFICATE----- ...';

CREATE CONNECTION csr_ssl TO CONFLUENT SCHEMA REGISTRY (
    URL 'https://rp-f00000bar.cloud.redpanda.com:30993',
    SSL CERTIFICATE = SECRET csr_ssl_cert,
    SSL KEY = SECRET csr_ssl_key,
    -- Specifying a certificate authority is only required if your cluster's
    -- certificates are not issued by a CA trusted by the Mozilla root store.
    SSL CERTIFICATE AUTHORITY = SECRET ca_cert
);
```

#### Network security {#csr-network-security}

If your Confluent Schema Registry server is not exposed to the public internet,
you can tunnel the connection through an AWS PrivateLink service (Materialize Cloud) or an SSH bastion host.

**AWS PrivateLink (Materialize Cloud):**

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

##### Example {#csr-privatelink-example}

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
    SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
    AVAILABILITY ZONES ('use1-az1', 'use1-az4')
);

CREATE CONNECTION csr_privatelink TO CONFLUENT SCHEMA REGISTRY (
    URL 'http://my-confluent-schema-registry:8081',
    AWS PRIVATELINK privatelink_svc
);
```

**SSH tunnel:**

##### Example {#csr-ssh-example}

```mzsql
CREATE CONNECTION ssh_connection TO SSH TUNNEL (
    HOST '<SSH_BASTION_HOST>',
    USER '<SSH_BASTION_USER>',
    PORT <SSH_BASTION_PORT>
);

CREATE CONNECTION csr_ssh TO CONFLUENT SCHEMA REGISTRY (
    URL 'http://my-confluent-schema-registry:8081',
    SSH TUNNEL ssh_connection
);
```

### AWS Glue Schema Registry

> **Public Preview:** This feature is in public preview.

An AWS Glue Schema Registry connection establishes a link to an [AWS Glue Schema
Registry]. You can use AWS Glue Schema Registry connections in the `FORMAT`
clause of [`CREATE SOURCE`] statements to decode Avro-encoded messages, and of
[`CREATE SINK`] statements to encode them, with schemas managed in AWS Glue.

The connection authenticates to AWS through a separate [AWS connection](#aws),
which supplies the credentials and region. See [AWS](#aws) for how to grant
Materialize access to your AWS account.

#### Syntax {#glue-syntax}

```mzsql
CREATE CONNECTION <connection_name> TO AWS GLUE SCHEMA REGISTRY (
    AWS CONNECTION = <aws_connection_name>,
    REGISTRY = '<registry_name>'
)
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `AWS CONNECTION` | *Value:* object name. Required.  The name of an [AWS connection](#aws) that provides the credentials Materialize uses to authenticate to AWS Glue. The Schema Registry's region is taken from this connection.  |
| `REGISTRY` | *Value:* `text`. Required.  The name of the AWS Glue Schema Registry to use (for example, `default-registry`). Sources read schemas from the registry, and sinks register schemas in it. The registry must already exist. Must not be empty.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `VALIDATE` \| `boolean` \| Whether [connection validation](#connection-validation) should be performed on connection creation. Default: `true`. \|  |

#### Examples {#glue-example}

```mzsql
CREATE CONNECTION aws_conn TO AWS (
    ASSUME ROLE ARN = 'arn:aws:iam::123456789000:role/MaterializeGlue'
);

CREATE CONNECTION glue_conn TO AWS GLUE SCHEMA REGISTRY (
    AWS CONNECTION = aws_conn,
    REGISTRY = 'default-registry'
);
```

#### Permissions {#glue-permissions}

The IAM role assumed by the [AWS connection](#aws) must be allowed to access the
registry. Sources only read. Sinks also register schemas. Materialize uses the
following AWS Glue actions:

| Action | When it is used |
|--------|-----------------|
| `glue:GetRegistry` | At connection creation, to validate the connection. Only required when `VALIDATE` is `true` (the default). |
| `glue:GetSchemaVersion` | Source: when the source is created, to pin the schema, and at runtime, to fetch the writer schema for each new schema version encountered. Sink: to poll a newly registered schema version until it becomes available. Always required. |
| `glue:GetSchemaByDefinition` | Sink, to find an existing version matching the schema being registered. |
| `glue:RegisterSchemaVersion` | Sink, to add a version to an existing schema. |
| `glue:CreateSchema` | Sink, to create a schema on its first publish. |
| `glue:GetSchema` | Sink, to read an existing schema's compatibility level and warn when it differs from the requested one. Optional. |

A least-privilege policy for a source, scoped to a single registry, grants only
the read actions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "glue:GetRegistry",
                "glue:GetSchemaVersion"
            ],
            "Resource": [
                "arn:aws:glue:<region>:<account>:registry/<registry-name>",
                "arn:aws:glue:<region>:<account>:schema/<registry-name>/*"
            ]
        }
    ]
}
```

A sink additionally needs the schema-write actions on the same resources:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "glue:GetRegistry",
                "glue:GetSchemaVersion",
                "glue:GetSchemaByDefinition",
                "glue:RegisterSchemaVersion",
                "glue:CreateSchema",
                "glue:GetSchema"
            ],
            "Resource": [
                "arn:aws:glue:<region>:<account>:registry/<registry-name>",
                "arn:aws:glue:<region>:<account>:schema/<registry-name>/*"
            ]
        }
    ]
}
```

If you create the connection with `WITH (VALIDATE = false)`, you can omit
`glue:GetRegistry`. The registry itself must already exist. Materialize sinks
create and version schemas within it but never create the registry. For details
on creating and authorizing the AWS connection, see [AWS](#aws).

### MySQL

A MySQL connection establishes a link to a [MySQL] server. You can use
MySQL connections to create [sources](/sql/create-source/mysql).

#### Syntax {#mysql-syntax}

```mzsql
CREATE CONNECTION <connection_name> TO MYSQL (
    HOST '<hostname>',
    PORT <port>,
    USER '<username>',
    PASSWORD SECRET <secret_name>,
    SSL MODE = { 'disabled' | 'required' | 'verify_ca' | 'verify_identity' },
    SSL CERTIFICATE AUTHORITY = { '<pem>' | SECRET <secret_name> },
    SSL CERTIFICATE = { '<pem>' | SECRET <secret_name> },
    SSL KEY = SECRET <secret_name>,
    AWS CONNECTION <aws_connection_name>,
    AWS PRIVATELINK <privatelink_connection_name>,
    SSH TUNNEL <ssh_connection_name>
)
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `HOST` | *Value:* `text`. Required.  Database hostname.  |
| `PORT` | *Value:* `integer`  Port number to connect to at the server host.  Default: `3306`.  |
| `USER` | *Value:* `text`. Required.  Database username.  |
| `PASSWORD` | *Value:* secret  Password for the connection.  |
| `SSL MODE` | *Value:* `text`  Enables SSL connections if set to `required`, `verify_ca`, or `verify_identity`. See the [MySQL documentation](https://dev.mysql.com/doc/refman/8.0/en/using-encrypted-connections.html) for more details.  Default: `disabled`.  |
| `SSL CERTIFICATE AUTHORITY` | *Value:* secret or `text`  The certificate authority (CA) certificate in PEM format. Used for both SSL client and server authentication. If unspecified, uses the system's default CA certificates.  |
| `SSL CERTIFICATE` / `SSL KEY` | *Value:* secret or `text` / secret  Client SSL certificate and key in PEM format.  |
| `AWS CONNECTION` | <a name="mysql-aws-connection"></a> *Value:* object name  The name of an [AWS connection](#aws) to use when performing IAM authentication with an Amazon RDS MySQL cluster.  Only valid if `SSL MODE` is set to `required`, `verify_ca`, or `verify_identity`. Incompatible with `PASSWORD` being set.  |
| `AWS PRIVATELINK` | *Value:* object name  The name of an [AWS PrivateLink connection](#aws-privatelink) to route network traffic through.  |
| `SSH TUNNEL` | *Value:* object name  The name of an [SSH tunnel connection](#ssh-tunnel) to route network traffic through.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `VALIDATE` \| `boolean` \| Whether [connection validation](#connection-validation) should be performed on connection creation. Default: `true`. \|  |

#### Example {#mysql-example}

```mzsql
CREATE SECRET mysqlpass AS '<POSTGRES_PASSWORD>';

CREATE CONNECTION mysql_connection TO MYSQL (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 3306,
    USER 'root',
    PASSWORD SECRET mysqlpass
);
```

#### Network security {#mysql-network-security}

If your MySQL server is not exposed to the public internet, you can tunnel the
connection through an AWS PrivateLink service (Materialize Cloud) or an
SSH bastion host.

**AWS PrivateLink (Materialize Cloud):**

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

##### Example {#mysql-privatelink-example}

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
   SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
   AVAILABILITY ZONES ('use1-az1', 'use1-az4')
);

CREATE CONNECTION mysql_connection TO MYSQL (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 3306,
    USER 'root',
    PASSWORD SECRET mysqlpass,
    AWS PRIVATELINK privatelink_svc
);
```

For step-by-step instructions on creating AWS PrivateLink connections and
configuring an AWS PrivateLink service to accept connections from Materialize,
check [this guide](/ops/network-security/privatelink/).

**SSH tunnel:**

##### Example {#mysql-ssh-example}

```mzsql
CREATE CONNECTION tunnel TO SSH TUNNEL (
    HOST 'bastion-host',
    PORT 22,
    USER 'materialize'
);

CREATE CONNECTION mysql_connection TO MYSQL (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    SSH TUNNEL ssh_connection
);
```

For step-by-step instructions on creating SSH tunnel connections and configuring
an SSH bastion server to accept connections from Materialize, check [this guide](/ops/network-security/ssh-tunnel/).

**AWS IAM:**

##### Example {#mysql-aws-connection-example}

```mzsql
CREATE CONNECTION aws_rds_mysql TO AWS (
    ASSUME ROLE ARN = 'arn:aws:iam::000000000000:role/MaterializeRDS',
    REGION = 'us-west-1'
);

CREATE CONNECTION mysql_connection TO MYSQL (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 3306,
    USER 'root',
    AWS CONNECTION aws_rds_mysql,
    SSL MODE 'verify_identity'
);
```

### PostgreSQL

A Postgres connection establishes a link to a single database of a
[PostgreSQL] server. You can use Postgres connections to create [sources](/sql/create-source/postgres).

#### Syntax {#postgres-syntax}

```mzsql
CREATE CONNECTION <connection_name> TO POSTGRES (
    HOST '<hostname>',
    PORT <port>,
    DATABASE '<database>',
    USER '<username>',
    PASSWORD SECRET <secret_name>,
    SSL MODE = { 'disable' | 'require' | 'verify_ca' | 'verify_full' },
    SSL CERTIFICATE AUTHORITY = { '<pem>' | SECRET <secret_name> },
    SSL CERTIFICATE = { '<pem>' | SECRET <secret_name> },
    SSL KEY = SECRET <secret_name>,
    AWS PRIVATELINK <privatelink_connection_name>,
    SSH TUNNEL <ssh_connection_name>
)
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `HOST` | *Value:* `text`. Required.  Database hostname.  |
| `PORT` | *Value:* `integer`  Port number to connect to at the server host.  Default: `5432`.  |
| `DATABASE` | *Value:* `text`. Required.  Target database.  |
| `USER` | *Value:* `text`. Required.  Database username.  |
| `PASSWORD` | *Value:* secret  Password for the connection.  |
| `SSL MODE` | *Value:* `text`  Enables SSL connections if set to `require`, `verify_ca`, or `verify_full`.  Default: `disable`.  |
| `SSL CERTIFICATE AUTHORITY` | *Value:* secret or `text`  The certificate authority (CA) certificate in PEM format. Used for both SSL client and server authentication. If unspecified, uses the system's default CA certificates.  |
| `SSL CERTIFICATE` / `SSL KEY` | *Value:* secret or `text` / secret  Client SSL certificate and key in PEM format.  |
| `AWS PRIVATELINK` | *Value:* object name  The name of an [AWS PrivateLink connection](#aws-privatelink) to route network traffic through.  |
| `SSH TUNNEL` | *Value:* object name  The name of an [SSH tunnel connection](#ssh-tunnel) to route network traffic through.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `VALIDATE` \| `boolean` \| Whether [connection validation](#connection-validation) should be performed on connection creation. Default: `true`. \|  |

#### Example {#postgres-example}

```mzsql
CREATE SECRET pgpass AS '<POSTGRES_PASSWORD>';

CREATE CONNECTION pg_connection TO POSTGRES (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 5432,
    USER 'postgres',
    PASSWORD SECRET pgpass,
    SSL MODE 'require',
    DATABASE 'postgres'
);
```

#### Network security {#postgres-network-security}

If your PostgreSQL server is not exposed to the public internet, you can tunnel
the connection through an AWS PrivateLink service (Materialize Cloud)or an SSH bastion host.

**AWS PrivateLink:**

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

##### Example {#postgres-privatelink-example}

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
   SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
   AVAILABILITY ZONES ('use1-az1', 'use1-az4')
);

CREATE CONNECTION pg_connection TO POSTGRES (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 5432,
    DATABASE postgres,
    USER postgres,
    PASSWORD SECRET pgpass,
    AWS PRIVATELINK privatelink_svc
);
```

For step-by-step instructions on creating AWS PrivateLink connections and
configuring an AWS PrivateLink service to accept connections from Materialize,
check [this guide](/ops/network-security/privatelink/).

**SSH tunnel:**

##### Example {#postgres-ssh-example}

```mzsql
CREATE CONNECTION tunnel TO SSH TUNNEL (
    HOST 'bastion-host',
    PORT 22,
    USER 'materialize'
);

CREATE CONNECTION pg_connection TO POSTGRES (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 5432,
    SSH TUNNEL tunnel,
    DATABASE 'postgres'
);
```

For step-by-step instructions on creating SSH tunnel connections and configuring
an SSH bastion server to accept connections from Materialize, check [this guide](/ops/network-security/ssh-tunnel/).

### SQL Server

A SQL Server connection establishes a link to a single database of a
[SQL Server] instance. You can use SQL Server connections to create [sources](/sql/create-source/sql-server).

#### Syntax {#sql-server-syntax}

```mzsql
CREATE CONNECTION <connection_name> TO SQL SERVER (
    HOST '<hostname>',
    PORT <port>,
    DATABASE '<database>',
    USER '<username>',
    PASSWORD SECRET <secret_name>,
    SSL MODE = { 'disabled' | 'required' | 'verify_ca' | 'verify' },
    SSL CERTIFICATE AUTHORITY = { '<pem>' | SECRET <secret_name> }
)
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `HOST` | *Value:* `text`. Required.  Database hostname.  |
| `PORT` | *Value:* `integer`  Port number to connect to at the server host.  Default: `1433`.  |
| `DATABASE` | *Value:* `text`. Required.  Target database.  |
| `USER` | *Value:* `text`. Required.  Database username.  |
| `PASSWORD` | *Value:* secret. Required.  Password for the connection.  |
| `SSL MODE` | *Value:* `text`  Enables SSL connections if set to `required`, `verify_ca`, or `verify`. See the [SQL Server documentation](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/configure-sql-server-encryption) for more details.  - `disabled` - no encryption. - `required` - encryption required, no certificate validation. - `verify` - encryption required, validate server certificate using OS configured CA. - `verify_ca` - encryption required, validate server certificate using provided CA certificates (requires `SSL CERTIFICATE AUTHORITY`).  Default: `disabled`.  |
| `SSL CERTIFICATE AUTHORITY` | *Value:* secret or `text`  One or more client SSL certificates in PEM format.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `VALIDATE` \| `boolean` \| Whether [connection validation](#connection-validation) should be performed on connection creation. Default: `true`. \|  |

#### Example {#sql-server-example}

```mzsql
CREATE SECRET sqlserver_pass AS '<SQL_SERVER_PASSWORD>';

CREATE CONNECTION sqlserver_connection TO SQL SERVER (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 1433,
    USER 'SA',
    PASSWORD SECRET sqlserver_pass,
    DATABASE 'my_db'
);
```

### Iceberg Catalog

> **Public Preview:** This feature is in public preview.

An Iceberg catalog connection establishes a link to an [Apache Iceberg](https://iceberg.apache.org/)
catalog. You can use Iceberg catalog connections to create [Iceberg sinks](/sql/create-sink/iceberg).

Materialize supports the following catalog type and destination combinations:

| Catalog type | Destination | Authentication |
| --- | --- | --- |
| `'s3tablesrest'` | [AWS S3 Tables](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html) | [AWS connection](#aws) |
| `'rest'` | [Google Cloud BigLake](https://docs.cloud.google.com/lakehouse/docs/lakehouse-iceberg-rest-catalog) <a class="private-preview-inline" href="https://materialize.com/preview-terms/">(feature in private preview)</a>
 | [GCP connection](#gcp) |
| `'rest'` | Any [Iceberg REST catalog](https://iceberg.apache.org/spec/), including [Databricks Unity Catalog](/export-data/iceberg-databricks/) | OAuth2 credentials in a secret |

#### Syntax {#iceberg-catalog-syntax}

**AWS S3 Tables:**

```mzsql
CREATE CONNECTION <connection_name> TO ICEBERG CATALOG (
    CATALOG TYPE = 's3tablesrest',
    URL = '<catalog_url>',
    WAREHOUSE = '<warehouse>',
    AWS CONNECTION = <aws_connection>
);

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `URL` | *Value:* `text`. Required.  S3 Tables Iceberg catalog URL: `https://s3tables.<region>.amazonaws.com/iceberg`  |
| `WAREHOUSE` | *Value:* `text`. Required.  S3 Tables bucket ARN: `arn:aws:s3tables:<region>:<account-id>:bucket/<bucket-name>`  |
| `AWS CONNECTION` | *Value:* object name. Required.  The name of an [AWS connection](#aws) to use for authentication.  |

**GCP BigLake:**

```mzsql
CREATE CONNECTION <connection_name> TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = '<catalog_url>',
    WAREHOUSE = '<warehouse>',
    GCP CONNECTION = <gcp_connection>,
    ACCESS DELEGATION = 'vended-credentials'
);

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `URL` | *Value:* `text`. Required.  GCP BigLake Iceberg catalog URL: `https://biglake.googleapis.com/iceberg/v1/restcatalog`  |
| `WAREHOUSE` | *Value:* `text`. Required.  GCS bucket URI: `gs://<bucket>`  |
| `GCP CONNECTION` | *Value:* object name. Required.  The name of a [GCP connection](#gcp) to use for authentication.  |
| `ACCESS DELEGATION` | *Value:* `'vended-credentials'`. Optional.  Requests temporary, table-scoped storage credentials from the catalog. Requires [credential vending enabled on the catalog](https://docs.cloud.google.com/lakehouse/docs/enable-credential-vending). Omit it to reach the warehouse bucket with the GCP connection's service account instead.  See [Storage access delegation](/sql/create-connection/#iceberg-catalog-access-delegation).  |

**Iceberg REST catalog:**

> **Public Preview:** This feature is in public preview.

```mzsql
CREATE CONNECTION <connection_name> TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = '<catalog_url>',
    WAREHOUSE = '<warehouse>',
    CREDENTIAL = SECRET <secret_name>,
    OAUTH2 SERVER URL = '<token_url>',
    SCOPE = '<scope>',
    ACCESS DELEGATION = 'vended-credentials'
);

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `URL` | *Value:* `text`. Required.  The catalog's Iceberg REST endpoint, the path the catalog serves `/v1/` under. Consult your catalog's documentation for the exact URL.  |
| `WAREHOUSE` | *Value:* `text`. Optional.  The warehouse to operate in. What this names is catalog-specific: some catalogs expect a storage location, others the name of a catalog or warehouse object.  |
| `CREDENTIAL` | *Value:* secret name or `text`. Required unless `GCP CONNECTION` is used.  OAuth2 client credentials as `<client_id>:<client_secret>`. A value with no colon is sent as the client secret alone.  |
| `OAUTH2 SERVER URL` | *Value:* `text`. Optional.  The token endpoint to exchange `CREDENTIAL` at. Defaults to `<url>/v1/oauth/tokens`, the endpoint the Iceberg REST specification derives from the catalog URL.  Required for catalogs that serve their token endpoint elsewhere, or behind an auth gateway that will not serve an unauthenticated exchange.  |
| `SCOPE` | *Value:* `text`. Optional.  The OAuth2 scope to request. Defaults to `catalog`, the scope the Iceberg REST specification defines.  |
| `ACCESS DELEGATION` | *Value:* `'vended-credentials'`. Optional.  Requests temporary, table-scoped storage credentials from the catalog. Required for catalogs that manage their own storage and vend credentials as the only way to reach it.  See [Storage access delegation](/sql/create-connection/#iceberg-catalog-access-delegation).  |

#### Examples {#iceberg-catalog-examples}

**AWS S3 Tables:**

The following example creates an [AWS connection](/sql/create-connection/#aws) and an [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog) for AWS S3 Tables:
```mzsql
-- First, create an AWS connection for authentication
CREATE CONNECTION aws_connection
  TO AWS (ASSUME ROLE ARN = 'arn:aws:iam::123456789012:role/MaterializeIceberg');

-- Create the Iceberg catalog connection pointing to S3 Tables
CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 's3tablesrest',
    URL = 'https://s3tables.us-east-1.amazonaws.com/iceberg',
    WAREHOUSE = 'arn:aws:s3tables:us-east-1:123456789012:bucket/my-table-bucket',
    AWS CONNECTION = aws_connection
);

```

**GCP BigLake:**

The following example creates a [GCP connection](/sql/create-connection/#gcp) and an [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog) for Google Cloud BigLake. The service account reaches both the catalog and the warehouse bucket, so no credential vending is involved:
```mzsql
-- Using the base64-encoded service account key (e.g. base64 < sa_key.json)
CREATE SECRET gcp_service_account_key
  AS decode('<base64-encoded service account key JSON>', 'base64');

-- Create a GCP connection that uses the service-account key.
CREATE CONNECTION gcp_connection TO GCP (
    SERVICE ACCOUNT KEY = SECRET gcp_service_account_key
);

-- Create the Iceberg catalog connection pointing to BigLake.
CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = 'https://biglake.googleapis.com/iceberg/v1/restcatalog',
    WAREHOUSE = 'gs://<bucket>',
    GCP CONNECTION = gcp_connection
);

```

**Iceberg REST catalog:**

> **Public Preview:** This feature is in public preview.

The following example creates an [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog) for Databricks Unity Catalog:
```mzsql
-- Store the service principal's OAuth credentials as `<client_id>:<client_secret>`.
CREATE SECRET databricks_oauth
  AS '<client_id>:<client_secret>';

-- Create the Iceberg catalog connection pointing to Unity Catalog.
CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = 'https://<workspace>.cloud.databricks.com/api/2.1/unity-catalog/iceberg-rest',
    WAREHOUSE = '<catalog_name>',
    CREDENTIAL = SECRET databricks_oauth,
    OAUTH2 SERVER URL = 'https://<workspace>.cloud.databricks.com/oidc/v1/token',
    SCOPE = 'all-apis',
    ACCESS DELEGATION = 'vended-credentials'
);

```

#### Storage access delegation {#iceberg-catalog-access-delegation}

Some Iceberg catalogs manage the object storage behind their tables and mint
temporary, table-scoped credentials for it on request, rather than expecting
clients to hold credentials of their own. The Iceberg specification calls this
credential vending.

The `ACCESS DELEGATION` option asks the catalog to vend credentials:

| | |
| --- | --- |
| **Value** | `'vended-credentials'`. This is the only accepted value. |
| **Default** | Unset, meaning Materialize does not request delegation. |
| **Valid with** | `CATALOG TYPE = 'rest'`, using either `CREDENTIAL` or `GCP CONNECTION`. Not supported for `CATALOG TYPE = 's3tablesrest'`, which authenticates to storage through an [AWS connection](#aws). |

Exactly one source of storage credentials is used, determined by how the
connection is configured. There is no fallback between them:

| Connection | Storage credentials used |
| --- | --- |
| `CATALOG TYPE = 'rest'` with `CREDENTIAL` and `ACCESS DELEGATION` | Only the table-scoped credentials the catalog vends, refreshed as they expire. Any storage credentials the catalog returns in its configuration are ignored. |
| `CATALOG TYPE = 'rest'` with `CREDENTIAL` and no `ACCESS DELEGATION` | Only the storage credentials the catalog returns in its configuration. |
| `CATALOG TYPE = 'rest'` with `GCP CONNECTION` and `ACCESS DELEGATION` | Only the table-scoped credentials the catalog vends, refreshed as they expire. The GCP connection's service account then authenticates the catalog alone. |
| `CATALOG TYPE = 'rest'` with `GCP CONNECTION` and no `ACCESS DELEGATION` | Only the GCP connection's service account. |
| `CATALOG TYPE = 's3tablesrest'` | Only the AWS connection's credentials, for both the catalog and its storage. |

Delegation is opt-in rather than always requested, because a catalog that gates
it behind privileges the principal does not hold rejects the whole request
rather than falling back. Requesting it unconditionally would break connections
that work today.

Some catalogs, including [Databricks Unity
Catalog](/export-data/iceberg-databricks/), vend
credentials as the only
way to reach their storage, so `ACCESS DELEGATION` is required there rather than
optional.

For more information about using Iceberg sinks, see the [Iceberg sink documentation](/export-data/iceberg/).

## Network security connections

### AWS PrivateLink (Materialize Cloud) {#aws-privatelink}

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

An AWS PrivateLink connection establishes a link to an [AWS PrivateLink] service.
You can use AWS PrivateLink connections in [Confluent Schema Registry connections](#confluent-schema-registry),
[Kafka connections](#kafka), and [Postgres connections](#postgresql).

#### Syntax {#aws-privatelink-syntax}

```mzsql
CREATE CONNECTION <connection_name> TO AWS PRIVATELINK (
    SERVICE NAME '<service_name>',
    AVAILABILITY ZONES ('<az_id1>', '<az_id2>', ...)
);

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `SERVICE NAME` | *Value:* `text`. Required.  The name of the AWS VPC endpoint service, which always starts with `com.amazonaws.`.  |
| `AVAILABILITY ZONES` | *Value:* `text[]`. Required.  The IDs of the AWS availability zones in which the service is accessible.  |

#### Permissions {#aws-privatelink-permissions}

Materialize assigns a unique principal to each AWS PrivateLink connection in
your region using an Amazon Resource Name of the
following form:

```
arn:aws:iam::664411391173:role/mz_<REGION-ID>_<CONNECTION-ID>
```

After creating the connection, you must configure the AWS PrivateLink service
to accept connections from the AWS principal Materialize will connect as. The
principals for AWS PrivateLink connections in your region are stored in
the [`mz_aws_privatelink_connections`](/sql/system-catalog/mz_catalog/#mz_aws_privatelink_connections)
system table.

```mzsql
SELECT * FROM mz_aws_privatelink_connections;
```
```
   id   |                                 principal
--------+---------------------------------------------------------------------------
 u1     | arn:aws:iam::664411391173:role/mz_20273b7c-2bbe-42b8-8c36-8cc179e9bbc3_u1
 u7     | arn:aws:iam::664411391173:role/mz_20273b7c-2bbe-42b8-8c36-8cc179e9bbc3_u7
```

For more details on configuring a trusted principal for your AWS PrivateLink service,
see the [AWS PrivateLink documentation](https://docs.aws.amazon.com/vpc/latest/privatelink/configure-endpoint-service.html#add-remove-permissions).

> **Warning:** Do **not** grant access to the root principal for the Materialize AWS account.
> Doing so will allow any Materialize customer to create a connection to your
> AWS PrivateLink service.

#### Accepting connection requests {#aws-privatelink-requests}

If your AWS PrivateLink service is configured to require acceptance of
connection requests, you must additionally approve the connection request from
Materialize after creating the connection. For more details on manually
accepting connection requests, see the [AWS PrivateLink documentation](https://docs.aws.amazon.com/vpc/latest/privatelink/configure-endpoint-service.html#accept-reject-connection-requests).

#### Example {#aws-privatelink-example}

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
    SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
    AVAILABILITY ZONES ('use1-az1', 'use1-az4')
);
```

### SSH tunnel

An SSH tunnel connection establishes a link to an SSH bastion server. You can
use SSH tunnel connections in [Kafka connections](#kafka), [MySQL connections](#mysql),
and [Postgres connections](#postgresql).

#### Syntax {#ssh-tunnel-syntax}

```mzsql
CREATE CONNECTION <connection_name> TO SSH TUNNEL (
    HOST '<hostname>',
    PORT <port>,
    USER '<username>'
);

```

| Syntax element | Description |
| --- | --- |
| `<connection_name>` | A name for the connection.  |
| `HOST` | *Value:* `text`. Required.  The hostname of the SSH bastion server.  |
| `PORT` | *Value:* `integer`. Required.  The port to connect to.  |
| `USER` | *Value:* `text`. Required.  The name of the user to connect as.  |

#### Key pairs {#ssh-tunnel-keypairs}

Materialize automatically manages the key pairs for an SSH tunnel connection.
Each connection is associated with two key pairs. The private key for each key
pair is stored securely within your region and cannot be retrieved. The public
key for each key pair is stored in the [`mz_ssh_tunnel_connections`] system
table.

When Materialize connects to the SSH bastion server, it presents both keys for
authentication. To allow key pair rotation without downtime, you should
configure your SSH bastion server to accept both key pairs. You can
then **rotate the key pairs** using [`ALTER CONNECTION`].

Materialize currently generates SSH key pairs using the [Ed25519 algorithm],
which is fast, secure, and [recommended by security
professionals][latacora-crypto]. Some legacy SSH servers do not support the
Ed25519 algorithm. You will not be able to use these servers with Materialize's
SSH tunnel connections.

We routinely evaluate the security of the cryptographic algorithms in use in
Materialize. Future versions of Materialize may use a different SSH key
generation algorithm as security best practices evolve.

#### Examples {#ssh-tunnel-example}

Create an SSH tunnel connection:

```mzsql
CREATE CONNECTION ssh_connection TO SSH TUNNEL (
    HOST 'bastion-host',
    PORT 22,
    USER 'materialize'
);
```

Retrieve the public keys for the SSH tunnel connection you just created:

```mzsql
SELECT
    mz_connections.name,
    mz_ssh_tunnel_connections.*
FROM
    mz_connections
JOIN
    mz_ssh_tunnel_connections USING(id)
WHERE
    mz_connections.name = 'ssh_connection';
```
```
 id    | public_key_1                          | public_key_2
-------+---------------------------------------+---------------------------------------
 ...   | ssh-ed25519 AAAA...76RH materialize   | ssh-ed25519 AAAA...hLYV materialize
```

## Connection validation {#connection-validation}

Materialize automatically validates the connection and authentication parameters
for most connection types on connection creation:

Connection type             | Validated by default |
----------------------------|----------------------|
AWS                         |                      |
Kafka                       | ✓                    |
Confluent Schema Registry   | ✓                    |
AWS Glue Schema Registry    | ✓                    |
MySQL                       | ✓                    |
PostgreSQL                  | ✓                    |
SSH Tunnel                  |                      |
AWS PrivateLink             |                      |

For connection types that are validated by default, if the validation step
fails, the creation of the connection will also fail and a validation error is
returned. You can disable connection validation by setting the `VALIDATE`
option to `false`. This is useful, for example, when the parameters are known
to be correct but the external system is unavailable at the time of creation.

Connection types that require additional setup steps after creation, like AWS
and SSH tunnel connections, can be **manually validated** using the [`VALIDATE
CONNECTION`](/sql/validate-connection) syntax once all setup steps are
completed.

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all connections and secrets used in the connection definition.
- `USAGE` privileges on the schemas that all connections and secrets in the statement are contained in.

## Related pages

- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE SOURCE`](/sql/create-source)
- [`CREATE SINK`](/sql/create-sink)

[AWS PrivateLink]: https://aws.amazon.com/privatelink/
[Confluent Schema Registry]: https://docs.confluent.io/platform/current/schema-registry/index.html#sr-overview
[AWS Glue Schema Registry]: https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html
[Kafka]: https://kafka.apache.org
[MySQL]: https://www.mysql.com/
[PostgreSQL]: https://www.postgresql.org
[SQL Server]: https://www.microsoft.com/en-us/sql-server
[`ALTER CONNECTION`]: /sql/alter-connection
[`CREATE SOURCE`]: /sql/create-source
[`CREATE SINK`]: /sql/create-sink
[`mz_aws_privatelink_connections`]: /sql/system-catalog/mz_catalog/#mz_aws_privatelink_connections
[`mz_connections`]: /sql/system-catalog/mz_catalog/#mz_connections
[`mz_ssh_tunnel_connections`]: /sql/system-catalog/mz_catalog/#mz_ssh_tunnel_connections
[Ed25519 algorithm]: https://ed25519.cr.yp.to
[latacora-crypto]: https://latacora.micro.blog/2018/04/03/cryptographic-right-answers.html
[trust policy]: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_terms-and-concepts.html#term_trust-policy
[external ID]: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html

<!-- mz-docs page: sql/create-database -->

# CREATE DATABASE
`CREATE DATABASE` creates a new database.
Use `CREATE DATABASE` to create a new database.

## Syntax

```mzsql
CREATE DATABASE [IF NOT EXISTS] <database_name>;

```

| Syntax element | Description |
| --- | --- |
| `IF NOT EXISTS` | If specified, do not generate an error if a database of the same name already exists. If not specified, throw an error if a database of the same name already exists.  |
| `<database_name>` | A name for the database.  |

## Details

Databases can contain schemas. By default, each database has a schema called
`public`. For more information about databases, see
[Namespaces](/sql/namespaces).

## Examples

```mzsql
CREATE DATABASE IF NOT EXISTS my_db;
```
```mzsql
SHOW DATABASES;
```
```nofmt
materialize
my_db
```

## Privileges

The privileges required to execute this statement are:

- `CREATEDB` privileges on the system.

## Related pages

- [`DROP DATABASE`](../drop-database)
- [`SHOW DATABASES`](../show-databases)

<!-- mz-docs page: sql/create-index -->

# CREATE INDEX
`CREATE INDEX` creates an in-memory index on a source, view, or materialized view.
`CREATE INDEX` creates an in-memory [index](/fundamentals/concepts/indexes/) on a source, view, or materialized view.

In Materialize, indexes store query results in memory within a specific [cluster](/fundamentals/concepts/clusters/), and keep these results **incrementally updated** as new data arrives. This ensures that indexed data remains [fresh](/fundamentals/concepts/reaction-time), reflecting the latest changes with minimal latency.

The primary use case for indexes is to accelerate direct queries issued via [`SELECT`](/sql/select/) statements.
By maintaining fresh, up-to-date results in memory, indexes can significantly [optimize query performance](/transform-data/optimization/), reducing both response time and compute load—especially for resource-intensive operations such as joins, aggregations, and repeated subqueries.

Because indexes are scoped to a single cluster, they are most useful for accelerating queries within that cluster. For results that must be shared across clusters or persisted to durable storage, consider using a [materialized view](/sql/create-materialized-view), which also maintains fresh results but is accessible system-wide.

## Syntax

**CREATE INDEX:**

Create an index using the specified columns as the index key.

```mzsql
CREATE INDEX [<index_name>]
[IN CLUSTER <cluster_name>]
ON <obj_name> [USING <method>] (<col_expr>, ...)
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `<index_name>` | A name for the index.  |
| `IN CLUSTER <cluster_name>` | The [cluster](/sql/create-cluster) to maintain this index. If not specified, defaults to the active cluster.  |
| `<obj_name>` | The name of the source, view, or materialized view on which you want to create an index.  |
| `USING <method>` | The name of the index method to use. The only supported method is [`arrangement`](/overview/arrangements).  |
| `(<col_expr>, ...)` | The expressions to use as the key for the index.  |
| `WITH (<with_option>[,...])` | The following `<with_option>` is supported: \| Option                     \| Description \| \|----------------------------\|-------------\| \| `RETAIN HISTORY FOR`    \|  ***Private preview.** This option has known performance or stability issues and is under active development.* Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period). **Note:** Configuring indexes to retain history is not recommended. Instead, consider creating a materialized view for your subscription query and configuring the history retention period on the view instead. See [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`. \|  |

**CREATE DEFAULT INDEX:**

Create a default index using a set of columns that uniquely identify each row.
If this set of columns cannot be inferred, all columns are used.

```mzsql
CREATE DEFAULT INDEX
[IN CLUSTER <cluster_name>]
ON <obj_name> [USING <method>]
[WITH (<with_options>)];

```

| Syntax element | Description |
| --- | --- |
| `IN CLUSTER <cluster_name>` | The [cluster](/sql/create-cluster) to maintain this index. If not specified, defaults to the active cluster.  |
| `<obj_name>` | The name of the source, view, or materialized view on which you want to create an index.  |
| `USING <method>` | The name of the index method to use. The only supported method is [`arrangement`](/overview/arrangements).  |
| `WITH (<with_option>[,...])` | The following `<with_option>` is supported: \| Option                     \| Description \| \|----------------------------\|-------------\| \| `RETAIN HISTORY FOR`    \|  ***Private preview.** This option has known performance or stability issues and is under active development.* Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period). **Note:** Configuring indexes to retain history is not recommended. Instead, consider creating a materialized view for your subscription query and configuring the history retention period on the view instead. See [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`. \|  |

## Details

### Restrictions

-   You can only reference the columns available in the `SELECT` list of the query
    that defines the view. For example, if your view was defined as `SELECT a, b FROM src`, you can only reference columns `a` and `b`, even if `src` contains
    additional columns.

-   You cannot exclude any columns from being in the index's "value" set. For
    example, if your view is defined as `SELECT a, b FROM ...`, all indexes will
    contain `{a, b}` as their values.

    If you want to create an index that only stores a subset of these columns,
    consider creating another materialized view that uses `SELECT some_subset FROM this_view...`.

### Structure

Indexes in Materialize have the following structure for each unique row:

```nofmt
((tuple of indexed expressions), (tuple of the row, i.e. stored columns))
```

#### Indexed expressions vs. stored columns

Automatically created indexes will use all columns as key expressions for the
index, unless Materialize is provided or can infer a unique key for the source
or view.

For instance, unique keys can be...

-   **Provided** by the schema provided for the source, e.g. through the Confluent
    Schema Registry.
-   **Inferred** when the query...
    -   Concludes with a `GROUP BY`.
    -   Uses sources or views that have a unique key without damaging this property.
        For example, joining a view with unique keys against a second, where the join
        constraint uses foreign keys.

When creating your own indexes, you can choose the indexed expressions.

### Memory footprint

The in-memory sizes of indexes are proportional to the current size of the source
or view they represent. The actual amount of memory required depends on several
details related to the rate of compaction and the representation of the types of
data in the source or view.

Creating an index may also force the first materialization of a view, which may
cause Materialize to install a dataflow to determine and maintain the results of
the view. This dataflow may have a memory footprint itself, in addition to that
of the index.

#### Best practices

Before creating an index, consider the following:

- If you create stacked views (i.e., views that depend on other views) to
  reduce SQL complexity, we recommend that you create an index **only** on the
  view that will serve results, taking into account the expected data access
  patterns.

- Materialize can reuse indexes across queries that concurrently access the same
  data in memory, which reduces redundancy and resource utilization per query.
  In particular, this means that joins do **not** need to store data in memory
  multiple times.

- For queries that have no supporting indexes, Materialize uses the same
  mechanics used by indexes to optimize computations. However, since this
  underlying work is discarded after each query run, take into account the
  expected data access patterns to determine if you need to index or not.

### Usage patterns

#### Indexes on views vs. materialized views

In Materialize, both [indexes](/fundamentals/concepts/indexes) on views and [materialized
views](/fundamentals/concepts/views/#materialized-views) incrementally update the view
results when Materialize ingests new data. Whereas materialized views persist
the view results in durable storage and can be accessed across clusters, indexes
on views compute and store view results in memory within a **single** cluster.

Some general guidelines for usage patterns include:

| Usage Pattern | General Guideline |
|--------------------------------------------------------------------------------|--------------------|
| View results are accessed from a single cluster only;<br>such as in a 1-cluster or a 2-cluster architecture. | View with an [index](/sql/create-index) |
| View used as a building block for stacked views; i.e., views not used to serve results. | View |
| View results are accessed across [clusters](/fundamentals/concepts/clusters);<br>such as in a 3-cluster architecture. | Materialized view (in the transform cluster)<br>Index on the materialized view (in the serving cluster) |
| Use with a [sink](/export-data/) or a [`SUBSCRIBE`](/sql/subscribe) operation | Materialized view  |
| Use with [temporal filters](/transform-data/patterns/temporal-filters/) | Materialized view  |

#### Indexes and query optimizations

You might want to create indexes when...

-   You want to use non-primary keys (e.g. foreign keys) as a join condition. In
    this case, you could create an index on the columns in the join condition.
-   You want to speed up searches filtering by literal values or expressions.

Specific instances where indexes can be useful to improve performance include:

- When used in ad-hoc queries.

- When used by multiple queries within the same cluster.

- When used to enable [delta
  joins](/transform-data/optimization/#optimize-multi-way-joins-with-delta-joins).

For more information, see [Optimization](/transform-data/optimization).

## Examples

### Optimizing joins with indexes

You can optimize the performance of `JOIN` on two relations by ensuring their
join keys are the key columns in an index.

```mzsql
CREATE MATERIALIZED VIEW active_customers AS
    SELECT guid, geo_id, last_active_on
    FROM customer_source
    WHERE last_active_on > now() - INTERVAL '30' DAYS;

CREATE INDEX active_customers_geo_idx ON active_customers (geo_id);

CREATE MATERIALIZED VIEW active_customer_per_geo AS
    SELECT geo.name, count(*)
    FROM geo_regions AS geo
    JOIN active_customers ON active_customers.geo_id = geo.id
    GROUP BY geo.name;
```

In the above example, the index `active_customers_geo_idx`...

-   Helps us because it contains a key that the view `active_customer_per_geo` can
    use to look up values for the join condition (`active_customers.geo_id`).

    Because this index is exactly what the query requires, the Materialize
    optimizer will choose to use `active_customers_geo_idx` rather than build
    and maintain a private copy of the index just for this query.

-   Obeys our restrictions by containing only a subset of columns in the result
    set.

### Speed up filtering with indexes

If you commonly filter by a certain column being equal to a literal value, you can set up an index over that column to speed up your queries:

```mzsql
CREATE MATERIALIZED VIEW active_customers AS
    SELECT guid, geo_id, last_active_on
    FROM customer_source
    GROUP BY geo_id;

CREATE INDEX active_customers_idx ON active_customers (guid);

-- This should now be very fast!
SELECT * FROM active_customers WHERE guid = 'd868a5bf-2430-461d-a665-40418b1125e7';

-- Using indexed expressions:
CREATE INDEX active_customers_exp_idx ON active_customers (upper(guid));
SELECT * FROM active_customers WHERE upper(guid) = 'D868A5BF-2430-461D-A665-40418B1125E7';

-- Filter using an expression in one field and a literal in another field:
CREATE INDEX active_customers_exp_field_idx ON active_customers (upper(guid), geo_id);
SELECT * FROM active_customers WHERE upper(guid) = 'D868A5BF-2430-461D-A665-40418B1125E7' and geo_id = 'ID_8482';
```

Create an index with an expression to improve query performance over a frequently used expression, and
avoid building downstream views to apply the function like the one used in the example: `upper()`.
Take into account that aggregations like `count()` cannot be used as indexed expressions.

For more details on using indexes to optimize queries, see [Optimization](../../ops/optimization/).

## Privileges

The privileges required to execute this statement are:

- Ownership of the object on which to create the index.
- `CREATE` privileges on the containing schema.
- `CREATE` privileges on the containing cluster.
- `USAGE` privileges on all types used in the index definition.
- `USAGE` privileges on the schemas that all types in the statement are contained in.

## Related pages

-   [`SHOW INDEXES`](../show-indexes)
-   [`DROP INDEX`](../drop-index)

<!-- mz-docs page: sql/create-materialized-view -->

# CREATE MATERIALIZED VIEW
`CREATE MATERIALIZED VIEW` defines a view that is persisted in durable storage and incrementally updated as new data arrives.
Use `CREATE MATERIALIZED VIEW` to:

- Create a materialized view that maintains [fresh
  results](/fundamentals/concepts/reaction-time) by persisting them in durable storage and
  incrementally updating them as new data arrives.

- Create a replacement for an existing materialized view that can be applied in
  place with [`ALTER MATERIALIZED VIEW ... APPLY
  REPLACEMENT`](/sql/alter-materialized-view/).

Materialized views are particularly useful when you need **cross-cluster
access** to results or want to sink data to external systems like
[Kafka](/sql/create-sink). When you create a materialized view, a
[cluster](/fundamentals/concepts/clusters/), responsible for maintaining the view, is
associated with it, but the results can be **queried from any cluster**. This
allows you to separate the compute resources used for view maintenance from
those used for serving queries.

If you do not need durability or cross-cluster sharing, and you are primarily
interested in fast query performance within a single cluster, you may prefer to
[create a view and index it](/fundamentals/concepts/views/#views). In Materialize, [indexes
on views](/fundamentals/concepts/indexes/) also maintain results incrementally, but store
them in memory, scoped to the cluster where the index was created. This approach
offers lower latency for direct querying within that cluster.

## Syntax

**CREATE MATERIALIZED VIEW:**

```mzsql
CREATE MATERIALIZED VIEW [IF NOT EXISTS] <view_name>
[(<col_ident>, ...)]
[IN CLUSTER <cluster_name>]
[WITH (<with_options>)]
AS <select_stmt>;

```

| Syntax element | Description |
| --- | --- |
| `IF NOT EXISTS` | If specified, do not generate an error if a materialized view of the same name already exists.  |
| `<view_name>` | A name for the materialized view.  |
| `(<col_ident>, ...)` | Rename the `SELECT` statement's columns to the list of identifiers. Both must be the same length. Note that this is required for statements that return multiple columns with the same identifier.  |
| `IN CLUSTER <cluster_name>` | The cluster to maintain this materialized view. If not specified, defaults to the active cluster.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `ASSERT NOT NULL` *col_ident* \| `text` \| The column identifier for which to create a [non-null assertion](#non-null-assertions). To specify multiple columns, use the option multiple times. \| \| `PARTITION BY` *columns* \| `(ident [, ident]*)` \| The key by which Materialize should internally partition this durable collection. See the [partitioning guide](/transform-data/patterns/partition-by/) for restrictions on valid values and other details. \| \| `RETAIN HISTORY FOR` *retention_period* \| `interval` \| ***Private preview.*** Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`. \|  |
| `<select_stmt>` | The [`SELECT` statement](/sql/select) whose results you want to maintain incrementally updated.  |

**CREATE REPLACEMENT MATERIALIZED VIEW:**

> **Public Preview:** This feature is in public preview.

Create a replacement materialized view for an existing materialized view.

```mzsql
CREATE REPLACEMENT MATERIALIZED VIEW <name>
FOR <target_name>
[IN CLUSTER <cluster_name>]
[WITH (<with_options>)]
AS <select_stmt>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | A name for the replacement materialized view.  |
| `<target_name>` | The name of the existing materialized view to be replaced. The replacement materialized view can only be applied to this materialized view.  |
| `IN CLUSTER <cluster_name>` | The cluster to maintain this replacement materialized view. If not specified, defaults to the active cluster.  |
| `WITH (<with_options>)` | Same options as `CREATE MATERIALIZED VIEW`.  |
| `<select_stmt>` | The [`SELECT` statement](/sql/select) for the replacement view. The statement must produce the same output schema as the target materialized view; i.e., column names, column types, column order, nullability, and keys must all match.  |

The created replacement materialized view starts hydrating immediately and can
later be applied to replace the specified materialized view. For more
information, see [Creating replacement materialized
views](#creating-replacement-materialized-views).

## Details

### Usage pattern

In Materialize, both [indexes](/fundamentals/concepts/indexes) on views and [materialized
views](/fundamentals/concepts/views/#materialized-views) incrementally update the view
results when Materialize ingests new data. Whereas materialized views persist
the view results in durable storage and can be accessed across clusters, indexes
on views compute and store view results in memory within a **single** cluster.

Some general guidelines for usage patterns include:

| Usage Pattern | General Guideline |
|--------------------------------------------------------------------------------|--------------------|
| View results are accessed from a single cluster only;<br>such as in a 1-cluster or a 2-cluster architecture. | View with an [index](/sql/create-index) |
| View used as a building block for stacked views; i.e., views not used to serve results. | View |
| View results are accessed across [clusters](/fundamentals/concepts/clusters);<br>such as in a 3-cluster architecture. | Materialized view (in the transform cluster)<br>Index on the materialized view (in the serving cluster) |
| Use with a [sink](/export-data/) or a [`SUBSCRIBE`](/sql/subscribe) operation | Materialized view  |
| Use with [temporal filters](/transform-data/patterns/temporal-filters/) | Materialized view  |

### Indexing materialized views

Although you can query a materialized view directly, these queries will be
issued against Materialize's storage layer. This is expected to be fast, but
still slower than reading from memory. To improve the speed of queries on
materialized views, we recommend creating [indexes](../create-index) based on
common query patterns.

It's important to keep in mind that indexes are **local** to a cluster, and
maintained in memory. As an example, if you create a materialized view and
build an index on it in the `quickstart` cluster, querying the view from a
different cluster will _not_ use the index; you should create the appropriate
indexes in each cluster you are referencing the materialized view in.

[//]: # "TODO(morsapaes) Point to relevant operational guide on indexes once
this exists+add detail about using indexes to optimize materialized view
stacking."

### Non-null assertions

Because materialized views may be created on arbitrary queries, it may not in
all cases be possible for Materialize to automatically infer non-nullability of
some columns that can in fact never be null. In such a case, `ASSERT NOT NULL`
clauses may be used as described in the syntax section above. Specifying
`ASSERT NOT NULL` for a column forces that column's type in the materialized
view to include `NOT NULL`. If this clause is used erroneously, and a `NULL`
value is in fact produced in a column for which `ASSERT NOT NULL` was
specified, querying the materialized view will produce an error until the
offending row is deleted.

### Creating replacement materialized views

> **Public Preview:** This feature is in public preview.

You can use [`CREATE REPLACEMENT MATERIALIZED
VIEW`](/sql/create-materialized-view/) with [`ALTER MATERIALIZED VIEW ... APPLY
REPLACEMENT`](/sql/alter-materialized-view) to replace materialized views
in-place without recreating dependent objects or incurring downtime.

To create a replacement materialized view, you must:
- Specify the target materialized view.
- Specify a `SELECT` statement for the replacement view that produces the
  same output schema (including column order and keys) as the target view.

Upon creation, the replacement view starts hydrating in the background.

Before applying the replacement view, verify that the replacement view is
hydrated to avoid downtime:

The replacement view is dropped when you apply the replacement view. For more
information on applying the replacement view, including recommendations and
CPU/memory considerations, see [`ALTER MATERIALIZED VIEW ... APPLY
REPLACEMENT...`](/sql/alter-materialized-view/#replacing-a-materialized-view)

See also:

- [Replace materialized
views](/transform-data/updating-materialized-views/replace-materialized-view/)
guide for a step-by-step tutorial.

#### Query performance of replacement views

You can query a replacement materialized view to validate its results before
replacing. However, when queried, replacement materialized views are treated
like a [view](/sql/create-view), and the query results are re-computed as part
of the query execution. As such, queries against replacement materialized views
are slower and more computationally expensive than queries against regular
materialized views.

#### Restrictions and limitations

A replacement materialized view can only be applied to the target materialized
view specified in the `FOR` clause of the [`CREATE REPLACEMENT MATERIALIZED
VIEW`](/sql/create-materialized-view/) statement.

You cannot create dependent objects using [replacement materialized
views](/sql/create-materialized-view/#creating-replacement-materialized-views);
for example, you cannot create an index on a replacement materialized view or
create other views on a replacement materialized view.

## Examples

### Creating a materialized view

The following example creates a `winning_bids` materialized view:
```mzsql
CREATE MATERIALIZED VIEW winning_bids AS
SELECT DISTINCT ON (a.id) b.*, a.item, a.seller
FROM auctions AS a
JOIN bids AS b
  ON a.id = b.auction_id
WHERE b.bid_time < a.end_time
  AND mz_now() >= a.end_time
ORDER BY a.id,
  b.amount DESC,
  b.bid_time,
  b.buyer;

```

### Using non-null assertions

```mzsql
CREATE MATERIALIZED VIEW users_and_orders WITH (
  -- The semantics of a FULL OUTER JOIN guarantee that user_id is not null,
  -- because one of `users.id` or `orders.user_id` must be not null, but
  -- Materialize cannot yet automatically infer that fact.
  ASSERT NOT NULL user_id
)
AS
SELECT
  coalesce(users.id, orders.user_id) AS user_id,
  ...
FROM users FULL OUTER JOIN orders ON users.id = orders.user_id
```

[//]: # "TODO(morsapaes) Add more elaborate examples with \timing that show
things like querying materialized views from different clusters, indexed vs.
non-indexed, and so on."

### Creating a replacement materialized view

> **Public Preview:** This feature is in public preview.

The following example creates a replacement materialized view
`winning_bids_replacement` for the `winning_bids` materialized view. The
replacement view specifies a different filter `mz_now() > a.end_time` than
the existing view `mz_now() >= a.end_time`.
```mzsql
CREATE REPLACEMENT MATERIALIZED VIEW winning_bids_replacement
FOR winning_bids AS
SELECT DISTINCT ON (a.id) b.*, a.item, a.seller
FROM auctions AS a
JOIN bids AS b
  ON a.id = b.auction_id
WHERE b.bid_time < a.end_time
  AND mz_now() > a.end_time
ORDER BY a.id,
  b.amount DESC,
  b.bid_time,
  b.buyer;

```

To replace the existing view with its replacement, see [`ALTER MATERIALIZED
VIEW`](../alter-materialized-view).

See also:

- [Replace materialized views guide
](/transform-data/updating-materialized-views/replace-materialized-view/)

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `CREATE` privileges on the containing cluster.
- `USAGE` privileges on all types used in the materialized view definition.
- `USAGE` privileges on the schemas for the types used in the statement.

## Additional information

- Materialized views are not monotonic; that is, materialized views cannot be
  recognized as append-only.

## Related pages

- [`ALTER MATERIALIZED VIEW`](../alter-materialized-view)
- [`SHOW MATERIALIZED VIEWS`](../show-materialized-views)
- [`SHOW CREATE MATERIALIZED VIEW`](../show-create-materialized-view)
- [`DROP MATERIALIZED VIEW`](../drop-materialized-view)

<!-- mz-docs page: sql/create-network-policy -->

# CREATE NETWORK POLICY (Cloud)
`CREATE NETWORK POLICY` creates a network policy that restricts access to a Materialize Cloud region using IP-based rules.
*Available for Materialize Cloud only*

`CREATE NETWORK POLICY` creates a network policy that restricts access to a
Materialize region using IP-based rules. Network policies are part of
Materialize's framework for [access control](/security/cloud/).

## Syntax

```mzsql
CREATE NETWORK POLICY <name> (
  RULES (
    <rule_name> (action='allow', direction='ingress', address=<address>)
    [, ...]
  )
)
;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the network policy to modify.  |
| `<rule_name>` | The name for the network policy rule. Must be unique within the network policy.  |
| `<address>` | The Classless Inter-Domain Routing (CIDR) block to which the rule applies.  |

## Details

### Pre-installed network policy

When you enable a Materialize region, a default network policy named `default`
will be pre-installed. This policy has a wide open ingress rule `allow
0.0.0.0/0`. You can modify or drop this network policy at any time.

> **Note:** The default value for the `network_policy` session parameter is `default`.
> Before dropping the `default` network policy, a _superuser_ (i.e. `Organization
> Admin`) must run [`ALTER SYSTEM SET network_policy`](/sql/alter-system-set) to
> change the default value.

## Privileges

The privileges required to execute this statement are:

- `CREATENETWORKPOLICY` privileges on the system.

## Examples

```mzsql
CREATE NETWORK POLICY office_access_policy (
  RULES (
    new_york (action='allow', direction='ingress',address='1.2.3.4/28'),
    minnesota (action='allow',direction='ingress',address='2.3.4.5/32')
  )
);
```

```mzsql
ALTER SYSTEM SET network_policy = office_access_policy;
```

## Related pages

- [`ALTER NETWORK POLICY`](../alter-network-policy)
- [`DROP NETWORK POLICY`](../drop-network-policy)
- [`GRANT ROLE`](../grant-role)

<!-- mz-docs page: sql/create-role -->

# CREATE ROLE
`CREATE ROLE` creates a new role.
Use `CREATE ROLE` [^1] to:
- Create functional roles (*Both Cloud and Self-Managed*).
- Create roles with login/password/superuser privileges (*Self-Managed only*).

When you connect to Materialize, you must specify the name of a valid role in
the system.

[^1]: Materialize does not support the `CREATE USER` command.

## Syntax

**Cloud:**

The following syntax is used to create a role in Materialize Cloud.

```mzsql
CREATE ROLE <role_name> [[WITH] INHERIT];

```

| Syntax element | Description |
| --- | --- |
| `INHERIT` | *Optional.* If specified, grants the role the ability to inherit privileges of other roles. *Default.*  |

**Note:**
- Materialize Cloud does not support the `NOINHERIT` option for `CREATE
ROLE`.
- Materialize Cloud does not support the `LOGIN` and `SUPERUSER` attributes
  for `CREATE ROLE`.  See [Organization
  roles](/security/cloud/users-service-accounts/#organization-roles)
  instead.
- Materialize Cloud does not use role attributes to determine a role's
ability to create top level objects such as databases and other roles.
Instead, Materialize uses system level privileges. See [GRANT
PRIVILEGE](../grant-privilege) for more details.

**Self-Managed:**

The following syntax is used to create a role in Materialize Self-Managed.

```mzsql
CREATE ROLE <role_name>
[WITH]
    [ SUPERUSER | NOSUPERUSER ],
    [ LOGIN | NOLOGIN ]
    [ INHERIT ]
    [ PASSWORD <text> ]
;

```

| Syntax element | Description |
| --- | --- |
| `INHERIT` | *Optional.* If specified, grants the role the ability to inherit privileges of other roles. *Default.*  |
| `LOGIN` | *Optional.* If specified, allows a role to login via the PostgreSQL or web endpoints  |
| `NOLOGIN` | *Optional.* If specified, prevents a role from logging in. This is the default behavior if `LOGIN` is not specified.  |
| `SUPERUSER` | *Optional.* If specified, grants the role superuser privileges.  |
| `NOSUPERUSER` | *Optional.* If specified, prevents the role from having superuser privileges. This is the default behavior if `SUPERUSER` is not specified.  |
| `PASSWORD` | ***Public Preview***  *Optional.* This feature may have minor stability issues. If specified, allows you to set a password for the role.  |

**Note:**
- Self-Managed Materialize does not support the `NOINHERIT` option for
`CREATE ROLE`.
- With the exception of the `SUPERUSER` attribute, Self-Managed Materialize
does not use role attributes to determine a role's ability to create top
level objects such as databases and other roles. Instead, Self-Managed
Materialize uses system level privileges. See [GRANT PRIVILEGE](../grant-privilege) for more details.

## Restrictions

You may not specify redundant or conflicting sets of options. For example,
Materialize will reject the statement `CREATE ROLE ... INHERIT INHERIT`.

## Privileges

The privileges required to execute this statement are:

- `CREATEROLE` privileges on the system.

## Examples

### Create a functional role

In Materialize Cloud and Self-Managed, you can create a functional role:

```mzsql
CREATE ROLE db_reader;
```

### Create a role with login and password (Self-Managed)

```mzsql
CREATE ROLE db_reader WITH LOGIN PASSWORD 'password';
```

You can verify that the role was created by querying the `mz_roles` system catalog:

```mzsql
SELECT name FROM mz_roles;
```

```nofmt
 db_reader
 mz_system
 mz_support
```

### Create a superuser role (Self-Managed)

Unlike regular roles, superusers have unrestricted access to all objects in the system and can perform any action on them.

```mzsql
CREATE ROLE super_user WITH SUPERUSER LOGIN PASSWORD 'password';
```

You can verify that the superuser role was created by querying the `mz_roles` system catalog:

```mzsql
SELECT name FROM mz_roles;
```

```nofmt
 db_reader
 mz_system
 mz_support
 super_user
```

You can also verify that the role has superuser privileges by checking the `pg_authid` system catalog:

```mzsql
SELECT rolsuper FROM pg_authid WHERE rolname = 'super_user';
```

```nofmt
 true
```

## Related pages

- [`ALTER ROLE`](../alter-role)
- [`DROP ROLE`](../drop-role)
- [`DROP USER`](../drop-user)
- [`GRANT ROLE`](../grant-role)
- [`REVOKE ROLE`](../revoke-role)
- [`ALTER OWNER`](/sql/#rbac)
- [`GRANT PRIVILEGE`](../grant-privilege)
- [`REVOKE PRIVILEGE`](../revoke-privilege)

<!-- mz-docs page: sql/create-schema -->

# CREATE SCHEMA
`CREATE SCHEMA` creates a new schema.
`CREATE SCHEMA` creates a new schema.

## Syntax

```mzsql
CREATE SCHEMA [IF NOT EXISTS] <schema_name>;

```

| Syntax element | Description |
| --- | --- |
| `IF NOT EXISTS` | If specified, do not generate an error if a schema of the same name already exists. If not specified, throw an error if a schema of the same name already exists.  |
| `<schema_name>` | A name for the schema. You can specify the database for the schema with a preceding `database_name.schema_name`, e.g. `my_db.my_schema`, otherwise the schema is created in the current database.  |

## Details

By default, each database has a schema called `public`.

For more information, see [Namespaces](../namespaces).

## Examples

```mzsql
CREATE SCHEMA my_db.my_schema;
```
```mzsql
SHOW SCHEMAS FROM my_db;
```
```nofmt
public
my_schema
```

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing database.

## Related pages

- [`DROP DATABASE`](../drop-database)
- [`SHOW DATABASES`](../show-databases)

<!-- mz-docs page: sql/create-secret -->

# CREATE SECRET
`CREATE SECRET` securely stores credentials in Materialize's secret management system.
A secret securely stores sensitive credentials (like passwords and SSL keys) in Materialize's secret management system. Optionally, a secret can also be used to store credentials that are generally not sensitive (like usernames and SSL certificates), so that all your credentials are managed uniformly.

## Syntax

```mzsql
CREATE SECRET [IF NOT EXISTS] <name> AS <value>;

```

| Syntax element | Description |
| --- | --- |
| `IF NOT EXISTS` | If specified, do not generate an error if a secret of the same name already exists.  |
| `<name>` | The identifier for the secret.  |
| `<value>` | The value for the secret. The value expression may not reference any relations, and must be implicitly castable to `bytea`.  |

## Examples

```mzsql
CREATE SECRET kafka_ca_cert AS decode('c2VjcmV0Cg==', 'base64');
```

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.

## Related pages

- [`CREATE CONNECTION`](../create-connection)
- [`ALTER SECRET`](../alter-secret)
- [`DROP SECRET`](../drop-secret)
- [`SHOW SECRETS`](../show-secrets)

<!-- mz-docs page: sql/create-sink -->

# CREATE SINK

`CREATE SINK` connects Materialize to an external data sink.

A [sink](/fundamentals/concepts/sinks/) describes an external system you
want Materialize to write data to, and provides details about how to encode
that data. You can define a sink over a materialized view, source, or table.

## Syntax summary

<!--"Docs Note: Using include-example shortcode instead of include-syntax since only want the code snippet on this page."
-->

**Kafka/Redpanda:**

**Format Avro:**

<no value>```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_col1> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
FORMAT AVRO
    USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name> [
      (
        [AVRO KEY FULLNAME '<avro_key_fullname>']
        [, AVRO VALUE FULLNAME '<avro_value_fullname>']
        [, NULL DEFAULTS <null_defaults>]
        [, DOC ON <doc_on_option> [, ...]]
        [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
        [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
      )
    ]
  | USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> [
      (
        [KEY SCHEMA NAME '<key_schema_name>']
        [, VALUE SCHEMA NAME '<value_schema_name>']
        [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
        [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
      )
    ]
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

**Format JSON:**

<no value>```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_col1> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
FORMAT JSON
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

**Format TEXT/BYTES:**

<no value>```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
FORMAT TEXT | BYTES
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

**KEY FORMAT VALUE FORMAT:**

By default, the message key is encoded using the same format as the message value. However, you can set the key and value encodings explicitly using the `KEY FORMAT ... VALUE FORMAT`.

<no value>```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_col1> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
KEY FORMAT <key_format> VALUE FORMAT <value_format>
-- <key_format> and <value_format> can be:
-- AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name> [
--     (
--       [AVRO KEY FULLNAME '<avro_key_fullname>']
--       [, AVRO VALUE FULLNAME '<avro_value_fullname>']
--       [, NULL DEFAULTS <null_defaults>]
--       [, DOC ON <doc_on_option> [, ...]]
--       [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
--       [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
--     )
-- ]
-- | AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> [
--     (
--       [KEY SCHEMA NAME '<key_schema_name>']
--       [, VALUE SCHEMA NAME '<value_schema_name>']
--       [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
--       [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
--     )
-- ]
-- | JSON | TEXT | BYTES
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

For details, see [CREATE Sink: Kafka/Redpanda](/sql/create-sink/kafka/).

**Iceberg:**

> **Public Preview:** This feature is in public preview.

**MODE UPSERT:**

<no value>```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO ICEBERG CATALOG CONNECTION <catalog_connection> (
  NAMESPACE = '<namespace>',
  TABLE = '<table>'
)
KEY ( <key_col> [, ...] ) [NOT ENFORCED]
MODE UPSERT
WITH (COMMIT INTERVAL = '<interval>')

```

**MODE APPEND:**

<no value>```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO ICEBERG CATALOG CONNECTION <catalog_connection> (
  NAMESPACE = '<namespace>',
  TABLE = '<table>'
)
MODE APPEND
WITH (COMMIT INTERVAL = '<interval>')

```

For details, see [CREATE Sink: Iceberg](/sql/create-sink/iceberg/).

## Best practices

### Sizing a sink

Some sinks require relatively few resources to handle data ingestion, while
others are high traffic and require hefty resource allocations. The cluster in
which you place a sink determines the amount of CPU and memory available to the
sink.

Sinks share the resource allocation of their cluster with all other objects in
the cluster. Colocating multiple sinks onto the same cluster can be more
resource efficient when you have many low-traffic sinks that occasionally need
some burst capacity.

## Details

A sink cannot be created directly on a catalog object. As a workaround you can
create a materialized view on a catalog object and create a sink on the
materialized view.

[//]: # "TODO(morsapaes) Add best practices for sizing sinks."

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `SELECT` privileges on the item being written out to an external system.
  - NOTE: if the item is a materialized view, then the view owner must also have the necessary privileges to
    execute the view definition.
- `CREATE` privileges on the containing cluster if the sink is created in an existing cluster.
- `CREATECLUSTER` privileges on the system if the sink is not created in an existing cluster.
- `USAGE` privileges on all connections and secrets used in the sink definition.
- `USAGE` privileges on the schemas that all connections and secrets in the
  statement are contained in.

## Related pages

- [Sinks](/fundamentals/concepts/sinks/)
- [`SHOW SINKS`](/sql/show-sinks/)
- [`SHOW COLUMNS`](/sql/show-columns/)
- [`SHOW CREATE SINK`](/sql/show-create-sink/)

<!-- mz-docs page: sql/create-sink/iceberg -->

# CREATE SINK: Iceberg
Connecting Materialize to an Apache Iceberg table
> **Public Preview:** This feature is in public preview.

Use `CREATE SINK ... INTO ICEBERG CATALOG...` to create Iceberg sinks. Iceberg
sinks write data from Materialize into an Iceberg table hosted on AWS S3
Tables or Google Cloud BigLake. As data changes in Materialize, your Iceberg
tables are automatically kept up to date.

To create an Iceberg sink, you need an [Iceberg catalog
connection](/sql/create-connection/#iceberg-catalog) that specifies access
parameters to your Iceberg catalog.

## Syntax

> **Note:** `CREATE SINK` no longer includes a `USING AWS CONNECTION` clause.
> Instead, the sink inherits credentials from the [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog).
> Existing Iceberg sinks are not affected and will continue to function as before.

**MODE UPSERT:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO ICEBERG CATALOG CONNECTION <catalog_connection> (
  NAMESPACE = '<namespace>',
  TABLE = '<table>'
)
KEY ( <key_col> [, ...] ) [NOT ENFORCED]
MODE UPSERT
WITH (COMMIT INTERVAL = '<interval>')

```

| Syntax element | Description |
| --- | --- |
| `<sink_name>` | The name for the sink.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a sink with the same name already exists.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this sink. If unspecified, defaults to the active cluster.  |
| `<item_name>` | The name of the source, table, or materialized view to sink.  |
| **ICEBERG CATALOG CONNECTION** `<catalog_connection>` | The name of the [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog) to use.  |
| **NAMESPACE** `'<namespace>'` | The Iceberg namespace (database) containing the table.  |
| **TABLE** `'<table>'` | The name of the unpartitioned Iceberg table to write to. If the table doesn't exist, Materialize creates it automatically. For details, see [Iceberg table creation](/sql/create-sink/iceberg/#iceberg-table-creation).  |
| **KEY** ( `<key_col>` [, ...] ) | The columns that uniquely identify rows. Materialize validates that the key is unique unless `NOT ENFORCED` is specified.  |
| **NOT ENFORCED** | Optional. Disable validation of key uniqueness. Use only when you have outside knowledge that the key is unique.  |
| **MODE UPSERT** | Indicates that the sink uses upsert semantics based on the `KEY`.  |
| **COMMIT INTERVAL** `'<interval>'` | How frequently to commit snapshots to Iceberg (e.g., `'1m'`, `'5m'`). Must be at least `'1s'`. See [Commit interval tradeoffs](#commit-interval-tradeoffs).  |

**MODE APPEND:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO ICEBERG CATALOG CONNECTION <catalog_connection> (
  NAMESPACE = '<namespace>',
  TABLE = '<table>'
)
MODE APPEND
WITH (COMMIT INTERVAL = '<interval>')

```

| Syntax element | Description |
| --- | --- |
| `<sink_name>` | The name for the sink.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a sink with the same name already exists.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this sink. If unspecified, defaults to the active cluster.  |
| `<item_name>` | The name of the source, table, or materialized view to sink.  |
| **ICEBERG CATALOG CONNECTION** `<catalog_connection>` | The name of the [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog) to use.  |
| **NAMESPACE** `'<namespace>'` | The Iceberg namespace (database) containing the table.  |
| **TABLE** `'<table>'` | The name of the unpartitioned Iceberg table to write to. If the table doesn't exist, Materialize creates it automatically. For details, see [Iceberg table creation](/sql/create-sink/iceberg/#iceberg-table-creation).  |
| **MODE APPEND** | Writes all changes as data rows instead of using Iceberg delete files. Two extra columns are appended to the Iceberg table: `_mz_diff` (`int`, `+1` for inserts, `-1` for deletes) and `_mz_timestamp` (`long`). An update produces two rows: one with `_mz_diff = -1` (old values) and one with `_mz_diff = +1` (new values). No `KEY` clause is permitted. See [Append mode](#append-mode).  |
| **COMMIT INTERVAL** `'<interval>'` | How frequently to commit snapshots to Iceberg (e.g., `'1m'`, `'5m'`). Must be at least `'1s'`. See [Commit interval tradeoffs](#commit-interval-tradeoffs).  |

## Details

Iceberg sinks continuously stream changes from Materialize to an Iceberg table.
Specifically, Materialize writes data as Parquet files to the object storage
backing your Iceberg catalog.

At each `COMMIT INTERVAL`:

1. All pending writes are flushed to Parquet data files. See [Type
   mapping](#type-mapping).
2. In **upsert** mode, delete files are written for any updates or deletes. See
   [Delete handling](#delete-handling). In **append** mode, no delete files are
   written; all changes are data rows. See [Append mode](#append-mode).
3. A new Iceberg snapshot is committed atomically.

When the snapshot is committed, the data is available to downstream query
engines. See [Commit interval tradeoffs](#commit-interval-tradeoffs).

### Iceberg table creation

If the specified Iceberg table does not exist, Materialize creates the table.
The new Iceberg table:
- Uses the schema derived from your Materialize object.
- Uses Iceberg format version 2.

Materialize creates unpartitioned tables. Partitioned tables are not supported.

See also: [Restrictions and limitations](#restrictions-and-limitations).

### Exactly-once delivery

Iceberg sinks provide **exactly-once delivery**. After a restart,
Materialize resumes from the last committed snapshot without duplicating
data.

Materialize stores progress information in Iceberg snapshot metadata
properties (`mz-frontier` and `mz-sink-version`).

### Commit interval tradeoffs

The `COMMIT INTERVAL` setting involves tradeoffs between latency and efficiency:

| Shorter intervals (e.g., < `1m`) | Longer intervals (e.g., `5m`) |
|---------------------------------|-------------------------------|
| Lower latency - data visible sooner | Higher latency - data takes longer to appear |
| More small files - can degrade query performance | Fewer, larger files - better query performance |
| Higher catalog overhead | Lower catalog overhead |
| Higher S3 write costs (more PUT requests) | Lower S3 write costs |

**Recommendations:**
- For production: `1m` to `5m`
- For batch analytics: `5m` to `15m`

Starting in v26.34, you can change the commit interval of an existing sink with
[`ALTER SINK`](/sql/alter-sink/).

> **Note:** Outside of development environments, commit intervals should be at least `1m`.
> Short commit intervals increase catalog overhead and produce many small files.
> Small files will result in degraded query performance. It also increases load on
> the Iceberg metadata, which can result in a degraded catalog and non-responsive
> queries.

### Unique keys

In upsert mode, the Iceberg sink uses upsert semantics based on the `KEY`. The columns you
specify as the `KEY` must uniquely identify rows. Materialize validates that the
key is unique; if it cannot prove uniqueness, you'll receive an error.

If you have outside knowledge that the key is unique, you can bypass validation
using `NOT ENFORCED`. However, if the key is not actually unique, downstream
consumers may see incorrect results.

### Append mode

In append mode (`MODE APPEND`), every change in the Materialize update stream
is written as a data row. No Iceberg delete files are produced. Two extra
columns are appended to the Iceberg table:

| Column | Iceberg type | Description |
|--------|-------------|-------------|
| `_mz_diff` | `int` | `+1` for insertions, `-1` for deletions. |
| `_mz_timestamp` | `long` | The Materialize logical timestamp of the change. |

- An **insert** produces one row with `_mz_diff = +1`.
- A **delete** produces one row with `_mz_diff = -1`.
- An **update** produces two rows: one with `_mz_diff = -1` (the old value) and
  one with `_mz_diff = +1` (the new value). Both carry the same `_mz_timestamp`.

No `KEY` clause is permitted with `MODE APPEND`.

### Type mapping

Materialize converts SQL types to Iceberg/Parquet types:

| SQL type | Iceberg type |
|----------|--------------|
| `boolean` | `boolean` |
| `smallint`, `integer` | `int` |
| `uint2` | `int` |
| `bigint` | `long` |
| `uint4` | `long` |
| `uint8` | `decimal(20, 0)` |
| `real` | `float` |
| `double precision` | `double` |
| `numeric` | `decimal(38, scale)` |
| `date` | `date` |
| `time` | `time` (microsecond) |
| `timestamp` | `timestamp` (microsecond) |
| `timestamptz` | `timestamptz` (microsecond) |
| `text`, `varchar` | `string` |
| `bytea` | `binary` |
| `uuid` | `fixed(16)` |
| `jsonb` | `string` |
| `interval` | `string` |
| `int4range`, `int8range`, `numrange`, `daterange`, `tsrange`, `tstzrange` | `struct` (fields: `lower`, `upper`, `lower_inclusive`, `upper_inclusive`, `empty`) |
| `record` | `struct` |
| `list` | `list` |
| `map` | `map` |

### Restrictions and limitations

- You cannot create an Iceberg sink into an existing Iceberg table. Materialize creates and manages the target Iceberg table itself, so the table named by the sink must not already exist.

- Partitioned tables are not supported.

- Schema evolution of an Iceberg table is not supported. If the `SINK FROM` object's schema changes, you must drop and recreate the sink.

### Delete handling

> **Note:** Delete handling applies to `MODE UPSERT` only. In `MODE APPEND`, all changes
> are written as data rows. See [Append mode](#append-mode).

Iceberg sinks use a hybrid delete strategy:

- **Position deletes**: Used when a row is inserted and then deleted or updated
  within the same commit interval. Materialize records the exact file path and
  row position.
- **Equality deletes**: Used when deleting or updating a row from a previous
  snapshot. Materialize writes a delete file containing the `KEY` column values.

This means short-lived rows use efficient position deletes, while updates to
older data use equality deletes.

> **Tip:** Consider running [Iceberg compaction](https://iceberg.apache.org/docs/latest/maintenance/#compacting-data-files) periodically to merge delete files and improve query performance.

## Required privileges

- `CREATE` privileges on the containing schema.
- `SELECT` privileges on the item being written out to an external system.
  - NOTE: if the item is a materialized view, then the view owner must also have the necessary privileges to
    execute the view definition.
- `CREATE` privileges on the containing cluster if the sink is created in an existing cluster.
- `CREATECLUSTER` privileges on the system if the sink is not created in an existing cluster.
- `USAGE` privileges on all connections and secrets used in the sink definition.
- `USAGE` privileges on the schemas that all connections and secrets in the
  statement are contained in.

## Troubleshooting

### Sink creation fails with "input compacted past resume upper"

This error occurs when the source data has been compacted beyond the point where
the sink last committed. This can happen after a Materialize backup/restore
operation. You may need to drop and recreate the sink, which will re-snapshot
the entire source relation.

### Commit conflicts

If another process modifies the Iceberg table while Materialize is committing,
you may see commit conflict errors. Materialize will automatically retry, but
if conflicts persist, ensure no other writers are modifying the same table.

## Examples

### Prerequisites: Create connections

To create an Iceberg sink, you need an [Iceberg catalog connection](/export-data/iceberg/):

**AWS S3 Tables:**

The following example creates an [AWS connection](/sql/create-connection/#aws) and an [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog) for AWS S3 Tables:
```mzsql
-- First, create an AWS connection for authentication
CREATE CONNECTION aws_connection
  TO AWS (ASSUME ROLE ARN = 'arn:aws:iam::123456789012:role/MaterializeIceberg');

-- Create the Iceberg catalog connection pointing to S3 Tables
CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 's3tablesrest',
    URL = 'https://s3tables.us-east-1.amazonaws.com/iceberg',
    WAREHOUSE = 'arn:aws:s3tables:us-east-1:123456789012:bucket/my-table-bucket',
    AWS CONNECTION = aws_connection
);

```

**GCP BigLake:**

The following example creates a [GCP connection](/sql/create-connection/#gcp) and an [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog) for Google Cloud BigLake. The service account reaches both the catalog and the warehouse bucket, so no credential vending is involved:
```mzsql
-- Using the base64-encoded service account key (e.g. base64 < sa_key.json)
CREATE SECRET gcp_service_account_key
  AS decode('<base64-encoded service account key JSON>', 'base64');

-- Create a GCP connection that uses the service-account key.
CREATE CONNECTION gcp_connection TO GCP (
    SERVICE ACCOUNT KEY = SECRET gcp_service_account_key
);

-- Create the Iceberg catalog connection pointing to BigLake.
CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = 'https://biglake.googleapis.com/iceberg/v1/restcatalog',
    WAREHOUSE = 'gs://<bucket>',
    GCP CONNECTION = gcp_connection
);

```

### Creating an upsert sink

Using the previously created AWS and Iceberg catalog connection, the
following example creates an Iceberg sink with a composite key:
```mzsql
CREATE SINK user_events_iceberg
  IN CLUSTER analytics_cluster
  FROM user_events
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = 'events',
    TABLE = 'user_events'
  )
  KEY (user_id, event_timestamp)
  MODE UPSERT
  WITH (COMMIT INTERVAL = '1m');

```

In upsert mode, the required `KEY` clause uniquely identifies rows; in this
example, it uses a composite key of `user_id` and `event_timestamp`.
Materialize validates that this key is unique in the source data.

### Bypassing unique key validation

If Materialize cannot prove your key is unique but you have outside knowledge
that it is, you can bypass validation by including `NOT ENFORCED` option:

```mzsql
CREATE SINK deduped_sink
  IN CLUSTER my_cluster
  FROM my_source
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = 'raw',
    TABLE = 'events'
  )
  KEY (event_id) NOT ENFORCED
  MODE UPSERT
  WITH (COMMIT INTERVAL = '1m');
```

> **Warning:** If the key is not actually unique, downstream consumers may see incorrect
> results.

### Creating an append sink

Create an Iceberg sink in append mode. All changes are written as data
rows with `_mz_diff` and `_mz_timestamp` columns:
```mzsql
CREATE SINK events_log_iceberg
  IN CLUSTER analytics_cluster
  FROM user_events
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = 'events',
    TABLE = 'user_events_log'
  )
  MODE APPEND
  WITH (COMMIT INTERVAL = '1m');

```

The Iceberg table will contain all columns from `user_events` plus two
additional columns: `_mz_diff` and `_mz_timestamp`. See [Append
mode](#append-mode).

## Related pages

- [Iceberg sink guide](/export-data/iceberg/)
- [`SHOW SINKS`](/sql/show-sinks)
- [`DROP SINK`](/sql/drop-sink)
- [`CREATE CONNECTION`](/sql/create-connection)

<!-- mz-docs page: sql/create-sink/kafka -->

# CREATE SINK: Kafka/Redpanda
Connecting Materialize to a Kafka or Redpanda broker sink
> **Note:** The `CREATE SINK` syntax, supported formats, and features are the
> same for Kafka and Redpanda broker. For simplicity, this page uses
> "Kafka" to refer to both Kafka and Redpanda.

`CREATE SINK` connects Materialize to an external system
you want to write data to, and provides details about how to encode that data.

To use a Kafka broker (and optionally a schema registry) as a sink, make sure that a connection that specifies access and authentication parameters to that broker already exists; otherwise, you first need to [create a connection](#creating-a-connection). Once created, a connection is **reusable** across multiple `CREATE SINK` and `CREATE SOURCE` statements.

Sink source type      | Description
----------------------|------------
**Source**            | Simply pass all data received from the source to the sink without modifying it.
**Table**             | Stream all changes to the specified table out to the sink.
**Materialized view** | Stream all changes to the view to the sink. This lets you use Materialize to process a stream, and then stream the processed values. Note that this feature only works with [materialized views](/sql/create-materialized-view), and _does not_ work with [non-materialized views](/sql/create-view).

## Syntax

**Format Avro:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_col1> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
FORMAT AVRO
    USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name> [
      (
        [AVRO KEY FULLNAME '<avro_key_fullname>']
        [, AVRO VALUE FULLNAME '<avro_value_fullname>']
        [, NULL DEFAULTS <null_defaults>]
        [, DOC ON <doc_on_option> [, ...]]
        [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
        [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
      )
    ]
  | USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> [
      (
        [KEY SCHEMA NAME '<key_schema_name>']
        [, VALUE SCHEMA NAME '<value_schema_name>']
        [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
        [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
      )
    ]
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

| Syntax element | Description |
| --- | --- |
| `<sink_name>` | The name for the sink.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a sink with the same name already exists. Instead, issue a notice and skip the sink creation.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this sink.  |
| `<item_name>` | The name of the source, table, or materialized view you want to send to the sink.  |
| **CONNECTION** `<connection_name>` | The name of the Kafka connection to use in the sink. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection) documentation page.  |
| **TOPIC** `'<topic>'` | The name of the Kafka topic to write to.  |
| **COMPRESSION TYPE** `<compression_type>` | Optional. The type of compression to apply to messages before they are sent to Kafka: `none`, `gzip`, `snappy`, `lz4`, or `zstd`.<br>Default: `lz4`  |
| **TRANSACTIONAL ID PREFIX** `'<transactional_id_prefix>'` | Optional. The prefix of the transactional ID to use when producing to the Kafka topic.<br>Default: `materialize-{REGION ID}-{CONNECTION ID}-{SINK ID}`.  |
| **PARTITION BY** = `<expression>` | Optional. A SQL expression returning a hash that can be used for partition assignment. See [Partitioning](#partitioning) for details.  |
| **PROGRESS GROUP ID PREFIX** `'<progress_group_id_prefix>'` | Optional. The prefix of the consumer group ID to use when reading from the progress topic.<br>Default: `materialize-{REGION ID}-{CONNECTION ID}-{SINK ID}`.  |
| **TOPIC REPLICATION FACTOR** `<replication_factor>` | Optional. The replication factor to use when creating the Kafka topic (if the Kafka topic does not already exist).<br>Default: Broker's default.  |
| **TOPIC PARTITION COUNT** `<partition_count>` | Optional. The partition count to use when creating the Kafka topic (if the Kafka topic does not already exist).<br>Default: Broker's default.  |
| **TOPIC CONFIG** `<topic_config>` | Optional. Any topic-level configs to use when creating the Kafka topic (if the Kafka topic does not already exist). See the [Kafka documentation](https://kafka.apache.org/documentation/#topicconfigs) for available configs.<br>Default: empty.  |
| **KEY** ( `<key_col1>` [, ...] ) [**NOT ENFORCED**] | Optional. A list of columns to use as the Kafka message key. If unspecified, the Kafka key is left unset. When using the upsert envelope, the key must be unique. Use **NOT ENFORCED** to disable validation of key uniqueness. See [Upsert key selection](#upsert-key-selection) for details.  |
| **HEADERS** `<headers_column>` | Optional. A column containing headers to add to each Kafka message emitted by the sink. The column must be of type `map[text => text]` or `map[text => bytea]`. See [Headers](#headers) for details.  |
| **FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION** `<csr_connection_name>` | Encode messages using Avro format with schemas published to the Confluent Schema Registry.  |
| **FORMAT AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION** `<glue_connection_name>` | ***Private preview.** This feature is under active development.*  Encode messages using Avro format with schemas registered in the AWS Glue Schema Registry named by the [AWS Glue Schema Registry connection](/sql/create-connection/#aws-glue-schema-registry). The registry must already exist. Only the `KEY SCHEMA NAME`, `VALUE SCHEMA NAME`, `KEY COMPATIBILITY LEVEL`, and `VALUE COMPATIBILITY LEVEL` options are supported. See [Avro](#avro) for details.  |
| **AVRO KEY FULLNAME** `'<avro_key_fullname>'` | Optional, Confluent Schema Registry only. Default: `row`. Sets the Avro fullname on the generated key schema, if a `KEY` is specified. When used, a value must be specified for `AVRO VALUE FULLNAME`.  |
| **AVRO VALUE FULLNAME** `'<avro_value_fullname>'` | Optional, Confluent Schema Registry only. Default: `envelope`. Sets the Avro fullname on the generated value schema. When `KEY` is specified, `AVRO KEY FULLNAME` must additionally be specified.  |
| **NULL DEFAULTS** `<null_defaults>` | Optional, Confluent Schema Registry only. Default: `false`. Whether to automatically default nullable fields to `null` in the generated schemas.  |
| **KEY SCHEMA NAME** `'<key_schema_name>'` | Optional, AWS Glue Schema Registry only. The name under which the key schema is registered, if a `KEY` is specified. Default: `<topic>-key`.  |
| **VALUE SCHEMA NAME** `'<value_schema_name>'` | Optional, AWS Glue Schema Registry only. The name under which the value schema is registered. Default: `<topic>-value`.  |
| **DOC ON** `<doc_on_option>` [, ...] | Optional, Confluent Schema Registry only. Add a documentation comment to the generated Avro schemas.  \| Option \| Description \| \|--------\|-------------\| \| `TYPE <type_name>` \| Names a SQL type or relation, e.g. `my_app.point`. \| \| `COLUMN <column_name>` \| Names a column of a SQL type or relation, e.g. `my_app.point.x`. \|  The `KEY` and `VALUE` options specify whether the comment applies to the key schema or the value schema. If neither `KEY` or `VALUE` is specified, the comment applies to both types of schemas.  See [Avro schema documentation](#avro-schema-documentation) for details on how documentation comments are added to the generated Avro schemas.  |
| **KEY COMPATIBILITY LEVEL** `'<key_compatibility_level>'` | Optional. If specified, set the [Compatibility Level](https://docs.confluent.io/platform/7.6/schema-registry/fundamentals/schema-evolution.html#schema-evolution-and-compatibility) for the generated key schema to one of: `BACKWARD`, `BACKWARD_TRANSITIVE`, `FORWARD`, `FORWARD_TRANSITIVE`, `FULL`, `FULL_TRANSITIVE`, `NONE`. With AWS Glue, the level is applied only when the sink creates the schema and maps to the [Glue equivalent](#avro).  |
| **VALUE COMPATIBILITY LEVEL** `'<value_compatibility_level>'` | Optional. If specified, set the [Compatibility Level](https://docs.confluent.io/platform/7.6/schema-registry/fundamentals/schema-evolution.html#schema-evolution-and-compatibility) for the generated value schema to one of: `BACKWARD`, `BACKWARD_TRANSITIVE`, `FORWARD`, `FORWARD_TRANSITIVE`, `FULL`, `FULL_TRANSITIVE`, `NONE`. With AWS Glue, the level is applied only when the sink creates the schema and maps to the [Glue equivalent](#avro).  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how changes to the sink's upstream relation are mapped to Kafka messages. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `DEBEZIUM` \| The generated schemas have a [Debezium-style diff envelope](#debezium-envelope) to capture changes in the input view or source. \| \| `UPSERT` \| The sink emits data with [upsert semantics](#upsert-envelope). Requires a unique key specified using the `KEY` option. \|  |
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `SNAPSHOT = <snapshot>` \| Default: `true`. Whether to emit the consolidated results of the query before the sink was created at the start of the sink. To see only results after the sink is created, specify `WITH (SNAPSHOT = false)`. \|  |

**Format JSON:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_col1> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
FORMAT JSON
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

| Syntax element | Description |
| --- | --- |
| `<sink_name>` | The name for the sink.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a sink with the same name already exists. Instead, issue a notice and skip the sink creation.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this sink.  |
| `<item_name>` | The name of the source, table, or materialized view you want to send to the sink.  |
| **CONNECTION** `<connection_name>` | The name of the Kafka connection to use in the sink. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection) documentation page.  |
| **TOPIC** `'<topic>'` | The name of the Kafka topic to write to.  |
| **COMPRESSION TYPE** `<compression_type>` | Optional. The type of compression to apply to messages before they are sent to Kafka: `none`, `gzip`, `snappy`, `lz4`, or `zstd`.<br>Default: `lz4`  |
| **TRANSACTIONAL ID PREFIX** `'<transactional_id_prefix>'` | Optional. The prefix of the transactional ID to use when producing to the Kafka topic.<br>Default: `materialize-{REGION ID}-{CONNECTION ID}-{SINK ID}`.  |
| **PARTITION BY** = `<expression>` | Optional. A SQL expression returning a hash that can be used for partition assignment. See [Partitioning](#partitioning) for details.  |
| **PROGRESS GROUP ID PREFIX** `'<progress_group_id_prefix>'` | Optional. The prefix of the consumer group ID to use when reading from the progress topic.<br>Default: `materialize-{REGION ID}-{CONNECTION ID}-{SINK ID}`.  |
| **TOPIC REPLICATION FACTOR** `<replication_factor>` | Optional. The replication factor to use when creating the Kafka topic (if the Kafka topic does not already exist).<br>Default: Broker's default.  |
| **TOPIC PARTITION COUNT** `<partition_count>` | Optional. The partition count to use when creating the Kafka topic (if the Kafka topic does not already exist).<br>Default: Broker's default.  |
| **TOPIC CONFIG** `<topic_config>` | Optional. Any topic-level configs to use when creating the Kafka topic (if the Kafka topic does not already exist). See the [Kafka documentation](https://kafka.apache.org/documentation/#topicconfigs) for available configs.<br>Default: empty.  |
| **KEY** ( `<key_col1>` [, ...] ) [**NOT ENFORCED**] | Optional. A list of columns to use as the Kafka message key. If unspecified, the Kafka key is left unset. When using the upsert envelope, the key must be unique. Use **NOT ENFORCED** to disable validation of key uniqueness. See [Upsert key selection](#upsert-key-selection) for details.  |
| **HEADERS** `<headers_column>` | Optional. A column containing headers to add to each Kafka message emitted by the sink. The column must be of type `map[text => text]` or `map[text => bytea]`. See [Headers](#headers) for details.  |
| **FORMAT JSON** | Encode messages using JSON format.  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how changes to the sink's upstream relation are mapped to Kafka messages. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `DEBEZIUM` \| The generated schemas have a [Debezium-style diff envelope](#debezium-envelope) to capture changes in the input view or source. \| \| `UPSERT` \| The sink emits data with [upsert semantics](#upsert-envelope). Requires a unique key specified using the `KEY` option. \|  |
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `SNAPSHOT = <snapshot>` \| Default: `true`. Whether to emit the consolidated results of the query before the sink was created at the start of the sink. To see only results after the sink is created, specify `WITH (SNAPSHOT = false)`. \|  |

**Format TEXT/BYTES:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
FORMAT TEXT | BYTES
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

| Syntax element | Description |
| --- | --- |
| `<sink_name>` | The name for the sink.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a sink with the same name already exists. Instead, issue a notice and skip the sink creation.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this sink.  |
| `<item_name>` | The name of the source, table, or materialized view you want to send to the sink. Note that `TEXT` and `BYTES` format options only support single-column encoding.  |
| **CONNECTION** `<connection_name>` | The name of the Kafka connection to use in the sink. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection) documentation page.  |
| **TOPIC** `'<topic>'` | The name of the Kafka topic to write to.  |
| **COMPRESSION TYPE** `<compression_type>` | Optional. The type of compression to apply to messages before they are sent to Kafka: `none`, `gzip`, `snappy`, `lz4`, or `zstd`.<br>Default: `lz4`  |
| **TRANSACTIONAL ID PREFIX** `'<transactional_id_prefix>'` | Optional. The prefix of the transactional ID to use when producing to the Kafka topic.<br>Default: `materialize-{REGION ID}-{CONNECTION ID}-{SINK ID}`.  |
| **PARTITION BY** = `<expression>` | Optional. A SQL expression returning a hash that can be used for partition assignment. See [Partitioning](#partitioning) for details.  |
| **PROGRESS GROUP ID PREFIX** `'<progress_group_id_prefix>'` | Optional. The prefix of the consumer group ID to use when reading from the progress topic.<br>Default: `materialize-{REGION ID}-{CONNECTION ID}-{SINK ID}`.  |
| **TOPIC REPLICATION FACTOR** `<replication_factor>` | Optional. The replication factor to use when creating the Kafka topic (if the Kafka topic does not already exist).<br>Default: Broker's default.  |
| **TOPIC PARTITION COUNT** `<partition_count>` | Optional. The partition count to use when creating the Kafka topic (if the Kafka topic does not already exist).<br>Default: Broker's default.  |
| **TOPIC CONFIG** `<topic_config>` | Optional. Any topic-level configs to use when creating the Kafka topic (if the Kafka topic does not already exist). See the [Kafka documentation](https://kafka.apache.org/documentation/#topicconfigs) for available configs.<br>Default: empty.  |
| **FORMAT TEXT** | Encode messages as plain text. Only supports single-column encoding.  |
| **FORMAT BYTES** | Encode messages as raw bytes. Only supports single-column encoding and scalar data types.  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how changes to the sink's upstream relation are mapped to Kafka messages. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `DEBEZIUM` \| The generated schemas have a [Debezium-style diff envelope](#debezium-envelope) to capture changes in the input view or source. \| \| `UPSERT` \| The sink emits data with [upsert semantics](#upsert-envelope). Requires a unique key specified using the `KEY` option. \|  |
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `SNAPSHOT = <snapshot>` \| Default: `true`. Whether to emit the consolidated results of the query before the sink was created at the start of the sink. To see only results after the sink is created, specify `WITH (SNAPSHOT = false)`. \|  |

**KEY FORMAT VALUE FORMAT:**

By default, the message key is encoded using the same format as the message value. However, you can set the key and value encodings explicitly using the `KEY FORMAT ... VALUE FORMAT`.

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_col1> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
KEY FORMAT <key_format> VALUE FORMAT <value_format>
-- <key_format> and <value_format> can be:
-- AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name> [
--     (
--       [AVRO KEY FULLNAME '<avro_key_fullname>']
--       [, AVRO VALUE FULLNAME '<avro_value_fullname>']
--       [, NULL DEFAULTS <null_defaults>]
--       [, DOC ON <doc_on_option> [, ...]]
--       [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
--       [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
--     )
-- ]
-- | AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> [
--     (
--       [KEY SCHEMA NAME '<key_schema_name>']
--       [, VALUE SCHEMA NAME '<value_schema_name>']
--       [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
--       [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
--     )
-- ]
-- | JSON | TEXT | BYTES
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

| Syntax element | Description |
| --- | --- |
| `<sink_name>` | The name for the sink.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a sink with the same name already exists. Instead, issue a notice and skip the sink creation.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this sink.  |
| `<item_name>` | The name of the source, table, or materialized view you want to send to the sink.  |
| **CONNECTION** `<connection_name>` | The name of the Kafka connection to use in the sink. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection) documentation page.  |
| **TOPIC** `'<topic>'` | The name of the Kafka topic to write to.  |
| **COMPRESSION TYPE** `<compression_type>` | Optional. The type of compression to apply to messages before they are sent to Kafka: `none`, `gzip`, `snappy`, `lz4`, or `zstd`.<br>Default: `lz4`  |
| **TRANSACTIONAL ID PREFIX** `'<transactional_id_prefix>'` | Optional. The prefix of the transactional ID to use when producing to the Kafka topic.<br>Default: `materialize-{REGION ID}-{CONNECTION ID}-{SINK ID}`.  |
| **PARTITION BY** = `<expression>` | Optional. A SQL expression returning a hash that can be used for partition assignment. See [Partitioning](#partitioning) for details.  |
| **PROGRESS GROUP ID PREFIX** `'<progress_group_id_prefix>'` | Optional. The prefix of the consumer group ID to use when reading from the progress topic.<br>Default: `materialize-{REGION ID}-{CONNECTION ID}-{SINK ID}`.  |
| **TOPIC REPLICATION FACTOR** `<replication_factor>` | Optional. The replication factor to use when creating the Kafka topic (if the Kafka topic does not already exist).<br>Default: Broker's default.  |
| **TOPIC PARTITION COUNT** `<partition_count>` | Optional. The partition count to use when creating the Kafka topic (if the Kafka topic does not already exist).<br>Default: Broker's default.  |
| **TOPIC CONFIG** `<topic_config>` | Optional. Any topic-level configs to use when creating the Kafka topic (if the Kafka topic does not already exist). See the [Kafka documentation](https://kafka.apache.org/documentation/#topicconfigs) for available configs.<br>Default: empty.  |
| **KEY** ( `<key_col1>` [, ...] ) [**NOT ENFORCED**] | Optional. A list of columns to use as the Kafka message key. If unspecified, the Kafka key is left unset. When using the upsert envelope, the key must be unique. Use **NOT ENFORCED** to disable validation of key uniqueness. See [Upsert key selection](#upsert-key-selection) for details.  |
| **HEADERS** `<headers_column>` | Optional. A column containing headers to add to each Kafka message emitted by the sink. The column must be of type `map[text => text]` or `map[text => bytea]`. See [Headers](#headers) for details.  |
| **KEY FORMAT** `<key_format>` | Set the key encoding explicitly. Supported formats: `AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>`, `AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name>`, `JSON`, `TEXT`, `BYTES`.  |
| **VALUE FORMAT** `<value_format>` | Set the value encoding explicitly. Supported formats: `AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>`, `AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name>`, `JSON`, `TEXT`, `BYTES`.  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how changes to the sink's upstream relation are mapped to Kafka messages. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `DEBEZIUM` \| The generated schemas have a [Debezium-style diff envelope](#debezium-envelope) to capture changes in the input view or source. \| \| `UPSERT` \| The sink emits data with [upsert semantics](#upsert-envelope). Requires a unique key specified using the `KEY` option. \|  |
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `SNAPSHOT = <snapshot>` \| Default: `true`. Whether to emit the consolidated results of the query before the sink was created at the start of the sink. To see only results after the sink is created, specify `WITH (SNAPSHOT = false)`. \|  |

## Headers

Materialize always adds a header with key `materialize-timestamp` to each
message emitted by the sink. The value of this header indicates the logical time
at which the event described by the message occurred.

The `HEADERS` option allows specifying the name of a column containing
additional headers to add to each message emitted by the sink. When the option
is unspecified, no additional headers are added. When specified, the named
column must be of type `map[text => text]` or `map[text => bytea]`.

Header keys starting with `materialize-` are reserved for Materialize's internal
use. Materialize will ignore any headers in the map whose key starts with
`materialize-`.

**Known limitations:**
  * Materialize does not permit adding multiple headers with
    the same key.
  * Materialize cannot omit the headers column from the message value.
  * Materialize only supports using the `HEADERS` option with the [upsert
    envelope](#upsert-envelope).

## Formats

The `FORMAT` option controls the encoding of the message key and value that
Materialize writes to Kafka.

To use a different format for keys and values, use `KEY FORMAT .. VALUE FORMAT ..`
to choose independent formats for each.

### Avro

<p style="font-size:14px"><b>Syntax:</b> <code>FORMAT AVRO</code></p>

When using the Avro format, the value of each Kafka message is an Avro record
containing a field for each column of the sink's upstream relation. The names
and ordering of the fields in the record match the names and ordering of the
columns in the relation.

If the `KEY` option is specified, the key of each Kafka message is an Avro
record containing a field for each key column, in the same order and with
the same names.

If a column name is not a valid Avro name, Materialize adjusts the name
according to the following rules:

  * Replace all non-alphanumeric characters with underscores.
  * If the name begins with a number, add an underscore at the start of the
    name.
  * If the adjusted name is not unique, add the smallest number possible to
    the end of the name to make it unique.

For example, consider a table with two columns named `col-a` and `col@a`.
Materialize will use the names `col_a` and `col_a1`, respectively, in the
generated Avro schema.

#### Using Confluent Schema Registry

  * Materialize will automatically publish Avro schemas for the key, if present,
    and the value to the registry.

  * You can specify the
    [fullnames](https://avro.apache.org/docs/++version++/specification/#names) for the
    Avro schemas Materialize generates using the `AVRO KEY FULLNAME` and `AVRO
    VALUE FULLNAME` [syntax](#syntax).

  * You can automatically have nullable fields in the Avro schemas default to `null`
    by using the [`NULL DEFAULTS` option](#syntax).

  * You can [add `doc` fields](#avro-schema-documentation) to the Avro schemas.

  * You can set the compatibility level for a subject with the `KEY COMPATIBILITY
    LEVEL` and `VALUE COMPATIBILITY LEVEL` [options](#schema-compatibility-levels).
    The level is applied only when the subject has no compatibility level yet. If
    the subject already has one, it is left unchanged.

#### Using [AWS Glue Schema Registry](/sql/create-connection/#aws-glue-schema-registry)

> **Public Preview:** This feature is in public preview.

  * Materialize registers Avro schemas for the key, if present, and the value in
    the registry named by the connection. The registry must already exist.

  * By default, each schema is named after the topic (`<topic>-value`, and
    `<topic>-key` when a key is present). You can override these with the
    `KEY SCHEMA NAME` and `VALUE SCHEMA NAME` options.

  * You can set the compatibility level applied to a newly created schema with
    the `KEY COMPATIBILITY LEVEL` and `VALUE COMPATIBILITY LEVEL`
    [options](#syntax), defaulting to `BACKWARD` when omitted. The level is set
    only when Materialize creates the schema. If the schema already exists, the
    sink adds a new version to it and leaves its compatibility level unchanged.

  * The `AVRO ... FULLNAME`, `NULL DEFAULTS`, and `doc` options are not supported.

##### Compatibility levels

To specify compatibility levels, use the Confluent compatibility level names shown
below. The table also shows the equivalent AWS Glue compatibility levels for
reference. AWS Glue's `DISABLED` compatibility level has no equivalent Confluent
compatibility level and is not supported.

Compatibility level | AWS Glue equivalent
--------------------|--------------------
`BACKWARD`          | `BACKWARD`
`BACKWARD_TRANSITIVE` | `BACKWARD_ALL`
`FORWARD`           | `FORWARD`
`FORWARD_TRANSITIVE` | `FORWARD_ALL`
`FULL`              | `FULL`
`FULL_TRANSITIVE`   | `FULL_ALL`
`NONE`              | `NONE`

#### Publishing Schemas

With either registry, Materialize publishes the schemas when the sink starts
running, not when you run `CREATE SINK`. The schema names and definitions are not
validated against the registry at `CREATE SINK` time, so registry errors (for
example a name that collides with an incompatible existing schema) surface once
the sink starts publishing rather than at creation.

SQL types are converted to Avro types according to the following conversion
table:

SQL type                         | Avro type
---------------------------------|----------
[`bigint`]                       | `"long"`
[`boolean`]                      | `"boolean"`
[`bytea`]                        | `"bytes"`
[`date`]                         | `{"type": "int", "logicalType": "date"}`
[`double precision`]             | `"double"`
[`integer`]                      | `"int"`
[`interval`]                     | `{"type": "fixed", "size": 16, "name": "com.materialize.sink.interval"}`
[`jsonb`]                        | `{"type": "string", "connect.name": "io.debezium.data.Json"}`
[`map`]                          | `{"type": "map", "values": ...}`
[`list`]                         | `{"type": "array", "items": ...}`
[`numeric(p,s)`][`numeric`]      | `{"type": "bytes", "logicalType": "decimal", "precision": p, "scale": s}`
[`oid`]                          | `{"type": "fixed", "size": 4, "name": "com.materialize.sink.uint4"}`
[`real`]                         | `"float"`
[`record`]                       | `{"type": "record", "name": ..., "fields": ...}`
[`smallint`]                     | `"int"`
[`text`]                         | `"string"`
[`time`]                         | `{"type": "long", "logicalType": "time-micros"}`
[`uint2`]                        | `{"type": "fixed", "size": 2, "name": "com.materialize.sink.uint2"}`
[`uint4`]                        | `{"type": "fixed", "size": 4, "name": "com.materialize.sink.uint4"}`
[`uint8`]                        | `{"type": "fixed", "size": 8, "name": "com.materialize.sink.uint8"}`
[`timestamp (p)`][`timestamp`]   | If precision `p` is less than or equal to 3:<br>`{"type": "long", "logicalType: "timestamp-millis"}`<br>Otherwise:<br>`{"type": "long", "logicalType: "timestamp-micros"}`
[`timestamptz (p)`][`timestamp`] | Same as `timestamp (p)`.
[Arrays]                         | `{"type": "array", "items": ...}`

If a SQL column is nullable, and its type converts to Avro type `t`
according to the above table, the Avro type generated for that column
will be `["null", t]`, since nullable fields are represented as unions
in Avro.

In the case of a sink on a materialized view, Materialize may not be
able to infer the non-nullability of columns in all cases, and will
conservatively assume the columns are nullable, thus producing a union
type as described above. If this is not desired, the materialized view
may be created using [non-null assertions](../../create-materialized-view#non-null-assertions).

#### Avro schema documentation

Materialize allows control over the `doc` attribute for record fields and types
in the generated Avro schemas for the sink.

For the container record type (named `row` for the key schema and `envelope` for
the value schema, unless overridden by the [`AVRO ... FULLNAME` options](#syntax)),
Materialize searches for documentation in the following locations, in order:

1. For the key schema, a [`KEY DOC ON TYPE` option](#syntax)
   naming the sink's upstream relation. For the value schema, a
   [`VALUE DOC ON TYPE` option](#syntax) naming the
   sink's upstream relation.
2. A [comment](/sql/comment-on) on the sink's upstream relation.

For record types within the container record type, Materialize searches for
documentation in the following locations, in order:

1. For the key schema, a [`KEY DOC ON TYPE` option](#syntax)
   naming the SQL type corresponding to the record type. For the value schema, a
   [`VALUE DOC ON TYPE` option](#syntax) naming the SQL type
   corresponding to the record type.
2. A [`DOC ON TYPE` option](#syntax) naming the SQL type
   corresponding to the record type.
3. A [comment](/sql/comment-on) on the SQL type corresponding to the record
   type.

Similarly, for each field of each record type in the Avro schema, Materialize
documentation in the following locations, in order:

1. For the key schema, a [`KEY DOC ON COLUMN` option](#syntax)
   naming the SQL column corresponding to the field. For the value schema, a
   [`VALUE DOC ON COLUMN` option](#syntax) naming the column
   corresponding to the field.
2. A [`DOC ON COLUMN` option](#syntax) naming the SQL column
   corresponding to the field.
3. A [comment](/sql/comment-on) on the SQL column corresponding to the field.

For each field or type, Materialize uses the documentation from the first
location that exists. If no documentation is found for a given field or type,
the `doc` attribute is omitted for that field or type.

### JSON

<p style="font-size:14px"><b>Syntax:</b> <code>FORMAT JSON</code></p>

When using the JSON format, the value of each Kafka message is a JSON object
containing a field for each column of the sink's upstream relation. The names
and ordering of the fields in the record match the names and ordering of the
columns in the relation.

If the `KEY` option is specified, the key of each Kafka message is a JSON
object containing a field for each key column, in the same order and with the
same names.

SQL values are converted to JSON values according to the following conversion
table:

SQL type                     | Conversion
-----------------------------|-------------------------------------
[`array`][`arrays`]          | Values are converted to JSON arrays.
[`bigint`]                   | Values are converted to JSON numbers.
[`boolean`]                  | Values are converted to `true` or `false`.
[`integer`]                  | Values are converted to JSON numbers.
[`list`]                     | Values are converted to JSON arrays.
[`numeric`]                  | Values are converted to a JSON string containing the decimal representation of the number.
[`record`]                   | Records are converted to JSON objects. The names and ordering of the fields in the object match the names and ordering of the fields in the record.
[`smallint`]                 | values are converted to JSON numbers.
[`timestamp`][`timestamp`]<br>[`timestamptz`][`timestamp`] | Values are converted to JSON strings containing the fractional number of milliseconds since the Unix epoch. The fractional component has microsecond precision (i.e., three digits of precision). Example: `"1720032185.312"`
[`uint2`]                    | Values are converted to JSON numbers.
[`uint4`]                    | Values are converted to JSON numbers.
[`uint8`]                    | Values are converted to JSON numbers.
Other                        | Values are cast to [`text`] and then converted to JSON strings.

### Text/Bytes

The `TEXT` and `BYTES` format options only support single-column encoding and
cannot be used for keys or values with multiple columns.

Additionally, the `BYTES` format only works with scalar data types.

## Envelopes

The sink's envelope determines how changes to the sink's upstream relation are
mapped to Kafka messages.

There are two fundamental types of change events:

  * An **insertion** event is the addition of a new row to the upstream
    relation.
  * A **deletion** event is the removal of an existing row from the upstream
    relation.

When a `KEY` is specified, an insertion event and deletion event that occur at
the same time are paired together into a single **update** event that contains
both the old and new value for the given key.

### Upsert

<p style="font-size:14px"><b>Syntax:</b> <code>ENVELOPE UPSERT</code></p>

The upsert envelope:

  * Requires that you specify a unique key for the sink's upstream relation
    using the `KEY` option. See [upsert key selection](#upsert-key-selection)
    for details.
  * For an insertion event, emits the row without additional decoration.
  * For an update event, emits the new row without additional decoration. The
    old row is not emitted.
  * For a deletion event, emits a message with a `null` value (i.e., a
    _tombstone_).

Consider using the upsert envelope if:

  * You need to follow standard Kafka conventions for upsert semantics.
  * You want to enable key-based compaction on the sink's Kafka topic while
    retaining the most recent value for each key.

### Debezium

<p style="font-size:14px"><b>Syntax:</b> <code>ENVELOPE DEBEZIUM</code></p>

The Debezium envelope wraps each event in an object containing a `before` and
`after` field to indicate whether the event was an insertion, deletion, or
update event:

```json
// Insertion event.
{"before": null, "after": {"field1": "val1", ...}}

// Deletion event.
{"before": {"field1": "val1", ...}, "after": null}

// Update event.
{"before": {"field1": "oldval1", ...}, "after": {"field1": "newval1", ...}}
```

Note that the sink will only produce update events if a `KEY` is specified.

Consider using the Debezium envelope if:

  * You have downstream consumers that want update events to contain both the
    old and new value of the row.
  * There is no natural `KEY` for the sink.

## Features

### Automatic topic creation

If the specified Kafka topic does not exist, Materialize will attempt to create
it using the broker's default number of partitions, default replication factor,
default compaction policy, and default retention policy, unless any specific
overrides are provided as part of the [connection options](#syntax).

If the connection's [progress topic](#exactly-once-processing) does not exist,
Materialize will attempt to create it with a single partition, the broker's
default replication factor, compaction enabled, and both size- and time-based
retention disabled. The replication factor can be overridden using the
`PROGRESS TOPIC REPLICATION FACTOR` option when creating a connection
[`CREATE CONNECTION`](/sql/create-connection).

To customize topic-level configuration, including compaction settings and other
values, use the `TOPIC CONFIG` option in the [connection options](#syntax)
to set any relevant kafka [topic configs](https://kafka.apache.org/documentation/#topicconfigs).

If you manually create the topic or progress topic in Kafka before
running `CREATE SINK`, observe the following guidance:

| Topic          | Configuration       | Guidance
|----------------|---------------------|---------
| Data topic     | Partition count     | Your choice, based on your performance and ordering requirements.
| Data topic     | Replication factor  | Your choice, based on your durability requirements.
| Data topic     | Compaction          | Your choice, based on your downstream applications' requirements. If using the [Upsert envelope](#upsert), enabling compaction is typically the right choice.
| Data topic     | Retention           | Your choice, based on your downstream applications' requirements.
| Progress topic | Partition count     | **Must be set to 1.** Using multiple partitions can cause Materialize to violate its [exactly-once guarantees](#exactly-once-processing).
| Progress topic | Replication factor  | Your choice, based on your durability requirements.
| Progress topic | Compaction          | We recommend enabling compaction to avoid accumulating unbounded state. Disabling compaction may cause performance issues, but will not cause correctness issues.
| Progress topic | Retention           | **Must be disabled.** Enabling retention can cause Materialize to violate its [exactly-once guarantees](#exactly-once-processing).
| Progress topic | Tiered storage      | We recommend disabling tiered storage to allow for more aggressive data compaction. Fully compacted data requires minimal storage, typically only tens of bytes per sink, making it cost-effective to maintain directly on local disk.
> **Warning:** Dropping a Kafka sink doesn't drop the corresponding topic. For more information, see the [Kafka documentation](https://kafka.apache.org/documentation/).

### Exactly-once processing

By default, Kafka sinks provide [exactly-once processing guarantees](https://kafka.apache.org/documentation/#semantics), which ensures that messages are not duplicated or dropped in failure scenarios.

To achieve this, Materialize stores some internal metadata in an additional
*progress topic*. This topic is shared among all sinks that use a particular
[Kafka connection](/sql/create-connection/#kafka). The name of the progress
topic can be specified when [creating a
connection](/sql/create-connection/#kafka); otherwise, a default name of
`_materialize-progress-{REGION ID}-{CONNECTION ID}` is used. In either case,
Materialize will attempt to create the topic if it does not exist. The contents
of this topic are not user-specified.

#### End-to-end exactly-once processing

Exactly-once semantics are an end-to-end property of a system, but Materialize
only controls the initial produce step. To ensure _end-to-end_ exactly-once
message delivery, you should ensure that:

- The broker is configured with replication factor greater than 3, with unclean
  leader election disabled (`unclean.leader.election.enable=false`).
- All downstream consumers are configured to only read committed data
  (`isolation.level=read_committed`).
- The consumers' processing is idempotent, and offsets are only committed when
  processing is complete.

For more details, see [the Kafka documentation](https://kafka.apache.org/documentation/).

### Partitioning

By default, Materialize assigns a partition to each message using the following
strategy:

  1. Encode the message's key in the specified format.
  2. If the format uses a schema registry (Confluent or AWS Glue), strip out
     the header carrying the schema ID from the encoded bytes.
  3. Hash the remaining encoded bytes using [SeaHash].
  4. Divide the hash value by the topic's partition count and assign the
     remainder as the message's partition.

If a message has no key, all messages are sent to partition 0.

To configure a custom partitioning strategy, you can use the `PARTITION BY`
option. This option allows you to specify a SQL expression that computes a hash
for each message, which determines what partition to assign to the message:

```sql
-- General syntax.
CREATE SINK ... INTO KAFKA CONNECTION <name> (PARTITION BY = <expression>) ...;

-- Example.
CREATE SINK ... INTO KAFKA CONNECTION <name> (
    PARTITION BY = kafka_murmur2(name || address)
) ...;
```

The expression:
  * Must have a type that can be assignment cast to [`uint8`].
  * Can refer to any column in the sink's underlying relation when using the
    [upsert envelope](#upsert-envelope).
  * Can refer to any column in the sink's key when using the
    [Debezium envelope](#debezium-envelope).

Materialize uses the computed hash value to assign a partition to each message
as follows:

  1. If the hash is `NULL` or computing the hash produces an error, assign
     partition 0.
  2. Otherwise, divide the hash value by the topic's partition count and assign
     the remainder as the message's partition (i.e., `partition_id = hash %
     partition_count`).

Materialize provides several [hash functions](/sql/functions/#hash-functions)
which are commonly used in Kafka partition assignment:

  * `crc32`
  * `kafka_murmur2`
  * `seahash`

For a full example of using the `PARTITION BY` option, see [Custom
partioning](#custom-partitioning).

## Required privileges

To execute the `CREATE SINK` command, you need:

- `CREATE` privileges on the containing schema.
- `SELECT` privileges on the item being written out to an external system.
  - NOTE: if the item is a materialized view, then the view owner must also have the necessary privileges to
    execute the view definition.
- `CREATE` privileges on the containing cluster if the sink is created in an existing cluster.
- `CREATECLUSTER` privileges on the system if the sink is not created in an existing cluster.
- `USAGE` privileges on all connections and secrets used in the sink definition.
- `USAGE` privileges on the schemas that all connections and secrets in the
  statement are contained in.

See also [Required Kafka ACLs](#required-kafka-acls).

## Required Kafka ACLs

The access control lists (ACLs) on the Kafka cluster must allow Materialize
to perform the following operations on the following resources:

Operation type  | Resource type    | Resource name
----------------|------------------|--------------
Read, Write     | Topic            | Consult `mz_kafka_connections.sink_progress_topic` for the sink's connection
Write           | Topic            | The specified [`TOPIC` option](#syntax)
Write           | Transactional ID | All transactional IDs beginning with the specified [`TRANSACTIONAL ID PREFIX` option](#syntax)
Read            | Group            | All group IDs beginning with the specified [`PROGRESS GROUP ID PREFIX` option](#syntax)

When using [automatic topic creation](#automatic-topic-creation), Materialize
additionally requires access to the following operations:

Operation type   | Resource type    | Resource name
-----------------|------------------|--------------
DescribeConfigs  | Cluster          | n/a
Create           | Topic            | The specified `TOPIC` option

## Kafka transaction markers

Materialize uses [Kafka
transactions](https://www.confluent.io/blog/transactions-apache-kafka/). When
Kafka transactions are used, special control messages known as **transaction
markers** are published to the topic. Transaction markers inform both the broker
and clients about the status of a transaction. When a topic is read using a
standard Kafka consumer, these markers are not exposed to the application, which
can give the impression that some offsets are being skipped.

## Troubleshooting

### Upsert key selection

The `KEY` that you specify for an upsert envelope sink must be a unique key of
the sink's upstream relation.

Materialize will attempt to validate the uniqueness of the specified key. If
validation fails, you'll receive an error message like one of the following:

```
ERROR:  upsert key could not be validated as unique
DETAIL: Materialize could not prove that the specified upsert envelope key
("col1") is a unique key of the upstream relation. There are no known
valid unique keys for the upstream relation.

ERROR:  upsert key could not be validated as unique
DETAIL: Materialize could not prove that the specified upsert envelope key
("col1") is a unique key of the upstream relation. The following keys
are known to be unique for the upstream relation:
  ("col2")
  ("col3", "col4")
```

The first error message indicates that Materialize could not prove the existence
of any unique keys for the sink's upstream relation. The second error message
indicates that Materialize could prove that `col2` and `(col3, col4)` were
unique keys of the sink's upstream relation, but could not provide the
uniqueness of the specified upsert key of `col1`.

There are three ways to resolve this error:

* Change the sink to use one of the keys that Materialize determined to be
  unique, if such a key exists and has the appropriate semantics for your
  use case.

* Create a materialized view that deduplicates the input relation by the
  desired upsert key:

  ```mzsql
  -- For each row with the same key `k`, the `ORDER BY` clause ensures we
  -- keep the row with the largest value of `v`.
  CREATE MATERIALIZED VIEW deduped AS
  SELECT DISTINCT ON (k) v
  FROM original_input
  ORDER BY k, v DESC;

  -- Materialize can now prove that `k` is a unique key of `deduped`.
  CREATE SINK s
  FROM deduped
  INTO KAFKA CONNECTION kafka_connection (TOPIC 't')
  KEY (k)
  FORMAT JSON ENVELOPE UPSERT;
  ```

  > **Note:** Maintaining the `deduped` materialized view requires memory proportional to the
>   number of records in `original_input`. Be sure to assign `deduped`
>   to a cluster with adequate resources to handle your data volume.

* Use the `NOT ENFORCED` clause to disable Materialize's validation of the key's
  uniqueness:

  ```mzsql
  CREATE SINK s
  FROM original_input
  INTO KAFKA CONNECTION kafka_connection (TOPIC 't')
  -- We have outside knowledge that `k` is a unique key of `original_input`, but
  -- Materialize cannot prove this, so we disable its key uniqueness check.
  KEY (k) NOT ENFORCED
  FORMAT JSON ENVELOPE UPSERT;
  ```

  You should only disable this verification if you have outside knowledge of
  the properties of your data that guarantees the uniqueness of the key you
  have specified.

  > **Warning:** If the key is not in fact unique, downstream consumers may not be able to
>   correctly interpret the data in the topic, and Kafka key compaction may
>   incorrectly garbage collect records from the topic.

## Examples

### Creating a connection

A connection describes how to connect and authenticate to an external system you
want Materialize to write data to.

Once created, a connection is **reusable** across multiple `CREATE SINK`
statements. For more details on creating connections, check the
[`CREATE CONNECTION`](/sql/create-connection) documentation page.

#### Broker

**SSL:**

```mzsql
CREATE SECRET kafka_ssl_key AS '<BROKER_SSL_KEY>';
CREATE SECRET kafka_ssl_crt AS '<BROKER_SSL_CRT>';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9093',
    SSL KEY = SECRET kafka_ssl_key,
    SSL CERTIFICATE = SECRET kafka_ssl_crt
);
```

**SASL:**

```mzsql
CREATE SECRET kafka_password AS '<BROKER_PASSWORD>';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9092',
    SASL MECHANISMS = 'SCRAM-SHA-256',
    SASL USERNAME = 'foo',
    SASL PASSWORD = SECRET kafka_password
);
```

#### Schema Registry

**Confluent:**

**SSL:**

```mzsql
CREATE SECRET csr_ssl_crt AS '<CSR_SSL_CRT>';
CREATE SECRET csr_ssl_key AS '<CSR_SSL_KEY>';
CREATE SECRET csr_password AS '<CSR_PASSWORD>';

CREATE CONNECTION csr_ssl TO CONFLUENT SCHEMA REGISTRY (
    URL 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9093',
    SSL KEY = SECRET csr_ssl_key,
    SSL CERTIFICATE = SECRET csr_ssl_crt,
    USERNAME = 'foo',
    PASSWORD = SECRET csr_password
);
```

**Basic HTTP Authentication:**

```mzsql
CREATE SECRET IF NOT EXISTS csr_username AS '<CSR_USERNAME>';
CREATE SECRET IF NOT EXISTS csr_password AS '<CSR_PASSWORD>';

CREATE CONNECTION csr_basic_http
  FOR CONFLUENT SCHEMA REGISTRY
  URL '<CONFLUENT_REGISTRY_URL>',
  USERNAME = SECRET csr_username,
  PASSWORD = SECRET csr_password;
```

**AWS Glue:**

> **Public Preview:** This feature is in public preview.

```mzsql
CREATE CONNECTION aws_conn TO AWS (
    ASSUME ROLE ARN = 'arn:aws:iam::123456789000:role/MaterializeGlue'
);

CREATE CONNECTION glue_conn TO AWS GLUE SCHEMA REGISTRY (
    AWS CONNECTION = aws_conn,
    REGISTRY = 'my-registry'
);
```

### Creating a sink

#### Upsert envelope

**Avro Confluent:**

```mzsql
CREATE SINK avro_sink
  FROM <source, table or mview>
  INTO KAFKA CONNECTION kafka_connection (TOPIC 'test_avro_topic')
  KEY (key_col)
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  ENVELOPE UPSERT;
```

**Avro AWS Glue:**

> **Public Preview:** This feature is in public preview.

The registry named by the connection must already exist. The IAM role assumed
by the AWS connection must have the schema-write permissions listed under [AWS
Glue Schema Registry](/sql/create-connection/#aws-glue-schema-registry).

```mzsql
CREATE SINK glue_sink
  IN CLUSTER my_io_cluster
  FROM <source, table or mview>
  INTO KAFKA CONNECTION kafka_connection (
    TOPIC 'test_avro_topic'
  )
  KEY (key_col)
  FORMAT AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION glue_conn
  ENVELOPE UPSERT;
```

See [Avro](#avro) for the schema-name defaults and how compatibility levels map
to their AWS Glue equivalents.

**JSON:**

```mzsql
CREATE SINK json_sink
  FROM <source, table or mview>
  INTO KAFKA CONNECTION kafka_connection (TOPIC 'test_json_topic')
  KEY (key_col)
  FORMAT JSON
  ENVELOPE UPSERT;
```

#### Debezium envelope

**Avro Confluent:**

```mzsql
CREATE SINK avro_sink
  FROM <source, table or mview>
  INTO KAFKA CONNECTION kafka_connection (TOPIC 'test_avro_topic')
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  ENVELOPE DEBEZIUM;
```

**Avro AWS Glue:**

> **Public Preview:** This feature is in public preview.

The registry named by the connection must already exist. The IAM role assumed
by the AWS connection must have the schema-write permissions listed under [AWS
Glue Schema Registry](/sql/create-connection/#aws-glue-schema-registry).

```mzsql
CREATE SINK glue_sink
  IN CLUSTER my_io_cluster
  FROM <source, table or mview>
  INTO KAFKA CONNECTION kafka_connection (
    TOPIC 'test_avro_topic'
  )
  KEY (key_col)
  FORMAT AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION glue_conn
  ENVELOPE DEBEZIUM;
```

See [Avro](#avro) for the schema-name defaults and how compatibility levels map
to their AWS Glue equivalents.

#### Topic configuration

```mzsql
CREATE SINK custom_topic_sink
  IN CLUSTER my_io_cluster
  FROM <source, table or mview>
  INTO KAFKA CONNECTION kafka_connection (
    TOPIC 'test_avro_topic',
    TOPIC PARTITION COUNT 4,
    TOPIC REPLICATION FACTOR 2,
    TOPIC CONFIG MAP['cleanup.policy' => 'compact']
  )
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  ENVELOPE UPSERT;
```

#### Schema compatibility levels

**Avro Confluent:**

```mzsql
CREATE SINK compatibility_level_sink
  IN CLUSTER my_io_cluster
  FROM <source, table or mview>
  INTO KAFKA CONNECTION kafka_connection (
    TOPIC 'test_avro_topic'
  )
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection (
    KEY COMPATIBILITY LEVEL 'BACKWARD',
    VALUE COMPATIBILITY LEVEL 'BACKWARD_TRANSITIVE'
  )
  ENVELOPE UPSERT;
```

**Avro AWS Glue:**

> **Public Preview:** This feature is in public preview.

```mzsql
CREATE SINK compatibility_level_sink
  IN CLUSTER my_io_cluster
  FROM <source, table or mview>
  INTO KAFKA CONNECTION kafka_connection (
    TOPIC 'test_avro_topic'
  )
  KEY (key_col)
  FORMAT AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION glue_conn (
    KEY COMPATIBILITY LEVEL 'BACKWARD',
    VALUE COMPATIBILITY LEVEL 'FULL'
  )
  ENVELOPE UPSERT;
```

See [Avro](#avro) for the schema-name defaults and how compatibility levels map
to their AWS Glue equivalents.

#### Documentation comments

Consider the following sink, `docs_sink`, built on top of a relation `t` with
several [SQL comments](/sql/comment-on) attached.

```mzsql
CREATE TABLE t (key int NOT NULL, value text NOT NULL);
COMMENT ON TABLE t IS 'SQL comment on t';
COMMENT ON COLUMN t.value IS 'SQL comment on t.value';

CREATE SINK docs_sink
FROM t
INTO KAFKA CONNECTION kafka_connection (TOPIC 'doc-commont-example')
KEY (key)
FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection (
    DOC ON TYPE t = 'Top-level comment for container record in both key and value schemas',
    KEY DOC ON COLUMN t.key = 'Comment on column only in key schema',
    VALUE DOC ON COLUMN t.key = 'Comment on column only in value schema'
)
ENVELOPE UPSERT;
```

When `docs_sink` is created, Materialize will publish the following Avro schemas
to the Confluent Schema Registry:

  * Key schema:

    ```json
    {
      "type": "record",
      "name": "row",
      "doc": "Top-level comment for container record in both key and value schemas",
      "fields": [
        {
          "name": "key",
          "type": "int",
          "doc": "Comment on column only in key schema"
        }
      ]
    }
    ```

  * Value schema:

    ```json
    {
      "type": "record",
      "name": "envelope",
      "doc": "Top-level comment for container record in both key and value schemas",
      "fields": [
        {
          "name": "key",
          "type": "int",
          "doc": "Comment on column only in value schema"
        },
        {
          "name": "value",
          "type": "string",
          "doc": "SQL comment on t.value"
        }
      ]
    }
    ```

See [Avro schema documentation](#avro-schema-documentation) for details
about the rules by which Materialize attaches `doc` fields to records.

#### Custom partitioning

Suppose your Materialize deployment stores data about customers and their
orders. You want to emit the order data to Kafka with upsert semantics so that
only the latest state of each order is retained. However, you want the data to
be partitioned by only customer ID (i.e., not order ID), so that all orders for
a given customer go to the same partition.

Create a sink using the `PARTITION BY` option to accomplish this:

```sql
CREATE SINK customer_orders
  FROM ...
  INTO KAFKA CONNECTION kafka_connection (
    TOPIC 'customer-orders',
    -- The partition hash includes only the customer ID, so the partition
    -- will be assigned only based on the customer ID.
    PARTITION BY = seahash(customer_id::text)
  )
  -- The key includes both the customer ID and order ID, so Kafka's compaction
  -- will keep only the latest message for each order ID.
  KEY (customer_id, order_id)
  FORMAT JSON
  ENVELOPE UPSERT;
```

## Related pages

- [`SHOW SINKS`](/sql/show-sinks)
- [`DROP SINK`](/sql/drop-sink)

[`bigint`]: ../../types/integer
[`boolean`]: ../../types/boolean
[`bytea`]: ../../types/bytea
[`date`]: ../../types/date
[`double precision`]: ../../types/float
[`integer`]: ../../types/integer
[`interval`]: ../../types/interval
[`jsonb`]: ../../types/jsonb
[`map`]: ../../types/map
[`list`]: ../../types/list
[`numeric`]: ../../types/numeric
[`oid`]: ../../types/oid
[`real`]: ../../types/float
[`record`]: ../../types/record
[`smallint`]: ../../types/integer
[`text`]: ../../types/text
[`time`]: ../../types/time
[`uint2`]: ../../types/uint
[`uint4`]: ../../types/uint
[`uint8`]: ../../types/uint
[`timestamp`]: ../../types/timestamp
[`timestamp with time zone`]: ../../types/timestamp
[arrays]: ../../types/array
[`kafka-topics.sh`]: https://docs.confluent.io/kafka/operations-tools/kafka-tools.html#kafka-topics-sh
[SeaHash]: https://docs.rs/seahash/latest/seahash/

<!-- mz-docs page: sql/create-source -->

# CREATE SOURCE

`CREATE SOURCE` connects Materialize to an external data source.

A source in Materialize represents an external data source. More concretely, it
specifies the connection and the ingestion configuration to use for a particular
external data source (e.g., PostgreSQL, Kafka). For those familiar with
PostgreSQL's foreign servers and foreign tables, a source is like a foreign
server, and the tables (or subsources) created from the source are like foreign
tables.

Before creating a source in Materialize, you must ensure that the external data
source is properly configured and accessible so that Materialize can establish a
connection and ingest its data. The exact configuration depends on the type of
data source.

## Syntax summary

<!--"Docs Note: Using include-example shortcode instead of include-syntax since only want the code snippet on this page."
-->

### New syntax

The new `CREATE SOURCE` syntax allows Materialize to handle certain upstream
schema changes, specifically adding or dropping columns, without downtime. It is
used in conjunction with the new [`CREATE TABLE ... FROM
SOURCE`](/sql/create-table/) syntax.

**PostgreSQL (New):**

To create a source from an external PostgreSQL:
```mzsql
CREATE SOURCE [IF NOT EXISTS] <source_name>
[IN CLUSTER <cluster_name>]
FROM POSTGRES CONNECTION <connection_name> (PUBLICATION '<publication_name>')
[WITH ( <with_option> [, ...] )]
;

```

For details, see [CREATE SOURCE: PostgreSQL (New Syntax)](/sql/create-source/postgres-v2/).

**MySQL (New):**

To create a source from an external MySQL database:
```mzsql
CREATE SOURCE [IF NOT EXISTS] <source_name>
[IN CLUSTER <cluster_name>]
FROM MYSQL CONNECTION <connection_name>
[WITH ( <with_option> [, ...] )]
;

```

For details, see [CREATE SOURCE: MySQL (New Syntax)](/sql/create-source/mysql-v2/).

**SQL Server (New):**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM SQL SERVER CONNECTION <connection_name>
[WITH ( <with_option> [, ...] )]

```

For details, see [CREATE SOURCE: SQL Server (New Syntax)](/sql/create-source/sql-server-v2/).

**Kafka/Redpanda (New):**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )];

```

For details, see [CREATE SOURCE: Kafka/Redpanda (New Syntax)](/sql/create-source/kafka-v2/).

**Webhook:**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM WEBHOOK
  BODY FORMAT <TEXT | JSON [ARRAY] | BYTES>
  [INCLUDE HEADER <header_name> AS <column_alias> [BYTES] |
   INCLUDE HEADERS [ ( [NOT] <header_name> [, [NOT] <header_name> ... ] ) ]
  ][...]
  [CHECK (
      [WITH ( <BODY|HEADERS|SECRET <secret_name>> [AS <alias>] [BYTES] [, ...])]
      <check_expression>
    )
  ]

```

For details, see [CREATE SOURCE: Webhook](/sql/create-source/webhook/).

### Legacy syntax

The legacy `CREATE SOURCE` syntax requires downtime to handle upstream schema
changes. Prefer the [new syntax](#new-syntax) for new sources where available.

**PostgreSQL (Legacy):**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM POSTGRES CONNECTION <connection_name> (
  PUBLICATION '<publication_name>'
  [, TEXT COLUMNS ( <col1> [, ...] ) ]
  [, EXCLUDE COLUMNS ( <col1> [, ...] ) ]
)
<FOR ALL TABLES | FOR SCHEMAS ( <schema1> [, ...] ) | FOR TABLES ( <table1> [AS <subsrc_name>] [, ...] )>
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

For details, see [CREATE SOURCE: PostgreSQL (Legacy)](/sql/create-source/postgres/).

**MySQL (Legacy):**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM MYSQL CONNECTION <connection_name> [
  (
    [TEXT COLUMNS ( <col1> [, ...] ) ]
    [, EXCLUDE COLUMNS ( <col1> [, ...] ) ]
  )
]
<FOR ALL TABLES | FOR SCHEMAS ( <schema1> [, ...] ) | FOR TABLES ( <table1> [AS <subsrc_name>] [, ...] )>
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

For details, see [CREATE SOURCE: MySQL (Legacy)](/sql/create-source/mysql/).

**SQL Server (Legacy):**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM SQL SERVER CONNECTION <connection_name>
  [ ( EXCLUDE COLUMNS (<col1> [, ...]) ) ]
  [ ( TEXT COLUMNS (<col1> [, ...]) ) ]
<FOR ALL TABLES | FOR TABLES ( <table1> [AS <subsrc_name>] [, ...] )>
[WITH ( <with_option> [, ...] )]

```

For details, see [CREATE SOURCE: SQL Server(Legacy)](/sql/create-source/sql-server/).

**Kafka/Redpanda (Legacy):**

**Format Avro:**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT AVRO
    USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>
      [KEY STRATEGY <key_strategy>]
      [VALUE STRATEGY <value_strategy>]
  | USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> (
      SCHEMA NAME = '<schema_name>'
    )
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | DEBEZIUM
  | UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]
]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**Format JSON:**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT JSON
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**Format TEXT/BYTES:**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT TEXT | BYTES
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**Format CSV:**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name> ( <col_name> [, ...] )
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT CSV WITH <n> COLUMNS | WITH HEADER [ ( <col_name> [, ...] ) ]
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**Format Protobuf:**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT PROTOBUF USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>
  | FORMAT PROTOBUF MESSAGE '<message_name>' USING SCHEMA '<schema_bytes>'
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]
]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**KEY FORMAT VALUE FORMAT:**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
KEY FORMAT <key_format> VALUE FORMAT <value_format>
-- <key_format> and <value_format> can be:
-- AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <conn_name>
--     [KEY STRATEGY <strategy>]
--     [VALUE STRATEGY <strategy>]
-- | AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_conn_name> (SCHEMA NAME = '<schema_name>')
-- | CSV WITH <num> COLUMNS DELIMITED BY <char>
-- | JSON | TEXT | BYTES
-- | PROTOBUF USING CONFLUENT SCHEMA REGISTRY CONNECTION <conn_name>
-- | PROTOBUF MESSAGE '<message_name>' USING SCHEMA '<schema_bytes>'
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | DEBEZIUM
  | UPSERT [(VALUE DECODING ERRORS = INLINE [AS name])]
]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

For details, see [CREATE SOURCE: Kafka/Redpanda (Legacy Syntax)](/sql/create-source/kafka/).

**Webhook:**

<no value>```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM WEBHOOK
  BODY FORMAT <TEXT | JSON [ARRAY] | BYTES>
  [INCLUDE HEADER <header_name> AS <column_alias> [BYTES] |
   INCLUDE HEADERS [ ( [NOT] <header_name> [, [NOT] <header_name> ... ] ) ]
  ][...]
  [CHECK (
      [WITH ( <BODY|HEADERS|SECRET <secret_name>> [AS <alias>] [BYTES] [, ...])]
      <check_expression>
    )
  ]

```

For details, see [CREATE SOURCE: Webhook](/sql/create-source/webhook/).

## Privileges

The privileges required to execute `CREATE SOURCE` are:

- `CREATE` privileges on the containing schema.
- `CREATE` privileges on the containing cluster if the source is created in an existing cluster.
- `CREATECLUSTER` privileges on the system if the source is not created in an existing cluster.
- `USAGE` privileges on all connections and secrets used in the source definition.
- `USAGE` privileges on the schemas that all connections and secrets in the
  statement are contained in.

## Available guides

The following guides step you through setting up sources:

| Type | External system |
|------|-----------------|
| **Databases (CDC): native connectors** | [PostgreSQL](/ingest-data/postgres/) <br> [MySQL](/ingest-data/mysql/) <br> [SQL Server](/ingest-data/sql-server/) |
| **Databases (CDC): via the Kafka connector** | [CockroachDB](/ingest-data/cdc-cockroachdb/) (using changefeeds) <br> [MongoDB](/ingest-data/mongodb/) (using Debezium) |
| **Message brokers** | [Kafka](/ingest-data/kafka/) <br> [Redpanda](/sql/create-source/kafka) |
| **Webhooks** | [Amazon EventBridge](/ingest-data/webhooks/amazon-eventbridge/) <br> [Segment](/ingest-data/webhooks/segment/) <br> [HubSpot](/ingest-data/webhooks/hubspot/) <br> [RudderStack](/ingest-data/webhooks/rudderstack/) <br> [SnowcatCloud](/ingest-data/webhooks/snowcatcloud/) <br> [Stripe](/ingest-data/webhooks/stripe/)|

## Best practices

### Separate cluster(s) for sources

In production, if possible, use a dedicated cluster for
[sources](/fundamentals/concepts/sources/); i.e., avoid putting sources on the same cluster
that hosts compute objects, sinks, and/or serves queries.

In addition, for upsert sources:

- Consider separating upsert sources from your other sources. Upsert sources
  have higher resource requirements (since, for upsert sources, Materialize
  maintains each key and associated last value for the key as well as to perform
  deduplication). As such, if possible, use a separate source cluster for upsert
  sources.

- Consider using a larger cluster size during snapshotting for upsert sources.
  Once the snapshotting operation is complete, you can downsize the cluster to
  align with the steady-state ingestion.

### Sizing a source

Some sources are low traffic and require relatively few resources to handle data ingestion, while others are high traffic and require hefty resource allocations. The cluster in which you place a source determines the amount of CPU, memory, and disk available to the source.

It's a good idea to size up the cluster hosting a source when:

  * You want to **increase throughput**. Larger sources will typically ingest data
    faster, as there is more CPU available to read and decode data from the
    upstream external system.

  * You are using the [upsert
    envelope](/sql/create-source/kafka/#upsert-envelope) or [Debezium
    envelope](/sql/create-source/kafka/#debezium-envelope), and your source
    contains **many unique keys**. These envelopes maintain state proportional
    to the number of unique keys in the upstream external system. Larger sizes
    can store more unique keys.

Sources share the resource allocation of their cluster with all other objects in
the cluster. Colocating multiple sources onto the same cluster can be more
resource efficient when you have many low-traffic sources that occasionally need
some burst capacity.

## Related pages

- [Sources](/fundamentals/concepts/sources/)
- [`SHOW SOURCES`](/sql/show-sources/)
- [`SHOW COLUMNS`](/sql/show-columns/)
- [`SHOW CREATE SOURCE`](/sql/show-create-source/)

