from fastapi import FastAPI
from db.database import Base, engine
from routers import cardapio_router
from middlewares.auth_middleware import auth_filter
from configs.cors_config import setup_cors

# Criação das tabelas no banco
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS1 - Cardápios",
    version="1.1",
    description="Gestão de cardápios diários integrando com MS-Estoque (Java) por IDs."
)

setup_cors(app)

#app.middleware("http")(auth_filter)

# Health check
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Microsserviço de cardápios rodando!"}

# Rotas
app.include_router(cardapio_router.router)

# Execução local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
