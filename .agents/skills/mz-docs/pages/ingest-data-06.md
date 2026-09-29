<!-- mz-docs page: ingest-data/webhooks/segment -->

# Segment
How to stream data from Segment to Materialize using webhooks
This guide walks through the steps to ingest data from [Segment](https://segment.com/)
into Materialize using the [Webhook source](/sql/create-source/webhook/).

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

### Before you begin

Ensure that you have:

- A Segment [source](https://segment.com/docs/connections/sources/) set up and running.

## Step 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your webhook
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

To create a cluster in Materialize, use the [`CREATE CLUSTER` command](/sql/create-cluster):

```mzsql
CREATE CLUSTER webhooks_cluster (SIZE = '25cc');

SET CLUSTER = webhooks_cluster;
```

## Step 2. Create a secret

To validate requests between Segment and Materialize, you must create a [secret](/sql/create-secret/):

```mzsql
CREATE SECRET segment_webhook_secret AS '<secret_value>';
```

Change the `<secret_value>` to a unique value that only you know and store it in a secure location.

## Step 3. Set up a webhook source

Using the secret from the previous step, create a [webhook source](/sql/create-source/webhook/)
in Materialize to ingest data from Segment. By default, the source will be
created in the active cluster; to use a different cluster, use the `IN
CLUSTER` clause.

```mzsql
CREATE SOURCE segment_source IN CLUSTER webhooks_cluster FROM WEBHOOK
  BODY FORMAT JSON
  INCLUDE HEADER 'event-type' AS event_type
  INCLUDE HEADERS
  CHECK (
    WITH ( BODY BYTES, HEADERS, SECRET segment_webhook_secret BYTES AS validation_secret)
    -- The constant_time_eq validation function **does not support** fully
    -- qualified secret names. We recommend always aliasing the secret name
    -- for ease of use.
    constant_time_eq(decode(headers->'x-signature', 'hex'), hmac(body, validation_secret, 'sha1'))
  );
```

After a successful run, the command returns a `NOTICE` message containing the
unique [webhook URL](/sql/create-source/webhook/#webhook-url)
that allows you to `POST` events to the source. Copy and store it. You will need
it for the next step.

The URL will have the following format:

```
https://<HOST>/api/webhook/<database>/<schema>/<src_name>
```

If you missed the notice, you can find the URLs for all webhook sources in the
[`mz_internal.mz_webhook_sources`](/sql/system-catalog/mz_internal/#mz_webhook_sources)
system table.

### Access and authentication

> **Warning:** Without a `CHECK` statement, **all requests will be accepted**. To prevent bad
> actors from injecting data into your source, it is **strongly encouraged** that
> you define a `CHECK` statement with your webhook sources.

The `CHECK` clause defines how to validate each request. At the time of writing,
Segment validates requests by signing them with an HMAC in the `X-Signature`
request header. The HMAC is a hex-encoded SHA1 hash using the secret
from **Step 2.** and the request body. Materialize decodes the signature using
the [`decode`](/sql/functions/#decode) function, getting the raw bytes, and
generate our own HMAC using the [`hmac`](/sql/functions/#hmac) function. If the
two values are equal, then the request is legitimate!

## Step 4. Create a webhook destination in Segment

1. In Segment, go to **Connections > Catalog**.

2. Search and click **Webhooks (Actions)**.

3. Click **Add destination**.

4. Select a data source and click **Next**.

5. Jot a *Destination Name* and click **Create Destination**.

## Step 5. Configure the mapping in Segment

A webhook destination in Segment requires a [data mapping](https://segment.com/blog/data-mapping/)
to send events from the source to the destination. For this guide, the
destination is the Materialize source. Follow these steps to create the correct
mapping:

1. Go to your webhook destination created in the previous step.

2. Click on **Mappings > New Mapping**.

3. Click **Send** and fill the configuration as follows:
   1. In **Select events to map and send**, fill the conditions as you wish.
   2. In **Add test**, select any of the events.
   3. In **Select mappings**, fill the fields as follows:
    Field               | Value
    ------------------- | ----------------------
    Url                 | Use the URL from the [Step 3](#step-3-set-up-a-webhook-source).
    Method              | `POST`
    Batch Size          | `0`
    Headers             | -
    Data                | `$event`
    Enable Batching     | `No`.

4. Click **Test Mapping** and validate the webhook is working.

5. After a succesful test, click **Save**.

  > **Note:** If **Test Mapping** fails in and throws a *"failed to validate the request"* error, it means the shared secret is not right. To fix this, follow this steps:
>  1. In **Segment**, go to your webhook destination created in the **Step 4**.
>  2. Click **Settings**.
>  3. In **Shared Secret**, enter the secret created in the **Step 2**.
>  4. Click **Save Changes**.

## Step 6. Validate incoming data

With the source set up in Materialize and the webhook destination configured in
Segment, you can now query the incoming data:

1. [In the Materialize console](/developer-tools/console/), navigate to
   the **SQL Shell**.

1. Use SQL queries to inspect and analyze the incoming data:

    ```mzsql
    SELECT * FROM segment_source LIMIT 10;
    ```

## Step 7. Transform incoming data

### JSON parsing

Webhook data is ingested as a JSON blob. We recommend creating a parsing view on
top of your webhook source that uses [`jsonb` operators](/sql/types/jsonb/#operators)
to map the individual fields to columns with the required data types.

**Page:**
```mzsql
CREATE VIEW parse_segment AS SELECT
    body->>'anonymousId' AS anonymousId,
    body->>'channel' AS channel,
    body->'context'->>'ip' AS context_ip,
    body->'context'->>'userAgent' AS context_user_agent,
    (body->'integrations'->>'All')::bool AS integrations_all,
    (body->'integrations'->>'Mixpanel')::bool AS integrations_mixpanel,
    (body->'integrations'->>'Salesforce')::bool AS integrations_salesforce,
    body->>'messageId' AS messageId,
    body->>'name' AS name,
    body->'properties'->>'title' AS properties_title,
    body->'properties'->>'url' AS properties_url,
    try_parse_monotonic_iso8601_timestamp(body->>'receivedAt') AS received_at,
    try_parse_monotonic_iso8601_timestamp(body->>'sentAt') AS sent_at,
    try_parse_monotonic_iso8601_timestamp(body->>'timestamp') AS timestamp,
    body->>'type' AS type,
    body->>'userId' AS user_id,
    body->>'version' AS version
FROM segment_source;
```

**Track:**

```mzsql
CREATE VIEW parse_segment AS SELECT
    body->>'anonymousId' AS anonymous_id,
    body->'context'->'library'->>'name' AS context_library_name,
    (body->'context'->'library'->>'version') AS context_library_version,
    body->'context'->'page'->>'path' AS context_page_path,
    body->'context'->'page'->>'referrer' AS context_page_referrer,
    body->'context'->'page'->>'search' AS context_page_search,
    body->'context'->'page'->>'title' AS context_page_title,
    body->'context'->'page'->>'url' AS context_page_url,
    body->'context'->>'userAgent' AS context_userAgent,
    body->'context'->>'ip' AS context_ip,
    body->>'event' AS event,
    body->>'messageId' AS message_id,
    body->'properties'->>'title' AS properties_title,
    try_parse_monotonic_iso8601_timestamp(body->>'receivedAt') AS received_at,
    try_parse_monotonic_iso8601_timestamp(body->>'sentAt') AS sent_at,
    try_parse_monotonic_iso8601_timestamp(body->>'timestamp') AS timestamp,
    body->>'type' AS type,
    body->>'userId' AS user_id,
    try_parse_monotonic_iso8601_timestamp(body->>'originalTimestamp') AS original_timestamp
FROM segment_source;
```

**Identity:**
```mzsql
CREATE VIEW parse_segment AS SELECT
    body->>'anonymousId' AS anonymous_id,
    body->>'channel' AS channel,
    body->'context'->>'ip' AS context_ip,
    body->'context'->>'userAgent' AS context_user_agent,
    (body->'integrations'->>'All')::bool AS integrations_all,
    (body->'integrations'->>'Mixpanel')::bool AS integrations_mixpanel,
    (body->'integrations'->>'Salesforce')::bool AS integrations_salesforce,
    body->>'messageId' AS messageId,
    try_parse_monotonic_iso8601_timestamp(body->>'receivedAt') AS received_at,
    try_parse_monotonic_iso8601_timestamp(body->>'sentAt') AS sent_at,
    try_parse_monotonic_iso8601_timestamp(body->>'timestamp') AS timestamp,
    body->'traits'->>'name' AS traits_name,
    body->'traits'->>'email' AS traits_email,
    body->'traits'->>'plan' AS traits_plan,
    (body->'traits'->>'logins')::numeric AS traits_logins,
    body->'traits'->'address'->>'street' AS traits_address_street,
    body->'traits'->'address'->>'city' AS traits_address_city,
    body->'traits'->'address'->>'state' AS traits_address_state,
    (body->'traits'->'address'->>'postalCode') AS traits_address_postalCode,
    body->'traits'->'address'->>'country' AS traits_address_country,
    body->>'type' AS type,
    body->>'userId' AS user_id,
    body->>'version' AS version
FROM segment_source;
```

Manually parsing JSON-formatted data in SQL can be tedious. You can use the [interactive JSON parser widget](https://materialize.com/docs/sql/types/jsonb/#parsing) to automatically turn a sample JSON payload into a parsing view with the individual fields mapped to columns.

### Timestamp handling

We highly recommend using the [`try_parse_monotonic_iso8601_timestamp`](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown)
function when casting from `text` to `timestamp`, which enables [temporal filter
pushdown](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

### Deduplication

With the vast amount of data processed and potential network issues, it's not
uncommon to receive duplicate records. You can use the `DISTINCT ON` clause to
efficiently remove duplicates. For more details, refer to the webhook source
[reference documentation](/sql/create-source/webhook/#handling-duplicated-and-partial-events).

## Next steps

With Materialize ingesting your Segment data, you can start exploring it,
computing real-time results that stay up-to-date as new data arrives, and
serving results efficiently. For more details, check out the
[Segment documentation](https://segment.com/docs/connections/destinations/catalog/actions-webhook/) and the
[webhook source reference documentation](/sql/create-source/webhook/).

<!-- mz-docs page: ingest-data/webhooks/snowcatcloud -->

# SnowcatCloud
How to stream data from SnowcatCloud to Materialize using webhooks
This guide walks through the steps to ingest data from [SnowcatCloud](https://www.snowcatcloud.com/)
into Materialize using the [Webhook source](/sql/create-source/webhook/).

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

## Before you begin

Ensure that you have:

- A [SnowcatCloud account](https://app.snowcatcloud.com/register)
- A Snowplow or Analytics.js compatible pipeline set up and running.

## Step 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your webhook
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

To create a cluster in Materialize, use the [`CREATE CLUSTER` command](/sql/create-cluster):

```mzsql
CREATE CLUSTER webhooks_cluster (SIZE = '25cc');

SET CLUSTER = webhooks_cluster;
```

## Step 2. Create a secret

To validate requests between SnowcatCloud and Materialize, you must create a [secret](/sql/create-secret/):

```mzsql
CREATE SECRET snowcat_webhook_secret AS '<secret_value>';
```

Change the `<secret_value>` to a unique value that only you know and store it in a secure location.

## Step 3. Set up a webhook source

Using the secret from the previous step, create a [webhook source](/sql/create-source/webhook/)
in Materialize to ingest data from SnowcatCloud. By default, the source will be
created in the active cluster; to use a different cluster, use the `IN
CLUSTER` clause.

```mzsql
CREATE SOURCE snowcat_source IN CLUSTER webhooks_cluster
  FROM WEBHOOK
    BODY FORMAT JSON
    CHECK (
      WITH (
        HEADERS,
        BODY AS body,
        SECRET snowcat_webhook_secret AS validation_secret
      )
      -- The constant_time_eq validation function **does not support** fully
      -- qualified secret names. We recommend always aliasing the secret name
      -- for ease of use.
      constant_time_eq(headers->'authorization', validation_secret)
);
```

After a successful run, the command returns a `NOTICE` message containing the
unique [webhook URL](/sql/create-source/webhook/#webhook-url)
that allows you to `POST` events to the source. Copy and store it. You will need
it for the next step.

The URL will have the following format:

```
https://<HOST>/api/webhook/<database>/<schema>/<src_name>
```

If you missed the notice, you can find the URLs for all webhook sources in the
[`mz_internal.mz_webhook_sources`](/sql/system-catalog/mz_internal/#mz_webhook_sources)
system table.

### Access and authentication

> **Warning:** Without a `CHECK` statement, **all requests will be accepted**. To prevent bad
> actors from injecting data into your source, it is **strongly encouraged** that
> you define a `CHECK` statement with your webhook sources.

The above webhook source uses [basic authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).
This enables a simple and rudimentary way to grant authorization to your webhook source.

## Step 4. Create a webhook destination in SnowcatCloud

To configure a Materialize webhook as a destination in SnowcatCloud, follow the
steps outlined below:

1.  **Select your SnowcatCloud pipe**

    Identify the pipeline you wish to add Materialize to as a destination.

1.  **Select Materialize as a destination**
    1. Navigate to the destinations section.
    1. Click **Configure** on the **Materialize** destination.

#### Connection settings

On the **Materialize Settings** page:

- **Webhook URL**: Define the endpoint where events will be dispatched by
    SnowcatCloud. Use the URL from **Step 3.**.

- **Secret**: Use the secret created in **Step 2.**.

- **Click Save & Test**: If the webhook is configured successfully, you will see
    a success message and the destination will start `PROVISIONING`; once it is
    `ACTIVE`, all your data will be streaming to Materialize's webhook.

## Step 5. Validate incoming data

With the source set up in Materialize and the webhook destination configured in
SnowcatCloud, you can now query the incoming data:

1. [In the Materialize console](/developer-tools/console/), navigate to
   the **SQL Shell**.

1. Use SQL queries to inspect and analyze the incoming data:

    ```mzsql
    SELECT * FROM segment_source LIMIT 10;
    ```

    Note that while the destination is `PROVISIONING`, you will only see the
    test event.

## Step 6. Transform incoming data

Webhook data is ingested as a JSON blob. We recommend creating a parsing view on
top of your webhook source that uses [`jsonb` operators](/sql/types/jsonb/#operators)
to map the individual fields to columns with the required data types.

To see what columns are available for your pipeline (enrichments), refer to
the [SnowcatCloud documentation](https://docs.snowcatcloud.com/).

```mzsql
CREATE VIEW events AS
SELECT
    body ->> 'app_id' AS app_id,
    body ->> 'platform' AS platform,
    try_parse_monotonic_iso8601_timestamp(body ->> 'etl_tstamp') AS etl_tstamp,
    try_parse_monotonic_iso8601_timestamp(body ->> 'collector_tstamp') AS collector_tstamp,
    try_parse_monotonic_iso8601_timestamp(body ->> 'dvce_created_tstamp') AS dvce_created_tstamp,
    body ->> 'event' AS event,
    body ->> 'event_id' AS event_id,
    body ->> 'txn_id' AS txn_id,
    body ->> 'name_tracker' AS name_tracker,
    body ->> 'v_tracker' AS v_tracker,
    body ->> 'v_collector' AS v_collector,
    body ->> 'v_etl' AS v_etl,
    body ->> 'user_id' AS user_id,
    body ->> 'user_ipaddress' AS user_ipaddress,
    body ->> 'user_fingerprint' AS user_fingerprint,
    body ->> 'domain_userid' AS domain_userid,
    body ->> 'domain_sessionidx' AS domain_sessionidx,
    body ->> 'network_userid' AS network_userid,
    (body -> 'contexts_com_dbip_location_1' -> 0 -> 'country' -> 'names' ->> 'en')::text AS geo_country,
    (body -> 'contexts_com_dbip_location_1' -> 0 -> 'subdivisions' -> 0 -> 'names' ->> 'en')::text AS geo_region,
    (body -> 'contexts_com_dbip_location_1' -> 0 -> 'city' -> 'names' ->> 'en')::text AS geo_city,
    (body -> 'contexts_com_dbip_location_1' -> 0 -> 'postal' ->> 'code')::text AS geo_zipcode,
    (body -> 'contexts_com_dbip_location_1' -> 0 -> 'location' ->> 'latitude')::numeric AS geo_latitude,
    (body -> 'contexts_com_dbip_location_1' -> 0 -> 'location' ->> 'longitude')::numeric AS geo_longitude,
    (body -> 'contexts_com_dbip_isp_1' -> 0 -> 'traits' ->> 'organization')::text AS ip_organization,
    (body -> 'contexts_com_dbip_isp_1' -> 0 -> 'traits' ->> 'isp')::text AS ip_isp,
    (body -> 'contexts_com_dbip_isp_1' -> 0 -> 'traits' ->> 'asn')::text AS ip_asn,
    (body -> 'contexts_com_dbip_isp_1' -> 0 -> 'traits' ->> 'connection_type')::text AS ip_connection_type,
    (body -> 'contexts_com_dbip_isp_1' -> 0 -> 'traits' ->> 'user_type')::text AS ip_user_type,
    body ->> 'page_url' AS page_url,
    body ->> 'page_title' AS page_title,
    body ->> 'page_referrer' AS page_referrer,
    body ->> 'page_urlscheme' AS page_urlscheme,
    body ->> 'page_urlhost' AS page_urlhost,
    body ->> 'page_urlport' AS page_urlport,
    body ->> 'page_urlpath' AS page_urlpath,
    body ->> 'page_urlquery' AS page_urlquery,
    body ->> 'page_urlfragment' AS page_urlfragment,
    body ->> 'refr_urlscheme' AS refr_urlscheme,
    body ->> 'refr_urlhost' AS refr_urlhost,
    body ->> 'refr_urlport' AS refr_urlport,
    body ->> 'refr_urlpath' AS refr_urlpath,
    body ->> 'refr_urlquery' AS refr_urlquery,
    body ->> 'refr_urlfragment' AS refr_urlfragment,
    body ->> 'refr_medium' AS refr_medium,
    body ->> 'refr_source' AS refr_source,
    body ->> 'refr_term' AS refr_term,
    body ->> 'mkt_medium' AS mkt_medium,
    body ->> 'mkt_source' AS mkt_source,
    body ->> 'mkt_term' AS mkt_term,
    body ->> 'mkt_content' AS mkt_content,
    body ->> 'mkt_campaign' AS mkt_campaign,
    body ->> 'se_category' AS se_category,
    body ->> 'se_action' AS se_action,
    body ->> 'se_label' AS se_label,
    body ->> 'se_property' AS se_property,
    (body ->> 'se_value')::numeric AS se_value,
    body ->> 'unstruct_event' AS unstruct_event,
    body ->> 'tr_orderid' AS tr_orderid,
    body ->> 'tr_affiliation' AS tr_affiliation,
    (body ->> 'tr_total')::numeric AS tr_total,
    (body ->> 'tr_tax')::numeric AS tr_tax,
    (body ->> 'tr_shipping')::numeric AS tr_shipping,
    body ->> 'tr_city' AS tr_city,
    body ->> 'tr_state' AS tr_state,
    body ->> 'tr_country' AS tr_country,
    body ->> 'ti_orderid' AS ti_orderid,
    body ->> 'ti_sku' AS ti_sku,
    body ->> 'ti_name' AS ti_name,
    body ->> 'ti_category' AS ti_category,
    (body ->> 'ti_price')::numeric AS ti_price,
    body ->> 'ti_quantity' AS ti_quantity,
    body ->> 'pp_xoffset_min' AS pp_xoffset_min,
    body ->> 'pp_xoffset_max' AS pp_xoffset_max,
    body ->> 'pp_yoffset_min' AS pp_yoffset_min,
    body ->> 'pp_yoffset_max' AS pp_yoffset_max,
    body ->> 'useragent' AS useragent,
    (body -> 'contexts_nl_basjes_yauaa_context_1' -> 0 ->> 'agentNameVersion')::text AS br_name,
    (body -> 'contexts_nl_basjes_yauaa_context_1' -> 0 ->> 'agentName')::text AS br_family,
    (body -> 'contexts_nl_basjes_yauaa_context_1' -> 0 ->> 'agentVersion')::text AS br_version,
    (body -> 'contexts_nl_basjes_yauaa_context_1' -> 0 ->> 'layoutEngineClass')::text AS br_type,
    body ->> 'br_lang' AS br_lang,
    body ->> 'br_features_pdf' AS br_features_pdf,
    body ->> 'br_features_flash' AS br_features_flash,
    body ->> 'br_features_java' AS br_features_java,
    body ->> 'br_features_director' AS br_features_director,
    body ->> 'br_features_quicktime' AS br_features_quicktime,
    body ->> 'br_features_realplayer' AS br_features_realplayer,
    body ->> 'br_features_windowsmedia' AS br_features_windowsmedia,
    body ->> 'br_features_gears' AS br_features_gears,
    body ->> 'br_features_silverlight' AS br_features_silverlight,
    body ->> 'br_cookies' AS br_cookies,
    body ->> 'br_colordepth' AS br_colordepth,
    body ->> 'br_viewwidth' AS br_viewwidth,
    body ->> 'br_viewheight' AS br_viewheight,
    (body -> 'contexts_nl_basjes_yauaa_context_1' -> 0 ->> 'operatingSystemName')::text AS os_name,
    (body -> 'contexts_nl_basjes_yauaa_context_1' -> 0 ->> 'operatingSystemClass')::text AS os_family,
    (body -> 'contexts_nl_basjes_yauaa_context_1' -> 0 ->> 'deviceBrand')::text AS os_manufacturer,
    body ->> 'os_timezone' AS os_timezone,
    (body -> 'contexts_nl_basjes_yauaa_context_1' -> 0 ->> 'deviceClass')::text AS dvce_type,
    (body ->> 'dvce_screenwidth')::numeric AS dvce_screenwidth,
    (body ->> 'dvce_screenheight')::numeric AS dvce_screenheight,
    body ->> 'doc_charset' AS doc_charset,
    (body ->> 'doc_width')::numeric AS doc_width,
    (body ->> 'doc_height')::numeric AS doc_height,
    body ->> 'tr_currency' AS tr_currency,
    (body ->> 'tr_total_base')::numeric AS tr_total_base,
    (body ->> 'tr_tax_base')::numeric AS tr_tax_base,
    (body ->> 'tr_shipping_base')::numeric AS tr_shipping_base,
    body ->> 'ti_currency' AS ti_currency,
    (body ->> 'ti_price_base')::numeric AS ti_price_base,
    body ->> 'base_currency' AS base_currency,
    body ->> 'geo_timezone' AS geo_timezone,
    body ->> 'mkt_clickid' AS mkt_clickid,
    body ->> 'mkt_network' AS mkt_network,
    body ->> 'etl_tags' AS etl_tags,
    try_parse_monotonic_iso8601_timestamp(body ->> 'dvce_sent_tstamp') AS dvce_sent_tstamp,
    body ->> 'refr_domain_userid' AS refr_domain_userid,
    try_parse_monotonic_iso8601_timestamp(body ->> 'refr_dvce_tstamp') AS refr_dvce_tstamp,
    body ->> 'domain_sessionid' AS domain_sessionid,
    try_parse_monotonic_iso8601_timestamp(body ->> 'derived_tstamp') AS derived_tstamp,
    body ->> 'event_vendor' AS event_vendor,
    body ->> 'event_name' AS event_name,
    body ->> 'event_format' AS event_format,
    body ->> 'event_version' AS event_version,
    body ->> 'event_fingerprint' AS event_fingerprint
FROM
    snowcat_source;
```

### Timestamp handling

We highly recommend using the [`try_parse_monotonic_iso8601_timestamp`](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown)
function when casting from `text` to `timestamp`, which enables [temporal filter
pushdown](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

### Deduplication

With the vast amount of data processed and potential network issues, it's not
uncommon to receive duplicate records. You can use the `DISTINCT ON` clause to
efficiently remove duplicates. For more details, refer to the webhook source
[reference documentation](/sql/create-source/webhook/#handling-duplicated-and-partial-events).

## Next steps

With Materialize ingesting your SnowcatCloud data, you can start exploring it,
computing real-time results that stay up-to-date as new data arrives, and
serving results efficiently. For more details, check out the
[SnowcatCloud documentation](https://docs.snowcatcloud.com/) and the
[webhook source reference documentation](/sql/create-source/webhook/).

<!-- mz-docs page: ingest-data/webhooks/stripe -->

# Stripe
How to stream data from Stripe to Materialize using webhooks
This guide walks through the steps to ingest data from [Stripe](https://stripe.com/)
into Materialize using the [Webhook source](/sql/create-source/webhook/).

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

### Before you begin

Ensure that you have a Stripe account.

## Step 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your webhook
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

To create a cluster in Materialize, use the [`CREATE CLUSTER` command](/sql/create-cluster):

```mzsql
CREATE CLUSTER webhooks_cluster (SIZE = '25cc');

SET CLUSTER = webhooks_cluster;
```

## Step 2. Create a secret

To validate requests between Stripe and Materialize, you must create a [secret](/sql/create-secret/):

```mzsql
CREATE SECRET stripe_webhook_secret AS '<secret_value>';
```

Change the `<secret_value>` to a unique value that only you know and store it in a secure location.

## Step 3. Set up a webhook source

Using the secret from the previous step, create a [webhook source](/sql/create-source/webhook/)
in Materialize to ingest data from Stripe. By default, the source will be
created in the active cluster; to use a different cluster, use the `IN
CLUSTER` clause.

```mzsql
CREATE SOURCE stripe_source IN CLUSTER webhooks_cluster
FROM WEBHOOK
    BODY FORMAT JSON;
    CHECK (
        WITH (BODY, HEADERS, SECRET stripe_webhook_secret AS validation_secret)
        (
            -- The constant_time_eq validation function **does not support** fully
            -- qualified secret names. We recommend always aliasing the secret name
            -- for ease of use.
            constant_time_eq(
                -- Sign the timestamp and body.
                encode(hmac(
                    (
                        -- Extract the `t` component from the `Stripe-Signature` header.
                        regexp_split_to_array(headers->'stripe-signature', ',|=')[
                            array_position(regexp_split_to_array(headers->'stripe-signature', ',|='), 't')
                            + 1
                        ]
                        || '.' ||
                        body
                    ),
                    validation_secret,
                    'sha256'
                ), 'hex'),
                -- Extract the `v1` component from the `Stripe-Signature` header.
                regexp_split_to_array(headers->'stripe-signature', ',|=')[
                    array_position(regexp_split_to_array(headers->'stripe-signature', ',|='), 'v1')
                    + 1
                ],
            )
        )
    );
```

After a successful run, the command returns a `NOTICE` message containing the
unique [webhook URL](/sql/create-source/webhook/#webhook-url)
that allows you to `POST` events to the source. Copy and store it. You will need
it for the next step.

The URL will have the following format:

```
https://<HOST>/api/webhook/<database>/<schema>/<src_name>
```

If you missed the notice, you can find the URLs for all webhook sources in the
[`mz_internal.mz_webhook_sources`](/sql/system-catalog/mz_internal/#mz_webhook_sources)
system table.

### Access and authentication

> **Warning:** Without a `CHECK` statement, **all requests will be accepted**. To prevent bad
> actors from injecting data into your source, it is **strongly encouraged** that
> you define a `CHECK` statement with your webhook sources.

The `CHECK` clause defines how to validate each request. For details on the
Stripe signing scheme, check out the [Stripe documentation](https://stripe.com/docs/webhooks#verify-manually).

## Step 4. Create a webhook endpoint in Stripe

1. In Stripe, go to **Developers > Webhooks**.

2. Click **Add endpoint**.

3. Enter the webhook URL from the previous step in the *Endpoint URL* field.

4. Configure the events you'd like to receive.

5. Create the endpoint.

6. Copy the signing secret and save it for the next step.

## Step 5. Validate incoming data

1. [In the Materialize console](/developer-tools/console/), navigate to
   the **SQL Shell**.

1. Use SQL queries to inspect and analyze the incoming data:

    ```mzsql
    SELECT * FROM stripe_source LIMIT 10;
    ```

    You may need to wait for webhook-generating events in Stripe to occur.

## Step 6. Transform incoming data

### JSON parsing

Webhook data is ingested as a JSON blob. We recommend creating a parsing view on
top of your webhook source that uses [`jsonb` operators](/sql/types/jsonb/#operators)
to map the individual fields to columns with the required data types.

```mzsql
CREATE VIEW parse_stripe AS SELECT
    body->>'api_version' AS api_version,
    to_timestamp((body->'created')::int) AS created,
    body->'data' AS data,
    body->'id' AS id,
    (body->'livemode')::boolean AS livemode,
    body->'object' AS object,
    body->>'pending_webhooks' AS pending_webhooks,
    body->'request'->'idempotency_key' AS idempotency_key,
    body->>'type' AS type
FROM stripe_source;
```

Manually parsing JSON-formatted data in SQL can be tedious. You can use the [interactive JSON parser widget](https://materialize.com/docs/sql/types/jsonb/#parsing) to automatically turn a sample JSON payload into a parsing view with the individual fields mapped to columns.

### Timestamp handling

We highly recommend using the [`try_parse_monotonic_iso8601_timestamp`](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown)
function when casting from `text` to `timestamp`, which enables [temporal filter
pushdown](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

### Deduplication

With the vast amount of data processed and potential network issues, it's not
uncommon to receive duplicate records. You can use the `DISTINCT ON` clause to
efficiently remove duplicates. For more details, refer to the webhook source
[reference documentation](/sql/create-source/webhook/#handling-duplicated-and-partial-events).

## Next steps

With Materialize ingesting your Stripe data, you can start exploring it,
computing real-time results that stay up-to-date as new data arrives, and
serving results efficiently. For more details, check out the
[Stripe documentation](https://stripe.com/docs/webhooks) and the
[webhook source reference documentation](/sql/create-source/webhook/).

<!-- mz-docs page: ingest-data/webhooks/webhook-quickstart -->

# Webhooks quickstart
Learn and prototype with the webhook source without external deoendencies
Webhook sources let your applications push webhook events into Materialize. This
quickstart uses an embedded **webhook event generator** that makes it easier for
you to learn and prototype with no external dependencies.

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

## Before you begin

All you need is a Materialize account. If you already have one —
great! If not, [sign up for a free trial account](https://materialize.com/register/?utm_campaign=General&utm_source=documentation) first.

When you're ready, head over to the [Materialize console](/developer-tools/console/),
and pop open the SQL Shell.

## Step 1. Create a secret

To validate requests between the webhook event generator and Materialize, you
need a [secret](/sql/create-secret/):

```mzsql
CREATE SECRET demo_webhook AS '<secret_value>';
```

Change the `<secret_value>` to a unique value that only you know and store it in
a secure location.

## Step 2. Set up a webhook source

Using the secret from the previous step, create a webhook source to ingest data
from the webhook event generator. By default, the source will be created in the
current cluster.

```mzsql
CREATE SOURCE webhook_demo FROM WEBHOOK
  BODY FORMAT JSON
  CHECK (
    WITH (
      HEADERS,
      BODY AS request_body,
      SECRET demo_webhook AS validation_secret
    )
    -- The constant_time_eq validation function **does not support** fully
    -- qualified secret names. We recommend always aliasing the secret name
    -- for ease of use.
    constant_time_eq(headers->'x-api-key', validation_secret)
  );
```

After a successful run, the command returns a `NOTICE` message containing the
unique [webhook URL](/sql/create-source/webhook/#webhook-url)
that allows you to `POST` events to the source. Copy and store it. You will need
it for the next step.

## Step 3. Generate webhook events

The webhook event generator uses [Faker.js](https://fakerjs.dev/) under the
covers, which means you can use any of the [supported modules](https://fakerjs.dev/api/)
to shape the events.

<div id="webhooks-datagen" class="json_widget">
  <div class="input_container">
    <div class="input_container-text">
      <input type="text" placeholder="Webhook URL" id="webhookURL" class="text-input" />
    </div>
  </div>
  <div class="input_container">
    <div class="input_container-text">
      <input type="password" placeholder="Secret (Step 1.)" id="authPassword" class="text-input" />
    </div>
  </div>
  <div class="input_container">
    <div class="input_container-text">
      <button id="startButton" class="btn">Generate webhook events!</button>
      <button id="stopButton" class="btn" style="display: none">Stop</button>
    </div>
  </div>
  <div class="input_container">
    <div class="input_container-text">
      <select id="useCaseSelect" class="text-input">
        <option value="">Select a Faker.js module</option>
        <option value="sensorData">Sensor data</option>
        <option value="userActivity">User activity</option>
        <option value="ecommerceTransaction">E-commerce transaction</option>
      </select>
    </div>
  </div>
  <div>
    <div class="json">
      <textarea placeholder="JSON schema" id="jsonSchema" rows="5" cols="30" class="json-textarea">
{
  "sensor_id": "faker.datatype.number({ max: 100, min: 1})",
  "timestamp": "faker.date.between('2020-01-01T00:00:00.000Z', '2030-01-01T00:00:00.000Z')",
  "location": {
      "latitude": "faker.datatype.number({ max: 90, min: -90})",
      "longitude": "faker.datatype.number({ max: 180, min: -180})"
  },
  "temperature": "faker.datatype.float({ min: 20, max: 95 })"
}
      </textarea>
      <div id="jsonError" class="error" style="display: none"></div>
    </div>
    <div class="log_output" id="logOutput" style="display: none"></div>
  </div>
</div>

<script type="module">
  import { faker } from 'https://esm.sh/@faker-js/faker@8.4.0';

  const webhookURLInput = document.getElementById("webhookURL");
  const authPasswordInput = document.getElementById("authPassword");
  const jsonSchemaTextarea = document.getElementById("jsonSchema");
  const startButton = document.getElementById("startButton");
  const stopButton = document.getElementById("stopButton");
  const jsonErrorDiv = document.getElementById("jsonError");
  const logOutputDiv = document.getElementById("logOutput");

  let logs = [];
  let isGenerating = false;
  let generationInterval;

  document.addEventListener("DOMContentLoaded", function () {
    formatJSON(); 
  });

  function validateJson(jsonString) {
    try {
      JSON.parse(jsonString);
      jsonErrorDiv.style.display = "none";
      return true;
    } catch (error) {
      jsonErrorDiv.style.display = "block";
      jsonErrorDiv.textContent = "Invalid JSON format";
      return false;
    }
  }

  function isFakerPathValid(path) {
    return path
      .split(".")
      .reduce((acc, curr) => (acc && acc[curr] ? acc[curr] : null), faker);
  }

  function generateDataAndSend() {
    const generatedData = JSON.parse(
      jsonSchemaTextarea.value.replace(/"faker\.(.+?)"/g, (_, match) => {
        try {
          const fakerValue = eval(`faker.${match}`);
          return JSON.stringify(fakerValue);
        } catch (error) {
          console.error("Error while generating faker data:", error);
          return '"Error"';
        }
      })
    );
    logs.unshift(`Sent: ${JSON.stringify(generatedData)}`); 
    logOutputDiv.innerHTML = logs
      .map((log, index) => `<p key="${index}">${log}</p>`)
      .join("");

    updateLogDisplay();

    console.log("URL:", webhookURLInput.value);
    console.log("Headers:", {
      "Content-Type": "application/json",
      "X-API-KEY": authPasswordInput.value,
    });
    console.log("Body:", JSON.stringify(generatedData));

    fetch(webhookURLInput.value, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": authPasswordInput.value,
      },
      body: JSON.stringify(generatedData),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response;
      })
      .then((data) => {

      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
        logs.unshift(`Error: ${error.message}`); 
        logOutputDiv.innerHTML = logs
          .map((log, index) => `<p key="${index}">${log}</p>`)
          .join("");

        updateLogDisplay();
      });
  }

  function startGeneration() {
    if (!webhookURLInput.value || !authPasswordInput.value) {
      alert("Webhook URL and Auth Password cannot be empty!");
      return;
    }
    if (validateJson(jsonSchemaTextarea.value)) {
      isGenerating = true;
      generationInterval = setInterval(generateDataAndSend, 1000);
      startButton.style.display = "none";
      stopButton.style.display = "inline-block";
    }
  }

  function stopGeneration() {
    isGenerating = false;
    clearInterval(generationInterval);
    startButton.style.display = "inline-block";
    stopButton.style.display = "none";
    generationInterval = null;
  }

  function updateLogDisplay() {
    logOutputDiv.style.display = logs.length > 0 ? "block" : "none";
  }

  startButton.addEventListener("click", startGeneration);
  stopButton.addEventListener("click", stopGeneration);
  updateLogDisplay();

  jsonSchemaTextarea.addEventListener("blur", formatJSON);

  function formatJSON() {
    const jsonString = jsonSchemaTextarea.value.trim();
    try {
      const formattedJSON = JSON.stringify(JSON.parse(jsonString), null, 2);
      jsonSchemaTextarea.value = formattedJSON;
    } catch (error) {

      console.error("Error while formatting JSON:", error);
    }
  }

  document.getElementById('useCaseSelect').addEventListener('change', function() {
    const selectedUseCase = this.value;
    const schema = schemas[selectedUseCase];
    if (schema) {
      jsonSchemaTextarea.value = schema;
      formatJSON(); 
    }
  });

  const schemas = {
    sensorData: `{
      "sensor_id": "faker.datatype.number({ max: 100, min: 1})",
      "timestamp": "faker.date.between('2020-01-01T00:00:00.000Z', '2030-01-01T00:00:00.000Z')",
      "location": {
          "latitude": "faker.datatype.number({ max: 90, min: -90})",
          "longitude": "faker.datatype.number({ max: 180, min: -180})"
      },
      "temperature": "faker.datatype.float({ min: 20, max: 95 })"
    }`,
    userActivity: `{
      "user_id": "faker.datatype.uuid()",
      "event": "faker.helpers.arrayElement(['page_view', 'click', 'scroll', 'navigation'])",
      "timestamp": "faker.date.recent()",
      "page": {
        "url": "faker.internet.url()",
        "title": "faker.lorem.words()"
      },
      "interaction": {
        "element": "faker.lorem.word()",
        "time_spent": "faker.datatype.number({ min: 1, max: 120 })"
      }
    }`,
    ecommerceTransaction: `{
      "user_id": "faker.datatype.uuid()",
      "event": "faker.helpers.arrayElement(['add_to_cart', 'remove_from_cart', 'purchase', 'view_product'])",
      "timestamp": "faker.date.recent()",
      "product": {
        "id": "faker.datatype.uuid()",
        "name": "faker.commerce.productName()",
        "category": "faker.commerce.department()",
        "price": "faker.commerce.price()"
      }
    }`
  };
</script>

In the SQL Shell, validate that the source is ingesting data:

```mzsql
SELECT jsonb_pretty(body) AS body FROM webhook_demo LIMIT 1;
```

As an example, if you use the `Sensor data` module of the webhook event
generator, the data will look like:
```json
{
  "location": {
    "latitude": 6,
    "longitude": 0
  },
  "sensor_id": 48,
  "temperature": 89.38,
  "timestamp": "2029-10-07T10:44:13.456Z"
}
```

## Step 4. Parse JSON

Manually parsing JSON-formatted data in SQL can be tedious. You can use the [interactive JSON parser widget](https://materialize.com/docs/sql/types/jsonb/#parsing) to automatically turn a sample JSON payload into a parsing view with the individual fields mapped to columns.

Webhook data is ingested as a JSON blob. We recommend creating a parsing view on
top of your webhook source that uses [jsonb operators](/sql/types/jsonb/#operators)
to map the individual fields to columns with the required data types. Using the
previous example:

```mzsql
CREATE VIEW webhook_demo_parsed AS SELECT
    (body->'location'->>'latitude')::numeric AS location_latitude,
    (body->'location'->>'longitude')::numeric AS location_longitude,
    (body->>'sensor_id')::numeric AS sensor_id,
    (body->>'temperature')::numeric AS temperature,
    try_parse_monotonic_iso8601_timestamp(body->>'timestamp') AS timestamp
FROM webhook_demo;
```

## Step 5. Subscribe to see the output

To see results change over time, let’s [`SUBSCRIBE`](/sql/subscribe/) to the
`webhook_demo_parsed ` view:

```mzsql
SUBSCRIBE(SELECT * FROM webhook_demo_parsed) WITH (SNAPSHOT = FALSE);
```

You'll see results change as new webhook events are ingested. When you’re done,
cancel out of the `SUBSCRIBE` using **Stop streaming**.

## Step 6. Clean up

Once you’re done exploring the generated webhook data, remember to clean up your
environment:

```mzsql
DROP SOURCE webhook_demo CASCADE;

DROP SECRET demo_webhook;
```

## Next steps

To get started with your own data, check out the [reference documentation](/sql/create-source/webhook/)
for the webhook source.

