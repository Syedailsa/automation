from fastapi import APIRouter

from app.api.v1 import auth, users, notebooks, sources, outputs, agent, tasks

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth.router)
v1_router.include_router(users.router)
v1_router.include_router(notebooks.router)
v1_router.include_router(sources.router)
v1_router.include_router(outputs.router)
v1_router.include_router(agent.router)
v1_router.include_router(tasks.router)
