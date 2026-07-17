"""FastAPI Gateway — entrypoint duy nhất của hệ thống V-Nexus Tutor."""
from fastapi import FastAPI

from .auth import UserCreate, UserRead, UserUpdate, auth_backend, fastapi_users
from .routes.chat import router as chat_router
from .routes.diagnostic import router as diagnostic_router
from .routes.parent import router as parent_router
from .routes.practice import router as practice_router
from .routes.teacher import router as teacher_router

app = FastAPI(title="V-Nexus Tutor Gateway")

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"]
)

app.include_router(diagnostic_router)
app.include_router(practice_router)
app.include_router(teacher_router)
app.include_router(parent_router)
app.include_router(chat_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
