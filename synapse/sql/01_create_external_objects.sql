CREATE MASTER KEY ENCRYPTION BY PASSWORD = '<replace-with-secure-password>';
GO

CREATE DATABASE SCOPED CREDENTIAL adls_managed_identity
WITH IDENTITY = 'Managed Identity';
GO

CREATE EXTERNAL DATA SOURCE curated_adls
WITH (
    LOCATION = 'abfss://curated@<storage-account>.dfs.core.windows.net',
    CREDENTIAL = adls_managed_identity
);
GO

CREATE EXTERNAL FILE FORMAT parquet_format
WITH (
    FORMAT_TYPE = PARQUET
);
GO

CREATE SCHEMA reporting;
GO

CREATE EXTERNAL TABLE reporting.customer_360_external (
    customer_id VARCHAR(100),
    customer_name VARCHAR(500),
    lifetime_revenue BIGINT,
    ticket_count INT,
    last_ticket_at DATETIME2
)
WITH (
    LOCATION = '/customer_360/',
    DATA_SOURCE = curated_adls,
    FILE_FORMAT = parquet_format
);
GO
