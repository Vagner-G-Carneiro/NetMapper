from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, rooms, measurements, speedtest

app = FastAPI(title="NetMapper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(measurements.router)
app.include_router(speedtest.router)


@app.get("/")
def root():
    return {"status": "ok", "app": "NetMapper"}
