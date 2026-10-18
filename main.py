from collections import defaultdict
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSIGNED_API_KEY = "ak_5ldh5wmj9jqobyfjqat9e7pr"
EMAIL = "24f3000972@ds.study.iitm.ac.in"


@app.post("/analytics")
async def analytics(request: Request):
    # Verify X-API-Key header (case-insensitive in HTTP headers)
    api_key = request.headers.get("x-api-key")
    if not api_key or api_key != ASSIGNED_API_KEY:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized"},
        )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid JSON"},
        )

    events = body.get("events", [])
    total_events = len(events)
    unique_users = set()
    total_revenue = 0.0
    user_positive_revenue = defaultdict(float)

    for ev in events:
        user = ev.get("user")
        if user is not None:
            unique_users.add(user)

        amt = ev.get("amount", 0)
        try:
            amt = float(amt)
        except (ValueError, TypeError):
            amt = 0.0

        if amt > 0:
            total_revenue += amt
            if user is not None:
                user_positive_revenue[user] += amt

    # Find top_user with highest positive revenue
    if user_positive_revenue:
        top_user = max(
            user_positive_revenue.keys(),
            key=lambda u: user_positive_revenue[u],
        )
    else:
        # Fallback if no positive amounts
        top_user = next(iter(unique_users)) if unique_users else ""

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": len(unique_users),
        "revenue": round(total_revenue, 2),
        "top_user": top_user,
    }


@app.get("/")
def root():
    return {"status": "ok", "service": "Analytics Aggregation Service"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
