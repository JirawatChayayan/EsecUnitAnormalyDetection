from fastapi import FastAPI,Response, status, APIRouter
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from proc.mqtt import MQTT


mqtt = MQTT()

app = FastAPI(
    title="Microcontroller Status",
    description="Status",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

@app.get("/")
async def redirect_typer():
    return RedirectResponse("http://0.0.0.0:8086/docs")


con = APIRouter(
    prefix="/status",
    tags=["status"],
    responses={404: {"description": "Not found"}},
)


@con.get("",status_code=200)
async def get(response:Response):
    return mqtt.dataFromMicro 


app.include_router(con)

@app.on_event("startup")
def startup():
    pass

@app.on_event("shutdown")
def shutdown():
    mqtt.disconnectMQTT()
    pass

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8086, log_level="info",debug = True)
    except KeyboardInterrupt:
        pass
