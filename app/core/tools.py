from langchain.tools import tool

# --- BILLING DEPARTMENT TOOL ---
@tool
def process_refund(transaction_id: str) -> str:
    """Processes a refund for a given transaction ID."""
    print(f"\n[TOOL CALLED] Processing refund for TXN: {transaction_id}")
    return f"Refund of ₹1500 successful for {transaction_id}."

# --- TECH DEPARTMENT TOOL ---
@tool
def troubleshoot_login(error_code: str) -> str:
    """Provides troubleshooting steps for app login errors."""
    print(f"\n[TOOL CALLED] Fixing Tech Error: {error_code}")
    return "Cleared cache and fixed the server sync issue."

# Hum in lists ko aage workers ke LLMs ke sath bind karenge
billing_tools = [process_refund]
tech_tools = [troubleshoot_login]