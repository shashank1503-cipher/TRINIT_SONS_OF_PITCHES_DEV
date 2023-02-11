from fastapi import FastAPI

app = FastAPI()

import api

@app.get("/")
async def root():
    routes = [{"name": route.name, "path": route.path} for route in app.routes]
    return {"routes": routes}
app.include_router(api.router, prefix="/api/v1", tags=["api"])
