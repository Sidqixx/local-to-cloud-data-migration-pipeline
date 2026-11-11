CREATE EXTERNAL TABLE IF NOT EXISTS olist_db.customers (
    customer_id STRING,
    customer_unique_id STRING,
    customer_zip_code_prefix BIGINT,
    customer_city STRING,
    customer_state STRING
)
STORED AS PARQUET
LOCATION 's3://BUCKET_NAME/processed/customers/';

CREATE EXTERNAL TABLE IF NOT EXISTS olist_db.orders (
    order_id STRING,
    customer_id STRING,
    order_status STRING,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
)
STORED AS PARQUET
LOCATION 's3://BUCKET_NAME/processed/orders/';

CREATE EXTERNAL TABLE IF NOT EXISTS olist_db.order_items (
    order_id STRING,
    order_item_id BIGINT,
    product_id STRING,
    seller_id STRING,
    shipping_limit_date TIMESTAMP,
    price DECIMAL(12,2),
    freight_value DECIMAL(12,2)
)
STORED AS PARQUET
LOCATION 's3://BUCKET_NAME/processed/order_items/';