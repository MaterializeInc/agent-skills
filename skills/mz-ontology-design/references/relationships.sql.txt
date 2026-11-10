-- Generic shape for the public relationship registry. Replace these sample
-- edges with the ontology's complete set of direct reference edges.
create materialized view core.public.relationships
in cluster ontology_compute as
select
    relationship_name,
    table_name,
    columns,
    referenced_table,
    referenced_columns,
    cardinality,
    optionality,
    description
from (
    values
        (
            'orders_customer',
            'orders',
            jsonb_build_array('customer_id'),
            'customers',
            jsonb_build_array('customer_id'),
            'many_to_one',
            'required',
            'The customer that placed the order.'
        ),
        (
            'order_items_order',
            'order_items',
            jsonb_build_array('store_id', 'order_id'),
            'orders',
            jsonb_build_array('store_id', 'order_id'),
            'many_to_one',
            'required',
            'The order containing the line item.'
        ),
        (
            'order_items_product',
            'order_items',
            jsonb_build_array('product_id'),
            'products',
            jsonb_build_array('product_id'),
            'many_to_one',
            'required',
            'The product represented by the line item.'
        ),
        (
            'employees_manager',
            'employees',
            jsonb_build_array('manager_id'),
            'employees',
            jsonb_build_array('employee_id'),
            'many_to_one',
            'optional',
            'The employee''s current manager, when assigned.'
        )
) as relationships (
    relationship_name,
    table_name,
    columns,
    referenced_table,
    referenced_columns,
    cardinality,
    optionality,
    description
);

comment on materialized view core.public.relationships is
    'The complete registry of direct reference edges between public semantic objects. Relationship objects represent attributed, historical, heuristic, and many-to-many associations; this registry records their direct references to participating objects.';
comment on column core.public.relationships.relationship_name is
    'Unique semantic name for the directed reference edge.';
comment on column core.public.relationships.table_name is
    'Public object containing the referencing columns.';
comment on column core.public.relationships.columns is
    'Referencing columns as a JSON array, positionally matched to referenced_columns.';
comment on column core.public.relationships.referenced_table is
    'Public object identified by the reference.';
comment on column core.public.relationships.referenced_columns is
    'Unique-key columns in the referenced object, positionally matched to columns.';
comment on column core.public.relationships.cardinality is
    'Cardinality from the referencing side: many_to_one or one_to_one.';
comment on column core.public.relationships.optionality is
    'Required when every row carries a complete reference; optional when all referencing columns may be null.';
comment on column core.public.relationships.description is
    'Consumer-facing meaning of the reference and any condition under which it applies.';
