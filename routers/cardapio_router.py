from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from db.database import get_db
from models.models import Cardapio, TurnoEnum
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String
from schemas.cardapio_schema import (
    CardapioCreate,
    CardapioUpdate,
    CardapioPartialUpdate,
    CardapioOut
)
from services.estoque_service import validate_ids

router = APIRouter()
BASE_ROUTE = "/api/v1/cardapios"


# ------------------------------
# Criar cardápio
# ------------------------------
@router.post(
    BASE_ROUTE + "/",
    response_model=CardapioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar cardápio"
)
def criar_cardapio(cardapio: CardapioCreate, db: Session = Depends(get_db)):
    q = db.query(Cardapio).filter(Cardapio.data == cardapio.data)
    if cardapio.turno is None:
        q = q.filter(Cardapio.turno.is_(None))
    else:
        q = q.filter(func.lower(cast(Cardapio.turno, String)) == cardapio.turno.value.lower())
    if q.first():
        raise HTTPException(status_code=409, detail="Já existe cardápio para esta data/turno")

    validate_ids({
        "prato_principal_ids": cardapio.prato_principal_ids,
        "acompanhamento_ids":  cardapio.acompanhamento_ids,
        "salada_ids":          cardapio.salada_ids,
        "sobremesa_ids":       cardapio.sobremesa_ids,
        "bebida_ids":          cardapio.bebida_ids,
    })

    novo = Cardapio(**cardapio.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


# ------------------------------
# Cardápios de hoje
# ------------------------------
@router.get(
    BASE_ROUTE + "/hoje",
    response_model=List[CardapioOut],
    summary="Cardápios de hoje",
    description="Retorna todos os cardápios do dia corrente. Se informado, filtra por turno (case-insensitive)."
)
def cardapios_hoje(
    turno: Optional[TurnoEnum] = Query(None, description="Turno (manhã/tarde/noite)"),
    db: Session = Depends(get_db)
):
    hoje = date.today()
    query = db.query(Cardapio).filter(Cardapio.data == hoje)
    if turno:
        query = db.query(Cardapio).filter(Cardapio.turno == turno)

    cardapios = query.all()
    if not cardapios:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum cardápio encontrado para hoje"
        )
    return cardapios

# ------------------------------
# Atualizar cardápio (PUT)
# ------------------------------
@router.put(BASE_ROUTE + "/{id}", response_model=CardapioOut)
def atualizar_cardapio(id: int, payload: CardapioUpdate, db: Session = Depends(get_db)):
    card = db.query(Cardapio).filter(Cardapio.id == id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")

    q = db.query(Cardapio).filter(Cardapio.data == payload.data)
    if payload.turno is None:
        q = q.filter(Cardapio.turno.is_(None))
    else:
        q = q.filter(func.lower(cast(Cardapio.turno, String)) == payload.turno.value.lower())
    if q.filter(Cardapio.id != id).first():
        raise HTTPException(status_code=409, detail="Já existe cardápio para esta data/turno")

    validate_ids({
        "prato_principal_ids": payload.prato_principal_ids,
        "acompanhamento_ids":  payload.acompanhamento_ids,
        "salada_ids":          payload.salada_ids,
        "sobremesa_ids":       payload.sobremesa_ids,
        "bebida_ids":          payload.bebida_ids,
    })

    for k, v in payload.model_dump().items():
        setattr(card, k, v)
    db.commit()
    db.refresh(card)
    return card


# ------------------------------
# Atualizar cardápio parcialmente (PATCH)
# ------------------------------
@router.patch(BASE_ROUTE + "/{id}", response_model=CardapioOut)
def atualizar_cardapio_parcial(id: int, payload: CardapioPartialUpdate, db: Session = Depends(get_db)):
    card = db.query(Cardapio).filter(Cardapio.id == id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")

    dados = payload.model_dump(exclude_unset=True)
    nova_data = dados.get("data", card.data)
    novo_turno = dados.get("turno", card.turno)

    q = db.query(Cardapio).filter(Cardapio.data == nova_data)
    if novo_turno is None:
        q = q.filter(Cardapio.turno.is_(None))
    else:
        # se vier TurnoEnum, pega o .value
        valor_turno = novo_turno.value if hasattr(novo_turno, "value") else novo_turno
        q = q.filter(func.lower(cast(Cardapio.turno, String)) == valor_turno.lower())

    if q.filter(Cardapio.id != id).first():
        raise HTTPException(status_code=409, detail="Já existe cardápio para esta data/turno")

    listas_para_validar = {k: v for k, v in dados.items() if k.endswith("_ids")}
    if listas_para_validar:
        validate_ids(listas_para_validar)

    for k, v in dados.items():
        setattr(card, k, v)
    db.commit()
    db.refresh(card)
    return card


# ------------------------------
# Listar cardápios
# ------------------------------
@router.get(BASE_ROUTE + "/listar", response_model=List[CardapioOut])
def listar_cardapios(db: Session = Depends(get_db)):
    return db.query(Cardapio).all()


# ------------------------------
# Obter cardápio por ID
# ------------------------------
@router.get(BASE_ROUTE + "/{id}", response_model=CardapioOut)
def obter_cardapio(id: int, db: Session = Depends(get_db)):
    card = db.query(Cardapio).filter(Cardapio.id == id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    return card


# ------------------------------
# Remover cardápio
# ------------------------------
@router.delete(BASE_ROUTE + "/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_cardapio(id: int, db: Session = Depends(get_db)):
    card = db.query(Cardapio).filter(Cardapio.id == id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Cardápio não encontrado")
    db.delete(card)
    db.commit()
    return None
