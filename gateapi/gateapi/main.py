import uvicorn
from fastapi import FastAPI
from gateapi.api.routers import order, product
from gateapi.api.dependencies import destroy_nameko_pool, config

app = FastAPI()

# Load routes
app.include_router(order.router)
app.include_router(product.router)

# Setting up nameko cluster rpc client pool connections
@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # stopping nameko rpc pool
    destroy_nameko_pool()

if __name__ == "__main__":
    uvicorn.run("gateapi.main:app", host="0.0.0.0", port=config['PORT'], workers=config['WEB_CONCURRENCY'])