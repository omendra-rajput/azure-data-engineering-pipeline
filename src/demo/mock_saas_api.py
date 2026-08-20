from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


DATASETS: dict[str, list[dict[str, object]]] = {
    "/salesforce/accounts": [
        {"Id": "CUST-1001", "Name": "Northwind Analytics", "Region": "North America", "LastModifiedDate": "2026-08-20T08:10:00Z"},
        {"Id": "CUST-1002", "Name": "Contoso Retail", "Region": "Europe", "LastModifiedDate": "2026-08-20T08:30:00Z"},
        {"Id": "CUST-1003", "Name": "Fabrikam Cloud", "Region": "Asia Pacific", "LastModifiedDate": "2026-08-20T09:05:00Z"},
        {"Id": "CUST-1004", "Name": "Adventure Works", "Region": "North America", "LastModifiedDate": "2026-08-20T09:25:00Z"},
        {"Id": "CUST-1005", "Name": "Blue Yonder Labs", "Region": "India", "LastModifiedDate": "2026-08-20T09:45:00Z"}
    ],
    "/hubspot/contacts": [
        {"id": "CON-1", "customer_id": "CUST-1001", "email": "ops@northwind.example", "properties": {"role": "Operations"}, "updatedAt": "2026-08-20T08:20:00Z"},
        {"id": "CON-2", "customer_id": "CUST-1002", "email": "revops@contoso.example", "properties": {"role": "Revenue"}, "updatedAt": "2026-08-20T08:40:00Z"},
        {"id": "CON-3", "customer_id": "CUST-1003", "email": "success@fabrikam.example", "properties": {"role": "Success"}, "updatedAt": "2026-08-20T09:10:00Z"}
    ],
    "/stripe/charges": [
        {"id": "ch_001", "customer_id": "CUST-1001", "amount": 245000, "currency": "usd", "created": 1787204100},
        {"id": "ch_002", "customer_id": "CUST-1002", "amount": 87000, "currency": "usd", "created": 1787205100},
        {"id": "ch_003", "customer_id": "CUST-1003", "amount": 310000, "currency": "usd", "created": 1787206100},
        {"id": "ch_004", "customer_id": "CUST-1004", "amount": 142000, "currency": "usd", "created": 1787207100},
        {"id": "ch_005", "customer_id": "CUST-1005", "amount": 99000, "currency": "usd", "created": 1787208100}
    ],
    "/zendesk/tickets": [
        {"id": 7001, "customer_id": "CUST-1001", "subject": "API question", "status": "solved", "priority": "low", "updated_at": "2026-08-20T07:10:00Z"},
        {"id": 7002, "customer_id": "CUST-1002", "subject": "Billing mismatch", "status": "open", "priority": "high", "updated_at": "2026-08-20T08:30:00Z"},
        {"id": 7003, "customer_id": "CUST-1003", "subject": "SLA breach", "status": "open", "priority": "urgent", "updated_at": "2026-08-20T09:05:00Z"},
        {"id": 7004, "customer_id": "CUST-1003", "subject": "Slow dashboard", "status": "pending", "priority": "high", "updated_at": "2026-08-20T09:20:00Z"},
        {"id": 7005, "customer_id": "CUST-1005", "subject": "Export failure", "status": "open", "priority": "normal", "updated_at": "2026-08-20T09:40:00Z"},
        {"id": 7006, "customer_id": "CUST-1002", "status": "open", "priority": "normal", "updated_at": "2026-08-20T09:55:00Z"}
    ],
    "/jira/issues": [
        {"id": "10001", "key": "DATA-101", "customer_id": "CUST-1003", "status": "In Progress", "updated": "2026-08-20T10:00:00Z"},
        {"id": "10002", "key": "DATA-102", "customer_id": "CUST-1002", "status": "Done", "updated": "2026-08-20T10:10:00Z"}
    ],
    "/shopify/orders": [
        {"id": 9001, "customer_id": "CUST-1004", "total_price": "4200.00", "updated_at": "2026-08-20T06:45:00Z"},
        {"id": 9002, "customer_id": "CUST-1005", "total_price": "7800.00", "updated_at": "2026-08-20T07:15:00Z"}
    ],
    "/netsuite/invoices": [
        {"internalId": "INV-2201", "customer_id": "CUST-1001", "amountDue": 0, "lastModifiedDate": "2026-08-20T05:00:00Z"},
        {"internalId": "INV-2202", "customer_id": "CUST-1003", "amountDue": 12500, "lastModifiedDate": "2026-08-20T05:30:00Z"}
    ],
    "/google-analytics/events": [
        {"eventId": "EVT-1", "customer_id": "CUST-1001", "eventName": "dashboard_view", "eventDate": "2026-08-20T03:00:00Z"},
        {"eventId": "EVT-2", "customer_id": "CUST-1002", "eventName": "export_csv", "eventDate": "2026-08-20T03:15:00Z"},
        {"eventId": "EVT-3", "customer_id": "CUST-1003", "eventName": "failed_login", "eventDate": "2026-08-20T03:30:00Z"}
    ]
}


class MockSaaSHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self.respond({"status": "ok", "sources": len(DATASETS)})
            return

        if parsed.path not in DATASETS:
            self.respond({"error": "unknown endpoint", "path": parsed.path}, status=404)
            return

        params = parse_qs(parsed.query)
        page = int(params.get("page", ["1"])[0])
        page_size = int(params.get("page_size", ["2"])[0])
        records = DATASETS[parsed.path]
        start = (page - 1) * page_size
        end = start + page_size
        next_url = None
        if end < len(records):
            next_url = f"{parsed.path}?page={page + 1}&page_size={page_size}"

        self.respond(
            {
                "data": records[start:end],
                "page": page,
                "page_size": page_size,
                "total": len(records),
                "next": next_url
            }
        )

    def log_message(self, format: str, *args: object) -> None:
        return

    def respond(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), MockSaaSHandler)
    print(f"Mock SaaS API server running at http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
