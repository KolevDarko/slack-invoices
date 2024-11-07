import json
import random
import requests
import datetime
import os

base_url = "https://api.request.finance"
headers = {"Authorization": os.environ["REQ_API_KEY"]}


def format_invoice_items(raw_items):
    """
    [
            {
                "currency": "USD",
                "name": "Television",
                "quantity": 1,
                "tax": {"type": "fixed", "amount": "0"},
                "unitPrice": "9999",
            }
        ],
    """
    response = []
    for item in raw_items:
        real_name = item.get("item") or item.get("name") or item.get("description")
        response.append(
            {
                "currency": "USD",
                "name": real_name,
                "quantity": item["quantity"],
                "unitPrice": item["price"] * 100,
                "tax": {"type": "fixed", "amount": "0"},
            }
        )
    return response


def format_date(some_date):
    isoformat = some_date.isoformat()
    just_date = isoformat.split(".")[0]
    return f"{just_date}.000Z"


def create_invoice(invoice_data_str):
    invoice_data = json.loads(invoice_data_str)
    if "invoice_schema" in invoice_data:
        invoice_data = invoice_data["invoice_schema"]

    random_num = random.randint(2000, 9000000)
    now = datetime.datetime.utcnow()
    due_date = now + datetime.timedelta(days=31)
    body = {
        "creationDate": format_date(now),
        "invoiceItems": format_invoice_items(invoice_data["items"]),
        "invoiceNumber": f"A{random_num}",
        "buyerInfo": {
            "email": invoice_data.get("recipient_email")
            or invoice_data.get("email")
            or invoice_data.get("recipient"),
        },
        "paymentTerms": {"dueDate": format_date(due_date)},
        "paymentAddress": "0x4886E85E192cdBC81d42D89256a81dAb990CDD74",
        "paymentCurrency": "USDC-matic",
    }
    response = requests.post(f"{base_url}/invoices", json=body, headers=headers)
    print(">>>> Invoice response")
    print(response.json())
    return response.json()["id"]


def request_from_invoice(invoice_id):
    return requests.post(f"{base_url}/invoices/{invoice_id}", headers=headers)


if __name__ == "__main__":
    response = create_invoice()
    print(response.json())
