import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from exceptions import ValidationError
from routes.upload import router as upload_router
from routes.status import router as status_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="Audience Uploader API")

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

app.include_router(upload_router)
app.include_router(status_router)