import uvicorn
from fastapi import FastAPI
from gateapi.api.routers import order, product

app = FastAPI()

app.include_router(order.router)
app.include_router(product.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)