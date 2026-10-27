"""Utility functions for currency formatting, logging, and data helpers."""

def format_inr(amount: float) -> str:
    """
    Format a numeric amount according to Indian numbering system (Lakhs and Crores).
    Example: 1234567 -> ₹12,34,567
    """
    s = f"{int(round(amount))}"
    if len(s) <= 3:
        return f"₹{s}"
    last_three = s[-3:]
    remaining = s[:-3]
    chunks = []
    while len(remaining) > 2:
        chunks.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        chunks.insert(0, remaining)
    chunks.append(last_three)
    return "₹" + ",".join(chunks)
