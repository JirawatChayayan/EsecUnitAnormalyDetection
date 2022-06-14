#!/usr/bin/env python 
import uvicorn
from fastapi import FastAPI
from resultImage.controller import result_reject
from stopMCLog.controller import mc_log
from AITrainingLog.controller import logAI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RESULT SERVER",
    description="EDIT CONFIC BELOW",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(logAI)
app.include_router(result_reject)
app.include_router(mc_log)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8085, log_level="info", debug = True)
