class InvalidQueryError(Exception):
    pass

def build_sql(parsed):
    table = parsed.get("entity")
    agg = parsed.get("agg")
    filt = parsed.get("filter", "")

    if not table:
        raise InvalidQueryError("No target entity (table) identified.")

    # If aggregator and no field specified, try to map to a known metric in parsed
    if agg:
        # for MVP, assume agg(*) is ok for count, but sum/avg ideally need a numeric field
        if agg.upper() == "COUNT":
            select = "COUNT(*) AS value"
        else:
            # try to use parsed["field"] if present, else fallback to "*"
            field = parsed.get("field")
            if not field:
                # safer error than broken SQL
                raise InvalidQueryError(f"Aggregation {agg} requires a numeric field; none detected.")
            select = f"{agg}({field}) AS value"
    else:
        select = "*"

    # Basic SQL assembly; use simple safety limits
    sql = f"SELECT {select} FROM {table}"
    if filt:
        sql += f" WHERE {filt}"
    sql += " LIMIT 100"
    return sql
