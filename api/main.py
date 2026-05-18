from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import search, nlp, history

app = FastAPI(title="PCSorted API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(nlp.router)
app.include_router(history.router)

@app.get("/health")
def health():
    return {"status": "ok"}