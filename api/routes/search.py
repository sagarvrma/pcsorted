from fastapi import APIRouter, Query
from typing import Optional
import api.db as db

router = APIRouter()

@router.get("/search")
def search(
    q: Optional[str] = None,
    gpu: Optional[str] = None,
    cpu: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_ram: Optional[int] = None,
    min_storage: Optional[int] = None,
    source: Optional[str] = None,
    condition: Optional[str] = None,
    device_type: Optional[str] = None,
    sort: Optional[str] = "price_asc",
    limit: int = Query(default=50, le=200),
    offset: int = 0,
):
    conn = db.get_conn()
    cur = db.get_cursor(conn)

    filters = []
    params = []

    if q:
        filters.append("title ILIKE %s")
        params.append(f"%{q}%")
    if gpu:
        filters.append("gpu ILIKE %s")
        params.append(f"%{gpu}%")
    if cpu:
        filters.append("cpu ILIKE %s")
        params.append(f"%{cpu}%")
    if min_price is not None:
        filters.append("current_price >= %s")
        params.append(min_price)
    if max_price is not None:
        filters.append("current_price <= %s")
        params.append(max_price)
    if min_ram is not None:
        filters.append("ram_gb >= %s")
        params.append(min_ram)
    if min_storage is not None:
        filters.append("storage_gb >= %s")
        params.append(min_storage)
    if source:
        filters.append("source = %s")
        params.append(source)
    if condition:
        filters.append("condition = %s")
        params.append(condition)
    if device_type:
        filters.append("device_type = %s")
        params.append(device_type)

    where = "WHERE " + " AND ".join(filters) if filters else ""

    sort_map = {
        "price_asc": "current_price ASC",
        "price_desc": "current_price DESC",
        "newest": "created_at DESC",
        "last_seen": "last_seen_at DESC",
    }
    order = sort_map.get(sort, "current_price ASC")

    sql = f"""
        SELECT
            id, source, title, url, image_url, brand,
            device_type, condition, in_stock, cpu, gpu,
            ram_gb, storage_gb, current_price, last_seen_at
        FROM listings
        {where}
        AND current_price IS NOT NULL
        ORDER BY {order}
        LIMIT %s OFFSET %s
    """

    # Fix WHERE clause if no filters
    if not filters:
        sql = sql.replace("AND current_price IS NOT NULL", "WHERE current_price IS NOT NULL")

    params.extend([limit, offset])
    cur.execute(sql, params)
    results = cur.fetchall()

    # Get total count
    count_sql = f"SELECT COUNT(*) FROM listings {where}"
    if not filters:
        count_sql += " WHERE current_price IS NOT NULL"
    else:
        count_sql += " AND current_price IS NOT NULL"

    cur.execute(count_sql, params[:-2])
    total = cur.fetchone()['count']

    cur.close()
    conn.close()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": [dict(r) for r in results]
    }