# Operations Runbook

## Daily Checks

- Confirm ADF pipeline success rate is above 99%.
- Review failed activity details and retry transient API failures.
- Check schema drift alerts for new or removed fields.
- Validate Synapse reporting views refresh successfully.
- Confirm Power BI dataset refresh latency is within SLA.

## Failure Playbook

1. Identify failed source and activity in ADF monitor.
2. Check API status page and HTTP response code.
3. Inspect raw landing folder for partial files.
4. Review schema validation output.
5. Move invalid payloads to quarantine.
6. Restart the pipeline from the failed activity after remediation.

## SLA Targets

- Hourly sources available in Power BI within 30 minutes.
- Daily sources available by 07:00 local business time.
- Pipeline failure rate below 1%.
