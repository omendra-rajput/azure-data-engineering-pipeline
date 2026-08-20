CREATE OR ALTER VIEW reporting.vw_customer_health AS
SELECT
    customer_id,
    customer_name,
    lifetime_revenue,
    ticket_count,
    last_ticket_at,
    CASE
        WHEN ticket_count >= 10 THEN 'High Risk'
        WHEN ticket_count >= 5 THEN 'Watch'
        ELSE 'Healthy'
    END AS health_status
FROM reporting.customer_360_external;
GO

CREATE OR ALTER VIEW reporting.vw_executive_kpis AS
SELECT
    COUNT(DISTINCT customer_id) AS active_customers,
    SUM(COALESCE(lifetime_revenue, 0)) AS total_revenue,
    AVG(CAST(COALESCE(ticket_count, 0) AS FLOAT)) AS avg_support_tickets
FROM reporting.customer_360_external;
GO
