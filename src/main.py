import uvicorn
from src.pages.router import router as router_pages
from src.applications.router import router as application_router
from src.distribution.router import router as distribution_router
from src.redistribution.router import router as redistribution_router
from fastapi import FastAPI
from src.setting import settings
from src.pages.router import router as pages_router
from src.auth.router import router as auth_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title = 'TheNest')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    application_router,
    prefix=settings.application.prefix,
    tags=[settings.application.tags]
)

app.include_router(
    distribution_router,
    prefix=settings.distribution.prefix,
    tags=[settings.distribution.tags]
)

app.include_router(
    redistribution_router,
    prefix=settings.redistribution.prefix,
    tags=[settings.redistribution.tags]
)

app.include_router(
    pages_router,
    prefix=settings.pages.prefix,
    tags=[settings.pages.tags]
)

app.include_router(auth_router)
app.include_router(router_pages)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
