from fastapi import APIRouter, HTTPException
import api.db as db

router = APIRouter()

@router.get("/listing/{listing_id}/history")
def get_price_history(listing_id: str):
    conn = db.get_conn()
    cur = db.get_cursor(conn)

    cur.execute(
        "SELECT price, recorded_at FROM price_history WHERE listing_id = %s ORDER BY recorded_at ASC",
        (listing_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="Listing not found")

    return {"history": [dict(r) for r in rows]}