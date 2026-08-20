# Power BI Dashboard

Connect Power BI Desktop to Synapse SQL and import these reporting views:

- `reporting.vw_customer_health`
- `reporting.vw_executive_kpis`

## Suggested Pages

- Executive Overview
- Customer Health
- Revenue Performance
- Support SLA Trends
- Data Pipeline Operations

## Visual Layout

| Page | Visuals |
| --- | --- |
| Executive Overview | KPI cards, revenue trend, customer health distribution |
| Customer Health | Customer table, churn-risk segmentation, support-ticket drillthrough |
| Revenue Performance | Revenue by product, region, and customer segment |
| Support SLA Trends | SLA breach trend, ticket aging, high-risk customer list |
| Data Pipeline Operations | Pipeline success rate, latency, retries, quarantined records |

## Core Measures

```DAX
Total Revenue = SUM('Customer Health'[lifetime_revenue])

Active Customers = DISTINCTCOUNT('Customer Health'[customer_id])

Average Tickets = AVERAGE('Customer Health'[ticket_count])

High Risk Customers =
CALCULATE(
    DISTINCTCOUNT('Customer Health'[customer_id]),
    'Customer Health'[health_status] = "High Risk"
)

Pipeline Success Rate =
DIVIDE(
    SUM('Pipeline Metrics'[total_runs]) - SUM('Pipeline Metrics'[failed_runs]),
    SUM('Pipeline Metrics'[total_runs])
)
```
