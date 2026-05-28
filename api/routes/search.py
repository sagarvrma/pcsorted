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

    # GPU: comma-separated list, OR within group, LIKE matching
    if gpu:
        gpu_list = [g.strip() for g in gpu.split(",") if g.strip()]
        if gpu_list:
            gpu_clauses = " OR ".join(["gpu ILIKE %s"] * len(gpu_list))
            filters.append(f"({gpu_clauses})")
            params.extend([f"%{g}%" for g in gpu_list])

    # CPU: comma-separated list, OR within group, LIKE matching
    if cpu:
        cpu_list = [c.strip() for c in cpu.split(",") if c.strip()]
        if cpu_list:
            cpu_clauses = " OR ".join(["cpu ILIKE %s"] * len(cpu_list))
            filters.append(f"({cpu_clauses})")
            params.extend([f"%{c}%" for c in cpu_list])

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

    # Source: comma-separated, OR within group
    if source:
        source_list = [s.strip() for s in source.split(",") if s.strip()]
        if source_list:
            source_clauses = " OR ".join(["source = %s"] * len(source_list))
            filters.append(f"({source_clauses})")
            params.extend(source_list)

    # Condition: comma-separated, OR within group
    if condition:
        condition_list = [c.strip() for c in condition.split(",") if c.strip()]
        if condition_list:
            condition_clauses = " OR ".join(["condition = %s"] * len(condition_list))
            filters.append(f"({condition_clauses})")
            params.extend(condition_list)

    if device_type:
        filters.append("device_type = %s")
        params.append(device_type)

    # Always filter out null prices
    filters.append("current_price IS NOT NULL")

    where = "WHERE " + " AND ".join(filters)

    sort_map = {
        "price_asc": "current_price ASC",
        "price_desc": "current_price DESC",
        "newest": "created_at DESC",
        "last_seen": "last_seen_at DESC",
        "recently_seen": "last_seen_at DESC",
    }
    order = sort_map.get(sort, "current_price ASC")

    sql = f"""
        SELECT
            id, source, title, url, image_url, brand,
            device_type, condition, in_stock, cpu, gpu,
            ram_gb, storage_gb, current_price, last_seen_at
        FROM listings
        {where}
        ORDER BY {order}
        LIMIT %s OFFSET %s
    """

    count_sql = f"SELECT COUNT(*) FROM listings {where}"

    params.extend([limit, offset])
    cur.execute(sql, params)
    results = cur.fetchall()

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