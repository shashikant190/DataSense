import re

AGG_MAP = {
    "total": "SUM",
    "sum": "SUM",
    "number of": "COUNT",
    "count": "COUNT",
    "average": "AVG",
    "avg": "AVG",
    "mean": "AVG",
}

TIME_PATTERNS = {
    r"last\s+(\d+)\s+days": lambda n: f"NOW() - INTERVAL '{n} days'",
    r"last\s+(\d+)\s+weeks": lambda n: f"NOW() - INTERVAL '{int(n)*7} days'",
    r"yesterday": lambda _: "NOW() - INTERVAL '1 day'"
}


def parse_query(text: str, schema: dict):
    text_low = (text or "").lower()

    # detect entity by exact match or synonyms in schema
    target_entity = None
    for e, meta in (schema.get("entities") or {}).items():
        # check direct name
        if e.lower() in text_low:
            target_entity = e
            break
        # synonyms list support
        synonyms = meta.get("synonyms", [])
        for s in synonyms:
            if s.lower() in text_low:
                target_entity = e
                break
        if target_entity:
            break

    # detect aggregation and field if possible
    agg = None
    for key, val in AGG_MAP.items():
        if key in text_low:
            agg = val
            break

    # simple heuristic: if "orders" and "amount" words present, treat "amount" as numeric field
    field = None
    if "amount" in text_low:
        field = "orders.amount"
    elif target_entity:
        # try to pick first numeric-seeming field from schema if agg != COUNT
        if agg and agg != "COUNT":
            fields = schema["entities"].get(target_entity, {}).get("fields", [])
            # choose a likely numeric field
            for f in fields:
                if any(substr in f.lower() for substr in ["amount", "price", "total", "value", "cost"]):
                    field = f"{target_entity}.{f}"
                    break

    # time filters
    filter_sql = ""
    for pattern, func in TIME_PATTERNS.items():
        m = re.search(pattern, text_low)
        if m:
            arg = m.group(1) if m.groups() else ""
            filter_sql = f"created_at >= {func(arg)}"
            break

    return {
        "entity": target_entity,
        "agg": agg,
        "field": field,
        "filter": filter_sql,
    }
