from fastapi import FastAPI
from db.database import Base, engine
from routers import cardapio_router
from middlewares.auth_middleware import auth_filter
from configs.cors_config import setup_cors

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS1 - Cardápios",
    version="1.1",
    description="Gestão de cardápios diários integrando com MS-Estoque (Java) por IDs."
)

setup_cors(app)
#app.middleware("http")(auth_filter)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Microsserviço de cardápios rodando!"}


app.include_router(cardapio_router.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
