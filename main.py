from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List

from database import Base, engine, SessionLocal
from models import Cardapio, TurnoEnum
from schemas import (
    CardapioCreate, CardapioUpdate, CardapioPartialUpdate,
    CardapioOut
)

app = FastAPI(
    title="MS1 - Cardápios",
    version="1.0",
    description="Microsserviço responsável pela gestão de cardápios diários (MS1)."
)

# Cria tabelas (apenas desenvolvimento)
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


BASE_ROUTE = "/api/v1/cardapios"

# ---------- CRUD ----------

@app.post(
    BASE_ROUTE + "/",
    response_model=CardapioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar cardápio",
    description="Cria um novo cardápio para uma determinada data (e turno, se aplicável). "
                "Regra: um por data quando sem turno; um por (data, turno) quando com turno."
)
def criar_cardapio(cardapio: CardapioCreate, db: Session = Depends(get_db)):
    q = db.query(Cardapio).filter(Cardapio.data == cardapio.data)
    if cardapio.turno is None:
        q = q.filter(Cardapio.turno.is_(None))
    else:
        q = q.filter(Cardapio.turno == cardapio.turno)
    if q.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe cardápio para esta data/turno")

    novo = Cardapio(**cardapio.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@app.get(
    BASE_ROUTE + "/listar",
    response_model=List[CardapioOut],
    summary="Listar cardápios",
    description="Lista todos os cardápios, com filtros opcionais por data e turno."
)
def listar_cardapios(
    db: Session = Depends(get_db),
    data: Optional[date] = Query(None, description="Data do cardápio"),
    turno: Optional[TurnoEnum] = Query(None, description="Turno (manhã/tarde/noite)")
):
    query = db.query(Cardapio)
    if data:
        query = query.filter(Cardapio.data == data)
    if turno:
        query = query.filter(Cardapio.turno == turno)

    return query.all()


@app.get(
    BASE_ROUTE + "/hoje",
    response_model=List[CardapioOut],
    summary="Cardápios de hoje",
    description="Retorna todos os cardápios do dia corrente. Se informado, filtra por turno."
)
def cardapios_hoje(
    turno: Optional[TurnoEnum] = Query(None, description="Turno (manhã/tarde/noite)"),
    db: Session = Depends(get_db)
):
    hoje = date.today()
    query = db.query(Cardapio).filter(Cardapio.data == hoje)
    if turno:
        query = query.filter(Cardapio.turno == turno)

    cardapios = query.all()
    if not cardapios:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum cardápio encontrado para hoje"
        )
    return cardapios


@app.get(
    BASE_ROUTE + "/{id}",
    response_model=CardapioOut,
    summary="Detalhar cardápio",
    description="Retorna os detalhes de um cardápio pelo ID."
)
def detalhar_cardapio(id: int, db: Session = Depends(get_db)):
    cardapio = db.query(Cardapio).filter(Cardapio.id == id).first()
    if not cardapio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cardápio não encontrado")
    return cardapio


@app.put(
    BASE_ROUTE + "/{id}",
    response_model=CardapioOut,
    summary="Atualizar cardápio (inteiro)",
    description="Atualiza todos os campos de um cardápio existente."
)
def atualizar_cardapio(id: int, payload: CardapioUpdate, db: Session = Depends(get_db)):
    card = db.query(Cardapio).filter(Cardapio.id == id).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cardápio não encontrado")

    q = db.query(Cardapio).filter(Cardapio.data == payload.data)
    if payload.turno is None:
        q = q.filter(Cardapio.turno.is_(None))
    else:
        q = q.filter(Cardapio.turno == payload.turno)
    conflito = q.filter(Cardapio.id != id).first()
    if conflito:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe cardápio para esta data/turno")

    for k, v in payload.model_dump().items():
        setattr(card, k, v)

    db.commit()
    db.refresh(card)
    return card


@app.patch(
    BASE_ROUTE + "/{id}",
    response_model=CardapioOut,
    summary="Atualizar cardápio (parcial)",
    description="Atualiza apenas os campos enviados no corpo da requisição."
)
def atualizar_cardapio_parcial(id: int, payload: CardapioPartialUpdate, db: Session = Depends(get_db)):
    card = db.query(Cardapio).filter(Cardapio.id == id).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cardápio não encontrado")

    dados = payload.model_dump(exclude_unset=True)
    nova_data = dados.get("data", card.data)
    novo_turno = dados.get("turno", card.turno)

    q = db.query(Cardapio).filter(Cardapio.data == nova_data)
    if novo_turno is None:
        q = q.filter(Cardapio.turno.is_(None))
    else:
        q = q.filter(Cardapio.turno == novo_turno)
    conflito = q.filter(Cardapio.id != id).first()
    if conflito:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe cardápio para esta data/turno")

    for k, v in dados.items():
        setattr(card, k, v)

    db.commit()
    db.refresh(card)
    return card


@app.delete(
    BASE_ROUTE + "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover cardápio",
    description="Remove um cardápio existente."
)
def remover_cardapio(id: int, db: Session = Depends(get_db)):
    card = db.query(Cardapio).filter(Cardapio.id == id).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cardápio não encontrado")

    db.delete(card)
    db.commit()
    return


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
