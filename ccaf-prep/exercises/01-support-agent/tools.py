"""
Exercise 1 — backend "MCP" tools for the customer-support agent.

These are plain Python functions standing in for MCP tools. In a real MCP server
(see ../../claude-with-anthropic-api/cli_project/mcp_server.py) each would be an
@mcp.tool(); the *concepts* the exam tests are identical:

  - D2.1  Tool descriptions are the PRIMARY tool-selection mechanism. Flip
          GOOD_DESCRIPTIONS=False to feel misrouting between the two similar tools
          (get_customer vs lookup_order) — that is sample Q2.
  - D2.2  Structured error responses: every failure returns errorCategory
          (transient | validation | business | permission), isRetryable, and a
          human-readable description — NOT a generic "operation failed".
  - D5.2  Multiple customer matches -> ask for more identifiers, never guess.
"""

# ---- toggle: flip to False to study the D2.1 / Q2 anti-pattern (vague descriptions)
GOOD_DESCRIPTIONS = True

# ---- fake backend ---------------------------------------------------------------
_CUSTOMERS = [
    {"id": "C001", "name": "John Smith", "email": "john.s@mail.com", "tier": "gold"},
    {"id": "C002", "name": "John Smith", "email": "jsmith@work.com", "tier": "silver"},
    {"id": "C003", "name": "Maria Garcia", "email": "maria@mail.com", "tier": "gold"},
]
_ORDERS = {
    "12345": {"order_id": "12345", "customer_id": "C003", "total": 240.00, "status": "delivered"},
    "67890": {"order_id": "67890", "customer_id": "C001", "total": 900.00, "status": "delivered"},
}


def _err(category, retryable, description):
    """D2.2 — the structured error shape the agent can actually reason about."""
    return {"isError": True, "errorCategory": category, "isRetryable": retryable,
            "description": description}


def get_customer(name=None, customer_id=None, email=None):
    # Teaching simplification: this is a LOOK-UP that the exercise treats as "verification".
    # Real systems verify identity via an authenticated session, not a self-asserted name/ID
    # typed in chat. We collapse the two so the D1.4 verify-before-refund gate is demonstrable.
    if customer_id:
        hit = next((c for c in _CUSTOMERS if c["id"] == customer_id), None)
        return hit or _err("validation", False, f"No customer with id {customer_id}.")
    if email:
        hit = next((c for c in _CUSTOMERS if c["email"] == email), None)
        return hit or _err("validation", False, f"No customer with email {email}.")
    if name:
        hits = [c for c in _CUSTOMERS if c["name"].lower() == name.lower()]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            # D5.2 — multiple matches: ask for more identifiers, do NOT pick one.
            return _err("validation", False,
                        f"{len(hits)} customers named '{name}'. Ask the customer for an "
                        f"email or customer ID to disambiguate.")
        return _err("validation", False, f"No customer named '{name}'.")
    return _err("validation", False, "Provide customer_id, email, or name.")


def lookup_order(order_id=None):
    if not order_id:
        return _err("validation", False, "order_id is required.")
    order = _ORDERS.get(str(order_id))
    return order or _err("validation", False, f"No order {order_id}.")


def process_refund(order_id=None, amount=None, verified_customer_id=None):
    # NOTE: the >$500 and "must be verified" rules are ALSO enforced in agent.py's gate
    # (D1.4/D1.5). Business logic here is the backstop; the gate is the deterministic one.
    order = _ORDERS.get(str(order_id))
    if not order:
        return _err("validation", False, f"No order {order_id}.")
    if amount and amount > order["total"]:
        return _err("business", False,
                    f"Refund {amount} exceeds order total {order['total']}.")
    return {"isError": False, "refund_id": f"R-{order_id}", "amount": amount,
            "status": "refunded"}


def escalate_to_human(reason=None, summary=None):
    # D1.4 — structured handoff: the human has NO access to the transcript.
    return {"isError": False, "ticket": "H-7781", "reason": reason,
            "handoff_summary": summary, "status": "escalated"}


DISPATCH = {"get_customer": get_customer, "lookup_order": lookup_order,
            "process_refund": process_refund, "escalate_to_human": escalate_to_human}


def tool_schemas():
    """D2.1 — descriptions decide tool selection. The two 'lookup' tools are
    deliberately similar; only the descriptions disambiguate them."""
    if GOOD_DESCRIPTIONS:
        get_desc = ("Retrieve a CUSTOMER account record (identity, tier, contact). Use FIRST "
                    "to verify who you are talking to. Accepts customer_id, email, or name. "
                    "Use this for 'who is this account / verify me', NOT for order details.")
        order_desc = ("Retrieve a single ORDER record (items, total, status) by its order_id "
                      "(e.g. '12345'). Use when the user references an order/purchase. Does NOT "
                      "identify or verify the customer — call get_customer for that.")
    else:
        # anti-pattern: minimal descriptions -> the model confuses the two (sample Q2)
        get_desc = "Retrieves customer information."
        order_desc = "Retrieves order details."
    return [
        {"name": "get_customer", "description": get_desc, "input_schema": {
            "type": "object", "properties": {
                "name": {"type": "string"}, "customer_id": {"type": "string"},
                "email": {"type": "string"}}}},
        {"name": "lookup_order", "description": order_desc, "input_schema": {
            "type": "object", "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"]}},
        {"name": "process_refund", "description":
            "Issue a refund for an order. Requires order_id and amount.", "input_schema": {
            "type": "object", "properties": {
                "order_id": {"type": "string"}, "amount": {"type": "number"}},
            "required": ["order_id", "amount"]}},
        {"name": "escalate_to_human", "description":
            "Hand the case to a human agent. Provide reason and a full handoff summary "
            "(customer id, issue, root cause, recommended action) — the human cannot see "
            "this conversation.", "input_schema": {
            "type": "object", "properties": {
                "reason": {"type": "string"}, "summary": {"type": "string"}},
            "required": ["reason", "summary"]}},
    ]
