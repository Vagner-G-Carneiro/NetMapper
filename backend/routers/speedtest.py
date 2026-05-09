from fastapi import APIRouter, Request
from fastapi.responses import Response, FileResponse
import os

router = APIRouter(prefix="/backend", tags=["speedtest"])

GARBAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "garbage.bin")


@router.get("/garbage")
def garbage():
    return FileResponse(GARBAGE_PATH, media_type="application/octet-stream")


@router.post("/empty")
async def empty(request: Request):
    await request.body()
    return Response(status_code=200)


@router.get("/getIp")
def get_ip(request: Request):
    ip = request.client.host
    return {"processedString": ip, "rawIspInfo": ""}
