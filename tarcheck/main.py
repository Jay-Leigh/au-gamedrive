import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from exceptions import ValidationError
from routes.upload import router as upload_router
from routes.status import router as status_router
from db.database import engine, Base
import models.logging
import db.models

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.create_all(bind=engine)
    _check_migrations_applied()
    yield

app = FastAPI(title="Audience Uploader API", lifespan=lifespan)

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

app.include_router(upload_router)
app.include_router(status_router)

def _check_migrations_applied():
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    from sqlalchemy import inspect, text
    script = ScriptDirectory.from_config(Config("alembic.ini"))
    head = script.get_current_head()
    with engine.connect() as conn:
        if not inspect(engine).has_table("alembic_version"):
            raise RuntimeError("DB not migrated: run `alembic upgrade head`")
        current = conn.execute(text("select version_num from alembic_version")).scalar()
        if current != head:
            raise RuntimeError(f"DB schema stale: at {current}, head is {head}")