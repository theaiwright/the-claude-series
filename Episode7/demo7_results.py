"""
Episode 7 Demo - Part 2: RESULTS AND ERRORS

This demo runs offline. It needs no API key and no internet access.

Part A shows why a tool should return only the fields Claude needs.
Part B shows why an error message should say what to try next.

Setup:
  python3 demo7_results.py
"""

import json

# Stands in for a database row. The internal fields should never reach Claude.
ORDERS = {
    "A1001": {
        "order_id": "A1001",
        "status": "shipped",
        "carrier": "BlueDart",
        "eta": "2026-10-22",
        "customer_email": "customer42@example.com",
        "payment_token": "tok_9f3a7c2e81b4",
        "warehouse_code": "WH-07-B",
        "internal_notes": "Packed by night shift. Label reprinted once.",
        "audit_log": [f"event {n}: scan at dock {n % 9}" for n in range(1, 41)],
    }
}


def lookup_order_bloated(order_id: str) -> str:
    """Returns the whole database row."""
    return json.dumps(ORDERS[order_id])


def lookup_order_concise(order_id: str) -> str:
    """Returns only the fields a support agent needs to answer the customer."""
    order = ORDERS[order_id]
    return json.dumps({
        "order_id": order["order_id"],
        "status": order["status"],
        "carrier": order["carrier"],
        "eta": order["eta"],
    })


def tool_error_vague(order_id: str) -> dict:
    return {"type": "tool_result", "tool_use_id": "toolu_demo", "is_error": True,
            "content": "Error 500"}


def tool_error_instructive(order_id: str) -> dict:
    return {"type": "tool_result", "tool_use_id": "toolu_demo", "is_error": True,
            "content": (f"Order {order_id} was not found. Check the order id and try again. "
                        "Order ids look like A1001. If the id is correct, tell the customer "
                        "the order cannot be found right now.")}


print("PART A: WHAT CLAUDE RECEIVES")
print("=" * 60)
bloated = lookup_order_bloated("A1001")
concise = lookup_order_concise("A1001")
print(f"Bloated result: {len(bloated)} characters")
print(f"Concise result: {len(concise)} characters")
print("\nConcise result, exactly as Claude receives it:")
print(concise)
print("\nFields in the bloated result that Claude does not need:")
extra = sorted(set(json.loads(bloated)) - set(json.loads(concise)))
print(", ".join(extra))

print("\n\nPART B: WHAT CLAUDE RECEIVES WHEN A TOOL FAILS")
print("=" * 60)
print("Vague error:")
print(json.dumps(tool_error_vague("A9999"), indent=2))
print("\nInstructive error:")
print(json.dumps(tool_error_instructive("A9999"), indent=2))
